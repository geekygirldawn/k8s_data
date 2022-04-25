#!/usr/local/bin/python3

# Copyright (C) 2022 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

"""
This dataset uses the Istio teams.yaml file along with CNCF Affiliation data
to gather information about maintainers and other leadership positions. Where
affiliations weren't found in the CNCF data, the GitHub REST API is used to
get company information from the user profile if available.

As input, this script requires that you have a GitHub API token in a file
called 'gh_key' in this directory.

The output is saved as a csv of the format:
output/owners_data_istio_YYYY-MM-DD.csv
"""

import yaml
from datetime import datetime
from common_functions import read_key, read_cncf_affiliations, download_file, write_affil_line_istio

affil_dict = read_cncf_affiliations()

api_token = read_key('gh_key')

# Load the teams.yaml file
owners_url = 'https://raw.githubusercontent.com/istio/community/master/org/teams.yaml'
leaders_file = download_file(owners_url)
leaders_yaml = yaml.safe_load(leaders_file)

# Open the CSV file for writing and write the license and header lines
today = datetime.today().strftime('%Y-%m-%d')
outfile_name = 'output/owners_data_istio_' + today + '.csv'
csv_file = open(outfile_name,'w')

csv_file.write("License: Creative Commons Attribution-ShareAlike 4.0 International License\n")
csv_file.write("License Link: http://creativecommons.org/licenses/by-sa/4.0/\n")
csv_file.write("Author: Dr. Dawn M. Foster\n")
csv_file.write("Status: Updated on " + str(today) + "\n")
csv_file.write("Source URL: https://github.com/geekygirldawn/k8s_data/datasets\n\n")

csv_file.write("company,username,team\n")
    
# Gets the members from the top level teams
for x in leaders_yaml['teams'].items():
    team = x[0]
    for username in x[1]['members']:
        write_affil_line_istio (username, team, affil_dict, api_token, csv_file)

# Gets members data for WGs with subteams
for x in leaders_yaml['teams']['Maintainers']['teams'].items():
    team = x[0]
    for username in x[1]['members']:
        write_affil_line_istio (username, team, affil_dict, api_token, csv_file)

    try:
        for z in x[1]['teams'].items():
            team = z[0]
            for username in z[1]['members']:
                write_affil_line_istio (username, team, affil_dict, api_token, csv_file)
    except:
        pass

csv_file.close()
