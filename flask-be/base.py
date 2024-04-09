# backend/app.py
from flask import Flask, jsonify, request
import requests
import base64
import json

app = Flask(__name__)

'''
    DESCRIPTION -   A function to handle the get_readme button click
    INPUTS -        Repository URL
    OUTPUTS -       Repository README or error
    NOTES -         Outward facing (called from the Frontend)
'''
@app.route('/api/get_readme', methods=['POST'])
def get_readme():
    # Extract JSON data from the request
    data = request.get_json()

    # Retrieve the repository URL from the JSON data
    repo_url = data.get('repo_url')

    # Check if the repository URL is provided
    if not repo_url:
        # Return an error response if the URL is missing
        return jsonify({'error': 'Please provide a GitHub repository URL'}), 400

    # Construct the GitHub API URL to fetch the README file
    # TODO: Replace this with the documentation generation logic
    api_url = f'https://api.github.com/repos/{repo_url}/readme'

    # Send a GET request to fetch the README file from GitHub
    response = requests.get(api_url)

    # Check the response status code
    if response.status_code != 200:
        # Return an error response if fetching the README fails
        return jsonify({'error': 'Failed to fetch README from GitHub'}), 500

    # Extract the content of the README file from the response
    readme_content = response.json().get('content', '')

    # Return the content of the README file as a JSON response
    return jsonify({'readme_content': readme_content})


'''
    DESCRIPTION -   A function to handle the push to repo button click
    INPUTS -        repo_url: Modified text from frontend
    OUTPUTS -       Success message, a test_branch with the modified document
    NOTES -         Outward facing (called from the Frontend)
'''
@app.route('/api/push_edits', methods=['POST'])
def push_edits():
    try:
        # Extract JSON data from the request
        data = request.get_json()

        # Retrieve the repository URL and new README content from the JSON data
        repo_url = data.get('repo_url')
        new_readme_content = data.get('readme_content')

        # Check if the repository URL and new README content are provided
        if not repo_url or not new_readme_content:
            # Return an error response if either the repository URL or new README content is missing
            return jsonify({'error': 'Please provide a GitHub repository URL and new readme content'}), 400
        
        # use github access token from oauth instead of the personal token for authorization
        authorization_header = request.headers.get('Authorization')
        
        # # Retrieve GitHub token from a JSON file
        # with open('token.json') as f:
        #     tokens = json.load(f)
        # github_token = str(tokens.get('github_token'))

        # Construct the GitHub API URL to modify the README file
        api_url = f'https://api.github.com/repos/{repo_url}/contents/README.md'
        
        # Set headers for the GitHub API request
        headers = {
            'Authorization': authorization_header,
            'Accept': 'application/vnd.github.v3+json'
        }

        # TODO: Dynamically create a unique branch name to avoid collisions (i.e. this should always 404)
        # Check if the test branch exists
        branch_url = f'https://api.github.com/repos/{repo_url}/branches/test-branch'
        branch_response = requests.get(branch_url, headers=headers)

        if branch_response.status_code == 404:
            # Branch doesn't exist, create it
            create_branch_url = f'https://api.github.com/repos/{repo_url}/git/refs'
            mainSHA = getBranchSHA(repo_url, headers, "main")
            create_branch_params = {
                'ref': 'refs/heads/test-branch',
                'sha': mainSHA
            }
            create_branch_response = requests.post(create_branch_url, headers=headers, json=create_branch_params)

            if create_branch_response.status_code != 201:
                return jsonify({'error': 'Failed to create branch'}), 500

        # Retrieve the SHA of the README.md file in the test branch
        # TODO: Replace this with logic to create + push a new file with the documentation
        readme_url = f'https://api.github.com/repos/{repo_url}/contents/README.md?ref=test-branch'
        readme_response = requests.get(readme_url, headers=headers)

        if readme_response.status_code == 200:
            readme_data = readme_response.json()
            readme_sha = readme_data.get('sha')
        else:
            return jsonify({'error': 'Failed to retrieve SHA of README.md file in test branch'}), 500
        
        # Push changes to the test branch
        params = {
            'message': 'Updated README',
            'content': base64.b64encode(new_readme_content.encode()).decode(),
            'branch': 'test-branch',
            'sha': readme_sha
        }
        response = requests.put(api_url, headers=headers, json=params)

        if response.status_code == 200:
            # Return a success response if the README is updated successfully
            return jsonify({'success': 'README updated successfully'}), 200
        else:
            # Return an error response if the README update fails
            return jsonify({'error': f'Failed to update README: {response.text}'}), 500
    except Exception as e:
        # Return an error response if an exception occurs
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


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
    branch_url = f'https://api.github.com/repos/{repo_url}/branches/{branch}'

    # Send a GET request to retrieve branch information
    branch_response = requests.get(branch_url, headers=headers)

    # Check the response status code
    if branch_response.status_code == 200:
        # Extract branch data from the response
        branch_data = branch_response.json()

        # Retrieve the SHA of the latest commit on the specified branch
        sha_of_latest_commit = branch_data['commit']['sha']

        # Convert the SHA to a string and return it
        return str(sha_of_latest_commit)
    else:
        # Return an error message if retrieval fails
        return jsonify({'error': f'Failed to retrieve SHA of latest commit on {branch} branch'}), 500

@app.route('/api/get_access_token', methods=['GET'])
def get_access_token():
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
    # Retrieve GitHub token from a JSON file
    with open('token.json') as f:
        tokens = json.load(f)
    client_id = str(tokens.get('client_id'))
    client_secret = str(tokens.get('client_secret'))
    return client_id, client_secret


if __name__ == '__main__':
    app.run(debug=True)
