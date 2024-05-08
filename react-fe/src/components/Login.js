import { loginWithClientId, linkToConfluenceAccount } from "../util/login";

export default function Login() {
  const ConfluenceLoginButton = (
    <button
      type="button"
      class="btn btn-success align-middle"
      onClick={linkToConfluenceAccount}
    >
      Link To Confluence
    </button>
  );

  const GithubLoginButton = (
    <button class="btn btn-success align-middle" onClick={loginWithClientId}>
      Login with Github: Generate your own project documentation
    </button>
  );

  return (
    <div>
      <div class="mb-3">
        {localStorage.getItem("accessToken") !== null
          ? "Github account has linked"
          : GithubLoginButton}
      </div>
      <div>
        {localStorage.getItem("confluenceAccessToken") !== null
          ? "Confluence account has linked"
          : ConfluenceLoginButton}
      </div>
    </div>
  );
}
