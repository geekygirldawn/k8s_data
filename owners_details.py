#!/usr/local/bin/python3

# Copyright (C) 2019 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

# Note: This only uses a subset of k8s OWNERS files. 
# Uses owners files found in sigs.yaml plus the OWNERS_ALIASES file containing leads

def download_file(url):

    # Takes a URL and downloads the contents of the file into a var to be used by other functions

    # NOTE: Make sure you pass in a raw yaml file, not html.
    # Example: sig_file = download_file('https://raw.githubusercontent.com/kubernetes/community/master/sigs.yaml')

    import urllib.request
    
    sig_file = urllib.request.urlopen(url)

    return sig_file

def read_cncf_affiliations():
    
    # Download the contents of the CNCF json file and create an affiliation dictionary indexed
    # by GitHub username to make finding affilions faster for later functions.
    # Includes only current affiliation and excludes robot accounts.

    import json
    
    filename = download_file('https://raw.githubusercontent.com/cncf/devstats/master/github_users.json')
    affil_file = json.load(filename)
    
    affil_dict = {}
    
    for item in affil_file:
        username = item['login']
        
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

def write_affil_line(username, role, sig_name, subproject, owners_url, csv_file, affil_dict):
    
    # Writes a single line to the csv file with data about owners, including
    # SIG/WG, subproject (if applicable), affiliation, owners url

    if username in affil_dict:
        affil = affil_dict[username]
        if affil == '?':
            affil = 'NotFound'
    else:
        affil = 'NotFound'
        
    line = ",".join([affil, username, role, sig_name, subproject, owners_url]) + "\n"
    csv_file.write(line)

def write_aliases(role, alias_url, csv_file, affil_dict):

    # Takes OWNERS_ALIASES file with details about SIG/WG leadership and
    # writes those details to the csv file with role of 'lead' and NA
    # for subproject.
     
    import yaml

    alias_file = download_file(alias_url)
    aliases = yaml.safe_load(alias_file)
    
    for x in aliases['aliases'].items():
        sig_or_wg = x[0][:-6] #Note: this strips the -leads from the end of the sig name
        for username in x[1]:
            write_affil_line(username, role, sig_or_wg, 'NA', alias_url, csv_file, affil_dict)
    
def build_owners_csv():

    # This is the primary function that pulls all of this together.
    # It gets the list of OWNERS files from sigs.yaml, downloads the 
    # content of each OWNERS file, and writes details about owners to a
    # csv file which is dropped into the current directory.
  
    import yaml

    affil_dict = read_cncf_affiliations()

    sig_file = download_file('https://raw.githubusercontent.com/kubernetes/community/master/sigs.yaml')    
    sigs = yaml.safe_load(sig_file)
    
    csv_file = open('owners_data.csv','w')
    csv_file.write("company,username,status,sig_name,subproject,owners_file\n")
    
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
    
                # Download contents of owners files and load them. Print error message for files that 404
                try:
                    owners_file = download_file(owners_url)
                    #stream = open(owners_file, 'r')
                    #owners = yaml.safe_load(stream)
                    owners = yaml.safe_load(owners_file)
                    
                except:
                    print("Cannot get", sig_name, owners_url)

                # Wrapped with 'try' since not every owners file has approvers and reviewers. 
                try:
                    for username in owners['approvers']:
                        write_affil_line(username, 'approver', sig_name, subproject, owners_url, csv_file, affil_dict)
                except:
                    pass
                            
                try: 
                    for username in owners['reviewers']:
                        write_affil_line(username, 'reviewer', sig_name, subproject, owners_url, csv_file, affil_dict)
                except:
                    pass
                
    csv_file.close()   
    
build_owners_csv()
        
