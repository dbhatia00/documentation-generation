import boto3
import time

from utils import load_config, set_environment_variables, num_tokens_from_messages, get_git_files, get_data_files
import sys
import os
config       = load_config('config.yaml')
set_environment_variables(config)
ACCESS_TOKEN = os.environ['GIT_ACCESS_TOKEN']
sys.path.append("/database")

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from database import get_documentation_by_url, put_new_repository_documentation, get_file_documentation
from repo_processor import process_file, parallel_process_files, download_and_process_repo_url
from langchain_community.document_loaders import GithubFileLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_community.callbacks import get_openai_callback
from ConfluenceChain import ConfluenceChain, Parser
from pymongo import MongoClient
import matplotlib.pyplot as plt
import networkx as nx
from tqdm import tqdm
import pandas as pd
import nest_asyncio
import shutil
nest_asyncio.apply()


sqs                   = boto3.client('sqs', 'us-east-1')
queue_url              = 'https://sqs.us-east-1.amazonaws.com/018192622412/doc-gen'
supported_languages   = ['python', 'java', 'javascript']


def handle_message(message_body):
    # print("Processing repository URL:", message_body)
    logger.info(f"Processing repository URL: {message_body}")
    download_and_process_repo_url(message_body, supported_languages)
    
while True:
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20  # Long polling
    )

    messages = response.get('Messages', [])
    for message in messages:
        handle_message(message['Body'])
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )

    time.sleep(1)
