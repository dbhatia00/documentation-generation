import services.confluence.db
import services.confluence.formatter
import requests
import json
import uuid


def handle_repo_confluence_pages(
    repo_url, cloud_id, confluence_access_code, commit_hash
):
    """
    Outputs the documentation content to Confluence pages for all files in a given repo. If space_id is not given, a new space will be created.

    Args:
        repo_url (str): The url of the repository.
        cloud_id (str): The cloud id of the Confluence instance.
        confluence_access_code (str): The access code for the Confluence instance.
        commit_hash (str): The commit hash of the repository.

    Returns:
        tuple: A tuple containing the success status and the space key.
            - success (bool): True if the documentation generation and upload to Confluence was successful, False otherwise.
            - space_key (str): The key of the Confluence space where the documentation was uploaded. None if the documentation generation was unsuccessful.
    """
    repo_info = services.confluence.db.get_repo_info(repo_url=repo_url)
    if repo_info is None:
        return False, None

    # create new space
    # TODO: construct space URL from space_key and return to front-end
    space_key, space_id = _create_space(
        cloud_id=cloud_id,
        confluence_access_code=confluence_access_code,
        repo_name=repo_info["repo_name"],
        commit_hash=commit_hash,
    )
    # unsuccessful space creation
    if space_key is None or space_id is None:
        print("confluence.api.handle_repo_confluence_pages: _create_space failed")
        return False, None

    # update the home page of the space with the repo summary
    success = update_home_page(
        cloud_id=cloud_id, 
        confluence_access_code=confluence_access_code, 
        space_id=space_id,
        repo_overview=repo_info["repo_overview"],
    )
    if success is False:
        print("confluence.api.handle_repo_confluence_pages: update_home_page failed")
        return False, None

    # create a new page or update an existing page for each file in the repo
    for file_info in repo_info["file_info_list"]:
        success = handle_file_confluence_page(
            file_info=file_info,
            cloud_id=cloud_id,
            space_id=space_id,
            confluence_access_code=confluence_access_code,
        )
        if success is False:
            print(
                f"confluence.api.handle_repo_confluence_pages: handle_file_confluence_page failed for {file_info['file_path']}"
            )
            return False, None

    # TODO: ideally, confluence page hierarchy should reflect structure of directories in repo - parse file paths to determine hierarchy

    return True, space_key


def _create_space(cloud_id, confluence_access_code, repo_name, commit_hash):
    """
    Creates a new space in Confluence.

    Args:
        cloud_id (str): The cloud id of the Confluence instance.
        confluence_access_code (str): The access code for the Confluence instance.
        repo_name (str): The name of the repository.
        commit_hash (str): The commit hash of the repository.

    Returns:
        tuple: A tuple containing the space key and space id of the created space. If the operation fails, returns None.
    """
    headers = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer " + confluence_access_code }

    space_key = (
        "".join([char for char in repo_name if char.isalnum()])
        + commit_hash
        + uuid.uuid4().hex[:6]
    )
    payload = json.dumps(
        {
            "name": repo_name + ": Auto Generated Documentation",
            "key": space_key,
        }
    )

    url = f"https://api.atlassian.com/ex/confluence/{cloud_id}/wiki/rest/api/space"
    response = requests.request("POST", url, data=payload, headers=headers)

    if response.status_code != 200:
        return None, None
    else:
        data = response.json()
        return data["key"], str(data["id"])


