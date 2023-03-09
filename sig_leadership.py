# Copyright (C) 2019 Dawn M. Foster
# Licensed under GNU General Public License (GPL), version 3 or later: http://www.gnu.org/licenses/gpl.txt

def get_sig_leaders():

    from common_functions import process_sig_yaml, create_file

    sigs_wgs = process_sig_yaml()

    output_list = ['group,name,github_id,company\n']
    
    for k in sigs_wgs["sigs"]:
        group = 'SIG ' + k['name']
        leadership_list = k['leadership']['chairs']

        for leader in leadership_list:
            line = group + ',' + leader['name'] + ',' + leader['github'] + ',' + leader['company'] + '\n'
            output_list.append(line)

    for k in sigs_wgs["workinggroups"]:
        group = 'WG ' + k['name']
        leadership_list = k['leadership']['chairs']

        for leader in leadership_list:
            line = group + ',' + leader['name'] + ',' + leader['github'] + ',' + leader['company'] + '\n'
            output_list.append(line)

    # prepare output file and write header and list to csv
    try:
        file, file_path = create_file("k8s_SIG_WG_Leads")

        with open(file_path, "w") as out_file:
            #wr = csv.writer(out_file)
            for out_line in output_list:
                out_file.write(out_line)
            #wr.writerow('group,name,github_id,company')
            #wr.writerows(output_list)

    except:
        print('Could not write to csv file. This may be because the output directory is missing or you do not have permissions to write to it. Exiting')


get_sig_leaders()
