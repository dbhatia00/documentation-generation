"""
This module provides functions for converting JSON data to Pydantic models representing repository and file structures.

The module includes functions to convert JSON data from external sources or databases into Pydantic models such as RepositoryConfluenceOutput and FileConfluenceOutput.

Classes:
- PackageDetail: Represents details of a package used in a file.
- FunctionDetail: Represents details of a function defined in a file.
- FileConfluenceOutput: Represents a file in a repository with its details.
- RepositoryConfluenceOutput: Represents a repository with its files and details.

Functions:
- external_json_to_respsitory_confluence_output: Converts external JSON data to RepositoryConfluenceOutput.
- external_json_to_file_confluence_output: Converts external JSON data to FileConfluenceOutput.
- database_json_to_respsitory_confluence_output: Converts database JSON data to RepositoryConfluenceOutput.
- database_json_to_file_confluence_output: Converts database JSON data to FileConfluenceOutput.
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class PackageDetail(BaseModel):
    """
    Represents details of a package used in a file.

    Attributes:
    - usage: How the package is used in the file.
    - description: Description of the package.
    """
    usage: str = Field(description="How the package is used in the file")
    description: str = Field(description="Description of the package")

class FunctionDetail(BaseModel):
    """
    Represents details of a function defined in a file.

    Attributes:
    - name: Name of the function.
    - description: Description of what the function does.
    - class_declaration: Declaration of the class to which the function belongs. Should include everything from class to function.
    - additional_details: Additional information about the function.
    """
    name: str = Field(..., description="Name of the function")
    description: str = Field(..., description="Description of what the function does")
    class_declaration: str = Field(description="Declaration of the class to which the function belongs. Should include everything from class to function.", default="")
    additional_details: str = Field(description="Additional information about the function", default="")

class FileConfluenceOutput(BaseModel):
    """
    Represents a file in a repository with its details.

    Attributes:
    - file_path: Path of the file.
    - overall_summary: Overall summary of the file.
    - packages: Packages used in the file with their details.
    - functions: Functions defined in the file with their details.
    """
    file_path: str = Field(..., description="Path of the file")
    overall_summary: str = Field(description="Overall summary of the file", default="")
    packages: dict[str, PackageDetail] = Field(description="Packages used in the file with their details")
    functions: dict[str, FunctionDetail] = Field(description="Functions defined in the file with their details")


class RepoOverviewOutput(BaseModel):
    """
    Represents a general overview of a repository.

    Attributes:
    - overall_summary: General summary of the repository.
    - functionalities: Key functionalities provided by the repository.
    - project_components: Main components of the project.
    - database_components: Components related to the repository's database.
    - tech_stack: Technology stack used in the repository.
    """
    overall_summary: str = Field(description="General summary of the repository")
    functionalities: dict[str, str] = Field(description="Key functionalities provided by the repository")
    project_components: dict[str, str] = Field(description="Main components of the project")
    database_components: dict[str, str] = Field(description="Components related to the repository's database")
    tech_stack: dict[str, str] = Field(description="Technology stack used in the repository")


class RepositoryConfluenceOutput(BaseModel):
    """
    Represents a repository with its files and details.

    Attributes:
    - repository_url: URL of the repository.
    - repository_name: Name of the repository.
    - repository_summary: Summary of the repository.
    - confluence_id: Confluence ID of the page.
    - files: Files in the repository with their details.
    - created_at: Time when the repository was created.
    - last_modified: Time when the repository was last modified.
    """
    repository_url: str = Field(..., description="URL of the repository")
    repository_name: str = Field(..., description="Name of the repository")
    repository_summary: str = Field(description="Summary of the repository", default="")
    confluence_id : str = Field(description="Confluence ID of the page", default="")
    files: dict[str, FileConfluenceOutput] = Field(description="Files in the repository")
    created_at: datetime = Field(description="Time when the repository was created", default_factory=datetime.now)
    last_modified: datetime = Field(description="Time when the repository was last modified", default_factory=datetime.now)
    repo_overview_data: Optional[RepoOverviewOutput] = Field(description="General overview of the repository", default=None)
    
class Status(BaseModel):
    """
    Represents the status of a repository's llm generation process.

    Attributes:
    - repository_url: URL of the repository.
    - status: Status of the llm generation process. Defaults to "Not started" if not provided.
    """
    repository_url: str = Field(..., description="URL of the repository")
    overall_status: str = Field(description="Status of the llm generation process", default="Not started")
    file_level_status: dict[str, str] = Field(description="Status of the llm generation process for each file", default={})

def external_json_to_respsitory_confluence_output(json_data: dict) -> RepositoryConfluenceOutput:
    """
    Converts external JSON data to a RepositoryConfluenceOutput object.
    Replaces periods in file paths with underscores.

    Parameters:
    - json_data (dict): External JSON data to convert.

    Returns:
    - RepositoryConfluenceOutput: Converted object.
    """
    formatted_json = {}
    formatted_json["repository_url"] = json_data["repository_url"]
    formatted_json["repository_name"] = json_data["repository_name"]
    formatted_json["repository_summary"] = json_data.get("repository_summary", "")
    formatted_json["confluence_id"] = json_data.get("confluence_id", "")
    formatted_json["files"] = {}
    files = json_data["files"]
    for file_path, file_data in files.items():
        file_object = external_json_to_file_confluence_output({file_path : file_data})
        file_path = file_path.replace(".", "_")
        formatted_json["files"][file_path] = file_object
    print(formatted_json)
    return RepositoryConfluenceOutput(**formatted_json)

def external_json_to_file_confluence_output(json_data: dict) -> FileConfluenceOutput:
    """
    Converts external JSON data to a FileConfluenceOutput object.

    Parameters:
    - json_data (dict): External JSON data to convert.

    Returns:
    - FileConfluenceOutput: Converted object.
    """
    formatted_json = {}
    file_name = next(iter(json_data.keys()))
    file = json_data[file_name]
    formatted_json["file_path"] = file_name
    formatted_json["overall_summary"] = file.get("overall_summary", "")
    packages = file.get("packages", {})
    functions = file.get("functions", {})
    for package_name, package_data in packages.items():
        packages[package_name] = PackageDetail(**package_data)
    for function_name, function_data in functions.items():
        functions[function_name] = FunctionDetail(**function_data)
    formatted_json["packages"] = packages
    formatted_json["functions"] = functions
    print(formatted_json)
    return FileConfluenceOutput(**formatted_json)

def database_json_to_respsitory_confluence_output(json_data: dict) -> RepositoryConfluenceOutput:
    """
    Converts database JSON data to a RepositoryConfluenceOutput object.
    Replaces underscores in file paths with periods.

    Parameters:
    - json_data (dict): Database JSON data to convert.

    Returns:
    - RepositoryConfluenceOutput: Converted object.
    """
    formatted_json = {}
    formatted_json["repository_url"] = json_data["repository_url"]
    formatted_json["repository_name"] = json_data["repository_name"]
    formatted_json["repository_summary"] = json_data.get("repository_summary", "")
    formatted_json["confluence_id"] = json_data.get("confluence_id", "")
    formatted_json["files"] = {}
    files = json_data["files"]
    for file_path, file_data in files.items():
        replacement_file_name = file_path.replace("_", ".")
        file_data["file_path"] = replacement_file_name
        print("Now the file path is", file_data["file_path"])
        packages = file_data.get("packages", {})
        functions = file_data.get("functions", {})
        for package_name, package_data in packages.items():
            packages[package_name] = PackageDetail(**package_data)
        for function_name, function_data in functions.items():
            functions[function_name] = FunctionDetail(**function_data)
        replacement_file_name = file_path.replace("_", ".")
        formatted_json["files"][replacement_file_name]= FileConfluenceOutput(**file_data)
    return RepositoryConfluenceOutput(**formatted_json)

def database_json_to_file_confluence_output(json_data: dict) -> FileConfluenceOutput:
    """
    Converts database JSON data to a FileConfluenceOutput object.

    Parameters:
    - json_data (dict): Database JSON data to convert.

    Returns:
    - FileConfluenceOutput: Converted object.
    """
    formatted_json = {}
    file_name = next(iter(json_data.keys()))
    file = json_data[file_name]
    formatted_json["file_path"] = file_name
    packages = file.get("packages", {})
    functions = file.get("functions", {})
    for package_name, package_data in packages.items():
        packages[package_name] = PackageDetail(**package_data)
    for function_name, function_data in functions.items():
        functions[function_name] = FunctionDetail(**function_data)
    formatted_json["packages"] = packages
    formatted_json["functions"] = functions
    print(formatted_json)
    return FileConfluenceOutput(**formatted_json)


def external_json_to_repo_overview_output(json_data: dict) -> RepoOverviewOutput:
    """
    Converts external JSON data to a RepoOverviewOutput object.

    Parameters:
    - json_data (dict): External JSON data to convert.

    Returns:
    - RepoOverviewOutput: Converted object.
    """
    # Extracting and formatting the relevant information from the JSON data.
    overview = json_data.get("overall_summary", "")
    functionalities = json_data.get("functionalities", {})
    project_components = json_data.get("project_components", {})
    database_components = json_data.get("database_components", {})
    tech_stack = json_data.get("tech_stack", {})

    # Constructing the RepoOverviewOutput with the formatted data.
    repo_overview = RepoOverviewOutput(
        overall_summary=overview,
        functionalities=functionalities,
        project_components=project_components,
        database_components=database_components,
        tech_stack=tech_stack
    )
    return repo_overview