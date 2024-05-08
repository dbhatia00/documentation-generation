import hmac
import os
import dotenv
from flask import Flask, abort, jsonify, request
from requests.auth import HTTPBasicAuth
import requests
import base64
import json
import services.confluence.api
import logging
from urllib.parse import urlparse


from services.database.database import (
    watch_mongodb_stream,
    start_llm_generation,
    get_all_tokens,
    update_single_confluence_oauth,
)

app = Flask(__name__)
dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)

@app.route('/api/get_doc', methods=['POST'])
def get_doc():
    """
    DESCRIPTION: A function to handle the get_doc button click.
    
    INPUTS:
    - Repository URL
    
    OUTPUTS:
    - Repository doc or error
    
    NOTES:
    - Outward facing (called from the Frontend)
    """
    # Extract JSON data from the request
    data = request.get_json()

    # Retrieve the repository URL from the JSON data
    repo_url = data.get('repo_url')

    # Check if the repository URL is provided
    if not repo_url:
        # Return an error response if the URL is missing
        return jsonify({'error': 'Please provide a GitHub repository URL'}), 400

    api_url = f'https://api.github.com/repos/{repo_url}/contents/'
    response = requests.get(api_url)
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch source code from GitHub'}), 500
    
    commit_hash = get_latest_commit_hash(repo_url)
    if commit_hash is None:
        return jsonify({'error': 'Failed to fetch commit hash from GitHub'}), 500

    repo_url = "https://github.com/" + repo_url
    url_to_process_repo = f"https://bjxdbdicckttmzhrhnpl342k2q0pcthx.lambda-url.us-east-1.on.aws/?repo_url={repo_url}"
    #LLM should not start put the repo in the status database. It might cause sync issues since we start listening straight away
    start_llm_generation(repo_url)
    requests.get(url_to_process_repo)

    database_response = watch_mongodb_stream(repo_url)
    
    return jsonify({'doc_content': database_response.model_dump(), 'commit_hash': commit_hash}), 200


def get_latest_commit_hash(repo_url):
    """
    DESCRIPTION: Retrieves the latest commit hash for a given GitHub repository URL.

    INPUTS:
    - repo_url (str): The URL of the repository.

    OUTPUTS:
    - The latest commit hash (str). If the request to retrieve the commit hash fails, None is returned.

    NOTES:
    - Internal Helper function
    """
    commit_hash_url = f"https://api.github.com/repos/{repo_url}/commits"
    commit_hash_response = requests.get(commit_hash_url)

    commit_hash = commit_hash_response.json()[0]["sha"]

    if commit_hash_response.status_code != 200:
        return None
    return commit_hash


@app.route('/api/get_access_token', methods=['GET'])
def get_access_token():
    """
    DESCRIPTION: A function to get the access token from GitHub.
    
    INPUTS:
    - None
    
    OUTPUTS:
    - Access token or error
    
    NOTES:
    - Outward facing (called from the Frontend)
    """
    try:
        # Extract client code from frontend
        client_code = request.args.get('code')

        if not client_code:
            # Return an error response if the code is missing
            return jsonify({'error': 'Login error with github'}), 400

        client_id, client_secret = retrieve_client_info()
        params = '?client_id=' + client_id + '&client_secret=' + client_secret + '&code=' + client_code
        get_access_token_url = "http://github.com/login/oauth/access_token" + params
        headers = { 'Accept': 'application/json'}

        access_token_response = requests.get(get_access_token_url, headers=headers)

        if access_token_response.status_code == 200:
            return jsonify(access_token_response.json()), 200
        else:
            return jsonify({'error': f'Failed to fetch access token: {access_token_response.text}'}), 500

    except Exception as e:
        # Return an error response if an exception occurs
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


def retrieve_client_info(): 
    """
    DESCRIPTION: Retrieve GitHub client ID and client secret from a JSON file named 'token_server.json'.

    INPUTS:
    - None

    OUTPUTS:
    - Tuple containing client ID and client secret (both as strings).

    NOTES:
    - Internal helper function
    """
    # Retrieve GitHub token from a JSON file
    with open('token_server.json') as f:
        tokens = json.load(f)
    client_id = str(tokens.get('client_id'))
    client_secret = str(tokens.get('client_secret'))
    return client_id, client_secret


