# Input
This service takes in the output of our RAG service, which would ideally include the following in JSON format:
* Project-level Documentation
  * Functionalities
  * Project Components
  * Database Structure
  * Tech Stack
* File-level Documentation
  * Overall Summary
  * Packages
      * Package Summary
  * Function-level Documentation
      * Function Name : Function Description

# Output
Depending on whether a Confluence Space ID is provided, this service will either modify the existing space by inserting pages and subpages, or create a new Confluence Space with the pages inserted. The output of this service will be the existing / newly created Confluence Space.

# Main Functionalities
This service parses the JSON output of our RAG service into a structured HTML page, and then feeds the HTML to a Confluence API request. We intend to use the `Create page` endpoint of the Confluence REST API for each page (one project page and many per-file pages). This service handles the responses from the Confluence API, outputting a link to the Confluence Space if pages were successfully created, or handles any error properly. API calls will be issued in a concurrent manner. 

Main components:
* Parser (JSON -> HTML)
* API Request Constructor
* API Orchestrator (Calling API and handling response)
