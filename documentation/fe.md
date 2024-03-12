# Input
1. After user login, getting user’s information and documentation history from backend.
2. Taking a github url from the user.
3. After getting generated documentation from the LLM model, allowing the user to edit the documentation.
4. Getting confluence url from the confluence interface server and displaying the preview to the user.

# Output
1. After validating the github url, sending the link to backend.

# Component Groups

### Login page
1. User name entry
2. Password entry
3. Third-party site account login option (Github)  
### Home/Main page
1. Background
2. Team info cards
3. URL entry
4. Generate button  
### Documentation page
1. Back button, and regenerate button
2. Documentation
   - IFrame for Confluence page (edit and save functionalities are inside the confluence page)
   - Push Documentation
     - Push button
     - Pop-up window after clicking the push: if the user logged in with a normal account, this window would ask for authorization; if the user logged in with the Github account, this window would ask for confirmation.
### User Info/History page
1. User private information
2. All history generated Confluence page URLs