def update_home_page(cloud_id, confluence_access_code, space_id, repo_overview):
    """
    Updates the home page for the space with space_id with the repo_summary provided.

    Args:
        cloud_id (str): The cloud id of the Confluence instance.
        confluence_access_code (str): The access code for the Confluence instance.
        space_id (str): The ID of the space where the home page will be updated.
        repo_overview (str): A string containing the summary information for the repository.

    Returns:
        bool: True if the home page was successfully updated, False otherwise.
    """
    # getting home page ID
    headers = {"Accept": "application/json", "Authorization": "Bearer " + confluence_access_code}
    url = f"https://api.atlassian.com/ex/confluence/{cloud_id}/wiki/api/v2/spaces/{space_id}"
    response = requests.request("GET", url, headers=headers)

    if response.status_code != 200:
        print("confluence.api.update_home_page: response.status_code != 200")
        return False
    else:
        data = response.json()
        homepage_id = data["homepageId"]
        if homepage_id is None:
            print("confluence.api.update_home_page: homepage_id is None")
            return False

    # add repo_summary to the home page
    headers = {"Accept": "application/json", "Content-Type": "application/json",  "Authorization": "Bearer " + confluence_access_code}
    get_page_result, version_number = _get_page_version(
        page_id=homepage_id, cloud_id=cloud_id, confluence_access_code=confluence_access_code,
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
    url = f"https://api.atlassian.com/ex/confluence/{cloud_id}/wiki/api/v2/pages/{homepage_id}"
    response = requests.request("PUT", url, data=payload, headers=headers)

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


def handle_file_confluence_page(file_info, space_id, cloud_id, confluence_access_code):
    """
    Outputs the documentation content to a Confluence page for a given file in a given repo. Creates the Confluence page and writes the page_id to the database if it does not already exist.

    Args:
        file_info (dict): A dictionary containing information about the file, pulled from the database.
        space_id (str): The ID of the space where the page will be created.
        cloud_id (str): The cloud id of the Confluence instance.
        confluence_access_code (str): The access code for the Confluence instance.

    Returns:
        bool: True if the page update (and creation) was successful, False otherwise.
    """

    # create page for the given file
    create_result, page_id = _create_page(
        file_info=file_info,
        cloud_id=cloud_id,
        confluence_access_code=confluence_access_code,
        space_id=space_id,
    )
    if create_result is False:
        return False

    # insert documentation content into the confluence page
    update_result = _update_page(
        file_info=file_info,
        page_id=page_id,
        cloud_id=cloud_id,
        confluence_access_code=confluence_access_code,
    )
    if update_result is False:
        return False

    return True


def _create_page(file_info, cloud_id, confluence_access_code, space_id):
    """
    Creates a new page in Confluence.

    Args:
        file_info (dict): A dictionary containing information about the file, pulled from the database.
        cloud_id (str): The cloud id of the Confluence instance.
        confluence_access_code (str): The access code for the Confluence instance.
        space_id (str): The ID of the space where the page will be created.

    Returns:
        tuple: A tuple containing a boolean value indicating the success of the operation
        and the ID of the created page. If the operation fails, the boolean value will be False
        and the ID will be None.
    """
    title = file_info["file_path"]
    headers = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer " + confluence_access_code}
    payload = json.dumps(
        {
            "spaceId": space_id,
            "status": "current",
            "title": title,
        }
    )

    url = f"https://api.atlassian.com/ex/confluence/{cloud_id}/wiki/api/v2/pages"
    response = requests.request("POST", url, data=payload, headers=headers)

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


def _update_page(file_info, page_id, cloud_id, confluence_access_code):
    """
    Updates a Confluence page with the documentation.

    Args:
        file_info (dict): A dictionary containing information about the file, pulled from the database.
        page_id (str): The ID of the page to be updated.
        cloud_id (str): The cloud id of the Confluence instance.
        confluence_access_code (str): The access code for the Confluence instance.

    Returns:
        bool: True if the page was successfully updated, False otherwise.
    """
    # domain = file_info["domain"]
    headers = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer " + confluence_access_code}

    get_page_result, version_number = _get_page_version(
        page_id=page_id, cloud_id=cloud_id, confluence_access_code=confluence_access_code,
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
            "title": file_info["file_path"],
            "body": {
                "representation": "atlas_doc_format",
                "value": json.dumps(file_body),
            },
            "version": {"number": version_number + 1},
        }
    )

    url = f"https://api.atlassian.com/ex/confluence/{cloud_id}/wiki/api/v2/pages/{page_id}"
    response = requests.request("PUT", url, data=payload, headers=headers)

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


def _get_page_version(page_id, cloud_id, confluence_access_code):
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
    headers = {"Accept": "application/json", "Authorization": "Bearer " + confluence_access_code}
    url = f"https://api.atlassian.com/ex/confluence/{cloud_id}/wiki/api/v2/pages/{page_id}"
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        return False, None
    else:
        data = response.json()
        return True, data["version"]["number"]
