#!/usr/local/bin/python3

# Copyright (C) 2019-2022 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

# Note: This only uses a subset of k8s OWNERS files. 
# Uses the owners files found in sigs.yaml plus the OWNERS_ALIASES file containing leads


from common_functions import files_done


def read_cncf_affiliations():
    
    # Download the contents of the CNCF json file and create an affiliation dictionary indexed
    # by GitHub username to make finding affilions faster for later functions.
    # Includes only current affiliation and excludes robot accounts.

    import json
    from common_functions import download_file
    
    filename = download_file('https://github.com/cncf/devstats/blob/master/github_users.json?raw=true')
    affil_file = json.load(filename)
    
    affil_dict = {}
    
    for item in affil_file:
        # Force username to lower case for consistent affiliation checks
        username = item['login'].lower()
        
        try:
            affiliation = item['affiliation']
        
            if '(Robots)' not in affiliation:
                if ',' in affiliation: # get only current affiliation
                    affil_dict[username] = affiliation.rsplit(',', 1)[1].strip()
                else:
                    affil_dict[username] = affiliation
                
        except:
            affiliation = 'N/A'
            
    return affil_dict
    
def write_aliases(role, alias_url, csv_file, affil_dict):

    # Takes OWNERS_ALIASES file with details about SIG/WG leadership and
    # writes those details to the csv file with role of 'lead' and NA
    # for subproject.
     
    import yaml
    from common_functions import download_file, write_affil_line

    alias_file = download_file(alias_url)
    aliases = yaml.safe_load(alias_file)
    
    # Filter out anything that isn't a SIG/WG (committees, etc.)
    for x in aliases['aliases'].items():
        if x[0].startswith('sig') or x[0].startswith('wg'):
            sig_or_wg = x[0][:-6] #Note: this strips the -leads from the end of the sig name
            for username in x[1]:
                write_affil_line(username, role, sig_or_wg, 'NA', alias_url, csv_file, affil_dict)

def get_sig_list(sigs):

    # Gets the list of SIGs from sigs.yaml using the dir format sig-name

    import yaml
    
    sig_name_list = []
    
    for k in sigs["sigs"]:
        sig_name_list.append(k['dir'])
        
    return sig_name_list

def find_sig(sig_name_list, area):
    
    # Uses the sig-name formatted data from sigs.yaml and compares to data from OWNERS_ALIASES 
    # to determine the SIG name

    sig_name = 'NA'
    for name in sig_name_list:
        if area.startswith(name):
            sig_name = area[:len(name)]
            
    return sig_name

def kk_aliases(sigs, csv_file, affil_dict):

    # Reads OWNERS_ALIASES file from k/k and uses the find_sig function to split the
    # area into SIG, subproject, and role for things that are mostly, but not always,
    # formatted like sig-name-subproject-role. Example: sig-auth-audit-approvers
    # Then it grabs org affiliation and other data before saving it to the CSV file.

    import yaml
    from common_functions import download_file, write_affil_line

    sig_name_list = get_sig_list(sigs)

    owners_url = 'https://raw.githubusercontent.com/kubernetes/kubernetes/master/OWNERS_ALIASES'
    k_k_alias_file = download_file(owners_url)
    k_k_aliases = yaml.safe_load(k_k_alias_file)

    for x in k_k_aliases.items():
        for y in x[1].items():
            area = y[0]

            if area.endswith('approvers'):
                role = 'approver'
                role_len = 9
            elif area.endswith('reviewers'):
                role = 'reviewer'
                role_len = 9
            elif area.endswith('maintainer'):
                role = 'maintainer'
                role_len = 10
            elif area.endswith('maintainers'):
                role = 'maintainer'
                role_len = 11
            else:
                role = 'unknown'
                role_len = 0

            sig_name = find_sig(sig_name_list, area)

            if area.startswith('release-engineering'):
                sig_name = 'sig-release'
                subproject = 'release-engineering'
            else:
                subproject = area[len(sig_name)+1:-role_len-1]

            if subproject == '':
                subproject = 'NA'

            if 'NA' not in sig_name:
                for username in y[1]:
                    write_affil_line(username, role, sig_name, subproject, owners_url, csv_file, affil_dict)
 
def build_owners_csv():

    # This is the primary function that pulls all of this together.
    # It gets the list of OWNERS files from sigs.yaml, downloads the 
    # content of each OWNERS file, and writes details about owners to a
    # csv file which is dropped into the current directory.
  
    import yaml
    import csv
    from datetime import datetime
    from common_functions import download_file, read_owners_file, files_done

    affil_dict = read_cncf_affiliations()

    sig_file = download_file('https://raw.githubusercontent.com/kubernetes/community/master/sigs.yaml')    
    sigs = yaml.safe_load(sig_file)
   
    today = datetime.today().strftime('%Y-%m-%d')
    outfile_name = 'output/owners_data_' + today + '.csv'
    csv_file = open(outfile_name,'w')
    csv_file.write("company,username,status,sig_name,subproject,owners_file\n")
    
    kk_aliases(sigs, csv_file, affil_dict)
 
    # Get list of SIG / WG leads and add them to the csv file
    alias_url = 'https://raw.githubusercontent.com/kubernetes/community/master/OWNERS_ALIASES'
    write_aliases('lead', alias_url, csv_file, affil_dict)

    # Gather data for each SIG in sigs.yaml
    # NOTE: WGs don't have OWNERS files in sigs.yaml
    for x in sigs['sigs']:

        sig_name = x['dir']
        for y in x['subprojects']:
            for owners_url in y['owners']:
                subproject = y['name']
    
                read_owners_file(owners_url, sig_name, subproject, csv_file, affil_dict)
    csv_file.close()

    # Gather data from an additional list of OWNERS files if available
    # REPLACE THIS with argument from command line
    additional_owners = True

    if additional_owners == True:
        # Open output csv from earlier for reading and close it again before writing to it
        csv_file = open(outfile_name,'r')
        files_doneDF = files_done(csv_file)
        print(files_doneDF)
        csv_file.close()

        # REPLACE THIS with argument from command line
        new_owners_file = '/Users/fosterd/gitrepos/k8s_data/output/test_owners.csv'

        # Open csv with new list of owners files
        with open(new_owners_file, newline='') as f:
            new_owners_list = list(csv.reader(f))

        #re-open original output file to append data from new owners files
        csv_file = open(outfile_name,'a')

        for owners_url_list in new_owners_list:
            owners_url = owners_url_list[0]
            if files_doneDF['owners_file'].str.contains(owners_url).any() == False:
                sig_name = 'NA'
                subproject = 'NA'
                read_owners_file(owners_url, sig_name, subproject, csv_file, affil_dict)
        
        csv_file.close()
    
build_owners_csv()
        
