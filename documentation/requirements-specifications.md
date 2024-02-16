# Requirements and Specifications Document

## Specifications
1. The initial implementation of our project will be a web app that, when provided with a github link, generates a confluence page describing what the app does based on classes/methods within.
2. The confluence pages shall follow the same file structure as the source code and shall have a one to one mapping. Each page shall describe the source code at the functional level, ensuring that the source code is covered to an acceptable level.
3. We will be implementing a Retrieval-Augmented Generation (RAG) backend. RAG is the process of optimizing the output of a large language model, so it references an authoritative knowledge base outside of its training data sources before generating a response. The Retrieval-Augmented Generation (RAG) approach enhances Large Language Models (LLMs) by integrating a step to fetch new data based on user inputs, thus improving response accuracy. This process involves collecting new information from diverse sources (a code base in our use case) and converting it into a format the LLM can search
4. As far as updating goes, we will integrate Github Actions with our implementation such that a push to main in a hypothetical target repository would trigger a regeneration of the confluence page. This will ensure that the documentation remains up to date
