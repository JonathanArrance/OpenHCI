#
# Nimble specific config functions
#

import transcirrus.operations.third_party_storage.common as common

# Constants
NIMBLE_NAME = "Nimble"


def add_nimble_to_cinder (data):
    if not common.add_backend (NIMBLE_NAME):
        return (False)
    add_nimble_stanza (data)
    return (True)


def update_nimble_in_cinder (data):
    if not common.delete_stanza (NIMBLE_NAME):
        return (False)
    add_nimble_stanza (data)
    return (True)


def add_nimble_stanza (data):
    curr_file = common.CINDER_CONF
    outfile = open (curr_file, 'a')

    outfile.writelines ("\n")
    outfile.writelines ("[" + NIMBLE_NAME + "]\n")
    outfile.writelines ("# static data\n")
    outfile.writelines ("volume_group=cinder-volume-nimble\n")
    outfile.writelines ("volume_backend_name=" + NIMBLE_NAME + "\n")
    outfile.writelines ("volume_driver=cinder.volume.drivers.nimble.NimbleISCSIDriver\n")
    outfile.writelines ("# data below is customer supplied\n")
    outfile.writelines ("san_ip=" + data['server'] + "\n")
    outfile.writelines ("san_login=" + data['login'] + "\n")
    outfile.writelines ("san_password=" + data['pwd'] + "\n")

    outfile.close()
    return


def get_nimble_data():
    curr_file = common.CINDER_CONF
    infile = open (curr_file, 'rU')

    row = infile.readlines()

    data = {}
    found_stanza = False
    for line in row:
        if found_stanza:
            if line.find("san_ip") > -1:
                data['server'] = common.get_params (line)[0]
            if line.find("san_login") > -1:
                data['login'] = common.get_params (line)[0]
            if line.find("san_password") > -1:
                data['pwd'] = common.get_params (line)[0]
                break

        if line.find("[" + NIMBLE_NAME + "]") > -1:
            found_stanza = True

    infile.close()
    return (data)
