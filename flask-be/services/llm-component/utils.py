import os
import yaml
import logging
import tiktoken
import pandas as pd
from langchain_community.document_loaders import GitLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path):
    try:
        with open(config_path, 'r') as c_file:
            config = yaml.safe_load(c_file)
            return config
    except Exception as e:
        logger.error(f"Error loading configuration file: {e}")
        raise

def set_environment_variables(config):
    # Iterate through the config file and set the environment variables
    for key, value in config.items():
        if type(key) == str and type(value) == str:
            os.environ[key] = value
        
    os.environ['OPENAI_API_KEY'] = config['OPENAI_API_KEY']
    os.environ['OPENAI_API_VERSION'] = config['OPENAI_API_VERSION']
    os.environ['AZURE_OPENAI_ENDPOINT'] = config['AZURE_OPENAI_ENDPOINT']
    os.environ['AZURE_OPENAI_API_KEY'] = config['AZURE_OPENAI_KEY']
    
    
    
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def get_data_files(files, language ):
    dict_file_ext = {
        'python': '.py',
        'java': '.java',
        'javascript': '.js'
    }    
    if language not in dict_file_ext.keys():
        raise ValueError('Language not supported')
    file_ext = dict_file_ext[language]
    files = [x for x in files if x.metadata['file_type'] == file_ext and 'tests' not in x.metadata['file_path']]
    
    temp_str = " ".join([x.page_content for x in files])
    total_tokens = num_tokens_from_messages([{"message": temp_str}], model="gpt-4-32k-0613") 
    
    num_per_file = [num_tokens_from_messages([{"message": x.page_content}], model="gpt-4-32k-0613") for x in files]
    num_per_file = pd.Series( num_per_file )
    print(num_per_file.describe())
    # $10.00 / 1M tokens	$30.00 / 1M tokens

    input_costs = 10 * ( total_tokens / 1e6)
    output_costs = 30 * ( total_tokens / 1e6)
    print(f"Total Tokens: {total_tokens}")
    print(f"Input Token Costs: ${input_costs:.2f}")
    print(f"Output Token Costs: ${output_costs:.2f}")
    print(f"Total Costs: ${input_costs + output_costs:.2f}")
    
    return files

# User needs to specify the clone_url, branch, and language of the repository they want to load.
def get_git_files(repo_path, clone_url, branch="master"):
    loader = GitLoader(
        clone_url=clone_url,
        repo_path=repo_path,
        branch=branch,
        # file_filter=lambda file_path: file_path.endswith(".py") #or file_path.endswith(".java") or file_path.endswith(".js"),
    )
    files = loader.load()
    return files