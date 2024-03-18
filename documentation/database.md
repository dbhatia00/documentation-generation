# Input
The MongoDB service takes in the combined outputs of our RAG service, which would ideally include the following in JSON format:
1. The github url of the repository
2. The name of the project
3. The confluence id of the documentation
4. The names of all files of the repository
5. The summary from each file with its file path. 

# Output
The output of this service returns the document from MongoDB. The format of the document will follow this format:
 ```
{
        "projectName": "Example Project",
        "githubUrl" : "https://github.com/dbhatia00/documentation-generation",
        "conluenceId" : "1234567",
        "files": [
          {
            "fileName": "exampleFile1.java",
            "filePath" : "client/src/exampleFile1.java",
            "summary": "This file does X, Y, and Z",
          },
          {
            "fileName": "exampleFile2.java",
            "filePath" : "client/src/exampleFile2.java",
            "summary": "This file does A, B, and C",
          },
          
            ],
  }
```

# Main Functionalities
This service stores the combined RAG results for the all the files in the github resposity, along with the file structure and the links required to uniquely identify a repository. We will be using classic database connection managers to achieve CRUD operations along with the functionality to create the required DTO. 

Main components:
1. CRUD operations
2. Database connection Manager
