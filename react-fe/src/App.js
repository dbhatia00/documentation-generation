// frontend/src/App.js
import React, { useState } from 'react';
import './App.css';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [readmeContent, setReadmeContent] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/get_readme', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      const data = await response.json();
      if (response.ok) {
        setReadmeContent(atob(data.readme_content)); // Decode base64 content
        setError('');
      } else {
        setError(data.error || 'Failed to fetch README');
      }
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to fetch README');
    }
  };

  return (
    <div className="App">
      <h1>GitHub README Viewer</h1>
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
        <button type="submit">Fetch README</button>
      </form>
      {error && <p className="error">{error}</p>}
      {readmeContent && (
        <div className="readme">
          <h2>README.md</h2>
          <pre>{readmeContent}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
