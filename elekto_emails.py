# Copyright (C) 2022 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

"""
Takes an elekto voters.yaml file with a list of "eligible_voters:"
GitHub logins, and attempts to use the GitHub API to get an email
for each person to make it possible to send email reminders to eligible
voters. 

If an email address is in the GitHub profile, that is used first. Otherwise,
it attempts to find an email address from the most recent commit. If the
email contains the string 'noreply' it is not written to the csv file.

As input, this script requires that you have a GitHub API token in a file
called 'gh_key' in this directory.

As output, a csv file of this format containing comma separated email addresses 
is created:
output/elekto_emails_GHorgName_YYYYMMDD.csv

A message with the number of email addresses found out of the total voters
is printed to the screen

Parameters
----------
org_name : str
    The primary GitHub organization for the vote.
    Used to gather email address from commits
file_name : str
    This should be an Elekto yaml file starting with "eligible_voters:"
"""

import sys
import yaml
import csv
from datetime import datetime
from common_functions import download_file

def read_args():
    """Reads the org name and yaml filename where the votes can be found.
    
    Parameters
    ----------
    None

    Returns
    -------
    org_name : str
        The primary GitHub organization for the vote.
        Used to gather email address from commits
    file_name : str
        This should be an Elekto yaml file (raw) starting with "eligible_voters:"
        https://raw.githubusercontent.com/knative/community/main/elections/2021-TOC/voters.yaml
    """
    import sys

    # read org name and filename from command line or prompt if no 
    # arguments were given.
    try:
        org_name = str(sys.argv[1])
        file_name = str(sys.argv[2])

    except:
        print("Please enter the org name and filename for voters.yaml.")
        org_name = input("Enter a GitHub org name (like kubernetes): ")
        file_name = input("Enter a file name (like https://raw.githubusercontent.com/knative/community/main/elections/2021-TOC/voters.yaml): ")

    return org_name, file_name

def get_email(org, username):
    """Attempts to get an email address from the GitHub profile first. 
    Otherwise, it attempts to find an email address from the most recent
    commit, which is why the name of the GitHub org is required. If the
    email contains the string 'noreply' it is not written to the csv file.
    
    Parameters
    ----------
    org : str
        The primary org name where the users can be found
    username : str
        GitHub username

    Returns
    -------
    email : str
    """

    import sys
    from github import Github # Uses https://github.com/PyGithub/
    from common_functions import read_key

    try:
        api_token = read_key('gh_key')
        g = Github(api_token)
    except:
        print("Cannot read gh_key file or does not contain a valid GitHub API token?")
        sys.exit()

    try:
        email = g.get_user(username).email

        email_list = []

        if email == None:
            repo_list = g.get_organization(org).get_repos()

            for repo in repo_list:
                commits = repo.get_commits(author=username)

                if commits.totalCount > 0:
                    email_list.append([commits[0].commit.author.email, commits[0].commit.author.date, repo.name])

            if len(email_list) > 0:
                newest = sorted(email_list, key = lambda x: x[1], reverse = True)
                email = newest[0][0]
            else:
                email = None
        if 'noreply' in email:
            email = None
    except:
        email = None

    return(email)

org_name, file_name = read_args()

# Loads the yaml file and creates a list of voters
try:
    voters_file = download_file(file_name)
    voters = yaml.safe_load(voters_file)
    voter_list = voters['eligible_voters']

except:
    print("Cannot load or process the yaml file. Did you use the raw link?")
    sys.exit()

# Open the CSV file for writing
today = datetime.today().strftime('%Y-%m-%d')
outfile_name = 'output/elekto_emails_' + org_name + "_" + today + '.csv'
f = open(outfile_name,'w')
csv_file = csv.writer(f)

# Create a list for the emails and initialize a counter for the
# number of emails found.
email_list = []
found_count = 0

# Attempt to get an email address for each voter. If an email address is found
# append it to the list and increment the counter.
for username in voter_list:
    email = get_email(org_name, username)
    print(username, email)
    if email:
        email_list.append(email)
        found_count+=1

# Print status and write emails to the csv file.
print("Found emails for", found_count, "out of", len(voter_list), "voters")
csv_file.writerow(email_list)
f.close()