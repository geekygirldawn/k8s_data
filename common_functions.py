# Copyright (C) 2019-2022 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

def read_cncf_affiliations():
    """    
    Download the contents of the CNCF json file and create an affiliation dictionary indexed
    by GitHub username to make finding affilions faster for later functions.
    Includes only current affiliation and excludes robot accounts.
    
    Returns
    -------
    affil_dict : dict
        Contains a mapping of github username to affiliation
    """
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

def get_affil(affil_dict, username, api_token):
    """Get the company affiliation for a username from the CNCF gitdm
    data if available. The GitHub API company field for a user is a secondary
    source of this data.
    Parameters
    ----------
    affil_dict : dict
       generated by the read_cncf_affiliations function
    username : str
    api_token : str
        string containing a GitHub API token

    Returns
    -------
    affil : str
    """
    from github import Github

    g = Github(api_token)

    affil = 'NotFound'
    if username in affil_dict:
        # If affiliation is listed on GH, use that instead as more
        # likely up to date
        try:
            affil = g.get_user(username).company
            if affil == None:
                affil = affil_dict[username]
        except:
            pass
    if affil == '?':
        affil = 'NotFound'
    if affil == 'NotFound':
        try:
            affil = g.get_user(username).company
        except:
            affil = 'NotFound'
    if affil == None:
        affil = 'NotFound'
    # remove any commas from the company name
    affil = affil.replace(",","")
    return affil

def download_file(url):

    # Takes a URL and downloads the contents of the file into a var to be used by other functions

    # NOTE: Make sure you pass in a raw yaml file, not html.
    # Example: sig_file = download_file('https://raw.githubusercontent.com/kubernetes/community/master/sigs.yaml')

    import urllib.request
    
    sig_file = urllib.request.urlopen(url)

    return sig_file

def read_sig_yaml(sig_file):
    import yaml

    stream = open(sig_file, 'r')
    sigs_wgs = yaml.safe_load(stream)

    return sigs_wgs

def process_sig_yaml():

    sig_file = download_file('https://raw.githubusercontent.com/kubernetes/community/master/sigs.yaml', '/tmp/sigs.yaml')

    sigs_wgs = read_sig_yaml(sig_file)

    return sigs_wgs

def write_affil_line_istio (username, team, affil_dict, api_token, csv_file):
    """Used to write istio data to the CSV file
    Parameters
    ----------
    username : str
    team : str
    affil_dict : dict
       generated by the read_cncf_affiliations function
    api_token : str
        string containing a GitHub API token
    csv_file : csv
    """
    affil = get_affil(affil_dict, username, api_token)
    if affil == None or affil == '':
        affil = 'NotFound'
    line = ",".join([affil, username, team]) + "\n"
    csv_file.write(line)

def write_affil_line(username, role, sig_name, subproject, owners_url, csv_file, affil_dict):
    
    # Writes a single line to the csv file with data about owners, including
    # SIG/WG, subproject (if applicable), affiliation, owners url

    # Make sure username is lower case before checking affiliation
    username = username.lower()

    # Only print real users to the csv file. Need to filter out aliases.
    ban = ['approve', 'review', 'maintain', 'provider', 'leads', 'sig-', 'admins', 'release', 'licensing', 'github-admin-team', 'test-infra-oncall', 'managers', 'owners', 'committee', 'steering']

    flag = 1
    for b in ban:
        if b in username:
            flag = 0
    if flag == 1:
        if username in affil_dict:
            affil = affil_dict[username]
            if affil == '?':
                affil = 'NotFound'
        else:
            affil = 'NotFound'

        line = ",".join([affil, username, role, sig_name, subproject, owners_url]) + "\n"
        csv_file.write(line)

def read_owners_file(owners_url, sig_name, subproject, csv_file, affil_dict):
    # Download contents of owners files and load them. Print error message for files that 404
    
    import yaml

    try:
        owners_file = download_file(owners_url)
        #stream = open(owners_file, 'r')
        #owners = yaml.safe_load(stream)
        owners = yaml.safe_load(owners_file)
        
    except:
        print("Cannot get", sig_name, owners_url)

    # Wrapped with 'try' since not every owners file has approvers and reviewers. 
    try:
        for label in owners['labels']:
                label_spl = label.split('/')
                if subproject == 'NA' and label_spl[0] == 'area':
                    subproject = label_spl[1]
                elif sig_name == 'NA' and label_spl[0] == 'sig':
                    sig_name = 'sig-' + label_spl[1]
    except:
        pass

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

def files_done(owners_file_csv):
    """
    Reads the output csv file generated by reading the intial list of
    OWNERS files and is used to avoid re-reading files again when
    an additional list of OWNERS files is provided.

    Parameters
    ----------
    owners_file_csv : file object

    Returns
    -------
    files_doneDF : dataframe
        Contains the contents of the csv file as a dataframe

    """
    import pandas as pd

    files_doneDF = pd.read_csv(owners_file_csv)
    return files_doneDF

def read_key(file_name):
    """Retrieves a GitHub API key from a file.
    
    Parameters
    ----------
    file_name : str

    Returns
    -------
    key : str
    """

    from os.path import dirname, join

    # Reads the first line of a file containing the GitHub API key
    # Usage: key = read_key('gh_key')

    current_dir = dirname(__file__)
    file2 = "./" + file_name
    file_path = join(current_dir, file2)

    with open(file_path, 'r') as kf:
        key = kf.readline().rstrip() # remove newline & trailing whitespace
    return key

def run_search_query(query, g, branch_name, owners_rows):
    """Runs the query against the GitHub search API, appends the results
       to owners_rows list and returns the list with results.
    
    Parameters
    ----------
    query : str
        String formatted as a search query.
    g : Github object
    branch_name : str
        Default branch name from the API to use to build the URL
    owners_rows: list

    Returns
    -------
    owners_rows : list
    """
    import time

    # Run the search query to get all of the owners files
    output = g.search_code(query=query)
    print("Total number found", output.totalCount)

    # Format the results for each owners file to get the full path as a url
    # Sleep in the loop to avoid secondary rate limit exception
    for owners in output:
        full_path = 'https://raw.githubusercontent.com/' + owners.repository.full_name + '/' + branch_name + '/' + owners.path
        owners_rows.append(full_path)
        time.sleep(5)
    
    # Add an extra sleep before returning to give it more time to
    # avoid the rate limit exception
    time.sleep(60)

    return owners_rows

def expand_name_df(df,old_col,new_col):
    """Takes a dataframe df with an API JSON object with nested elements in old_col, 
    extracts the name, and saves it in a new dataframe column called new_col

    Parameters
    ----------
    df : dataframe
    old_col : str
    new_col : str

    Returns
    -------
    df : dataframe
    """
    
    import pandas as pd

    def expand_name(nested_name):
        """Takes an API JSON object with nested elements and extracts the name
        Parameters
        ----------
        nested_name : JSON API object

        Returns
        -------
        object_name : str
        """
        if pd.isnull(nested_name):
            object_name = 'Likely Missing'
        else:
            object_name = nested_name['name']
        return object_name

    df[new_col] = df[old_col].apply(expand_name)
    return df