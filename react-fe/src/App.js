// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ReactTyped } from "react-typed";
import { useSpring, animated, config } from '@react-spring/web'
import './App.css';
import {
  loginWithClientId,
  linkToConfluenceAccount,
  getAccessToken,
  getConfluenceAccessToken,
} from './util/login';

const MainPageText = `
  <div class="mainbg-text-title">Project Name</div>

  <div class="mainbg-text-subtitle">Overview</div>
  <div class="mainbg-text-content">[Project Name] is an open-source Java library aimed at [brief description of the library's purpose or main functionality].</div>

  <div class="mainbg-text-subtitle">Features</div>
  <ul class="mainbg-text-content">
  <li>Feature 1: Description of feature 1.</li>
  <li>Feature 2: Description of feature 2.</li>
  <li>Feature 3: Description of feature 3.</li>
  </ul>
  <div class="mainbg-text-subtitle">Installation</div>
  <div class="mainbg-text-content">To use [Project Name] in your Java project, you can include it as a dependency in your build configuration. If you're using Maven, add the following dependency to your 'pom.xml'</div>
  <div class="mainbg-text-content">. . .</div>
  `;

const GithubLoggedInText = `
  <div class="mainbg-text-title col-md">Login Success</div>

  <div class="mainbg-text-subtitle">Fetch</div>
  <div class="mainbg-text-content">Almost there! Using the {username}/{repo name} format, enter your Github repo name below and click fetch.</div>

  <div class="mainbg-text-subtitle">Times</div>
  <ul class="mainbg-text-content">
  <li>Please note that it takes some time to generate the documentation</li>
  <li>One moment, please :)</li>
  </ul>
  <div class="mainbg-text-subtitle">Confluence Page</div>
  <div class="mainbg-text-content">To use [Project Name] Please use the "Link to Confluence" button below to give us authorization for your confluence page, so that we can store the generated documents in your confluence.</div>
`

const CreateConfluenceText = `
  <div class="mainbg-text-title col-md">Generated Successfully</div>

  <div class="mainbg-text-subtitle">Confluence Page</div>
  <div class="mainbg-text-content">Here we go! Please provide your email, Confluence domain, and API token. This way we can store your stuff in your Confluence so you can view and edit it!</div>

`

