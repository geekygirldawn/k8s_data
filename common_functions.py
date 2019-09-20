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
