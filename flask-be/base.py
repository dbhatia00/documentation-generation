# backend/app.py
from flask import Flask, jsonify, request
import requests

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

if __name__ == '__main__':
    app.run(debug=True)
