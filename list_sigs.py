# Copyright (C) 2019 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

def get_sig_list():

    from common_functions import process_sig_yaml

    sigs_wgs = process_sig_yaml()

    print('SIGs:')

    for k in sigs_wgs["sigs"]:
        print(' * ', k['name'])
    
    print('\nWGs:')

    for k in sigs_wgs["workinggroups"]:
        print(' * ', k['name'])

get_sig_list()
