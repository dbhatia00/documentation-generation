from database import add_file_to_repository, get_documentation_by_url, put_new_repository_documentation, get_file_documentation, start_file_processing, complete_file_processing, complete_llm_generation
from database import RepositoryConfluenceOutput, external_json_to_file_confluence_output, external_json_to_repo_overview_output, add_project_overview_to_repository
from utils import load_config, set_environment_variables, num_tokens_from_messages, get_git_files, get_data_files
from OverviewChain import OverviewParser, ConfluenceOverviewChain
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
import traceback

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_file(file, repository_url, repo_name):
    start_file_processing(repository_url, file.metadata['file_path'])
    try:
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
        
        complete_file_processing(repository_url, file.metadata['file_path'])
    except Exception as e:
        logger.error(f"Error processing file {file.metadata['file_path']}: {e}")
        complete_file_processing(repository_url, file.metadata['file_path'], False)
        traceback.print_exc()
        raise e
    
    return output
            

def parallel_process_files(files, repo_url, repo_name):
    data_dict = {}
    with ThreadPoolExecutor(max_workers=64) as executor:
        # Wrap tqdm around future results for progress bar functionality
        future_to_file = {executor.submit(process_file, file, repo_url, repo_name): file for file in files}
        for future in tqdm(as_completed(future_to_file), total=len(files)):
            file = future_to_file[future]
            try:
                data = future.result()
                data_dict[file.metadata['file_path']] = data
            except Exception as exc:
                print(f'{file.metadata["file_path"]} generated an exception: {exc}')
                
    return data_dict

import os
                
def download_and_process_repo_url(repo_url, supported_languages = ['python', 'java', 'javascript']):
    repo_name_with_owner  = repo_url.split("github.com/")[1]
    repo_name             = repo_name_with_owner.split("/")[1]
    local_repo_dir        = f"/tmp/{repo_name}"
    if os.path.exists(local_repo_dir):
        shutil.rmtree(local_repo_dir)
    files                 = get_git_files(local_repo_dir, repo_url)
    files                 = get_data_files(files, supported_languages)
    
    data_dict             = parallel_process_files(files, repo_url, repo_name)
    
    repo_overview         = process_and_add_repo_overview_to_db(repo_url, str(data_dict))

    
    if os.path.exists(local_repo_dir):
        shutil.rmtree(local_repo_dir)
    
    logger.info(f"Finished processing repository URL: {repo_url}")
    
    return data_dict

def get_repo_overview(name_of_repo, repo_data):
    total_tokens = num_tokens_from_messages([{"message":  str(repo_data)}], model="gpt-4-32k-0613") 
    logger.info(f"Total tokens for repo overview data: {total_tokens}")
    
    res          = ConfluenceOverviewChain.invoke({"name_of_repo": name_of_repo, "repo_data": str(repo_data), "output_instructions": OverviewParser.get_format_instructions()})
    
    logger.info(f"Finished generating repo overview for {name_of_repo}")
    return res

def process_and_add_repo_overview_to_db(repo_url, repo_data):
    try:
        start_file_processing(repo_url, 'repo-overview-data')
        repo_overview = get_repo_overview(repo_url, repo_data)
        with MongoClient() as client:
            repo_overview_pydantic = external_json_to_repo_overview_output(repo_overview)
            add_project_overview_to_repository(repo_url, repo_overview_pydantic)
            complete_file_processing(repo_url, 'repo-overview-data')
    except Exception as e:
        logger.error(f"Error processing file `repo_overview_data`: {e}")
        complete_file_processing(repo_url, 'repo-overview-data', False)
        raise e
    
    return repo_overview
