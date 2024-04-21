from services.database import get_file_documentation, get_documentation_by_url

TEST_DOMAIN = "csci-2340-docgen-dev.atlassian.net/"
TEST_SPACE_ID = "262148"


def get_file_info(repo_name, file_name):
    """
    Args:
        repo_name (str): the repo url stored in DB
        file_name (str): the name of the file that would like to fetch
        e.g., ("https://github.com/Adarsh9616/Electricity_Billing_System/", "src/LastBill_java")

    Returns:
        dict: None if there isn't relevant file info in DB, otherwise a dict containing the formatted file info
    """

    file_confluence_output = get_file_documentation(repo_name, file_name)
    if file_confluence_output == None:
        print("no data")
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

# Testing
# get_file_info("https://github.com/Adarsh9616/Electricity_Billing_System/", "src/LastBill_java")

# return {
#     "page_id": None,  # should be None if file is new
#     "domain": TEST_DOMAIN,
#     "space_id": TEST_SPACE_ID,
#     "file_details": {
#         "overall_summary": "The Java file defines a GUI application using Swing to generate and display billing details for selected customer meter numbers from a database. It allows users to select a meter number and view the customer's details and their billing history.",
#         "packages": {
#             "java.awt": {
#                 "usage": "Used for creating and managing components, such as buttons, labels, and panels, which are used in the graphical user interface.",
#                 "description": "Provides classes for managing user interface components for windows, including event handling.",
#             },
#             "javax.swing": {
#                 "usage": "Used to create the components of the GUI such as JFrame, JButton, JLabel, JTextArea, and JScrollPane.",
#                 "description": "Provides a set of 'lightweight' (all-Java language) components that, to the maximum degree possible, work the same on all platforms.",
#             },
#             "java.sql": {
#                 "usage": "Used for handling the database connectivity and executing SQL queries to fetch customer and billing information.",
#                 "description": "Provides the API for accessing and processing data stored in a data source (usually a relational database) using the Java programming language.",
#             },
#         },
#         "functions": {
#             "LastBill": {
#                 "name": "LastBill",
#                 "description": "Constructor for the LastBill class. It initializes the GUI components and sets up the layout and event handling.",
#                 "class_declaration": "public class LastBill extends JFrame implements ActionListener",
#                 "additional_details": "Sets up a JFrame with BorderLayout, adds components like labels, choice box, text area, and button. Also, sets the action listener for the button.",
#             },
#             "actionPerformed": {
#                 "name": "actionPerformed",
#                 "description": "Handles the action event triggered by the 'Generate Bill' button. It connects to the database, retrieves customer and billing information based on the selected meter number, and displays it in the text area.",
#                 "class_declaration": "public void actionPerformed(ActionEvent ae)",
#                 "additional_details": "Uses SQL queries to fetch data from 'emp' and 'bill' tables. Displays errors in the console if any exceptions occur.",
#             },
#             "main": {
#                 "name": "main",
#                 "description": "The main method that launches the GUI application.",
#                 "class_declaration": "public static void main(String[] args)",
#                 "additional_details": "Creates an instance of LastBill and makes it visible.",
#             },
#         },
#     },
# }
