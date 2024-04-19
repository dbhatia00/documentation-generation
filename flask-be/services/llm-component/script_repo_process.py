#!/usr/bin/env python3

from utils import load_config, set_environment_variables, num_tokens_from_messages, get_git_files, get_data_files
from database import complete_llm_generation
import sys
import os
import argparse

# Load configuration and set environment variables
config = load_config('config.yaml')
set_environment_variables(config)
ACCESS_TOKEN = os.environ['GIT_ACCESS_TOKEN']
sys.path.append("/database")

# Import database and processing functions
from repo_processor import download_and_process_repo_url
import nest_asyncio
nest_asyncio.apply()

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process a GitHub repository URL.')
parser.add_argument('repo_url', type=str, help='The URL of the GitHub repository to process.')
args = parser.parse_args()

# Supported languages
supported_languages = ['python', 'java', 'javascript']

print(f"Processing repository: {args.repo_url}")

try:
    # Call the main processing function
    download_and_process_repo_url(args.repo_url, supported_languages)
except Exception as e:
    print(f"Error processing repository: {args.repo_url}")
    print(e)
    complete_llm_generation(args.repo_url, False) 

# docker build --no-cache -t doc-gen-py-app:latest .

# docker run -p 8080:80 doc-gen-py-app:latest python script_repo_process.py 'https://github.com/Adarsh9616/Electricity_Billing_System/'

# docker tag doc-gen-py-app:latest 018192622412.dkr.ecr.us-east-1.amazonaws.com/doc-gen:latest

# docker push 018192622412.dkr.ecr.us-east-1.amazonaws.com/doc-gen:latest

# Notes:

# - Add the ability to update status of repo with Failed or Completed
# - Added get_status_by_file









