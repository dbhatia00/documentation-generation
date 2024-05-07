// frontend/src/App.js
import React, { useState, useEffect } from "react";
import { ReactTyped } from "react-typed";
import "./App.css";
import {
  getAccessToken,
  getConfluenceAccessToken,
  isUserLoggedIn,
  linkToConfluenceAccount
} from "./util/login";
import {
  MainPageText,
  GithubLoggedInText,
  CreateConfluenceText,
} from "./util/text";
import Info from "./components/Info";
import Login from "./components/Login";
import NavBar from "./components/NavBar";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [docContent, setdocContent] = useState("");
  const [output, setOutput] = useState("");
  const [cfOutput, setCfOutput] = useState("");
  const [rerender, setRerender] = useState(false);
  const [commitHash, setCommitHash] = useState("");

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
      getConfluenceAccessToken(repoUrl, codeParam, rerender, setRerender);
    }

    console.log(localStorage);
  }, []);
  const handleSetupWebhook = async () => {
    if (!repoUrl) {
      setOutput(
        "Please provide a GitHub repository URL before setting up a webhook."
      );
      return;
    }
    try {
      const response = await fetch("/setup-webhook", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + localStorage.getItem("accessToken"),
        },
        body: JSON.stringify({
          repo_url: repoUrl,
        }),
      });
      const data = await response.json();

      if (response.ok) {
        setCfOutput("Webhook setup successfully!");
      } else if (response.status === 500 && data.errors) {
        const hookAlreadyExists = data.errors.some(
          (error) => error.message === "Hook already exists on this repository"
        );

        if (hookAlreadyExists) {
          setCfOutput("Webhook already exists on this repository.");
        } else {
          setCfOutput("Failed to set up webhook: " + data.message);
        }
      } else {
        throw new Error(data.error || "Failed to set up webhook");
      }
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setOutput("Generating Content..."); // Generating Content...
    setCfOutput("")
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
        setCommitHash(data.commit_hash);
        console.log(commitHash)
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
      setCfOutput("Creating Confluence Space...");
      const response = await fetch("/api/create_confluence", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: "https://github.com/" + repoUrl,
          cloud_id: localStorage.getItem("confluenceCloudId"),
          confluence_access_code: localStorage.getItem("confluenceAccessToken"),
          commit_hash: commitHash,
        }),
      });

      if (response.ok) {
        alert("Confluence Page Created Successfully!");
        setCfOutput("Created Confluence Domain Successfully!");
      } else {
        alert("Failed to create confluence ");
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
        <div>{SetupWebhookButton}</div>
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

  const CreateConfluenceButton = (
    <button
      type="button"
      class="btn btn-dark mb-4"
      onClick={handleCreateConfluence}
    >
      Push to a new Confluence space
    </button>
  );

  const handleConfluencePush = () => {
    console.log(
      "push to confluence with access code",
      localStorage.getItem("confluenceAccessToken")
    );
    handleCreateConfluence()
  };

  const LinkConfluenceButton = (
    <div>
      {localStorage.getItem("confluenceAccessToken") ? (
        <>
          {!docContent && <p>You have linked to your Confluence account</p>}
          <button
            type="button"
            class="btn btn-dark"
            onClick={handleConfluencePush}
            
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
      {
        <div>
          {LinkConfluenceButton}
          {/* {localStorage.getItem("confluenceAccessToken") !== null && CreateConfluenceButton} */}
          {cfOutput && (
            <div class="fs-6">
              <CreateOutput />
            </div>
          )}
        </div>
      }
    </div>
  );
  const SetupWebhookButton = (
    <button
      type="button"
      className="btn btn-dark mb-4"
      onClick={handleSetupWebhook}
    >
      Setup Webhook
    </button>
  );

  const FetchRepoInputBox = (
    <div>
      <form onSubmit={handleSubmit}>
        <div className="input-group mb-4">
          <span className="input-group-text" id="enter-url">
            Enter GitHub Repository
          </span>
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            required
            className="form-control"
            id="basic-url"
            aria-describedby="enter-url"
            placeholder="{username}/{repo name}"
          />
          <button className="btn btn-dark" type="submit">
            Generate Docs
          </button>
        </div>
      </form>
      {output && (
        <div className="fs-6">
          <FetchOutput />
        </div>
      )}

      {CreateConfluenceField}

      {cfOutput === "Created Confluence Space Successfully!" && repoUrl && (
        <div>{SetupWebhookButton}</div>
      )}
    </div>
  );

  const LogoutButton = (
    <button
      class="btn btn-danger"
      onClick={() => {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("confluenceAccessToken");
        localStorage.removeItem("confluenceCloudId");
        setRerender(!rerender);
      }}
    >
      Logout
    </button>
  );

  return (
    <div class="main-theme">
      <div>
        <div class="row ps-4 pe-5">
          <div class="col-md-7 border border-2 border-secondary-subtle rounded-3 p-0">
            <div class="mb-5">
              <NavBar />
              <div class="mainbg-base mt-3 ms-5 me-5">
                <ReactTyped
                  strings={[
                    isUserLoggedIn() ? GithubLoggedInText : MainPageText,
                  ]}
                  typeSpeed={3}
                  contentType="html"
                  cursorChar=""
                />
              </div>

              <div class="mt-3 ms-5 me-5">
                <div class="maintitle opa-anime-two">
                  <div>
                    {isUserLoggedIn() ? (
                      <div>
                        {FetchRepoInputBox}
                        <div class="row mt-3">
                          <div class="col-md-6">{LogoutButton}</div>
                        </div>
                      </div>
                    ) : (
                      <Login />
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-5">
            <Info />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
