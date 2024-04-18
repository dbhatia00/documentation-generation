from datetime import datetime
from pydantic import BaseModel, Field

class PackageDetail(BaseModel):
    usage: str = Field(description="How the package is used in the file")
    description: str = Field(description="Description of the package")

class FunctionDetail(BaseModel):
    name: str = Field(..., description="Name of the function")
    description: str = Field(..., description="Description of what the function does")
    class_declaration: str = Field(description="Declaration of the class to which the function belongs. Should include everything from class to function.", default="")
    additional_details: str = Field(description="Additional information about the function", default="")

class FileConfluenceOutput(BaseModel):
    file_path: str = Field(..., description="Path of the file")
    overall_summary: str = Field(description="Overall summary of the file", default="")
    packages: dict[str, PackageDetail] = Field(description="Packages used in the file with their details")
    functions: dict[str, FunctionDetail] = Field(description="Functions defined in the file with their details")

class RepositoryConfluenceOutput(BaseModel):
    repository_url: str = Field(..., description="URL of the repository")
    repository_name: str = Field(..., description="Name of the repository")
    repository_summary: str = Field(description="Summary of the repository", default="")
    confluence_id : str = Field(description="Confluence ID of the page", default="")
    files: dict[str, FileConfluenceOutput] = Field(description="Files in the repository with their details")
    current_status: str = Field(description="Current status of the repository", default="Not started")
    created_at: datetime = Field(description="Time when the repository was created", default_factory=datetime.now)
    last_modified: datetime = Field(description="Time when the repository was last modified", default_factory=datetime.now)

def external_json_to_respsitory_confluence_output(json_data: dict) -> RepositoryConfluenceOutput:
    formatted_json = {}
    formatted_json["repository_url"] = json_data["repository_url"]
    formatted_json["repository_name"] = json_data["repository_name"]
    formatted_json["repository_summary"] = json_data.get("repository_summary", "")
    formatted_json["confluence_id"] = json_data.get("confluence_id", "")
    formatted_json["current_status"] = json_data.get("current_status", "Not started")
    formatted_json["files"] = {}
    files = json_data["files"]
    for file_path, file_data in files.items():
        file_data["file_path"] = file_path
        packages = file_data.get("packages", {})
        functions = file_data.get("functions", {})
        for package_name, package_data in packages.items():
            packages[package_name] = PackageDetail(**package_data)
        for function_name, function_data in functions.items():
            functions[function_name] = FunctionDetail(**function_data)
        replacement_file_name = file_path.replace(".", "_")
        formatted_json["files"][replacement_file_name]= FileConfluenceOutput(**file_data)
    return RepositoryConfluenceOutput(**formatted_json)

def external_json_to_file_confluence_output(json_data: dict) -> FileConfluenceOutput:
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
    # print(formatted_json)
    return FileConfluenceOutput(**formatted_json)

def database_json_to_respsitory_confluence_output(json_data: dict) -> RepositoryConfluenceOutput:
    formatted_json = {}
    formatted_json["repository_url"] = json_data["repository_url"]
    formatted_json["repository_name"] = json_data["repository_name"]
    formatted_json["repository_summary"] = json_data.get("repository_summary", "")
    formatted_json["confluence_id"] = json_data.get("confluence_id", "")
    formatted_json["current_status"] = json_data.get("current_status", "Not started")
    formatted_json["files"] = {}
    files = json_data["files"]
    for file_path, file_data in files.items():
        replacement_file_name = file_path.replace("_", ".")
        file_data["file_path"] = replacement_file_name
        # print("Now the file path is", file_data["file_path"])
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
    # print(formatted_json)
    return FileConfluenceOutput(**formatted_json)
