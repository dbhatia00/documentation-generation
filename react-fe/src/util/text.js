export const MainPageText = `
  <div class="mainbg-text-title border-bottom pb-2 mb-3">Automated Codebase Documentation Generator</div>

  <div class="mainbg-text-subtitle">Overview</div>
  <div class="mainbg-text-content">Documentation is difficult to write and keep up to date. 
  Tools exist to generate rudimentary JavaDoc for Java programs, but the result isn’t particularly helpful as it just gives parameter names and return types from the signature and no useful information. 
  The goal of this project is to provide a more reasonable initial documentation source using LLMs and other tools, formatted and pushed out to your confluence space. </div>

  <div class="mainbg-text-subtitle">Features</div>
  <ul class="mainbg-text-content">
  <li>Feature 1: Fetch your target repo from Github</li>
  <li>Feature 2: Run our LLM on it to generate the documentation</li>
  <li>Feature 3: Output the generated docs to Confluence</li>
  </ul>
  <div class="mainbg-text-subtitle">Using the Application</div>
  <div class="mainbg-text-content">To use the application, please sign in to Github and Confluence. Then, follow the instructions on the next page.</div>
  <div class="mainbg-text-subtitle">Confluence Page</div>
  <div class="mainbg-text-content">Our generated documentation will be stored in your Confluence as a new space. Please use the "Link to Confluence" button below to give us authorization for your confluence page.</div>
  <div class="mainbg-text-content">. . .</div>
`;

export const GithubLoggedInText = `
  <div class="mainbg-text-title col-md border-bottom pb-2 mb-3">Login Success</div>

  <div class="mainbg-text-subtitle">Fetch</div>
  <div class="mainbg-text-content">Almost there! Using the {username}/{repo name} format, enter your Github repo name below and click fetch.</div>

  <div class="mainbg-text-subtitle">Notes</div>
  <ul class="mainbg-text-content">
  <li>Please note that it takes some time to generate the documentation, depending on the size of the repository.</li>
  <li>The application currently supports Python, Javascript, and Java projects.</li>
  </ul>
`;
