# GitHub Action Workflow

## Input

When a push event occurs in the main branch of the repository, the GitHub Action is triggered.

- The GitHub Action is triggered by a push event in the main branch of the repository.
- It retrieves the modified source code file(s) and checks for existing Confluence pages associated with them.
- If an existing Confluence page is found, the GitHub Action sends the source code along with the Confluence page ID to the Flask backend. The backend then calls the Confluence page generation API to update the page.
- If no existing Confluence page is found for the file, the GitHub Action sends the source code to the Flask backend to initiate the process of generating new Confluence page(s).

## Flask Backend

The Flask backend receives the request from the GitHub Action. It then performs the necessary tasks:

- Calls the LLM and RAG API to analyze the source code and generate the updated documentation.
- Updates the Confluence pages based on the results obtained.
- Optionally, it could implement logic to identify and update only the parts of the documentation corresponding to the modified source code, optimizing resource usage.
- Once the documentation generation process is complete, the backend responds to the GitHub Action indicating the success or failure of the operation.

## Output

Upon receiving the response from the backend, the GitHub Action proceeds accordingly:

- If the documentation generation was successful, it completes the workflow, indicating success.
- If there is a failure, it handles the error gracefully, potentially triggering notifications or logging the issue for further investigation.
