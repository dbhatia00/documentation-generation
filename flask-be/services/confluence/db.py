from services.database.database import get_file_documentation, get_documentation_by_url

def get_file_info(repo_url, file_path):
    """
    Args:
        repo_url (str): the repo url stored in DB
        file_path (str): the path of the file that would like to fetch
        e.g., ("https://github.com/Adarsh9616/Electricity_Billing_System/", "src/LastBill_java")

    Returns:
        dict: None if there isn't relevant file info in DB, otherwise a dict containing the formatted file info
    """

    file_confluence_output = get_file_documentation(repo_url, file_path)
    if file_confluence_output == None:
        print("confluence.db.get_file_info returned None")
        return None

    packages_dict = {}
    functions_dict = {}
    for name, package_detail in file_confluence_output.packages.items():
        packages_dict[name] = {
            "usage": package_detail.usage,
            "description": package_detail.description,
        }
    for name, function_detail in file_confluence_output.functions.items():
        functions_dict[name] = {
            "name": function_detail.name,
            "description": function_detail.description,
            "class_declaration": function_detail.class_declaration,
            "additional_details": function_detail.additional_details,
        }

    result = {
        "page_id": None,
        "file_path": file_path,
        "file_details": {
            "overall_summary": file_confluence_output.overall_summary,
            "packages": packages_dict,
            "functions": functions_dict,
        },
    }
    return result


def get_repo_info(repo_url):
    """
    Args:
        repo_url (str): the repo url stored in DB

    Returns:
        dict: None if there isn't relevant repo info in DB, otherwise a dict containing the formatted repo info
            repo_name (str): the name of the repo
            repo_summary (str): the summary of the repo
            file_info_list (list): a list of file info dicts, each item is the output of get_file_info
    """
    repo_output = get_documentation_by_url(repo_url)
    if repo_output == None:
        print("confluence.db.repo_output returned None")
        return None

    file_info_list = []
    for file_path in repo_output.files.keys():
        file_info = get_file_info(repo_url, file_path)
        if file_info != None:
            file_info_list.append(file_info)

    return {
        "repo_name": repo_output.repository_name,
        "repo_summary": repo_output.repository_summary,
        "file_info_list": file_info_list,
    }
