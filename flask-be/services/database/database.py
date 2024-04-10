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

from datetime import datetime
from typing import Optional

from pymongo import MongoClient
from pymongo.results import InsertOneResult
from pymongo.results import UpdateResult
from pymongo.results import DeleteResult

DATABASE_URI = "mongodb+srv://udadmin:QPH4mmr1X3DYdL51@userdocumentation.hqqp2g2.mongodb.net/?retryWrites=true&w=majority&appName=UserDocumentation"
client = MongoClient(DATABASE_URI, tlsAllowInvalidCertificates=True)
db = client["user_documentation"]
collection = db["documentation_store"]
def get_documentation_by_url(repository_url: str) -> Optional[dict]:
    """
    Retrieves the first document from the MongoDB collection that matches the given repository URL.

    Parameters:
    - repository_url (str): The URL of the repository to find.

    Returns:
    - dict or None: Returns a dictionary representing the document if found, otherwise None.
    """
    return collection.find_one({"repository_url": repository_url})

def get_file_documentation(repository_url: str, file_path) -> Optional[dict]:
    """
    Retrieves the first file documentation from the MongoDB collection that matches the given repository URL and file path.

    Parameters:
    - repository_url (str): The URL of the repository to find.
    - file_path (str): The file path of the file.

    Returns:
    - dict or None: Returns a dictionary representing the file if found, otherwise None.
    """
    result = collection.find_one({"repository_url": repository_url})

    if result:
        for file in result.get("files", []):
            if file["file_path"] == file_path:
                return file
    return None


def put_new_documentation(repository_dto: dict) -> InsertOneResult:
    """
    Inserts a new repository document into the MongoDB collection.

    Parameters:
    - repository_dto (dict): Use create_repository_dto to create the DTO

    Returns:
    - InsertOneResult: An instance of InsertOneResult that contains information about the operation

    Raises:
    - TypeError: If the input is not a dictionary.
    - pymongo.errors.OperationFailure: If the insert operation fails due to MongoDB execution issues
    """
    return collection.insert_one(repository_dto)

def create_repository_dto(repository_url: str, repository_name: str, repository_summary:str, files: list) -> dict:
    """
    Creates a dictionary object representing a repository with its associated files.

    Parameters:
    - repository_url (str): The URL of the repository.
    - repository_name (str): The name of the repository.
    - files (list): A list of file DTOs associated with this repository.

    Returns:
    - dict: A dictionary object containing repository data.
    """
    repository_dto = {
        "repository_url": repository_url,
        "repository_name": repository_name,
        "repository_summary": repository_summary ,
        "files": files,
        "created_at": datetime.now(),
        "last_modified": datetime.now(),
    }
    return repository_dto

def create_file_dto(file_name: str, file_path: str, llm_summary: str, user_summary: str = '') -> dict:
    """
    Creates a dictionary object representing a file with summaries.

    Parameters:
    - file_name (str): The name of the file.
    - file_path (str): The path to the file.
    - llm_summary (str): The LLM-generated summary of the file.
    - user_summary (str): An optional user-modified summary of the file, default is an empty string.

    Returns:
    - dict: A dictionary object containing file data.
    """
    file_dto = {
        "file_path": file_path,
        "file_name": file_name,
        "llm_summary": llm_summary,
        "user_summary": user_summary,
        "created_at": datetime.now(),
        "last_modified": datetime.now()
    }
    return file_dto

def add_file_to_repository(repository_url: str, file_dto: dict) -> UpdateResult:
    """
    Adds a file to an existing repository document in MongoDB.

    Parameters:
    - repository_id: The ID of the repository document to update.
    - file_dto: Dictionary containing file data to add. (Use create_file_dto to create it)

    Returns:
    - The result of the update operation.
    """
    result = collection.update_one(
        {"repository_url": repository_url},
        {"$push": {"files": file_dto}}
    )
    return result

def update_documentation_by_file(repository_url: str, file_path: str, new_data: dict)->UpdateResult:
    """
    Updates specific fields of a file within a repository document.

    Parameters:
    - repository_url (str): The URL of the repository to update.
    - file_path (str): The path of the file within the repository to update.
    - new_data (dict): A dictionary of the fields to update.

    Returns:
    - The result of the update operation.
    """
    result = collection.update_one(
        {"repository_url": repository_url, "files.file_path": file_path},
        {"$set": {f"files.$[elem].{k}": v for k, v in new_data.items()}},
        array_filters=[{"elem.file_path": file_path}]
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

def delete_file_from_documentation(repository_url: str, file_path: str) -> UpdateResult:
    """
    Removes a file from a repository document.

    Parameters:
    - repository_url (str): The URL of the repository from which to remove the file.
    - file_path (str): The path of the file to remove.

    Returns:
    - The result of the delete operation.
    """
    result = collection.update_one(
        {"repository_url": repository_url},
        {"$pull": {"files": {"file_path": file_path}}}
    )
    return result

def update_user_summary_by_file(repository_url:str, file_path:str, user_summary:str) -> UpdateResult:
    """
    Updates the user-provided summary for a specific file within a repository document in MongoDB.

    Parameters:
    - repository_url (str): The URL of the repository containing the file.
    - file_path (str): The path of the file within the repository to update.
    - user_summary (str): The new user-provided summary to be updated in the file's record.

    Returns:
    - UpdateResult: An object containing information about the result of the update operation.

    Raises:
    - Exception: If the update fails due to database connection issues or document schema problems.
    """
    result = collection.update_one(
        {"repository_url": repository_url, "files.file_path": file_path},
        {"$set": {"files.$.user_summary": user_summary}}
    )
    return result
