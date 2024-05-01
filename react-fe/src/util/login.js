import clientInfo from '../token_client.json';

export const loginWithClientId = () => {
  // Adding more scope if needed in the future
  const scopes = 'repo';
  window.location.assign(
    'https://github.com/login/oauth/authorize?client_id=' +
      clientInfo.client_id +
      '&scope=' +
      scopes
  );
};

export const linkToConfluenceAccount = () => {
  // window.location.assign
  window.open(
    'https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=' +
      clientInfo.confluence_client_id +
      '&scope=write%3Aconfluence-content%20read%3Aconfluence-space.summary%20write%3Aconfluence-space%20write%3Aconfluence-file%20read%3Aconfluence-props%20write%3Aconfluence-props%20manage%3Aconfluence-configuration%20read%3Aconfluence-content.all%20read%3Aconfluence-content.summary%20search%3Aconfluence%20read%3Aconfluence-content.permission%20read%3Aconfluence-user%20read%3Aconfluence-groups%20write%3Aconfluence-groups%20readonly%3Acontent.attachment%3Aconfluence' +
      '&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2F' +
      '&state=confluence' +
      '&response_type=code&prompt=consent'
  );
};

export const getAccessToken = async (codeParam, rerender, setRerender) => {
  try {
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
        if (data.access_token) {
          localStorage.setItem('accessToken', data.access_token);
          setRerender(!rerender);
        }
      });
  } catch (err) {
    console.error('Failed to get access token', err);
  }
};

export const getConfluenceAccessToken = async (
  codeParam,
  rerender,
  setRerender
) => {
  try {
    await fetch('/api/get_confluence_token?code=' + codeParam, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (data.access_token) {
          localStorage.setItem('confluenceAccessToken', data.access_token);
          setRerender(!rerender);
        }
      });
  } catch (err) {
    console.error('Failed to get access token', err);
  }
};
