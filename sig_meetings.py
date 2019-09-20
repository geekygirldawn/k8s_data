# Copyright (C) 2019 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

def get_sig_meetings():

    from common_functions import process_sig_yaml

    sigs_wgs = process_sig_yaml()

    for k in sigs_wgs["sigs"]:
        print('\nSIG ', k['name'], ':', sep='')

        for x in k['meetings']:
            print(x['description'], x['day'], x['time'], x['tz'], x['frequency'])

        for y in k['subprojects']:
            try:
                #print(y['meetings'])
                for z in y['meetings']:
                    print(z['description'], z['day'], z['time'], z['tz'], z['frequency'])
            except:
                pass
    for k in sigs_wgs["workinggroups"]:
        print('\nWG ', k['name'], ':', sep='')

        for x in k['meetings']:
            print(x['description'], x['day'], x['time'], x['tz'], x['frequency'])



get_sig_meetings()