function App() {
  // State variables to store repository URL, doc content, and output messages
  // TODO: Remove all references to a doc, replace with the generated documentation
  const [repoUrl, setRepoUrl] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [confluenceDomain, setConfluenceDomain] = useState('');
  const [apiToken, setApiToken] = useState('');

  const [mainText, setMainText] = useState(MainPageText)

  const [docContent, setdocContent] = useState('');
  const [output, setOutput] = useState('');
  const [rerender, setRerender] = useState(false);
  const [{ background }] = useSpring(
    () => ({
      from: { background: '#ffffff' },
      to: [
        { background: '#ffffff' },
        { background: '#efefef' },
        { background: '#dedede' },
        { background: '#c9c9c9' },
        { background: '#dedede' },
        { background: '#efefef' },
      ],
      config: config.molasses,
      loop: {
        reverse: true,
      },
    }),
    []
  )

  // const [{ background: background2 }] = useSpring(
  //   () => ({
  //     from: { background: '#efefef' },
  //     to: [
  //       { background: '#efefef' },
  //       { background: '#dedede' },
  //       { background: '#c9c9c9' },
  //       { background: '#dedede' },
  //       { background: '#efefef' },
  //       { background: '#ffffff' },
  //     ],
  //     config: config.molasses,
  //     loop: {
  //       reverse: true,
  //     },
  //   }),
  //   []
  // )

  // const [{ background3 }] = useSpring(
  //   () => ({
  //     from: { background: '#dedede' },
  //     to: [
  //       { background: '#dedede' },
  //       { background: '#c9c9c9' },
  //       { background: '#dedede' },
  //       { background: '#efefef' },
  //       { background: '#ffffff' },
  //       { background: '#efefef' },
  //     ],
  //     config: config.molasses,
  //     loop: {
  //       reverse: true,
  //     },
  //   }),
  //   []
  // )
  

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
    setOutput('Generating Content...') // Generating Content...
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
        setOutput('Fetch successful!');
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

  const handleCreateConfluence = async () => {
    try {
      console.log("I've been there")
      console.log("email", userEmail)
      console.log("repo_url", repoUrl)
      console.log("confluence domain", confluenceDomain)
      console.log("api_token", apiToken)
      const response = await fetch('/api/create_confluence', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          confluence_domain: confluenceDomain,
          repo_url: "https://github.com/" + repoUrl,
          email: userEmail,
          api_token: apiToken,
        }),
      });

      if (response.ok) {
        alert("Confluence Page Created Successfully!")
      } else {
        alert("Confluence Page Creation: Error!")
      }
    
    } catch (error) {
      console.error('Error:', error);
      setOutput('Failed to create confluence');
    }
  }

  const FetchOutput = () => {
    if (output === 'Generating Content...') {
      return <div class="row">
                <div class="col-md-2"><p class="loader"></p></div>
                <div class="col-md-10">{output}</div>
              </div>
    } else if (output === '') {
      return <div> </div>
    } else if (output === 'Push successful!') {
      return <div>{output} <i class="fa-solid fa-thumbs-up"></i></div>
    } else if (output === 'Fetch successful!') {
      return <div>{output} <i class="fa-solid fa-thumbs-up"></i></div>
    }
    else {
      // all error case
      return <div>{output} <i class="fa-solid fa-bomb"></i></div>
    }
  }

  // TODO: Adding more logic related to confluence here
  const handleConfluencePush = () => {
    console.log(
      'push to confluence with access code',
      localStorage.getItem('confluenceAccessToken')
    );
  };

  const CreateConfluenceButton = (
    <button type="button" class="btn btn-dark mb-4" onClick={handleCreateConfluence}>
      Create Confluence Domain
    </button>
  )

  const CreateConfluenceField = (
    <div>
      {docContent && output === 'Fetch successful!' &&
        <div>
                <div class="row mt-4 mb-4">
          <div class="col-md">
              <div class="form-floating">
                <input type='text' value={confluenceDomain}
                    onChange={(e) => setConfluenceDomain(e.target.value)}
                    required
                    class="form-control"
                    id="confluence-domain">
                </input>
                <label for="confluence-domain">Confluence Domain</label>
              </div>
          </div>
          <div class="col-md">
            <div class="form-floating">
                <input type='email' value={userEmail}
                    onChange={(e) => setUserEmail(e.target.value)}
                    required
                    class="form-control"
                    id="user-email">
                </input>
                <label for="user-email">Email</label>
            </div>
          </div>
        </div>

        <div class="row mb-4">
            <div class="col form-floating">
                <input type='text' value={apiToken}
                    onChange={(e) => setApiToken(e.target.value)}
                    required
                    class="form-control"
                    id="api-token">
                </input>
                <label for="api-token">API Token</label>
            </div>
        </div>

        {CreateConfluenceButton}

        </div>
      }
    </div>
  )

  const LinkConfluenceButton = (
    <div>
      {localStorage.getItem('confluenceAccessToken') ? (
        <>
          {!docContent && <p>You have linked to your Confluence account</p>}
          <button
            type="button" class="btn btn-dark"
            onClick={handleConfluencePush}
            disabled={!docContent}
          >
            Push to Confluence
          </button>
        </>
      ) : (
        <>
          <button
            type="button" class="btn btn-dark"
            onClick={linkToConfluenceAccount}
          >
            Link To Confluence
          </button>
        </>
      )}
    </div>
  );

  const FetchRepoInputBox = (
    // <div class="border border-secondary-subtle rounded p-2">
    <div>
      {/* URL Input */}
      <form onSubmit={handleSubmit}>
        <div class="input-group mb-4">
          <span class="input-group-text" id="enter-url">Enter GitHub Repository</span>
          <input type="text" value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              required
              class="form-control"
              id="basic-url"
              aria-describedby="enter-url"
              placeholder='{username}/{repo name}'/>
              <button class="btn btn-dark" type="submit">Fetch</button>
        </div>
        {/* Get doc Button */}
      </form>
      {/* Output Label */}
      {output && <div class="fs-6"><FetchOutput /></div>}

      {CreateConfluenceField}

      {/* Box to hold doc data */}
      {
      // docContent && (
      //   <div className="doc">
      //     <h2>Generated Doc</h2>
      //     <textarea
      //       value={docContent}
      //       onChange={(e) => setdocContent(e.target.value)}
      //       rows={10}
      //       cols={80}
      //     />
      //     {/* Push edits to repository button */}
      //     <button onClick={handlePushEdits}>Push Edits</button>
      //   </div>
      // )
      }
    </div>
  );

  const CardClickNavigateOne = () => {
    window.open("https://github.com/dbhatia00/documentation-generation")
  }

  const CardClickNavigateTwo = () => {
    window.open("https://github.com/dbhatia00/documentation-generation/blob/main/documentation/Roles.md")
  }

  const CardClickNavigateThree = () => {
    window.open()
  }


  const fakeOnClick = () => {
    console.log(docContent)
    console.log(output)
    setdocContent("1111111")
    setOutput('Fetch successful!')
  }


  return (
    <div class="main-theme">
        <div class="container">
        <div class="row">
          <div class="col-6">
            <div class="mainbg-base">
              <ReactTyped strings={[
                localStorage.getItem('accessToken') ? GithubLoggedInText : (docContent && output === 'Fetch successful!') ? CreateConfluenceText : MainPageText
                ]} typeSpeed={3} contentType="html" cursorChar=""/>
              {/* <div className="cursor" style={{ display: 'inline-block' }}>|</div> */}
            </div>
          </div>
        </div>

        {/* <div>
          <button onClick={fakeOnClick}>fake click</button>
        </div> */}

          <div class="row mt-2">
            <div class="col-6">
              <div class="maintitle opa-anime-two">
                <div>
                {localStorage.getItem('accessToken') ? (
                    <div>
                      {FetchRepoInputBox}
                      <div class="row mt-2">
                        {/* <div class="col-md-6">
                          {LinkConfluenceButton}
                        </div> */}
                        {/* <div class="col-md-6 d-md-flex justify-content-md-end"> */}
                        <div class="col-md-6">
                          <button
                            class="btn btn-danger"
                            onClick={() => {
                              localStorage.removeItem('accessToken');
                              localStorage.removeItem('confluenceAccessToken');
                              setRerender(!rerender);
                            }}
                          >
                            Github Logout
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : <button class="btn btn-success align-middle" onClick={loginWithClientId}>Login with Github: Generate your own project documentation</button>}
                </div>
              </div>
              
              {/* <h1 class='fs-3 border border-success p-2 mb-2 border-3 rounded-pill border-opacity-75 roboto-regular mb-5 maintitle text-success opa-anime-two'>
                Documentation Generation <span></span>
              </h1> */}
              <div>

                </div>
            </div>
            <div class="col-6">
              <div class="col-container">
                    <animated.div class="card fixed-height mt-4 d-none d-md-block right-card" style={{ background }} onClick={CardClickNavigateOne}>
                      <div class="card-body">
                        <h5 class="card-title">Documentation Generation</h5>
                        <h6 class="card-subtitle mb-2 text-body-secondary">Learn more about our project</h6>
                        <p class="card-text">A web app that, when provided a github link, generates a confluence page describing what the app does based on classes/methods within. This process will work on most mainstream languages, but will be implemented focusing on a Java source code target. </p>
                      </div>  
                    </animated.div>
                    <animated.div class="card fixed-height mt-4 d-none d-md-block right-card" style={{ background }} onClick={CardClickNavigateTwo}>
                      <div class="card-body">
                        <h5 class="card-title">About Us</h5>
                        <h6 class="card-subtitle mb-2 text-body-secondary">Learn more about our team</h6>
                        <p class="card-text">Details details details details details details details details details details details details, details details details details details details details details. details details details details details details details details details details details details details details.</p>
                      </div>  
                    </animated.div>
                    <animated.div class="card fixed-height mt-4 d-none d-md-block right-card" style={{ background }} onClick={CardClickNavigateThree}>
                      <div class="card-body">
                        <h5 class="card-title">Looking Forward</h5>
                        <h6 class="card-subtitle mb-2 text-body-secondary">Learn more about future works</h6>
                        <p class="card-text">Details details details details details details details details details details details details, details details details details details details details details. details details details, details details details.</p>
                      </div>  
                    </animated.div>
                    {/* <div class="card-background"></div> */}
              </div>
            </div>
          </div>
        </div>
    </div>
  );
}

export default App;
