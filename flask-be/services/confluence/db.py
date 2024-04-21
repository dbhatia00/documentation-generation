from services.database.database import get_file_documentation

TEST_DOMAIN = "csci-2340-docgen-dev.atlassian.net/"
TEST_SPACE_ID = "262148"


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
        "domain": TEST_DOMAIN,
        "space_id": TEST_SPACE_ID,
        "file_details": {
            "overall_summary": file_confluence_output.overall_summary,
            "packages": packages_dict,
            "functions": functions_dict,
        },
    }
    print(result)
    return result