@app.route("/api/get_confluence_token", methods=["GET"])
def get_confluence_token():
    """
    DESCRIPTION: A function to get the Confluence access token.
    
    INPUTS:
    - None
    
    OUTPUTS:
    - Confluence access token or error
    
    NOTES:
    - Outward facing (called from the Frontend)
    """
    try:
        client_code = request.args.get("code")
        if not client_code:
            return jsonify({'error': 'Login error with Confluence'}), 400

        confluence_client_id, confluence_client_secret = retrieve_confluence_info()

        params = {
            'grant_type': 'authorization_code',
            'client_id': confluence_client_id,
            'client_secret': confluence_client_secret,
            'code': client_code,
            'redirect_uri': 'http://localhost:3000/'
        }

        get_access_token_url = 'https://auth.atlassian.com/oauth/token'
        headers = { 'Content-Type': 'application/json'}

        confluence_access_token_response = requests.post(get_access_token_url, json=params, headers=headers)
        response_json = confluence_access_token_response.json() 

        if confluence_access_token_response.status_code == 200:
            get_cloud_id_url = 'https://api.atlassian.com/oauth/token/accessible-resources'
            headers = { 'Authorization': 'Bearer ' + response_json['access_token'], 
                        'Accept': 'application/json',}
            cloudid_response = requests.get(get_cloud_id_url, headers=headers)

            if cloudid_response.status_code == 200:
                refresh_token = response_json["refresh_token"]
                cloud_id = cloudid_response.json()[0]["id"]
                return (
                    jsonify(
                        {
                            "access_token": response_json["access_token"],
                            "cloud_id": cloud_id,
                            "site_url": cloudid_response.json()[0]["url"],
                            "refresh_token": refresh_token,
                        }
                    ),
                    200,
                )
            else:
                return jsonify({'error': f'Failed to fetch confluence cloud id: {cloudid_response.text}'}), 500

        else:
            return jsonify({'error': f'Failed to fetch confluence access token: {confluence_access_token_response.text}'}), 500

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


def retrieve_confluence_info():
    """
    DESCRIPTION: Retrieve Confluence client ID and client secret from a JSON file named 'token_server.json'.

    INPUTS:
    - None

    OUTPUTS:
    - Tuple containing Confluence client ID and client secret (both as strings).

    NOTES:
    - Internal Helper function
    """
    with open('token_server.json') as f:
        tokens = json.load(f)
    confluence_client_id = str(tokens.get('confluence_client_id'))
    confluence_client_secret = str(tokens.get('confluence_client_secret'))
    return confluence_client_id, confluence_client_secret


def get_new_confluence_token(refresh_token, repo_url, cloud_id):
    """
    Retrieves a new Confluence access token for the provided repository URL and cloud ID. Also replaces the existing refresh token with the new one.

    Args:
        repo_url (str): The URL of the repository.
        cloud_id (str): The ID of the Confluence site.

    Returns:
        str: The new Confluence access token, or None if the token retrieval fails.
    """
    confluence_client_id, confluence_client_secret = retrieve_confluence_info()

    params = {
        "grant_type": "refresh_token",
        "client_id": confluence_client_id,
        "client_secret": confluence_client_secret,
        "refresh_token": refresh_token,
    }

    refresh_token_url = "https://auth.atlassian.com/oauth/token"
    headers = {"Content-Type": "application/json"}

    refresh_token_response = requests.post(
        refresh_token_url, json=params, headers=headers
    )
    response_json = refresh_token_response.json()

    if refresh_token_response.status_code == 200:
        new_refresh_token = response_json["refresh_token"]
        new_access_token = response_json["access_token"]
        # db: replace with new refresh token
        update_single_confluence_oauth(
            repository_url=repo_url,
            refresh_token=new_refresh_token,
            confluence_site_cloud_id=cloud_id,
        )
        return new_access_token
    else:
        return None


@app.route("/api/create_confluence", methods=["POST"])
def create_confluence():
    """
    DESCRIPTION -   A function that creates a confluence space and pages for a given repository
    INPUTS -        repo_url: The URL of the repository.
                    cloud_id: The ID of the Confluence cloud.
                    confluence_access_code: The access code for Confluence API.
    OUTPUTS -       If successful, returns the space key of the created space. If unsuccessful, returns an error message.
    NOTES -         Outward facing (called from the Frontend).
    """
    # Extract data from the request
    data = request.get_json()
    repo_url = data.get("repo_url")
    cloud_id = data.get("cloud_id")
    confluence_access_code = data.get("confluence_access_code")
    commit_hash = data.get("commit_hash")
    refresh_token = data.get("refresh_token")

    # Check if the required data is provided
    if (
        not repo_url
        or not cloud_id
        or not confluence_access_code
        or not commit_hash
        or not refresh_token
    ):
        # Return an error response if any of the required data is missing
        return jsonify({"error": "Please provide all variables"}), 400

    # adds {cloud_id: refresh_token} to db for repo_url
    update_single_confluence_oauth(
        repository_url=repo_url,
        confluence_site_cloud_id=cloud_id,
        refresh_token=refresh_token,
    )

    success, space_key = services.confluence.api.handle_repo_confluence_pages(
        repo_url=repo_url,
        cloud_id=cloud_id,
        confluence_access_code=confluence_access_code,
        commit_hash=commit_hash,
    )

    if not success:
        # Return an error response if the update fails
        return jsonify({"error": "Failed to update Confluence pages"}), 500
    else:
        return (
            jsonify(
                {
                    "spaceKey": space_key,
                }
            ),
            200,
        )


# Your webhook secret, which you must set both here and in your GitHub webhook settings
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "default_secret_if_not_set")


