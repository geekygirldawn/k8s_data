# Copyright (C) 2019 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

def get_sig_leaders():

    from common_functions import process_sig_yaml

    sigs_wgs = process_sig_yaml()

    for k in sigs_wgs["sigs"]:
        print('\nSIG ', k['name'], ':', sep='')
        leadership_list = k['leadership']['chairs']

        for leader in leadership_list:
            print(leader['name'], ', ', leader['github'], ', ', leader['company'], sep='')

    for k in sigs_wgs["workinggroups"]:
        print('\nWG ', k['name'], ':', sep='')
        leadership_list = k['leadership']['chairs']

        for leader in leadership_list:
            print(leader['name'], ', ', leader['github'], ', ', leader['company'], sep='')

get_sig_leaders()
