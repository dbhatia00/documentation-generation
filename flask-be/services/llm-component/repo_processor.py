from database import add_file_to_repository, get_documentation_by_url, put_new_repository_documentation, get_file_documentation
from utils import load_config, set_environment_variables, num_tokens_from_messages, get_git_files, get_data_files
from database import RepositoryConfluenceOutput, external_json_to_file_confluence_output
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
import ast

def process_file(file, repository_url, repo_name):
    output = ConfluenceChain.invoke({
        "file": file.page_content,
        "output_instructions": Parser.get_format_instructions(),
        "name_of_file": file.metadata['file_path']
    })
    file_confluence_output = external_json_to_file_confluence_output({
        file.metadata['file_path']: output
    })

    # Ensure thread-safe database access
    with MongoClient() as client:
        existing_doc = get_documentation_by_url(repository_url)
        
        if existing_doc:
            add_file_to_repository(repository_url, file_confluence_output)
        else:
            final_output_db = {file.metadata['file_path']: file_confluence_output}
            repository_data = RepositoryConfluenceOutput(
                repository_url=repository_url,
                repository_name=repo_name,
                files=final_output_db
            )
            put_new_repository_documentation(repository_data)
            

def parallel_process_files(files, repo_url, repo_name):
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Wrap tqdm around future results for progress bar functionality
        future_to_file = {executor.submit(process_file, file, repo_url, repo_name): file for file in files}
        for future in tqdm(as_completed(future_to_file), total=len(files)):
            file = future_to_file[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f'{file.metadata["file_path"]} generated an exception: {exc}')
                
                
def download_and_process_repo_url(repo_url, supported_languages = ['python', 'java', 'javascript']):
    repo_name_with_owner  = repo_url.split("github.com/")[1]
    repo_name             = repo_name_with_owner.split("/")[1]
    local_repo_dir        = f"example_data/{repo_name}"
    files                 = get_git_files(local_repo_dir, repo_url)
    files                 = get_data_files(files, supported_languages)
    
    parallel_process_files(files, repo_url, repo_name)
    
    return files