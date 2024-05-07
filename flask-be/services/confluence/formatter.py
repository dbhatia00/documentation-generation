def get_overview_page_body(repo_overview):
    content = []
    for section_title, section_info in repo_overview.items():
        if type(section_info) == dict:
            content.extend(_get_list_section_from_dict(section_title, section_info))
        else:
            content.extend(
                [
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [
                            {
                                "type": "text",
                                "text": str(section_title).replace("_", " ").title(),
                            }
                        ],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": section_info}],
                    },
                ]
            )
    print({"version": 1, "type": "doc", "content": content})
    return {"version": 1, "type": "doc", "content": content}


def _get_list_section_from_dict(title, info_dict):
    content_list = []
    for key, value in info_dict.items():
        content_list.append(
            {
                "type": "listItem",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": str(key) + ": ",
                                "marks": [{"type": "strong"}],
                            },
                            {"type": "text", "text": str(value)},
                        ],
                    }
                ],
            }
        )
    return [
        {
            "type": "heading",
            "attrs": {"level": 3},
            "content": [
                {
                    "type": "text",
                    "text": str(title).replace("_", " ").title(),
                }
            ],
        },
        {"type": "orderedList", "attrs": {"order": 1}, "content": content_list},
    ]


def get_file_page_body(file_details):
    """
    Generate the request body for updating the confluence page of a file.

    Args:
        file_details (dict): A dictionary containing the file details.
            - overall_summary (str): The overall summary of the file.
            - packages (dict): A dictionary containing the package details.
                - file_name (str): The name of the package.
                    - description (str): The description of the package.
                    - usage (str): The usage of the package.
            - functions (dict): A dictionary containing the function details.
                - function_name (str): The name of the function.
                    - description (str): The description of the function.
                    - class_declaration: The code snippet of function declaration.
                    - additional_details: Additional details of the function.

    Returns:
        dict: The body of the Confluence page (not serialized to JSON!).
    """
    content = []
    content.extend(_format_summary(file_details["overall_summary"]))
    content.extend(_format_packages(file_details["packages"]))
    content.extend(_format_functions(file_details["functions"]))
    return {"version": 1, "type": "doc", "content": content}


def _format_summary(overall_summary):
    """
    Format the overall summary section.

    Returns:
        list: A list of content nodes representing the formatted summary section.
    """
    return [
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "Overall Summary:",
                    "marks": [{"type": "strong"}],
                }
            ],
        },
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": overall_summary}],
        },
    ]


def _format_packages(packages):
    """
    Format the packages section.

    Returns:
        list: A list of content nodes representing the formatted packages section.
    """
    packages_table_rows = [_get_package_table_header_row()]
    for package_name, package_details in packages.items():
        packages_table_rows.append(
            _get_one_package_row(
                package_name=package_name,
                description=package_details["description"],
                usage=package_details["usage"],
            )
        )

    return [
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Packages", "marks": [{"type": "strong"}]}
            ],
        },
        {
            "type": "table",
            "attrs": {
                "layout": "custom",
            },
            "content": packages_table_rows,
        },
    ]


def _format_functions(functions):
    """
    Format the functions section.

    Returns:
        list: A list of content nodes representing the formatted functions section.
    """
    functions_table_rows = [_get_function_table_header_row()]
    for function_name, function_details in functions.items():
        functions_table_rows.append(
            _get_one_function_row(
                function_name=function_name,
                class_declaration=function_details["class_declaration"],
                description=function_details["description"],
                additional_details=function_details["additional_details"],
            )
        )

    return [
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Functions", "marks": [{"type": "strong"}]}
            ],
        },
        {
            "type": "table",
            "attrs": {
                "layout": "custom",
            },
            "content": functions_table_rows,
        },
    ]


def _get_package_table_header_row():
    """
    Return the formatted header row for the packages table as a list of content nodes.
    """
    return {
        "type": "tableRow",
        "content": [
            {
                "type": "tableHeader",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Package Name",
                                "marks": [{"type": "strong"}],
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableHeader",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Description",
                                "marks": [{"type": "strong"}],
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableHeader",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Usage",
                                "marks": [{"type": "strong"}],
                            }
                        ],
                    }
                ],
            },
        ],
    }


def _get_one_package_row(package_name, description, usage):
    """
    Return one formatted table row for the packages table as a list of content nodes, based on the given package.
    """
    return {
        "type": "tableRow",
        "content": [
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": package_name,
                                "marks": [{"type": "strong"}],
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description,
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": usage,
                            }
                        ],
                    }
                ],
            },
        ],
    }


def _get_function_table_header_row():
    """
    Return the formatted header row for the functions table as a list of content nodes.
    """
    return {
        "type": "tableRow",
        "content": [
            {
                "type": "tableHeader",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Function Name",
                                "marks": [{"type": "strong"}],
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableHeader",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Declaration",
                                "marks": [{"type": "strong"}],
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableHeader",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Description",
                                "marks": [{"type": "strong"}],
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableHeader",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Additional Details",
                                "marks": [{"type": "strong"}],
                            }
                        ],
                    }
                ],
            },
        ],
    }


def _get_one_function_row(
    function_name, description, class_declaration, additional_details
):
    """
    Return one formatted table row for the functions table as a list of content nodes, based on the given function.
    """
    return {
        "type": "tableRow",
        "content": [
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": function_name,
                                "marks": [{"type": "strong"}],
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": class_declaration,
                                "marks": [{"type": "code"}],
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description,
                            }
                        ],
                    }
                ],
            },
            {
                "type": "tableCell",
                "attrs": {},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": additional_details,
                            }
                        ],
                    }
                ],
            },
        ],
    }
