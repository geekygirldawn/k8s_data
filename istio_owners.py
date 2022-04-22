#!/usr/local/bin/python3

# Copyright (C) 2022 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

"""
"""

import yaml
from datetime import datetime
from common_functions import read_key, read_cncf_affiliations, get_affil, download_file, write_affil_line_istio

affil_dict = read_cncf_affiliations()

api_token = read_key('gh_key')

owners_url = 'https://raw.githubusercontent.com/istio/community/master/org/teams.yaml'
leaders_file = download_file(owners_url)
leaders_yaml = yaml.safe_load(leaders_file)

today = datetime.today().strftime('%Y-%m-%d')
outfile_name = 'output/owners_data_istio_' + today + '.csv'
csv_file = open(outfile_name,'w')
csv_file.write("company,username,team\n")
    
for x in leaders_yaml['teams'].items():
    team = x[0]
    for username in x[1]['members']:
        write_affil_line_istio (username, team, affil_dict, api_token, csv_file)

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
