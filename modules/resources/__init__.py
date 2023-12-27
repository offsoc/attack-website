from . import resources
from . import resources_config
import json


def get_priority():
    return resources_config.priority


def get_menu():
    return {
        "display_name": resources_config.module_name,
        "module_name": resources_config.module_name,
        "url": "/resources/",
        "external_link": False,
        "priority": resources_config.priority,
        "children": [
            {"display_name": "General Information", "url": "/resources/", "external_link": False, "children": []},
            {
                "display_name": "Get Started",
                "url": "/resources/getting-started/",
                "external_link": False,
                "children": [],
            },
            {
                "display_name": "Contribute",
                "url": "/resources/engage-with-attack/contribute/",
                "external_link": False,
                "children": [],
            },
            {"display_name": "Training", "url": "/resources/training/cti", "external_link": False, "children": []},
            {"display_name": "ATT&CKcon", "url": "/resources/attackcon/", "external_link": False, "children": []},
            {
                "display_name": "Working with ATT&CK",
                "url": "/resources/working-with-attack/",
                "external_link": False,
                "children": [],
            },
            {"display_name": "FAQ", "url": "/resources/faq/", "external_link": False, "children": []},
            {"display_name": "Updates", "url": "/resources/updates/", "external_link": False, "children": []},
            {
                "display_name": "Version History",
                "url": "/resources/versions/",
                "external_link": False,
                "children": [],
            },
            {
                "display_name": "Related Projects",
                "url": "/resources/related-projects/",
                "external_link": False,
                "children": [],
            },
            {
                "display_name": "Legal & Branding",
                "url": "/resources/brand/",
                "external_link": False,
                "children": [],
            },
        ],
    }


def run_module():
    return (resources.generate_resources(), resources_config.module_name)
