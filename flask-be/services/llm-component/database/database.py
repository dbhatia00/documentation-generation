"""
This module provides an interface for managing documentation related to GitHub repositories stored in a MongoDB database.

Capabilities include:
- Fetching documentation by repository URL.
- Fetching specific file documentation within a repository by URL and file path.
- Adding new repository documentation to the database.
- Creating data transfer objects (DTOs) for repositories and files to ensure consistent data handling.
- Adding new files to existing repository documentation.
- Updating specific documentation fields for files within a repository.
- Deleting entire repository documentation or specific files within a repository.
- Updating user-provided summaries for specific files.

Each function is designed to perform a specific CRUD (Create, Read, Update, Delete) operation, facilitating easy maintenance and scalability of the repository documentation system.

Dependencies:
- pymongo: To interact with the MongoDB database.
- datetime: For handling date and time information for logging and record management.

Example Usage:
To use these functions, ensure that the database URI is correctly specified in the DATABASE_URI variable.
"""

from typing import Optional
from .datamodels import RepositoryConfluenceOutput, FileConfluenceOutput, database_json_to_respsitory_confluence_output, external_json_to_respsitory_confluence_output
from .datamodels import Status, RepoOverviewOutput

from pymongo import MongoClient
from pymongo.results import InsertOneResult
from pymongo.results import UpdateResult
from pymongo.results import DeleteResult

DATABASE_URI = "mongodb+srv://udadmin:QPH4mmr1X3DYdL51@userdocumentation.hqqp2g2.mongodb.net/?retryWrites=true&w=majority&appName=UserDocumentation"
client = MongoClient(DATABASE_URI, tlsAllowInvalidCertificates=True)
db = client["user_documentation"]
collection = db["documentation_store"]

import logging 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ALL REPOSITORY LEVEL OPERATIONS
def get_documentation_by_url(repository_url: str) -> Optional[RepositoryConfluenceOutput]:
    """
    Retrieves the first document from the MongoDB collection that matches the given repository URL.

    Parameters:
    - repository_url (str): The URL of the repository to find.

    Returns:
    - dict or None: Returns an object of RepositoryConfluenceOutput representing the document if found, otherwise None.
    """

    result = collection.find_one({"repository_url": repository_url}, {"_id": 0})
    if result:
        return database_json_to_respsitory_confluence_output(result)
    return None




def put_new_repository_documentation(repository_confluence_output: RepositoryConfluenceOutput) -> InsertOneResult:
    """
    Inserts a new repository document into the MongoDB collection.

    Parameters:
    - file_confluence_output (FileConfluenceOutput): The repository data to insert. Use FileConfluenceOutput() from datamodels.py to create it.

    Returns:
    - InsertOneResult: An instance of InsertOneResult that contains information about the operation

    Raises:
    - pymongo.errors.OperationFailure: If the insert operation fails due to MongoDB execution issues
    """
    return collection.insert_one(repository_confluence_output.model_dump())


#ALL FILE LEVEL OPERATIONS
def add_file_to_repository(repository_url: str, file_confluence_output: FileConfluenceOutput) -> UpdateResult:
    """
    Adds a file to an existing repository document in MongoDB.

    Parameters:
    - repository_url: The url of the repository document to update.
    - file_confluence_output: The file data to add to the repository. Use FileConfluenceOutput() from datamodels.py to create it.

    Returns:
    - The result of the update operation.
    """
    update_query = {"repository_url": repository_url}
    file_data_key = "files." + file_confluence_output.file_path.replace('.', '_')  # Replace dots with underscores
    logger.info(f"Adding file to repository: {file_data_key}")
    file_data = {
        "$set": {
            file_data_key: file_confluence_output.model_dump()
        }
    }

    result = collection.update_one(update_query, file_data, upsert=True)
    return result

def add_project_overview_to_repository(repository_url: str, repo_overview_output: RepoOverviewOutput) -> UpdateResult:
    """

    """
    update_query = {"repository_url": repository_url}
    file_data_key = "repo_overview_data"  # Replace dots with underscores
    logger.info(f"Adding file to repository: {file_data_key}")
    file_data = {
        "$set": {
            file_data_key: repo_overview_output.model_dump()
        }
    }
    result = collection.update_one(update_query, file_data, upsert=True)
    return result

def get_file_documentation(repository_url: str, file_path: str) -> Optional[FileConfluenceOutput]:
    """
    Retrieves the first file documentation from the MongoDB collection that matches the given repository URL and file path.

    Parameters:
    - repository_url (str): The URL of the repository to find.
    - file_path (str): The file path of the file.

    Returns:
    - FileConfluenceOutput or None: Returns a FileConfluenceOutput object representing the file if found, otherwise None.
    """
    result = collection.find_one({"repository_url": repository_url})
    if result:
        file_data = result.get("files", {}).get(file_path.replace('.', '_'))
        if file_data:
            return FileConfluenceOutput(**file_data)
    return None


