import services.confluence.db
import services.confluence.formatter
import requests
import json

def handle_repo_confluence_pages(repo_url, domain, space_id, auth):
    """
    Outputs the documentation content to Confluence pages for all files in a given repo. If space_id is not given, a new space will be created. See handle_file_confluence_page() for more details.

    Args:
        repo_url (str): The url of the repository.
        domain (str): The domain of the Confluence instance.
        space_id (str): The ID of the space where the pages will be created.
        auth (requests.auth.HTTPBasicAuth): The authentication object for the Confluence instance.

    Returns:
        bool: True if all pages were successfully updated, False otherwise.
    """
    repo_info = services.confluence.db.get_repo_info(repo_url=repo_url)
    if repo_info is None:
        return False

    # create new space if space_id is not given
    if space_id is None:
        # TODO: construct space URL from space_key and return to front-end
        space_key, space_id = _create_space(
            domain=domain, auth=auth, repo_name=repo_info["repo_name"]
        )
        # unsuccessful space creation
        if space_key is None or space_id is None:
            return False

    # TODO: replace with or add a function that creates/updates repo level summary pages
    # update the home page of the space with the repo summary
    success = update_home_page(
        domain=domain,
        auth=auth,
        space_id=space_id,
        repo_overview=repo_info["repo_overview"],
    )
    if success is False:
        print("handle_repo_confluence_pages: update_home_page failed")
        return False

    # create a new page or update an existing page for each file in the repo
    for file_info in repo_info["file_info_list"]:
        success = handle_file_confluence_page(
            file_info=file_info,
            domain=domain,
            space_id=space_id,
            auth=auth,
        )
        if success is False:
            return False

    # TODO: ideally, confluence page hierarchy should reflect structure of directories in repo - need corresponding structures in LLM output

    return True


def _create_space(domain, auth, repo_name):
    """
    Creates a new space in Confluence.

    Args:
        domain (str): The domain of the Confluence instance.
        auth (requests.auth.HTTPBasicAuth): The authentication object for the Confluence instance.
        repo_name (str): The name of the repository.

    Returns:
        str: a tuple containing the space key and space id of the created space. If the operation fails, returns None.
    """
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = json.dumps(
        {
            "name": repo_name + ": Auto Generated Documentation",
            "key": "".join([char for char in repo_name if char.isalnum()]) + "Doc",
        }
    )

    url = f"https://{domain}/wiki/rest/api/space"
    response = requests.request("POST", url, data=payload, headers=headers, auth=auth)

    if response.status_code != 200:
        return None, None
    else:
        data = response.json()
        return data["key"], str(data["id"])


def update_home_page(domain, auth, space_id, repo_overview):
    """
    Updates the home page for the space with space_id with the repo_summary provided.

    Args:
        domain (str): The domain of the Confluence instance.
        auth (requests.auth.HTTPBasicAuth): The authentication object for the Confluence instance.
        repo_summary (str): A str containing the summary information for the repository.

    Returns:
        bool: True if the home page was successfully updated, False otherwise.
    """
    # TODO: store repo home page info in db, and get home page ID from db instead of from confluence API
    # getting home page ID
    headers = {"Accept": "application/json"}
    url = f"https://{domain}/wiki/api/v2/spaces"
    response = requests.request("GET", url, headers=headers, auth=auth)

    if response.status_code != 200:
        print("confluence.api.update_home_page: response.status_code != 200")
        return False
    else:
        data = response.json()
        homepage_id = None
        for space in data["results"]:
            if space["id"] == space_id:
                homepage_id = space["homepageId"]
        if homepage_id is None:
            print("confluence.api.update_home_page: homepage_id is None")
            return False

    # add repo_summary to the home page
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    get_page_result, version_number = _get_page_version(
        page_id=homepage_id, domain=domain, auth=auth
    )
    if get_page_result is False:
        print("confluence.api.update_home_page: get_page_result is False")
        return False
    overview_page_body = services.confluence.formatter.get_overview_page_body(
        repo_overview=repo_overview
    )
    payload = json.dumps(
        {
            "id": homepage_id,
            "status": "current",
            "title": "Project Overview",
            "body": {
                "representation": "atlas_doc_format",
                "value": json.dumps(overview_page_body),
            },
            "version": {"number": version_number + 1},
        }
    )
    url = f"https://{domain}/wiki/api/v2/pages/{homepage_id}"
    response = requests.request("PUT", url, data=payload, headers=headers, auth=auth)

    print(
        "UPDATE_HOME_PAGE:\n",
        json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        ),
    )

    if response.status_code != 200:
        return False
    else:
        return True


