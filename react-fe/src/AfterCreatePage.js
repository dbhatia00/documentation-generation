import { ReactTyped } from "react-typed";

const CreateConfluenceText = `
  <div class="mainbg-text-title col-md">Generated Successfully</div>

  <div class="mainbg-text-subtitle">Confluence Page</div>
  <div class="mainbg-text-content">Here we go! Please provide your email, Confluence domain, and API token. This way we can store your stuff in your Confluence so you can view and edit it!</div>

`

function AfterCreatePage() {
  return (
    <div class="main-theme">
    <div class="container">
    <div class="row">
      <div class="col-6">
        <div class="mainbg-base">
          <ReactTyped 
            strings={[
            CreateConfluenceText
            ]} typeSpeed={3} contentType="html" cursorChar=""/>
        </div>
      </div>
    </div>
    </div>
    </div>
  )
}

export default AfterCreatePage;