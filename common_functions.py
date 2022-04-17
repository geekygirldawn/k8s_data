# Copyright (C) 2019 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

def download_file(url,output_file):

    # Usage:
    # sig_file = download_file('https://raw.githubusercontent.com/kubernetes/community/master/sigs.yaml', '/tmp/sigs.yaml')

    import wget
    import os
    import shutil
    import random
    
    output_bak = output_file + '_bak_' + str(random.randint(0,1024))

    if os.path.exists(output_file):
        shutil.move(output_file, output_bak)

    print("Downloading", url, "to file", output_file)

    sig_file = wget.download(url, out=output_file)
    
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

def run_search_query(query, g, owners_rows):
    import time

    output = g.search_code(query=query)
    print("Total number found", output.totalCount)

    #i = 0
    for owners in output:
        full_path = owners.repository.full_name + '/' + owners.path
        owners_rows.append(full_path)
        time.sleep(1)

        #if i >= 10:
            #break
        #else:
            #i+=1
    
    return owners_rows