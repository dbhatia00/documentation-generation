// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';
import clientInfo from './token_client.json';

function loginWithClientId() {
  // Adding more scope if needed in the future
  const scopes = 'repo';
  window.location.assign(
    'https://github.com/login/oauth/authorize?client_id=' +
      clientInfo.client_id +
      '&scope=' +
      scopes
  );
}

function App() {
  // State variables to store repository URL, doc content, and output messages
  // TODO: Remove all references to a doc, replace with the generated documentation
  const [repoUrl, setRepoUrl] = useState('');
  const [docContent, setdocContent] = useState('');
  const [output, setOutput] = useState('');
  const [rerender, setRerender] = useState(false);

  useEffect(() => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const codeParam = urlParams.get('code');

    if (codeParam && localStorage.getItem('accessToken') === null) {
      async function getAccessToken() {
        await fetch('/api/get_access_token?code=' + codeParam, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
          .then((response) => {
            return response.json();
          })
          .then((data) => {
            console.log(data);
            if (data.access_token) {
              localStorage.setItem('accessToken', data.access_token);
              setRerender(!rerender);
            }
          });
      }

      getAccessToken();
    }
  }, [rerender]);

  // Button to handle the github URL and fetch the doc
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Sends the repo URL to the backend
      const response = await fetch('/api/get_doc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      // Acquires the doc content from the backend and dumps it in the box
      const data = await response.json();
      if (response.ok) {
        setdocContent((data.doc_content)); // Decode base64 content
        setOutput('');
      } else {
        setOutput(data.error || 'Failed to fetch doc');
      }
    } catch (error) {
      console.error('Error:', error);
      setOutput('Failed to fetch doc');
    }
  };

  // Button to push edits to git
  const handlePushEdits = async () => {
    try {
      // Send the updated text to the backend
      const response = await fetch('/api/push_edits', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + localStorage.getItem('accessToken'),
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          doc_content: docContent,
        }),
      });

      // Waits for a successful push from the backend
      const data = await response.json();
      if (response.ok) {
        // Clear Input fields
        setRepoUrl('');
        setdocContent('');
        setOutput('Push successful!');
        console.log(data); // Log success message or handle as required
      } else {
        setOutput(data.error || 'Failed to push edits');
      }
    } catch (error) {
      console.error('Error:', error);
      setOutput('Failed to push edits');
    }
  };

  const fetchRepoButton = (
    <div>
      {/* URL Input */}
      <form onSubmit={handleSubmit}>
        <label>
          Enter GitHub Repository URL:
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            required
          />
        </label>
        {/* Get doc Button */}
        <button type="submit">Fetch doc</button>
      </form>
      {/* Output Label */}
      {output && <p className="output">{output}</p>}

      {/* Box to hold doc data */}
      {docContent && (
        <div className="doc">
          <h2>Generated Doc</h2>
          <textarea
            value={docContent}
            onChange={(e) => setdocContent(e.target.value)}
            rows={10}
            cols={80}
          />
          {/* Push edits to repository button */}
          <button onClick={handlePushEdits}>Push Edits</button>
        </div>
      )}
    </div>
  );

  return (
    <div className="App">
      <h1>Documentation Generation</h1>
      <div>
        {localStorage.getItem('accessToken') ? (
          <div>
            {fetchRepoButton}
            <button
              onClick={() => {
                localStorage.removeItem('accessToken');
                setRerender(!rerender);
              }}
            >
              Logout
            </button>
          </div>
        ) : (
          <div>
            <button onClick={loginWithClientId}>Login with Github</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
