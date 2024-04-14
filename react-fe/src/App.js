// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';
import {
  loginWithClientId,
  linkToConfluenceAccount,
  getAccessToken,
  getConfluenceAccessToken,
} from './util/login';

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
    const stateParam = urlParams.get('state');
    const codeParam = urlParams.get('code');

    if (
      !stateParam &&
      codeParam &&
      localStorage.getItem('accessToken') === null
    ) {
      // fetch access token for github
      getAccessToken(codeParam, rerender, setRerender);
    }

    if (
      stateParam === 'confluence' &&
      localStorage.getItem('confluenceAccessToken') === null
    ) {
      getConfluenceAccessToken(codeParam, rerender, setRerender);
    }
  }, []);

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
        setdocContent(data.doc_content); // Decode base64 content
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

  // TODO: Adding more logic related to confluence here
  const handleConfluencePush = () => {
    console.log(
      'push to confluence with access code',
      localStorage.getItem('confluenceAccessToken')
    );
  };

  const LinkConfluenceButton = (
    <div
      style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}
    >
      {localStorage.getItem('confluenceAccessToken') ? (
        <>
          {!docContent && <p>You have linked to your Confluence account</p>}
          <button
            onClick={handleConfluencePush}
            disabled={!docContent}
            style={{ marginBottom: '20px', width: 'fit-content' }}
          >
            Push to Confluence
          </button>
        </>
      ) : (
        <>
          <p>
            You need to connect to your Confluence account to generate a
            confluence doc:
          </p>
          <button
            onClick={linkToConfluenceAccount}
            style={{ marginBottom: '20px', width: 'fit-content' }}
          >
            Link To Confluence
          </button>
        </>
      )}
    </div>
  );

  const FetchRepoButton = (
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
            {FetchRepoButton}
            {LinkConfluenceButton}
            <button
              onClick={() => {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('confluenceAccessToken');
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
