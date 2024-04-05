// frontend/src/App.js
import React, { useState } from 'react';
import './App.css';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [readmeContent, setReadmeContent] = useState('');
  const [output, setOutput] = useState('');

  // Button to handle the github URL and fetch the README
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Sends the repo URL to the backend
      const response = await fetch('/api/get_readme', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      // Acquires the readme content from the backend and dumps it in the box
      const data = await response.json();
      if (response.ok) {
        setReadmeContent(atob(data.readme_content)); // Decode base64 content
        setOutput('');
      } else {
        setOutput(data.error || 'Failed to fetch README');
      }
    } catch (error) {
      console.error('Error:', error);
      setOutput('Failed to fetch README');
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
        },
        body: JSON.stringify({ repo_url: repoUrl, readme_content: readmeContent }),
      });
  
      // Waits for a successful push from the backend
      const data = await response.json();
      if (response.ok) {
        // Clear Input fields
        setRepoUrl('');
        setReadmeContent('');
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
  
  return (
    <div className="App">
      <h1>GitHub README Viewer</h1>
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
        {/* Get README Button */}
        <button type="submit">Fetch README</button>
      </form>
      {output && <p className="output">{output}</p>}

      {readmeContent && (
        <div className="readme">
          <h2>README.md</h2>
          <textarea
            value={readmeContent}
            onChange={(e) => setReadmeContent(e.target.value)}
            rows={10} 
            cols={80} 
          />
          <button onClick={handlePushEdits}>Push Edits</button>
        </div>
      )}
    </div>
  );
}

export default App;
