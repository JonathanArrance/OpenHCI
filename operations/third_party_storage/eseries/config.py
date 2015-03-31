#
# E-Series specific config functions
#

import transcirrus.operations.third_party_storage.common as common

# Constants
ESERIES_NAME = "e-series"


def add_eseries_to_cinder (data):
    if not common.add_backend (ESERIES_NAME):
        return (False)
    add_eseries_stanza (data)
    return (True)


def add_eseries_stanza (data):
    curr_file = common.CINDER_CONF
    outfile = open (curr_file, 'a')

    outfile.writelines ("\n")
    outfile.writelines ("[" + ESERIES_NAME + "]\n")
    outfile.writelines ("# static data\n")
    outfile.writelines ("volume_group=cinder-volume-eseries\n")
    outfile.writelines ("volume_backend_name=" + ESERIES_NAME + "\n")
    outfile.writelines ("volume_driver=cinder.volume.drivers.netapp.common.NetAppDriver\n")
    outfile.writelines ("netapp_storage_protocol=iscsi\n")
    outfile.writelines ("netapp_storage_family=eseries\n")
    outfile.writelines ("netapp_webservice_path=/devmgr/v2\n")
    outfile.writelines ("# data below is customer supplied\n")
    outfile.writelines ("netapp_server_hostname=" + data['server'] + "\n")
    outfile.writelines ("netapp_login=" + data['login'] + "\n")
    outfile.writelines ("netapp_password=" + data['pwd'] + "\n")
    outfile.writelines ("netapp_sa_password=" + data['ctrl_pwd'] + "\n")
    outfile.writelines ("netapp_server_port=" + data['srv_port'] + "\n")
    outfile.writelines ("netapp_transport_type=" + data['transport'] + "\n")

    disk_pools = ""
    for disk in data['disk_pools']:
        disk_pools = disk_pools + disk + ","
    disk_pools = disk_pools[:-1] + "\n"
    outfile.writelines ("netapp_storage_pools=" + disk_pools)

    ip_addrs = ""
    for ips in data['ctrl_ips']:
        ip_addrs = ip_addrs + ips + ","
    ip_addrs = ip_addrs[:-1] + "\n"
    outfile.writelines ("netapp_controller_ips=" + ip_addrs)

    outfile.close()
    return


def get_eseries_data():
    curr_file = common.CINDER_CONF
    infile = open (curr_file, 'rU')

    row = infile.readlines()

    data = {}
    found_stanza = False
    for line in row:
        if found_stanza:
            if line.find("netapp_server_hostname") > -1:
                data['server'] = common.get_params (line)[0]
            if line.find("netapp_login") > -1:
                data['login'] = common.get_params (line)[0]
            if line.find("netapp_password") > -1:
                data['pwd'] = common.get_params (line)[0]
            if line.find("netapp_sa_password") > -1:
                data['ctrl_pwd'] = common.get_params (line)[0]
            if line.find("netapp_server_port") > -1:
                data['srv_port'] = common.get_params (line)[0]
            if line.find("netapp_transport_type") > -1:
                data['transport'] = common.get_params (line)[0]
            if line.find("netapp_storage_pools") > -1:
                data['disk_pools'] = common.get_params (line)
            if line.find("netapp_controller_ips") > -1:
                data['ctrl_ips'] = common.get_params (line)
                break

        if line.find("[" + ESERIES_NAME + "]") > -1:
            found_stanza = True

    infile.close()
    return (data)
