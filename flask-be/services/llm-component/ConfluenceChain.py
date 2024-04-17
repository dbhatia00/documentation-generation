from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
import os


class PackageDetail(BaseModel):
    usage: str = Field(description="How the package is used in the file")
    description: str = Field(description="Description of the package")


class FunctionDetail(BaseModel):
    name: str = Field(description="Name of the function")
    description: str = Field(description="Description of what the function does")
    class_declaration: str = Field(description="Declaration of the class to which the function belongs. Should include everything from class to function.", default="")
    additional_details: str = Field(description="Additional information about the function", default="")


class FileConfluenceOutput(BaseModel):
    overall_summary: str = Field(description="Overall summary of the file")
    packages: dict[str, PackageDetail] = Field(description="Packages used in the file with their details")
    functions: dict[str, FunctionDetail] = Field(description="Functions defined in the file with their details")


prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="Analyze the provided file to generate structured documentation. The analysis should cover key aspects of the file such as its overall purpose, packages used, and detailed descriptions of functions within the file."
        ),
        HumanMessagePromptTemplate.from_template(
            """
            ### File Analysis
            Generate a comprehensive documentation for the provided file. This should include:

            1. **Overall Summary**: A general overview of the file's purpose and functionality within its application context.
            2. **Packages**: Identify and describe the main packages utilized in the file, outlining their usage and purpose.
            3. **Function Level**: Provide details on the functions defined within the file, including their names, purposes, and any relevant class declarations.

            This structured output should help developers understand the key components and functionality of the file for development or maintenance purposes.
            
            Here is the file ({name_of_file}) for reference:
            
            {file}
            
            Follow the following output instructions:
            
            {output_instructions}
            
            Note: Make sure to follow the json provided structure very strictly. Do not change the structure of the json output. Do not include or remove any fields from the json output.
            """
        ),
    ]
)
# This setup provides a generic framework to analyze any  file, making it highly versatile for documentation generation purposes. The system message provides the task context, while the human message outlines a detailed template to be filled based on the file's content.


Parser            = JsonOutputParser(pydantic_object=FileConfluenceOutput) 
model             = ChatOpenAI(model="gpt-4-turbo", temperature=0)


list_of_fallback_models = [
    AzureChatOpenAI( deployment_name="gpt4-preview", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'], openai_api_key=os.environ['AZURE_OPENAI_KEY'] ),
    AzureChatOpenAI( deployment_name="gpt-4-east-us2", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_EAST_2'], openai_api_key=os.environ['AZURE_OPENAI_KEY_EAST_2'] ),
    AzureChatOpenAI( deployment_name="gpt-4-turbo-east-west-us1", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_WEST_1'], openai_api_key=os.environ['AZURE_OPENAI_KEY_WEST_1'] ),
    AzureChatOpenAI( deployment_name="gpt-4-turbo-east-canada", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_CANADA_EAST'], openai_api_key=os.environ['AZURE_OPENAI_KEY_CANADA_EAST'] ), 
    AzureChatOpenAI( deployment_name="gpt-4-turbo-east-aus", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_AUS_EAST'], openai_api_key=os.environ['AZURE_OPENAI_KEY_AUS_EAST'] ),
    AzureChatOpenAI( deployment_name="gpt-4-turbo-south-uk", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_UK_SOUTH'], openai_api_key=os.environ['AZURE_OPENAI_KEY_UK_SOUTH'] ),
    AzureChatOpenAI( deployment_name="gpt-4-turbo-central-swe", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_SWE_CENTRAL'], openai_api_key=os.environ['AZURE_OPENAI_KEY_SWE_CENTRAL'] ),
    ChatOpenAI(      model="gpt-4-turbo-preview", temperature=0 )
]


ConfluenceChain          = (
                      prompt
                    | model.with_fallbacks(list_of_fallback_models)
                    | Parser
                )