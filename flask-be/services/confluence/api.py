import services.confluence.db
import services.confluence.formatter
import requests
import json
import urllib.parse


def get_space_id_and_domain_from_confluence_url(confluence_url):
    """
    Extracts the space_id and domain from a Confluence URL.

    Args:
        confluence_url (str): The URL of the Confluence page.

    Returns:
        tuple: A tuple containing a boolean value indicating the success of the operation, the domain (str) and the space_id (str). If any operation fails, the boolean value will be False and the domain and space_id will be None.
    """
    # extract domain
    try:
        domain = urllib.parse.urlparse(confluence_url).netloc
    except ValueError:
        return False, None, None
    # extract space_id
    try:
        path = urllib.parse.urlparse(confluence_url).path
        space_key = path.split("/")[3]
    except (ValueError, IndexError):
        return False, None, None
    space_id = _get_space_id_from_space_key(space_key=space_key, domain=domain)

    if space_id is None:
        return False, None, None

    return True, domain, space_id


def _get_space_id_from_space_key(space_key, domain):
    """
    Retrieves the space_id of a Confluence space from the space key, via the Confluence Get Spaces endpoint (https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/#api-spaces-get).

    Args:
        space_key (str): The space key of the space.
        domain (str): The domain of the Confluence site.

    Returns:
        str: The ID of the space matching the space key. If no space with space_key is found, returns None.
    """
    headers = {"Accept": "application/json"}

    url = f"https://{domain}/wiki/api/v2/spaces"
    response = requests.request("GET", url, headers=headers, auth=auth)

    if response.status_code != 200:
        return None
    else:
        data = response.json()
        for space in data["results"]:
            if space["key"] == space_key:
                return space["id"]
        return None


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
        space_key, space_id = _create_space(
            domain=domain, auth=auth, repo_name=repo_info["repo_name"]
        )
        # unsuccessful space creation
        if space_key is None or space_id is None:
            return False

    # create a new page or update an existing page for each file in the repo
    for file_info in repo_info["file_info_list"]:
        file_path = file_info["file_path"]
        handle_file_confluence_page(
            repo_url=repo_url,
            file_path=file_path,
            domain=domain,
            space_id=space_id,
            auth=auth,
        )

    # TODO: create page for repo level documentation

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
            # "key": "".join([char for char in repo_name if char.isalnum()]),
            "key": "docgen",
        }
    )

    url = f"https://{domain}/wiki/rest/api/space"
    response = requests.request("POST", url, data=payload, headers=headers, auth=auth)

    print(
        "_CREATE_SPACE:\n",
        json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        ),
    )

    if response.status_code != 200:
        return None, None
    else:
        data = response.json()
        return data["key"], data["id"]


def handle_file_confluence_page(repo_url, file_path, domain, space_id, auth):
    """
    Outputs the documentation content to a Confluence page for a given file in a given repo. Creates the Confluence page and writes the page_id to the database if it does not already exist.

    TODO: 1. integrate with triggers: should be triggered after status of page becomes "complete" in db 2. write page_id to database

    Args:
        repo_url (str): The url of the repository.
        file_path (str): The path of the file in the repository.
        domain (str): The domain of the Confluence instance.
        space_id (str): The ID of the space where the page will be created.
        auth (requests.auth.HTTPBasicAuth): The authentication object for the Confluence instance.

    Returns:
        bool: True if the page update (and creation) was successful, False otherwise.
    """
    file_info = services.confluence.db.get_file_info(
        repo_url=repo_url, file_path=file_path
    )
    if file_info is None:
        return False

    file_info["space_id"] = space_id
    file_info["domain"] = domain

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