def update_documentation_by_file(repository_url: str, file_path: str, new_data: FileConfluenceOutput) -> UpdateResult:
    """
    Updates specific fields of a file within a repository document.

    Parameters:
    - repository_url (str): The URL of the repository to update.
    - file_path (str): The path of the file within the repository to update.
    - new_data (FileConfluenceOutput): The updated file data.

    Returns:
    - The result of the update operation.
    """
    new_data_dict = new_data.model_dump()
    file_path = file_path.replace('.', '_')
    update_query = {
        f"files.{file_path}": {k: v for k, v in new_data_dict.items() if k != 'file_path'}
    }
    result = collection.update_one(
        {"repository_url": repository_url, f"files.{file_path}": {"$exists": True}},
        {"$set": update_query}
    )
    return result


def delete_documentation_by_url(repository_url: str) -> DeleteResult:
    """
    Deletes an entire repository document.

    Parameters:
    - repository_url (str): The URL of the repository to delete.

    Returns:
    - The result of the delete operation.
    """
    result = collection.delete_one({"repository_url": repository_url})
    return result

def delete_file_from_documentation(repository_url: str, file_key: str) -> UpdateResult:
    """
    Removes a file from a repository document.

    Parameters:
    - repository_url (str): The URL of the repository from which to remove the file.
    - file_key (str): The key of the file to remove.

    Returns:
    - The result of the delete operation.
    """
    result = collection.update_one(
        {"repository_url": repository_url},
        {"$unset": {f"files.{file_key.replace('.', '_')}": ""}}
    )
    return result

#STATUS OPERATIONS
def start_llm_generation(repository_url: str) -> InsertOneResult:
    """
    Updates the status of the llm generation process to "In progress".

    Parameters:
    - repository_url (str): The URL of the repository to update.

    Returns:
    - The result of the update operation.
    """
    status_obj = Status(repository_url=repository_url, overall_status="In progress")
    result = db["status"].insert_one(status_obj.model_dump())
    return result

def complete_llm_generation(repository_url: str, success: bool=True) -> UpdateResult:
    """
    Updates the status of the llm generation process to "Completed".

    Parameters:
    - repository_url (str): The URL of the repository to update.

    Returns:
    - The result of the update operation.
    """
    str_complete = "Completed"
    if not success:
        str_complete = "Failed"
        
    result = db["status"].update_one(
        {"repository_url": repository_url},
        {"$set": {"overall_status": str_complete}}
    )
    return result

def start_file_processing(repository_url, file_name):
    """
    Updates the status of the file processing to "In progress".

    Parameters:
    - repository_url (str): The URL of the repository to update.
    - file_name (str): The name of the file to update.

    Returns:
    - The result of the update operation.
    """
    file_name = file_name.replace('.', '_')
    if(db["status"].find_one({"repository_url": repository_url}) is None):
        logger.info(f"Creating new status document for {repository_url}")
        start_llm_generation(repository_url)
    # result = db["status"].update_one(
    #     {"repository_url": repository_url},
    #     {"$set": {f"file_level_status.{file_name}": "In progress"}})
    return

def complete_file_processing(repository_url, file_name, success=True):
    """
    Updates the status of the file processing to "Completed".

    Parameters:
    - repository_url (str): The URL of the repository to update.
    - file_name (str): The name of the file to update.

    Returns:
    - The result of the update operation.
    """
    str_complete = "Completed"
    if not success:
        str_complete = "Failed"
    file_name = file_name.replace('.', '_')
    result = db["status"].update_one(
        {"repository_url": repository_url},
        {"$set": {f"file_level_status.{file_name}": str_complete}}
    )
    return result

def get_status(repository_url):
    """
    Retrieves the status of the llm generation process for a repository.

    Parameters:
    - repository_url (str): The URL of the repository to find.

    Returns:
    - dict or None: Returns a dictionary representing the status if found, otherwise None.
    """
    result = db["status"].find_one({"repository_url": repository_url}, {"_id": 0})
    if result:
        formated_dict = {}
        for key in result["file_level_status"]:
            formated_dict[key.replace('_', '.')] = result["file_level_status"][key]
        result["file_level_status"] = formated_dict
    return result

def get_status_by_file(repository_url, file_name):
    """
    Retrieves the processing status of a specific file within a repository.

    Parameters:
    - repository_url (str): The URL of the repository to find.
    - file_name (str): The name of the file whose status is to be retrieved.

    Returns:
    - str or None: Returns the status of the file if found, otherwise None.
    """
    # Modify the file name to fit the database format.
    file_name_db = file_name.replace('.', '_')

    # Query the database for the repository's status.
    repository_status = db["status"].find_one({"repository_url": repository_url}, {"_id": 0, "file_level_status": 1})

    # Check if the repository status exists and the specific file status is available.
    if repository_status and "file_level_status" in repository_status:
        file_status = repository_status["file_level_status"].get(file_name_db)
        if file_status:
            return file_status

    # Return None if the file status is not found.
    return None

def get_all_urls_in_db():
    """
    Retrieves all repository URLs stored in the database.

    Returns:
    - list: A list of repository URLs.
    """
    urls = collection.find({}, {"repository_url": 1, "_id": 0})
    return [url["repository_url"] for url in urls]