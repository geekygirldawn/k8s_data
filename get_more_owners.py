#!/usr/local/bin/python3

# Copyright (C) 2022 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt
"""
This script is designed to find the path to OWNERS files within Kubernetes
organizations, but it is generic enough to find any files of a specific
filename within a specified GitHub org.
Note: The GitHub search API is a little flaky, so it's likely that some
files are missing.

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
from common_functions import read_key, run_search_query, expand_name_df

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
    """Creates the query string for the GraphQL API call using after_cursor
       to handle multiple pages of results.
    
    Parameters
    ----------
    after_cursor : str

    Returns
    -------
    query : str
    """
    return """query RepoQuery($org_name: String!) {
             organization(login: $org_name) {
               repositories (first: 100 after: AFTER){
                 pageInfo {
                   hasNextPage
                   endCursor
                 }
                 nodes { 
                   name
                   defaultBranchRef {
                     name 
                   }
                 }
              }
              }
            }""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )

def get_repo_list(api_token, org_name):
    """Uses the make_repo_query function to run the GraphQL query and
    returns the results as a dataframe containing the default branch 
    and repo name for all of the repo within the org. Note: default
    branch is needed to build the url to the file.
    
    Parameters
    ----------
    api_token : str
    org_name : str

    Returns
    -------
    repo_info_df : dataframe
    """
    import requests
    import json
    import pandas as pd

    # Setting up the variables needed for the API
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'token %s' % api_token}
    
    repo_info_df = pd.DataFrame()

    # Initialize the variables needed to page through the results.
    # and while there are more pages, query a new page of results
    has_next_page = True
    after_cursor = None

    while has_next_page:

        query = make_repo_query(after_cursor)

        # Pass the variables into the query and run it using the graphQL
        # API returning a json file
        variables = {"org_name": org_name}
        r = requests.post(url=url, json={'query': query, 'variables': variables}, headers=headers)
        json_data = json.loads(r.text)

        # Convert the json file to a temporary dataframe that is added
        # to the main dataframe with all of the results to be returned.
        df_temp = pd.DataFrame(json_data['data']['organization']['repositories']['nodes'])
        repo_info_df = pd.concat([repo_info_df, df_temp])

        # Set variables that check for and handle results with 
        # multiple pages.
        has_next_page = json_data["data"]["organization"]["repositories"]["pageInfo"]["hasNextPage"]
        after_cursor = json_data["data"]["organization"]["repositories"]["pageInfo"]["endCursor"]
        
    return repo_info_df

# Runs the function that gets the repos from the graphQL API
# and convert the output dataframe to a list of repos.
repo_info_df = get_repo_list(api_token, org_name)
#repo_list = repo_info_df['name'].tolist()

repo_info_df = expand_name_df(repo_info_df,'defaultBranchRef','defaultBranch')

owners_rows = []

# Iterate through the list of repos and run a search API query that
# gets the owners files for each repo.
for item in repo_info_df.iterrows():
    repo_name = item[1]['name']
    branch_name = item[1]['defaultBranch']
    query = "filename:" + file_name + " repo:" + org_name + "/" + repo_name
    print(query)
    owners_rows = run_search_query(query, g, branch_name, owners_rows)

# prepare file and write rows to csv

try:
    today = datetime.today().strftime('%Y-%m-%d')
    output_filename = "./output/" + org_name + "_" + file_name + "_" + today + ".csv"
    current_dir = dirname(__file__)
    file_path = join(current_dir, output_filename)

    with open(file_path, 'w') as file:    
        file.writelines("%s\n" % item for item in owners_rows)

except:
    print('Could not write to csv file. This may be because the output directory is missing or you do not have permissions to write to it. Exiting')