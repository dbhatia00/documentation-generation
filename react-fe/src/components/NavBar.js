export default function NavBar() {
  return (
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
          <div class="btn-group me-2" role="group" aria-label="Button group">
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

          <div class="btn-group me-3" role="group" aria-label="Button group">
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
  );
}