def handle_file_confluence_page(file_info, domain, space_id, auth):
    """
    Outputs the documentation content to a Confluence page for a given file in a given repo. Creates the Confluence page and writes the page_id to the database if it does not already exist.

    TODO: 1. integrate with triggers: should be triggered after status of page becomes "complete" in db 2. write page_id to database

    Args:
        file_info (dict): A dictionary containing information about the file, pulled from the database.
        domain (str): The domain of the Confluence instance.
        space_id (str): The ID of the space where the page will be created.
        auth (requests.auth.HTTPBasicAuth): The authentication object for the Confluence instance.

    Returns:
        bool: True if the page update (and creation) was successful, False otherwise.
    """
    # TODO: get space_id and domain from db instead of passing down from handle_repo_confluence_pages
    file_info["space_id"] = space_id
    file_info["domain"] = domain
    file_path = file_info["file_path"]

    # check if file already has a corresponding confluence page_id
    # if not, create a new page
    page_id = file_info["page_id"]
    if page_id is None:
        create_result, page_id = _create_page(
            file_info=file_info, file_path=file_path, auth=auth
        )
        if create_result is False:
            return False
        # TODO: write page_id to database after successful creation

    # insert documentation content into the confluence page
    update_result = _update_page(
        file_info=file_info, file_path=file_path, page_id=page_id, auth=auth
    )
    if update_result is False:
        return False

    return True


def _create_page(file_info, file_path, auth):
    """
    Creates a new page in Confluence.

    Args:
        file_info (dict): A dictionary containing information about the file, pulled from the database.
            - space_id (str): The ID of the space where the page will be created.
            - domain (str): The domain of the Confluence instance.

        file_path (str): The path of the file in the repository.
        auth (requests.auth.HTTPBasicAuth): The authentication object for the Confluence instance.

    Returns:
        tuple: A tuple containing a boolean value indicating the success of the operation
        and the ID of the created page. If the operation fails, the boolean value will be False
        and the ID will be None.
    """
    space_id = file_info["space_id"]
    title = file_path
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = json.dumps(
        {
            "spaceId": space_id,
            "status": "current",
            "title": title,
        }
    )

    domain = file_info["domain"]
    url = f"https://{domain}/wiki/api/v2/pages"
    response = requests.request("POST", url, data=payload, headers=headers, auth=auth)

    print(
        "_CREATE_PAGE:\n",
        json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        ),
    )

    if response.status_code != 200:
        return False, None
    else:
        data = response.json()
        return True, data["id"]


def _update_page(file_info, file_path, page_id, auth):
    """
    Updates a Confluence page with the documentation.

    Args:
        file_info (dict): A dictionary containing information about the file, pulled from the database.
            - space_id (str): The ID of the space where the page will be created.
            - file_details (dictionary): A dictionary containing the documentation content for the file, see services.confluence.formatter.get_file_page_body() for more details.
        file_path (str): The path of the file in the repository.
        page_id (str): The ID of the page to be updated.
        auth (requests.auth.HTTPBasicAuth): The authentication object for the Confluence instance.

    Returns:
        bool: True if the page was successfully updated, False otherwise.
    """
    domain = file_info["domain"]
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    get_page_result, version_number = _get_page_version(
        page_id=page_id, domain=domain, auth=auth
    )
    if get_page_result is False:
        return False

    file_body = services.confluence.formatter.get_file_page_body(
        file_details=file_info["file_details"]
    )

    payload = json.dumps(
        {
            "id": page_id,
            "status": "current",
            "title": file_path,
            "body": {
                "representation": "atlas_doc_format",
                "value": json.dumps(file_body),
            },
            "version": {"number": version_number + 1},
        }
    )

    url = f"https://{domain}/wiki/api/v2/pages/{page_id}"
    response = requests.request("PUT", url, data=payload, headers=headers, auth=auth)

    print(
        "_UPDATE_PAGE:\n",
        json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        ),
    )

    if response.status_code != 200:
        return False
    else:
        return True


def _get_page_version(page_id, domain, auth):
    """
    Retrieves the version number of a Confluence page.

    Args:
        page_id (str): The ID of the page.
        domain (str): The domain of the Confluence site.
        auth (requests.auth.HTTPBasicAuth): The authentication object for the Confluence instance.

    Returns:
        tuple: A tuple containing a boolean value indicating the success of the request
               and the version number (int) of the page. If the request fails, the boolean value
               will be False and the version number will be None.
    """
    headers = {"Accept": "application/json"}
    url = f"https://{domain}/wiki/api/v2/pages/{page_id}"
    response = requests.request("GET", url, headers=headers, auth=auth)

    if response.status_code != 200:
        return False, None
    else:
        data = response.json()
        return True, data["version"]["number"]
