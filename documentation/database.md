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
This service parses the JSON output of our RAG service into a structured HTML page, and then feeds the HTML to a Confluence API request. We intend to use the `Create page` endpoint of the Confluence REST API for each page (one project page and many per-file pages). This service handles the responses from the Confluence API, outputting a link to the Confluence Space if pages were successfully created, or handles any error properly. API calls will be issued in a concurrent manner. 

Main components:
1. CRUD operations
2. Database connection Manager
