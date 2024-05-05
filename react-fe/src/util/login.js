import clientInfo from "../token_client.json";

export const loginWithClientId = () => {
  // Adding more scope if needed in the future
  const scopes = "repo";
  window.location.assign(
    "https://github.com/login/oauth/authorize?client_id=" +
      clientInfo.client_id +
      "&scope=" +
      scopes
  );
};

export const linkToConfluenceAccount = () => {
  // window.location.assign
  window.open(
    "https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=" +
      clientInfo.confluence_client_id +
      "&scope=offline_access%20write%3Aspace.permission%3Aconfluence%20read%3Aspace.permission%3Aconfluence%20read%3Aspace%3Aconfluence%20read%3Aspace-details%3Aconfluence%20write%3Aspace%3Aconfluence%20delete%3Aspace%3Aconfluence%20read%3Aspace.property%3Aconfluence%20write%3Aspace.property%3Aconfluence%20read%3Apermission%3Aconfluence%20read%3Acontent%3Aconfluence%20write%3Acontent%3Aconfluence%20read%3Acontent-details%3Aconfluence%20delete%3Acontent%3Aconfluence%20read%3Apage%3Aconfluence%20write%3Apage%3Aconfluence%20delete%3Apage%3Aconfluence%20read%3Aattachment%3Aconfluence%20read%3Acustom-content%3Aconfluence%20write%3Acustom-content%3Aconfluence%20delete%3Acustom-content%3Aconfluence%20read%3Atemplate%3Aconfluence%20write%3Atemplate%3Aconfluence%20read%3Auser.property%3Aconfluence%20read%3Aspace.setting%3Aconfluence%20write%3Aspace.setting%3Aconfluence&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2F&state=confluence&response_type=code&prompt=consent"
  );
};

export const getAccessToken = async (codeParam, rerender, setRerender) => {
  try {
    await fetch("/api/get_access_token?code=" + codeParam, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (data.access_token) {
          localStorage.setItem("accessToken", data.access_token);
          setRerender(!rerender);
        }
      });
  } catch (err) {
    console.error("Failed to get access token", err);
  }
};

export const getConfluenceAccessToken = async (
  codeParam,
  rerender,
  setRerender
) => {
  try {
    await fetch("/api/get_confluence_token?code=" + codeParam, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (data.access_token) {
          localStorage.setItem("confluenceAccessToken", data.access_token);
          localStorage.setItem("confluenceCloudId", data.cloud_id);
          setRerender(!rerender);
        }
      });
  } catch (err) {
    console.error("Failed to get access token", err);
  }
};

export const isUserLoggedIn = () => {
  return (
    localStorage.getItem("accessToken") !== null &&
    localStorage.getItem("confluenceAccessToken") !== null
  );
};
