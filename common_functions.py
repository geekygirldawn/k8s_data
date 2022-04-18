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