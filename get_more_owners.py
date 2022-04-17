#!/usr/local/bin/python3

# Copyright (C) 2022 Dawn M. Foster
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

from datetime import datetime
from os.path import dirname, join
from github import Github
from common_functions import read_key, run_search_query

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

def make_repo_query(after_cursor = None):
    return """query RepoQuery($org_name: String!) {
             organization(login: $org_name) {
               repositories (first: 100 after: AFTER){
                 pageInfo {
                   hasNextPage
                   endCursor
                 }
                 nodes { 
                   name
                 }
              }
              }
            }""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )

def get_repo_list(api_token, org_name):
    import requests
    import json
    import pandas as pd

    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'token %s' % api_token}
    
    repo_info_df = pd.DataFrame()

    has_next_page = True
    after_cursor = None

    while has_next_page:

        query = make_repo_query(after_cursor)

        variables = {"org_name": org_name}
        r = requests.post(url=url, json={'query': query, 'variables': variables}, headers=headers)
        json_data = json.loads(r.text)

        df_temp = pd.DataFrame(json_data['data']['organization']['repositories']['nodes'])
        repo_info_df = pd.concat([repo_info_df, df_temp])

        has_next_page = json_data["data"]["organization"]["repositories"]["pageInfo"]["hasNextPage"]
        after_cursor = json_data["data"]["organization"]["repositories"]["pageInfo"]["endCursor"]
        
    return repo_info_df

repo_info_df = get_repo_list(api_token, org_name)
repo_list = repo_info_df['name'].tolist()

owners_rows = []

for repo_name in repo_list:
    query = "filename:" + file_name + " repo:" + org_name + "/" + repo_name
    print(query)
    run_search_query(query, g, owners_rows)

# prepare file and write rows to csv

try:
    today = datetime.today().strftime('%Y-%m-%d')
    output_filename = "./output/" + org_name + "_" + file_name + "_" + today + ".csv"
    current_dir = dirname(__file__)
    file_path = join(current_dir, output_filename)
    #file = open(file_path, 'w', newline ='')

    with open(file_path, 'w') as file:    
        file.writelines("%s\n" % item for item in owners_rows)

except:
    print('Could not write to csv file. This may be because the output directory is missing or you do not have permissions to write to it. Exiting')