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
    overall_summary: str = Field(description="Overall summary of the file")
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
