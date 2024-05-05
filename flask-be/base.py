from flask import Flask, jsonify, request
from requests.auth import HTTPBasicAuth
import requests
import base64
import json
import services.confluence.api

from services.database.database import watch_mongodb_stream, start_llm_generation
app = Flask(__name__)

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
    
    repo_url = "https://github.com/" + repo_url
    url_to_process_repo = f"https://bjxdbdicckttmzhrhnpl342k2q0pcthx.lambda-url.us-east-1.on.aws/?repo_url={repo_url}"
    #LLM should not start put the repo in the status database. It might cause sync issues since we start listening straight away
    start_llm_generation(repo_url)
    requests.get(url_to_process_repo)

    database_response = watch_mongodb_stream(repo_url)
    
    return jsonify({'doc_content': database_response.model_dump()})


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

@app.route('/api/get_confluence_token', methods=['GET'])
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
        client_code = request.args.get('code')
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

            if confluence_access_token_response.status_code == 200:
                return jsonify({'access_token': response_json['access_token'], 'cloud_id' : cloudid_response.json()[0]['id']}), 200
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

"""
    DESCRIPTION -   A function that creates a confluence space and pages for a given repository
    INPUTS -        repo_url: The URL of the repository.
                    cloud_id: The ID of the Confluence cloud.
                    confluence_access_code: The access code for Confluence API.
    OUTPUTS -       Message of success or error.
    NOTES -         Outward facing (called from the Frontend).
"""
@app.route("/api/create_confluence", methods=["POST"])
def create_confluence():
    """
    DESCRIPTION: A function that creates a Confluence space and pages for a given repository.
    
    INPUTS:
    - Repository URL, confluence domain, email, api token
    
    OUTPUTS:
    - Message of success or error
    
    NOTES:
    - Outward facing (called from the Frontend)
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

    success = services.confluence.api.handle_repo_confluence_pages(
        repo_url=repo_url,
        cloud_id=cloud_id,
        confluence_access_code=confluence_access_code,
        commit_hash="TEST",
    )

    if not success:
        # Return an error response if the update fails
        return jsonify({"error": "Failed to update Confluence pages"}), 500
    else:
        return jsonify({"success": "Confluence pages updated successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)
