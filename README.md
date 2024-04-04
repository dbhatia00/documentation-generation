# documentation-generation

## Overview
Documentation is difficult to write and keep up to date.  Tools exist to generate rudimentary JavaDoc for Java programs, but the result isn’t particularly helpful as it just gives parameter names and return types from the signature and no useful information.  The goal of this project is to provide a more reasonable initial documentation source using LLMs and other tools.  There have been a number of research efforts along this line that could be a good starting point.

## Initial Implementation Goals

### Description
A web app that, when provided a github link, generates a confluence page describing what the app does based on classes/methods within. This process will work on most mainstream languages, but will be implemented focusing on a Java source code target. The confluence pages shall follow the same file structure as the source code and shall have a one to one mapping. Each page shall describe the source code at the functional level, ensuring that the source code is covered to an acceptable level. 


### LLM Implementation
We will be implementing a Retrieval-Augmented Generation (RAG) backend. RAG is the process of optimizing the output of a large language model, so it references an authoritative knowledge base outside of its training data sources before generating a response. The Retrieval-Augmented Generation (RAG) approach enhances Large Language Models (LLMs) by integrating a step to fetch new data based on user inputs, thus improving response accuracy. This process involves collecting new information from diverse sources (a code base in our use case) and converting it into a format the LLM can search. It then matches user queries with this external data using vector representations for precise retrieval. Finally, the process enriches user prompts with the retrieved data, enabling the LLM to generate responses that are not only accurate but also contextually relevant, leveraging both its pre-existing knowledge and newly acquired information.

### Documentation Regeneration
As far as updating goes, we will integrate Github Actions with our implementation such that a push to main in a hypothetical target repository would trigger a regeneration of the confluence page. This will ensure that the documentation remains up to date


# Run instructions

## Backend
1. python3 -m venv env
2. source env/bin/activate
3. pip install flask
4. pip install python-dotenv
5. pip install requests
6. cd flask-be
7. flask run

The backend should now be running

## Frontend
1. cd react_fe
2. npm install
3. npm start

The frontend screen should now be running

## Usage
Enter a github url in the following form - 
*{username}/{repo name}*