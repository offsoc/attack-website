import html
import json
import os
import pdb
import re

import bleach
from loguru import logger

import modules
from modules import site_config, versions

types = ["software", "datasources", "groups", "tactics", "techniques"]
sub_types = ["mobile", "enterprise", "ics"]
dist_words = 0


def generate_index():
    logger.info("Creating searchable index for the site")
    index = []
    for root, __, files in os.walk(site_config.web_directory):
        # don't walk previous routes
        skip = False
        for versions_dir in ["previous", "versions"]:
            if root.startswith(os.path.join(site_config.web_directory, versions_dir)):
                skip = True
        if skip:
            continue

        for thefile in filter(lambda fname: fname.endswith(".html"), files):
            thepath = os.path.join(root, thefile)
            global dist_words
            if any(file_name in thepath for file_name in types):
                file_name_split = thepath.split("/")
                if any(file_name in file_name_split for file_name in sub_types):
                    file_name_split = thepath.split("/")
                    type_temp = [file_name_split.index(val) for val in file_name_split if val in sub_types]
                    if "index.html" in file_name_split:
                        dist_words = file_name_split.index("index.html") - type_temp[0]
                else:
                    file_name_split = thepath.split("/")
                    type_temp = [file_name_split.index(val) for val in file_name_split if val in types]
                    if "index.html" in file_name_split:
                        dist_words = file_name_split.index("index.html") - type_temp[0]
            cleancontent, skipindex, title = clean(thepath)
            if dist_words == 1:
                skipindex = True
                dist_words = 0
            if thepath[6:] == "/index.html":
            	skipindex = True
            	dist_words = 0
            if not skipindex:
                # if title == "":
                #     print(thepath, "has generic title")
                #     title = "MITRE ATT&CK&trade;"

                index.append(
                    {
                        "id": len(index),
                        "title": title,
                        "path": thepath[6:],
                        "content": cleancontent,
                    }
                )
    if not os.path.isdir(site_config.web_directory):
        os.makedirs(site_config.web_directory)

    json.dump(index, open(os.path.join(site_config.web_directory, "index.json"), mode="w", encoding="utf8"), indent=0)

    if site_config.subdirectory:
        # update search base url to subdirectory
        search_file_path = os.path.join(site_config.web_directory, "theme", "scripts", "search_babelized.js")

        if os.path.exists(search_file_path):
            search_contents = ""

            with open(search_file_path, mode="r", encoding="utf8") as search_file:
                search_contents = search_file.read()
                search_contents = re.sub(
                    'site_base_url ?= ? ""', f'site_base_url = "/{site_config.subdirectory}/"', search_contents
                )

            with open(search_file_path, mode="w", encoding="utf8") as search_file:
                search_file.write(search_contents)

    preserve_current_version()


skiplines = ["breadcrumb-item", "nav-link"]


def skipline(line):
    for skip in skiplines:
        if skip in line:
            return True
    return False


def clean_line(line):
    """Clean unicode spaces from line."""
    # Replace unicode spaces
    line = line.replace("\u00a0", " ")
    line = line.replace("\u202f", " ")
    line = line.replace("&nbsp;", " ")
    line = line.replace("&nbsp", " ")

    return line


def clean(filepath):
    """Clean the file of all HTML tags and unnecessary data."""
    with open(filepath, mode="r", encoding="utf8") as f:
        lines = f.readlines()

    content = ""
    count = 0
    title = ""
    skipindex = False
    indexing = False

    for line in lines:
        if (not skipline(line)) and indexing:
            content += clean_line(line) + "\n"
        if "<!--start-indexing-for-search-->" in line:
            indexing = True
        if "<!--stop-indexing-for-search-->" in line:
            indexing = False
        if "<title>" in line:
            # e.g [Credential Access - Enterprise | MITRE ATT&CK&trade;] becomes [Credential Access - Enterprise]
            match = re.search(r"<title>(.*)\|.*</title>", line)
            if match:
                title = match.group(1).strip()
        if 'http-equiv="refresh"' in line:
            skipindex = True
            break
        if '<h5 class="mb-0">Deprecation Warning</h5>' in line:
            skipindex = True
            break

    # content = ps.stem(content)
    out = bleach.clean(content, tags=[], strip=True)  # remove tags
    out = re.sub(r"[\n ]+", " ", out)  # remove extra newlines, smush to 1 line
    out = html.unescape(out)  # fix &amp and &#nnn unicode escaping
    skipindex = skipindex or out == "" or out == " "
    count = count + 1
    return out, skipindex, title


def preserve_current_version():
    """Preserve current version"""

    # Check for intermodule dependency
    if [key["module_name"] for key in modules.run_ptr if key["module_name"] == "versions"]:
        versions.versions.deploy_current_version()
