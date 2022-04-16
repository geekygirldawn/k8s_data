#!/usr/local/bin/python3

# Copyright (C) 2019 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt
"""
This script is designed to find the path to OWNERS files within Kubernetes
organizations, but it is generic enough to find any files of a specific
filename within a specified GitHub org.
Note: GitHub search API is limited to 1000 files, so this is still missing some OWNERS files.

As input, this script requires that you have a GitHub API token in a file
called 'gh_key' in this directory.

Parameters
----------
org_name : str
    The GitHub organization to be searched
file_name : str
    The filename to search, like OWNERS or CODEOWNERS

"""

import time
from github import Github
from common_functions import read_key

api_token = read_key('gh_key')
g = Github(api_token)

def read_args():
    """Reads the org name and filename to be used in the search
    
    Parameters
    ----------
    None

    Output
    -------
    org_name : str
        The GitHub organization to be searched
    file_name : str
        The filename to search, like OWNERS or CODEOWNERS
    """
    import sys

    # read org name and filename from command line
    try:
        org_name = str(sys.argv[1])
        file_name = str(sys.argv[2])

    except:
        print("Please enter the org name and filename to search when prompted.")
        org_name = input("Enter a GitHub org name (like kubernetes): ")
        file_name = input("Enter a file name (like OWNERS): ")

    return org_name, file_name

org_name, file_name = read_args()

query = "org:" + org_name + " filename:" + file_name
print(query)

output = g.search_code(query=query, order='asc')
print("Total number found", output.totalCount)

import time

for owners in output:
    full_path = owners.repository.full_name + '/' + owners.path
    print(full_path)
    time.sleep(1)