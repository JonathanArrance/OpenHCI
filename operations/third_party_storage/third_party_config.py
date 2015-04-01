#
# Public configuration functions for 3rd party storage.
#
#   These functions will add, get, modify & delete a 3rd party storage
#   provider to cinder. These are the public facing functions which
#   will call functions that are unique to each 3rd party storage provider.
#   The private functions should not be called directly.
#

'''
 Background steps for manually configuring storage for cinder:

   changes to /etc/cinder.conf
     add new backend name to 'enabled_backends'
       enabled_backends=ssd,spindle,nfs,NetApp_E-Series
     add a stanza for the backend
     for nfs:
        [nfs]
        # static data
        volume_group=cinder-volume-nfs
        volume_driver = cinder.volume.drivers.nfs.NfsDriver
        volume_backend_name=nfs
        nfs_shares_config = /etc/cinder/shares_nfs.conf
        nfs_mount_point_base = /mnt/nfs-vols/cinder-volume

        create/append to /etc/cinder/shares_nfs.conf the nfs shares
        shares_nfs.conf
            # data below is customer supplied
            hostname1|ip-address1:/mountpoint1
            hostname1|ip-address1:/mountpoint2
            hostname2|ip-address2:/mountpoint3

     for E-Series:
        [NetApp_E-Series]
        # static data
        volume_group=cinder-volume-eseries
        volume_backend_name=e-series
        volume_driver=cinder.volume.drivers.netapp.common.NetAppDriver
        netapp_storage_protocol=iscsi
        netapp_storage_family=eseries
        netapp_webservice_path=/devmgr/v2
        # data below is customer supplied
        netapp_server_hostname=hostname/ip-address  # hostname or ip address of node running e-series web proxy service
        netapp_server_port=8080                     # port web proxy is listening on; default 8080 and 8443
        netapp_transport_type=http                  # transport type; either http or https
        netapp_login=rw                             # login to web proxy service
        netapp_password=rw                          # password to web proxy service
        netapp_controller_ips=ip-addr1,ip-addr2     # ip addresses for the mgmt ports on each storage controller
        netapp_sa_password=password                 # e-series controller(s) password
        netapp_storage_pools=DiskPool1,DiskPool2    # The disk pools to allocate storage from

'''

import transcirrus.operations.third_party_storage.common as common
import transcirrus.operations.third_party_storage.eseries.config as eseries
import transcirrus.operations.third_party_storage.nfs.config as nfs


# Return a list of supported 3rd party storage systems and
# if that system is currently configured.
# When a new 3rd party storage system is supported, add
# it to the list below.
def get_supported_third_party_storage():
    list = [{'name': "NetApp E-Series", 'configured': get_eseries()['enabled']},
            {'name': "nfs",             'configured': get_nfs()['enabled']}
           ]
    return (list)


# Add/Update/Get/Delete nfs data to cinder.
def add_nfs (mountpoints, auth):
    # mountpoints = ["hostname|ip-addr:/mountpoint", "hostname|ip-addr:/mountpoint"]
    if not nfs.add_nfs_to_cinder():
        return (False)
    nfs.add_nfs_conf (mountpoints)
    nfs.add_base_mountpoint()
    common.add_voltype (auth, nfs.NFS_NAME)
    common.restart_cinder_volume_proc()
    return (True)


# Update the mountpoints in the nfs config.
def update_nfs (mountpoints):
    nfs.delete_nfs_conf()
    nfs.add_nfs_conf (mountpoints)
    common.restart_cinder_volume_proc()
    return (True)


# Get nfs data from the nfs config.
def get_nfs():
    '''
    return data = {'enabled': "0/1",        "0" not enabled or "1" is enabled
                   'mountpoint': ["host1/ip-addr1:mountpoint", "host2/ip-addr2:mountpoint"]
                  }
    '''

    mountpoints = []
    if common.backend_configured (nfs.NFS_NAME):
        enabled = "1"
        mountpoints = nfs.get_nfs_data()
    else:
        enabled = "0"

    data = {'enabled': enabled, 'mountpoint': mountpoints}
    return (data)


# Delete nfs data from cinder and nfs configs.
def delete_nfs():
    common.delete_backend (nfs.NFS_NAME)
    common.delete_stanza (nfs.NFS_NAME)
    nfs.delete_nfs_conf (nfs.NFS_NAME)
    common.delete_voltype (auth, nfs.NFS_NAME)
    common.restart_cinder_volume_proc()
    return


# Add/Update/Get/Delete E-Series data to cinder.

# Add E-Series data to cinder config.
def add_eseries (data, auth, pre_existing=True):
    '''
    input: pre_existing = True/False           # use pre-existing web proxy server
           data = {'server':     "ip-addr",
                   'srv_port':   "port_num",
                   'transport':  "transport",
                   'login':      "username",
                   'pwd':        "password",
                   'ctrl_pwd':   "password",
                   'disk_pools': ["pool1", "pool2"],
                   'ctrl_ips':   ["ip-addr1", "ip-addr2"]
                  }
    '''
    if not pre_existing:
        data = eseries.get_eseries_pre_existing_data (data)
    if not eseries.add_eseries_to_cinder (data):
        return (False)
    common.add_voltype (auth, eseries.ESERIES_NAME)
    common.restart_cinder_volume_proc()
    return (True)


# Update E-Series data in cinder config.
def update_eseries (data):
    if not common.delete_stanza (eseries.ESERIES_NAME):
        return (False)
    eseries.add_eseries_stanza (data)
    common.restart_cinder_volume_proc()
    return (True)


# Get E-Series data from cinder config.
def get_eseries():
    '''
    return data = {'enabled':      "0/1",        "0" not enabled or "1" is enabled
                   'pre_existing': "0/1"         "0" not using pre-existing web proxy server or "1" using pre-existing web proxy server
                   'server':       "ip-addr",
                   'srv_port':     "port_num",
                   'transport':    "transport",
                   'login':        "username",
                   'pwd':          "password",
                   'ctrl_pwd':     "password",
                   'disk_pools':   ["pool1", "pool2"],
                   'ctrl_ips':     ["ip-addr1", "ip-addr2"]
                  }
    '''

    data = {}
    if common.backend_configured (eseries.ESERIES_NAME):
        enabled = "1"
        data = eseries.get_eseries_data()
        if data['server'] == "localhost":
            data['pre_existing'] = "0"
        else:
            data['pre_existing'] = "1"
    else:
        enabled = "0"

    data['enabled'] = enabled
    return (data)


# Get E-Series data for our internal web proxy service.
def get_eseries_pre_existing_data (data):
    '''
    return data = {'server':       "localhost",
                   'srv_port':     "8443",
                   'transport':    "https",
                   'service_path': "/devmgr/v2"
                   'login':        "rw",
                   'pwd':          "rw",
                   'ctrl_pwd':     given,
                   'disk_pools':   given,
                   'ctrl_ips':     given
                  }
    '''
    data['server']       = "localhost"
    data['srv_port']     = "8443"
    data['transport']    = "https"
    data['service_path'] = "/devmgr/v2"
    data['login']        = "rw"
    data['pwd']          = "rw"
    return (data)


# Delete E-Series data from cinder config.
def delete_eseries (auth):
    common.delete_backend (eseries.ESERIES_NAME)
    common.delete_stanza (eseries.ESERIES_NAME)
    common.delete_voltype (auth, eseries.ESERIES_NAME)
    common.restart_cinder_volume_proc()
    return