@app.route("/webhook", methods=["POST"])
def handle_webhook():

    logging.info("Webhook triggered")

    # Verify the request signature
    header_signature = request.headers.get("X-Hub-Signature")
    if header_signature is None:
        abort(400, "Missing X-Hub-Signature required for webhook validation")

    sha_name, signature = header_signature.split("=")
    if sha_name != "sha1":
        abort(501, "Operation not supported: We expect HMAC-SHA1 signatures")

    # Create a hash using the secret and compare it to the request signature
    mac = hmac.new(bytes(WEBHOOK_SECRET, "utf-8"), msg=request.data, digestmod="sha1")
    if not hmac.compare_digest(mac.hexdigest(), signature):
        abort(400, "Invalid signature")

    # Process the payload
    payload = request.json
    # Check if the 'ref' key is in the payload (Ensure that package is correct)
    if "repository" in payload and "html_url" in payload["repository"]:
        repo_url = payload["repository"]["html_url"]
        logging.info(f"Received a webhook for repository: {repo_url}")
        parsed_url = urlparse(repo_url)
        path_parts = parsed_url.path.strip("/").split("/")
        repo_url = "/".join(path_parts[-2:])
        logging.info(f"now repository url: {repo_url}")
    else:
        return (
            jsonify({"message": "Invalid payload format, missing repository URL"}),
            400,
        )

    # error in payload, quit before regeneration attempt
    if "ref" not in payload:
        return jsonify({"message": f"No ref key in payload{payload}"}), 400

    # TODO: should we return 500 error when any of the regeneration steps fail?
    if payload["ref"] == "refs/heads/main":
        logging.info("New commit to main branch detected.")
        for commit in payload["commits"]:
            # Spit out some basic info
            logging.info(f"Commit ID: {commit['id']}")
            logging.info(f"Commit message: {commit['message']}")

            # Directly call the internal documentation generation function
            result, status = generate_documentation(repo_url)
            if status == 200:
                logging.info("LLM document generation successful.")
            else:
                logging.error("LLM document generation failed.")

            # Generate the confluence space for each registered confluence site
            commit_hash = get_latest_commit_hash(repo_url)
            if commit_hash is None:
                logging.error("Failed to fetch commit hash from GitHub")

            tokens_dict = get_all_tokens(repo_url)
            for cloud_id, refresh_token in tokens_dict.items():
                confluence_access_code = get_new_confluence_token(
                    refresh_token=refresh_token,
                    repo_url=repo_url,
                    cloud_id=cloud_id,
                )
                success, space_key = (
                    services.confluence.api.handle_repo_confluence_pages(
                        repo_url=repo_url,
                        cloud_id=cloud_id,
                        confluence_access_code=confluence_access_code,
                        commit_hash=commit_hash,
                    )
                )
                if not success:
                    logging.error("Failed to update Confluence pages")
                else:
                    logging.info(
                        f"Confluence pages updated successfully. Site: {cloud_id}, Space key: {space_key}"
                    )

    return "OK", 200


@app.route("/setup-webhook", methods=["POST"])
def setup_webhook():
    data = request.get_json()
    repo_url = data.get("repo_url")
    if not repo_url:
        return (
            jsonify({"error": "Please provide a GitHub repository URL"}),
            400,
        )

    repo_owner = repo_url.split("/")[0]
    repo_name = repo_url.split("/")[1]

    # Extract the GitHub OAuth token from the Authorization header
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        return jsonify({"error": "Authorization header is missing"}), 401

    payload_url = os.getenv("WEBHOOK_PAYLOAD_URL")
    webhook_secret = os.getenv("WEBHOOK_SECRET")

    if not payload_url or not webhook_secret:
        return (
            jsonify(
                {
                    "error": f"Missing required parameters: webhook_payload_url and webhook_secret{payload_url},{webhook_secret}"
                }
            ),
            400,
        )
    logging.info("logging sth here")
    # Call the function to create a webhook
    response = create_webhook(
        authorization_header, repo_owner, repo_name, payload_url, webhook_secret
    )
    if response.get("id"):
        return (
            jsonify(
                {
                    "message": "Webhook created successfully",
                    "webhook_id": response["id"],
                }
            ),
            201,
        )
    else:
        logging.info(response)
        return (
            jsonify(
                {
                    "error": "Failed to create webhook",
                    "details": response["errors"][0]["message"],
                }
            ),
            500,
        )


def create_webhook(
    authorization_header, repo_owner, repo_name, webhook_url, webhook_secret
):
    """Create a GitHub webhook."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/hooks"
    headers = {
        "Authorization": authorization_header,
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "config": {
            "url": webhook_url,
            "content_type": "json",
            "secret": webhook_secret,
        },
        "events": ["push", "pull_request", "create"],
        "active": True,
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()


def generate_documentation(repo_url):
    """
    Generate documentation for the given repository URL.
    """
    api_url = f"https://api.github.com/repos/{repo_url}/contents/"
    response = requests.get(api_url)

    if response.status_code != 200:
        return {"error": "Failed to fetch source code from GitHub"}, 500

    repo_url = "https://github.com/" + repo_url
    url_to_process_repo = f"https://bjxdbdicckttmzhrhnpl342k2q0pcthx.lambda-url.us-east-1.on.aws/?repo_url={repo_url}"

    start_llm_generation(repo_url)
    requests.get(url_to_process_repo)

    database_response = watch_mongodb_stream(repo_url)

    return {"doc_content": database_response.model_dump()}, 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
