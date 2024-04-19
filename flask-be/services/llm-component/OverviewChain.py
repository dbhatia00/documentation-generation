from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
import os




class RepoOverviewOutput(BaseModel):
    overall_summary: str = Field(description="Overall summary of the repo")
    functionalities: dict[str, str] = Field(description="Functionalities of the repo")
    project_components: dict[str, str] = Field(description="Project components of the repo")
    database_components: dict[str, str] = Field(description="Database components of the repo")
    tech_stack: dict[str, str] = Field(description="Tech stack of the repo")


prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="Analyze the provided file summaries to generate structured documentation for a github repository. The analysis should cover key aspects of the repo such as its overall purpose, functionalities, project components, database components, and tech stack."
        ),
        HumanMessagePromptTemplate.from_template(
            """
            ### Project Overview
            Generate a comprehensive documentation for the provided repo. This should include:

            1. Overall Summary: A general overview of the repo's purpose and functionality within its application context.
                e.g. The "Electricity Billing System" project is a Java Swing GUI application designed to manage electricity billing operations ... and so on.
            
            2. Functionalities: Identify and describe the main functionalities of the repo, outlining their usage and purpose.
                e.g User Authentication: Users can create personal logins for secure access to the system.
                    Customer Management: Users can add customers and calculate their electricity bills.
                    Bill Management: Users can pay electricity bills and generate bills.
                    
            3. Project Components: Provide details on the project components of the repo, including their names and purposes.
                e.g Splash Screen Class: Handles the display of a splash screen when the application starts.
                    Login Screen Class: Manages user authentication and login functionality.
                    ……..
                    
            4. Database Components: Describe the database components used in the repo, outlining their roles and functionalities.
                e.g. Login Table: Stores user login credentials (Username, Password).
                    Bill Table: Stores information about electricity bills (MeterNumber, Units, Month, Amount).
                    ……..
            
            5. Tech Stack: List the technologies and tools used in the repo, including programming languages, frameworks, and libraries.
                e.g IntelliJ IDEA: Integrated Development Environment (IDE) for Java.
                    JDBC (Java Database Connectivity): Facilitates communication between Java application and MySQL database.
                    ……..
            

            This structured output should help developers understand the key components and functionality of the file for development or maintenance purposes.
            
            If no information is provided for any section simple add an empty dictionary.
            If overall summary is not provided, add an empty string. e.g. "overall_summary": ""
            
            Here is the repo ({name_of_repo}) for reference:
            
            {repo_data}
            
            Follow the following output instructions:
            
            {output_instructions}
            
            Note: Make sure to follow the json provided structure very strictly. Do not change the structure of the json output. Do not include or remove any fields from the json output.
            """
        ),
    ]
)
# This setup provides a generic framework to analyze any  file, making it highly versatile for documentation generation purposes. The system message provides the task context, while the human message outlines a detailed template to be filled based on the file's content.


OverviewParser    = JsonOutputParser(pydantic_object=RepoOverviewOutput) 
model             = AzureChatOpenAI( deployment_name="gpt4-preview", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'], openai_api_key=os.environ['AZURE_OPENAI_KEY'] ) #ChatOpenAI(model="gpt-4-turbo", temperature=0)


list_of_fallback_models = [
    AzureChatOpenAI( deployment_name="gpt-4-east-us2", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_EAST_2'], openai_api_key=os.environ['AZURE_OPENAI_KEY_EAST_2'] ),
    AzureChatOpenAI( deployment_name="gpt-4-turbo-east-west-us1", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_WEST_1'], openai_api_key=os.environ['AZURE_OPENAI_KEY_WEST_1'] ),
    AzureChatOpenAI( deployment_name="gpt-4-turbo-east-canada", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_CANADA_EAST'], openai_api_key=os.environ['AZURE_OPENAI_KEY_CANADA_EAST'] ), 
    AzureChatOpenAI( deployment_name="gpt-4-turbo-east-aus", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_AUS_EAST'], openai_api_key=os.environ['AZURE_OPENAI_KEY_AUS_EAST'] ),
    AzureChatOpenAI( deployment_name="gpt-4-turbo-south-uk", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_UK_SOUTH'], openai_api_key=os.environ['AZURE_OPENAI_KEY_UK_SOUTH'] ),
    AzureChatOpenAI( deployment_name="gpt-4-turbo-central-swe", temperature=0, azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT_SWE_CENTRAL'], openai_api_key=os.environ['AZURE_OPENAI_KEY_SWE_CENTRAL'] ),
    # ChatOpenAI(      model="gpt-4-turbo-preview", temperature=0 )
]


ConfluenceOverviewChain          = (
                      prompt
                    | model.with_fallbacks(list_of_fallback_models)
                    | OverviewParser
                )