# Copyright (C) 2019-2022 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

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

def write_affil_line(username, role, sig_name, subproject, owners_url, csv_file, affil_dict):
    
    # Writes a single line to the csv file with data about owners, including
    # SIG/WG, subproject (if applicable), affiliation, owners url

    # Make sure username is lower case before checking affiliation
    username = username.lower()

    # Only print real users to the csv file. Need to filter out aliases.
    ban = ['approve', 'review', 'maintain', 'leads', 'sig-', 'admins', 'release', 'licensing', 'managers', 'owners', 'committee', 'steering']

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
        for username in owners['approvers']:
            write_affil_line(username, 'approver', sig_name, subproject, owners_url, csv_file, affil_dict)
    except:
        pass
                
    try: 
        for username in owners['reviewers']:
            write_affil_line(username, 'reviewer', sig_name, subproject, owners_url, csv_file, affil_dict)
    except:
        pass

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