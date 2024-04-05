# backend/app.py
from flask import Flask, jsonify, request
import requests
import base64
import json

app = Flask(__name__)

@app.route('/api/get_readme', methods=['POST'])
def get_readme():
    data = request.get_json()
    repo_url = data.get('repo_url')
    print(repo_url)
    if not repo_url:
        return jsonify({'error': 'Please provide a GitHub repository URL'}), 400

    api_url = f'https://api.github.com/repos/{repo_url}/readme'
    response = requests.get(api_url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch README from GitHub'}), 500

    readme_content = response.json().get('content', '')
    return jsonify({'readme_content': readme_content})


@app.route('/api/push_edits', methods=['POST'])
def push_edits():
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        new_readme_content = data.get('readme_content')

        if not repo_url or not new_readme_content:
            return jsonify({'error': 'Please provide a GitHub repository URL and new readme content'}), 400
        
        # retrieve github token from json file
        with open('token.json') as f:
            tokens = json.load(f)
        github_token = str(tokens.get('github_token'))
        
        api_url = f'https://api.github.com/repos/{repo_url}/contents/README.md'
        headers = {
            'Authorization': 'token ' + github_token, 
            'Accept': 'application/vnd.github.v3+json'
        }

        # Check if the branch exists
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

        # After creating the branch, retrieve the SHA of the latest README commit on the test-branch
        # Retrieve the SHA of the README.md file in the test-branch
        readme_url = f'https://api.github.com/repos/{repo_url}/contents/README.md?ref=test-branch'
        readme_response = requests.get(readme_url, headers=headers)

        if readme_response.status_code == 200:
            readme_data = readme_response.json()
            readme_sha = readme_data.get('sha')
        else:
            return jsonify({'error': 'Failed to retrieve SHA of README.md file in test-branch'}), 500
        
        # Push changes to the new branch
        params = {
            'message': 'Updated README',
            'content': base64.b64encode(new_readme_content.encode()).decode(),
            'branch': 'test-branch',
            'sha': readme_sha
        }
        response = requests.put(api_url, headers=headers, json=params)

        if response.status_code == 200:
            return jsonify({'success': 'README updated successfully'}), 200
        else:
            return jsonify({'error': f'Failed to update README: {response.text}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

def getBranchSHA(repo_url, headers, branch):
    # Retrieve the SHA of the latest commit on the main branch
    main_branch_url = f'https://api.github.com/repos/{repo_url}/branches/{branch}'
    main_branch_response = requests.get(main_branch_url, headers=headers)

    if main_branch_response.status_code == 200:
        main_branch_data = main_branch_response.json()
        sha_of_latest_commit = main_branch_data['commit']['sha']
    else:
        return jsonify({'error': 'Failed to retrieve SHA of latest commit on {branch} branch'}), 500

    # Use the retrieved SHA as the base commit for creating the new branch
    return str(sha_of_latest_commit)



if __name__ == '__main__':
    app.run(debug=True)
