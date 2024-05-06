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


from services.database.database import watch_mongodb_stream, start_llm_generation

app = Flask(__name__)
dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)

"""
    DESCRIPTION -   A function to handle the get_doc button click
    INPUTS -        Repository URL
    OUTPUTS -       Repository doc or error
    NOTES -         Outward facing (called from the Frontend)
"""


@app.route("/api/get_doc", methods=["POST"])
@app.route("/api/get_doc", methods=["POST"])
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
    repo_url = data.get("repo_url")

    # Check if the repository URL is provided
    if not repo_url:
        # Return an error response if the URL is missing
        return jsonify({"error": "Please provide a GitHub repository URL"}), 400

    api_url = f"https://api.github.com/repos/{repo_url}/contents/"
    response = requests.get(api_url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch source code from GitHub"}), 500

    repo_url = "https://github.com/" + repo_url
    url_to_process_repo = f"https://bjxdbdicckttmzhrhnpl342k2q0pcthx.lambda-url.us-east-1.on.aws/?repo_url={repo_url}"
    # LLM should not start put the repo in the status database. It might cause sync issues since we start listening straight away
    start_llm_generation(repo_url)
    requests.get(url_to_process_repo)

    database_response = watch_mongodb_stream(repo_url)

    return jsonify({"doc_content": database_response.model_dump()})


"""
    DESCRIPTION -   A function to handle the push to repo button click
    INPUTS -        repo_url: Modified text from frontend
    OUTPUTS -       Success message, a test_branch with the modified document
    NOTES -         Outward facing (called from the Frontend)
"""


@app.route("/api/push_edits", methods=["POST"])
def push_edits():
    try:
        # Extract JSON data from the request
        data = request.get_json()

        # Retrieve the repository URL and new doc content from the JSON data
        repo_url = data.get("repo_url")
        new_doc_content = data.get("doc_content")

        # Check if the repository URL and new doc content are provided
        if not repo_url or not new_doc_content:
            # Return an error response if either the repository URL or new doc content is missing
            return (
                jsonify(
                    {
                        "error": "Please provide a GitHub repository URL and new doc content"
                    }
                ),
                400,
            )

        # use github access token from oauth instead of the personal token for authorization
        authorization_header = request.headers.get("Authorization")

        # Construct the GitHub API URL to modify the doc file
        api_url = (
            f"https://api.github.com/repos/{repo_url}/contents/AUTOGEN-DOCUMENTATION.md"
        )

        # Set headers for the GitHub API request
        headers = {
            "Authorization": authorization_header,
            "Accept": "application/vnd.github.v3+json",
        }

        # Check if the test branch exists
        branch_url = (
            f"https://api.github.com/repos/{repo_url}/branches/documentation-generation"
        )
        branch_response = requests.get(branch_url, headers=headers)

        if branch_response.status_code == 404:
            # Branch doesn't exist, create it
            create_branch_url = f"https://api.github.com/repos/{repo_url}/git/refs"
            mainSHA = getBranchSHA(repo_url, headers, "main")
            create_branch_params = {
                "ref": "refs/heads/documentation-generation",
                "sha": mainSHA,
            }
            create_branch_response = requests.post(
                create_branch_url, headers=headers, json=create_branch_params
            )

            if create_branch_response.status_code != 201:
                return jsonify({"error": "Failed to create branch"}), 500

        # Depending on if the doc exists already, alter the params passed to the request
        doc_url = f"https://api.github.com/repos/{repo_url}/contents/AUTOGEN-DOCUMENTATION.md?ref=documentation-generation"
        doc_response = requests.get(doc_url, headers=headers)
        if doc_response.status_code == 200:
            doc_sha = doc_response.json().get("sha")
            params = {
                "message": "Generated Documentation",
                "content": base64.b64encode(new_doc_content.encode()).decode(),
                "branch": "documentation-generation",
                "sha": doc_sha,
            }
        else:
            params = {
                "message": "Generated Documentation",
                "content": base64.b64encode(new_doc_content.encode()).decode(),
                "branch": "documentation-generation",
            }

        # Push changes to the test branch
        response = requests.put(api_url, headers=headers, json=params)

        if response.status_code == 201:
            # Return a success response if the file is created successfully
            return jsonify({"success": "Doc created successfully"}), 200
        elif response.status_code == 200:
            # Return a success response if the doc is updated successfully
            return jsonify({"success": "Doc updated successfully"}), 200
        else:
            # Return an error response if the file creation fails
            return jsonify({"error": f"Failed to create file: {response.text}"}), 500
    except Exception as e:
        # Return an error response if an exception occurs
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


"""
    DESCRIPTION -   Retrieve the SHA of the latest commit on the specified branch of the GitHub repository.

    INPUTS -        repo_url: The URL of the GitHub repository.
                    headers: Headers containing the authorization token for making GitHub API requests.
                    branch: The name of the branch for which to retrieve the SHA.
    OUTPUTS -       The SHA of the latest commit on the specified branch, or an error message if retrieval fails.
    NOTES -         Helper function, local to this file
"""


def getBranchSHA(repo_url, headers, branch):
    # Construct the URL to fetch information about the specified branch
    branch_url = f"https://api.github.com/repos/{repo_url}/branches/{branch}"

    # Send a GET request to retrieve branch information
    branch_response = requests.get(branch_url, headers=headers)

    # Check the response status code
    if branch_response.status_code == 200:
        # Extract branch data from the response
        branch_data = branch_response.json()

        # Retrieve the SHA of the latest commit on the specified branch
        sha_of_latest_commit = branch_data["commit"]["sha"]

        # Convert the SHA to a string and return it
        return str(sha_of_latest_commit)
    else:
        # Return an error message if retrieval fails
        return (
            jsonify(
                {"error": f"Failed to retrieve SHA of latest commit on {branch} branch"}
            ),
            500,
        )


@app.route("/api/get_access_token", methods=["GET"])
@app.route("/api/get_access_token", methods=["GET"])
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
        client_code = request.args.get("code")

        if not client_code:
            # Return an error response if the code is missing
            return jsonify({"error": "Login error with github"}), 400

        client_id, client_secret = retrieve_client_info()
        params = (
            "?client_id="
            + client_id
            + "&client_secret="
            + client_secret
            + "&code="
            + client_code
        )
        get_access_token_url = "http://github.com/login/oauth/access_token" + params
        headers = {"Accept": "application/json"}

        access_token_response = requests.get(get_access_token_url, headers=headers)

        if access_token_response.status_code == 200:
            return jsonify(access_token_response.json()), 200
        else:
            return (
                jsonify(
                    {
                        "error": f"Failed to fetch access token: {access_token_response.text}"
                    }
                ),
                500,
            )

            return (
                jsonify(
                    {
                        "error": f"Failed to fetch access token: {access_token_response.text}"
                    }
                ),
                500,
            )

    except Exception as e:
        # Return an error response if an exception occurs
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


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
    with open("token_server.json") as f:
        tokens = json.load(f)
    client_id = str(tokens.get("client_id"))
    client_secret = str(tokens.get("client_secret"))
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
            return jsonify({"error": "Login error with Confluence"}), 400

        confluence_client_id, confluence_client_secret = retrieve_confluence_info()

        params = {
            "grant_type": "authorization_code",
            "client_id": confluence_client_id,
            "client_secret": confluence_client_secret,
            "code": client_code,
            "redirect_uri": "http://localhost:3000/",
        }

        get_access_token_url = "https://auth.atlassian.com/oauth/token"
        headers = {"Content-Type": "application/json"}

        confluence_access_token_response = requests.post(
            get_access_token_url, json=params, headers=headers
        )
        response_json = confluence_access_token_response.json()

        if confluence_access_token_response.status_code == 200:
            get_cloud_id_url = (
                "https://api.atlassian.com/oauth/token/accessible-resources"
            )
            headers = {
                "Authorization": "Bearer " + response_json["access_token"],
                "Accept": "application/json",
            }
            cloudid_response = requests.get(get_cloud_id_url, headers=headers)

            if cloudid_response.status_code == 200:
                refresh_token = response_json["refresh_token"]
                cloud_id = cloudid_response.json()[0]["id"]
                # TODO: add refresh token & cloud id to db
                return (
                    jsonify(
                        {
                            "access_token": response_json["access_token"],
                            "cloud_id": cloud_id,
                            "site_url": cloudid_response.json()[0]["url"],
                        }
                    ),
                    200,
                )
            else:
                return (
                    jsonify(
                        {
                            "error": f"Failed to fetch confluence cloud id: {cloudid_response.text}"
                        }
                    ),
                    500,
                )

        else:
            return (
                jsonify(
                    {
                        "error": f"Failed to fetch confluence access token: {confluence_access_token_response.text}"
                    }
                ),
                500,
            )

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


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
    with open("token_server.json") as f:
        tokens = json.load(f)
    confluence_client_id = str(tokens.get("confluence_client_id"))
    confluence_client_secret = str(tokens.get("confluence_client_secret"))
    return confluence_client_id, confluence_client_secret


"""
    DESCRIPTION -   A function that creates a confluence space and pages for a given repository
    INPUTS -        Repository URL, confluence domain, email, api token
    OUTPUTS -       Message of success or error
    NOTES -         Outward facing (called from the Frontend)
"""


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

    # Check if the required data is provided
    if not repo_url or not cloud_id or not confluence_access_code:
        # Return an error response if any of the required data is missing
        return jsonify({"error": "Please provide all variables"}), 400

    success, space_key = services.confluence.api.handle_repo_confluence_pages(
        repo_url=repo_url,
        cloud_id=cloud_id,
        confluence_access_code=confluence_access_code,
        commit_hash="REPLACE",
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
    # Check if the 'ref' key is in the payload
    if "ref" not in payload:
        return jsonify({"message": f"No ref key in payload{payload}"}), 400
    if payload["ref"] == "refs/heads/main":
        logging.info("New commit to main branch detected.")
        for commit in payload["commits"]:
            # TODO: Replace this with the documentation regeneration logic
            logging.info(f"Commit ID: {commit['id']}")
            logging.info(f"Commit message: {commit['message']}")
            # Additional processing here if needed

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
                    "details": response.errors.message,
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
