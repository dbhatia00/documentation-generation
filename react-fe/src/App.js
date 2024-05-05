// frontend/src/App.js
import React, { useState, useEffect } from "react";
import { ReactTyped } from "react-typed";
import { useSpring, animated, config } from "@react-spring/web";
import "./App.css";
import {
  loginWithClientId,
  linkToConfluenceAccount,
  getAccessToken,
  getConfluenceAccessToken,
} from "./util/login";
import { MainPageText, GithubLoggedInText, CreateConfluenceText } from "./util/text";


function App() {
  // State variables to store repository URL, doc content, and output messages
  // TODO: Remove all references to a doc, replace with the generated documentation
  const [repoUrl, setRepoUrl] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [confluenceDomain, setConfluenceDomain] = useState("");
  const [apiToken, setApiToken] = useState("");

  // const [mainText, setMainText] = useState(MainPageText)

  const [docContent, setdocContent] = useState("");
  const [output, setOutput] = useState("");
  const [cfOutput, setCfOutput] = useState("");
  const [rerender, setRerender] = useState(false);
  const [{ background }] = useSpring(
    () => ({
      from: { background: "#ffffff" },
      to: [
        { background: "#ffffff" },
        { background: "#efefef" },
        { background: "#dedede" },
        { background: "#c9c9c9" },
        { background: "#dedede" },
        { background: "#efefef" },
      ],
      config: config.molasses,
      loop: {
        reverse: true,
      },
    }),
    []
  );

  useEffect(() => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const stateParam = urlParams.get("state");
    const codeParam = urlParams.get("code");

    if (
      !stateParam &&
      codeParam &&
      localStorage.getItem("accessToken") === null
    ) {
      // fetch access token for github
      getAccessToken(codeParam, rerender, setRerender);
    }

    if (
      stateParam === "confluence" &&
      localStorage.getItem("confluenceAccessToken") === null
    ) {
      getConfluenceAccessToken(codeParam, rerender, setRerender);
    }

    console.log(localStorage);
  }, []);

  // Button to handle the github URL and fetch the doc
  const handleSubmit = async (e) => {
    e.preventDefault();
    setOutput("Generating Content..."); // Generating Content...
    try {
      // Sends the repo URL to the backend
      const response = await fetch("/api/get_doc", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      // Acquires the doc content from the backend and dumps it in the box
      const data = await response.json();
      if (response.ok) {
        setdocContent(data.doc_content); // Decode base64 content
        setOutput("Fetch successful!");
      } else {
        setOutput(data.error || "Failed to fetch doc");
      }
    } catch (error) {
      console.error("Error:", error);
      setOutput("Failed to fetch doc");
    }
  };

  const handleCreateConfluence = async () => {
    try {
      const response = await fetch("/api/create_confluence", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          confluence_domain: confluenceDomain,
          repo_url: "https://github.com/" + repoUrl,
          email: userEmail,
          api_token: apiToken,
          cloud_id: localStorage.getItem("confluenceCloudId"),
          confluence_access_code: localStorage.getItem("confluenceAccessToken"),
        }),
      });

      if (response.ok) {
        alert("Confluence Page Created Successfully!");
        setCfOutput("Created Confluence Domain Successfully!");
      } else {
        alert("Failed to create confluence");
        setCfOutput("Failed to create confluence");
      }
    } catch (error) {
      console.error("Error:", error);
      setCfOutput("Failed to create confluence");
      setOutput("Failed to create confluence");
    }
  };

  const FetchOutput = () => {
    if (output === "Generating Content...") {
      return (
        <div class="row">
          <div class="col-md-2">
            <p class="loader"></p>
          </div>
          <div class="col-md-10">{output}</div>
        </div>
      );
    } else if (output === "") {
      return <div> </div>;
    } else if (output === "Push successful!") {
      return (
        <div>
          {output} <i class="fa-solid fa-thumbs-up"></i>
        </div>
      );
    } else if (output === "Fetch successful!") {
      return (
        <div>
          {output} <i class="fa-solid fa-thumbs-up"></i>
        </div>
      );
    } else {
      // all error case
      return (
        <div>
          {output} <i class="fa-solid fa-bomb"></i>
        </div>
      );
    }
  };

  const CreateOutput = () => {
    if (cfOutput === "Created Confluence Domain Successfully!") {
      return (
        <div>
          {cfOutput} Don't forget to refresh your Confluence{" "}
          <i class="fa-solid fa-thumbs-up"></i>
        </div>
      );
    } else {
      return (
        <div>
          {cfOutput} <i class="fa-solid fa-bomb"></i>
        </div>
      );
    }
  };

  // TODO: Adding more logic related to confluence here
  const handleConfluencePush = () => {
    console.log(
      "push to confluence with access code",
      localStorage.getItem("confluenceAccessToken")
    );
    handleCreateConfluence()
  };

  const CreateConfluenceButton = (
    <button
      type="button"
      class="btn btn-dark mb-4"
      onClick={handleCreateConfluence}
    >
      Create Confluence Domain
    </button>
  );


  const LinkConfluenceButton = (
    <div>
      {localStorage.getItem("confluenceAccessToken") ? (
        <>
          {!docContent && <p>You have linked to your Confluence account</p>}
          <button
            type="button"
            class="btn btn-dark"
            onClick={handleConfluencePush}
            disabled={!output}
          >
            Push to Confluence
          </button>
        </>
      ) : (
        <>
          <button
            type="button"
            class="btn btn-dark"
            onClick={linkToConfluenceAccount}
          >
            Link To Confluence
          </button>
        </>
      )}
    </div>
  );

  const CreateConfluenceField = (
    <div>
      { (
        // <div>
        //   <div class="row mt-4 mb-4">
        //   <div class="col-md">
        //       <div class="form-floating">
        //         <input type='text' value={confluenceDomain}
        //             onChange={(e) => setConfluenceDomain(e.target.value)}
        //             required
        //             class="form-control"
        //             id="confluence-domain">
        //         </input>
        //         <label for="confluence-domain">Confluence Domain</label>
        //       </div>
        //   </div>
        //   <div class="col-md">
        //     <div class="form-floating">
        //         <input type='email' value={userEmail}
        //             onChange={(e) => setUserEmail(e.target.value)}
        //             required
        //             class="form-control"
        //             id="user-email">
        //         </input>
        //         <label for="user-email">Email</label>
        //     </div>
        //   </div>
        // </div>

        // <div class="row mb-4">
        //     <div class="col form-floating">
        //         <input type='text' value={apiToken}
        //             onChange={(e) => setApiToken(e.target.value)}
        //             required
        //             class="form-control"
        //             id="api-token">
        //         </input>
        //         <label for="api-token">API Token</label>
        //     </div>
        // </div>
        <div>
          {LinkConfluenceButton}
          {/* {CreateConfluenceButton} */}
          {cfOutput && (
            <div class='fs-6'>
              <CreateOutput />
            </div>
          )}
        </div>
      )}
    </div>
  );


  const FetchRepoInputBox = (
    // <div class="border border-secondary-subtle rounded p-2">
    <div>
      {/* URL Input */}
      <form onSubmit={handleSubmit}>
        <div class="input-group mb-4">
          <span class="input-group-text" id="enter-url">
            Enter GitHub Repository
          </span>
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            required
            class="form-control"
            id="basic-url"
            aria-describedby="enter-url"
            placeholder="{username}/{repo name}"
          />
          <button class="btn btn-dark" type="submit">
            Fetch
          </button>
        </div>
        {/* Get doc Button */}
      </form>
      {/* Output Label */}
      {output && (
        <div class="fs-6">
          <FetchOutput />
        </div>
      )}

      {CreateConfluenceField}
    </div>
  );

  const CardClickNavigateOne = () => {
    window.open(
      "https://github.com/dbhatia00/documentation-generation/blob/main/README.md"
    );
  };

  const CardClickNavigateTwo = () => {
    window.open(
      "https://github.com/dbhatia00/documentation-generation/blob/main/documentation/Roles.md"
    );
  };

  const CardClickNavigateThree = () => {
    window.open("https://github.com/dbhatia00/documentation-generation/issues");
  };

  return (
    <div class="main-theme">
      <div>
        <div class="row ps-4 pe-5">
          <div class="col-md-7 border border-2 border-secondary-subtle rounded-3 p-0">
            <div class="mb-5">
              <nav class="navbar bg-body-tertiary custom-navbar border-top border-bottom border-2 border-secondary-subtle rounded-3">
                <div class="container-fluid ps-2">
                  <div class="justify-content-start">
                    <button
                      class="btn btn-sm btn-outline-secondary custom-preview ps-3 pe-3"
                      type="button"
                    >
                      <span class="custom-bold">Preview</span>
                    </button>
                    <button
                      class="btn btn-sm btn-light custom-code ps-3 pe-3"
                      type="button"
                    >
                      Code&nbsp;&nbsp;&nbsp;<span class="custom-bar">|</span>
                      &nbsp;&nbsp;&nbsp;Blame
                    </button>
                  </div>
                  <div>
                    <div
                      class="btn-group me-2"
                      role="group"
                      aria-label="Button group"
                    >
                      <button type="button" class="btn btn-sm btn-light border">
                        <span class="custom-bold">Raw</span>
                      </button>
                      <button type="button" class="btn btn-sm btn-light border">
                        <i class="fa-regular fa-copy custom-icon"></i>
                      </button>
                      <button type="button" class="btn btn-sm btn-light border">
                        <i class="fa-solid fa-download custom-icon"></i>
                      </button>
                    </div>

                    <div
                      class="btn-group me-3"
                      role="group"
                      aria-label="Button group"
                    >
                      <button type="button" class="btn btn-sm btn-light border">
                        <i class="fa-solid fa-pencil custom-icon"></i>
                      </button>
                      <button type="button" class="btn btn-sm btn-light border">
                        <i class="fa-solid fa-caret-down custom-icon"></i>
                      </button>
                    </div>

                    <i class="fa-solid fa-bars custom-icon"></i>
                  </div>
                </div>
              </nav>

              {/* <div class="line"></div> */}

              <div class="mainbg-base mt-3 ms-5 me-5">
                <ReactTyped
                  strings={[
                    localStorage.getItem("accessToken")
                      ? GithubLoggedInText
                      : MainPageText,
                  ]}
                  typeSpeed={3}
                  contentType="html"
                  cursorChar=""
                />
                {/* <div className="cursor" style={{ display: 'inline-block' }}>|</div> */}
              </div>

              <div class="mt-3 ms-5 me-5">
                <div class="maintitle opa-anime-two">
                  <div>
                    {localStorage.getItem("accessToken") ? (
                      <div>
                        {FetchRepoInputBox}
                        <div class="row mt-3">
                          <div class="col-md-6">
                            <button
                              class="btn btn-danger"
                              onClick={() => {
                                localStorage.removeItem("accessToken");
                                localStorage.removeItem(
                                  "confluenceAccessToken"
                                );
                                localStorage.removeItem("confluenceCloudId");
                                setRerender(!rerender);
                              }}
                            >
                              Github Logout
                            </button>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <button
                        class="btn btn-success align-middle"
                        onClick={loginWithClientId}
                      >
                        Login with Github: Generate your own project
                        documentation
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-5">
            <div class="col-container">
              <animated.div
                class="card fixed-height mt-4 d-none d-md-block right-card"
                style={{ background }}
                onClick={CardClickNavigateOne}
              >
                <div class="card-body">
                  <h5 class="card-title">Documentation Generation</h5>
                  <h6 class="card-subtitle mb-2 text-body-secondary">
                    Learn more about our project
                  </h6>
                  <p class="card-text">Take a look at our README!</p>
                </div>
              </animated.div>
              <animated.div
                class="card fixed-height mt-4 d-none d-md-block right-card"
                style={{ background }}
                onClick={CardClickNavigateTwo}
              >
                <div class="card-body">
                  <h5 class="card-title">About Us</h5>
                  <h6 class="card-subtitle mb-2 text-body-secondary">
                    Learn more about our team
                  </h6>
                  <p class="card-text">Take a look at our contributors!</p>
                </div>
              </animated.div>
              <animated.div
                class="card fixed-height mt-4 d-none d-md-block right-card"
                style={{ background }}
                onClick={CardClickNavigateThree}
              >
                <div class="card-body">
                  <h5 class="card-title">Looking Forward</h5>
                  <h6 class="card-subtitle mb-2 text-body-secondary">
                    Learn more about future works
                  </h6>
                  <p class="card-text">Take a look at our open issues!</p>
                </div>
              </animated.div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
