# Requirements and Specifications Document

## Functional Requirements
1. Input Sources:
   1.  The app should support various input sources, including source code files, comments, and documentation tags within the code.
2. Language Support:
   1. The app must be able to parse and generate documentation for multiple programming languages.
3. Customization:
   1. Users should be able to customize the documentation output by manually editing the output.
4. Version Control Integration:
   1. Integration with version control systems (e.g., Git) to track changes and update documentation accordingly.
5. Cross-Referencing:
   1. Provide automatic cross-referencing of code elements, allowing users to easily navigate between different parts of the documentation.
6. Documentation Preview:
   1. A real-time preview feature allowing users to see how the documentation will look before finalizing the generation.

## Specifications
1. User Interface
   1. The initial implementation of our project will be a web app that, when provided with a github link, generates a confluence page describing what the app does based on classes/methods within.
2. Output Structure
   1. The confluence pages shall follow the same file structure as the source code and shall have a one to one mapping. Each page shall describe the source code at the functional level, ensuring that the source code is covered to an acceptable level.
3. Manual Editing
   1. When the confluence page is displayed to the user, they will have the ability to manually update text within the Conlfuence app. The documentation shall be able to be updated within our database when a change in the confluence page is detected.  
4. Use of the LLM
   1. We will be implementing a Retrieval-Augmented Generation (RAG) backend. RAG is the process of optimizing the output of a large language model, so it references an authoritative knowledge base outside of its training data sources before generating a response. The Retrieval-Augmented Generation (RAG) approach enhances Large Language Models (LLMs) by integrating a step to fetch new data based on user inputs, thus improving response accuracy. This process involves collecting new information from diverse sources (a code base in our use case) and converting it into a format the LLM can search.
5. Automated Updating
   1. As far as updating goes, we will integrate Github Actions with our implementation such that a push to main in a hypothetical target repository would trigger a regeneration of the confluence page. This will ensure that the documentation remains up to date
