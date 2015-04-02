#
# E-Series class to manage E-Series storage controllers
# via the NetApp Web Proxy.
#

import time
import uuid
import sys
import socket
import __builtin__

# We have to add & remove python2.6 from the search path so that the e-series
# client code can find the correct packages. The client.py file had to be
# copied to our directory because the __init__ in the netapp.eseries directory
# imports a lot of stuff that screwed up the imports.
# The utils.py isn't needed because the 1 function needed (resolve_hostname)
# was just inserted into this file.
sys.path.append("/usr/lib/python2.6/site-packages/")
import transcirrus.operations.third_party_storage.eseries.client as client
#import cinder.volume.drivers.netapp.eseries.client as client
#from cinder.volume.drivers.netapp import utils
from cinder import units
sys.path.remove("/usr/lib/python2.6/site-packages/")

# Dummy function so in eseries.client.py the function "_"
# will just return the included message.
# We have to include the function into the "builtin" scope
# so it can find it.
def retmsg (message): return message
__builtin__._ = retmsg


class eseries_mgmt():
    SLEEP_SECS = 5

    def __init__ (self, scheme, host, port, service_path, username, password):
        self.scheme = scheme
        self.server = host
        self.port = port
        self.service_path = service_path
        self.username = username
        self.password = password
        self.ctrl_ips = None
        self.ctrl_password = None
        self.storage_pools = None
        self.host = None
        self.system = None
        self._client = client.RestClient (scheme, host, port, service_path, username, password)
        return

    def get_storage_systems (self):
        return (self._client.list_storage_systems())

    def set_ctrl_password_and_ips (self, ctrl_password, ctrl_ips):
        self.ctrl_ips = ctrl_ips
        self.ctrl_password = ctrl_password
        self._register_storage_system()
        return

    def get_storage_pools (self):
        return (self._client.list_storage_pools())

    def set_storage_pools (self, storage_pools):
        pools = [x.strip().lower() if x else None for x in storage_pools]

        ## NOTE: Need to verify if this is getting all storage pool from all controllers
        #        and not just from 1 controller.
        found_pools = self.get_storage_pools()

        for pool_label in pools:
            found = False
            for pool in found_pools:
                if pool_label == pool['label'].lower():
                    if pool['raidLevel'] != 'raidDiskPool':
                        raise Exception ("Storage/Disk pool %s must be a dynamic disk pool." % pool_label)
                    found = True
                    break
            if not found:
                raise Exception ("Storage/Disk pool %s not found on web proxy server." % pool_label)
        self.storage_pools = storage_pools
        return

    def get_storage_system_ips (self, id):
        path = "/storage-systems/" + id + "/configuration/ethernet-interfaces/"
        interfaces = self._client._invoke('GET', path, use_system=False)

        ips = []
        for interface in interfaces:
            if interface['ip'] == 0:
                continue
            ips.append(interface['ipv4Address'])
        return (ips)

    def get_pool_usage (self, id):
        tot_bytes = 0
        used_bytes = 0
        pools = self.get_storage_pools()
        for pool in pools:
            if pool['id'] == id:
                tot_bytes = int(pool['totalRaidedSpace'], 0)
                used_bytes = int(pool['usedSpace'], 0)
                break
        free_capacity_gb = (tot_bytes - used_bytes) / units.GiB
        total_capacity_gb = tot_bytes / units.GiB
        usage = {'free_capacity_gb': free_capacity_gb, 'total_capacity_gb': total_capacity_gb}
        return (usage)

    # taken from netapp.utils.py
    def resolve_hostname(self, hostname):
        """Resolves host name to IP address."""
        res = socket.getaddrinfo(hostname, None)[0]
        family, socktype, proto, canonname, sockaddr = res
        return sockaddr[0]

    # The following modified code was taken from cinder.volume.drivers.netapp.eseries.iscsi.py

    def _register_storage_system (self):
        """Does validity checks for storage system registry and health."""

        def _resolve_host (host):
            try:
                ip = self.resolve_hostname(host)
                return ip
            except socket.gaierror as e:
                raise exception.NoValidHost ("Controller IP '%(host)s' could not be resolved: %(e)s." % {'host': host, 'e': e})

        ips = [x for x in self.ctrl_ips if _resolve_host(x)]

        self.host = self.resolve_hostname (self.server)
        self.system = self._client.register_storage_system (ips, password=self.ctrl_password)
        self._client.set_system_id (self.system.get('id'))
        return

    def _check_storage_system (self):
        """Checks whether system is registered and has good status."""
        try:
            system = self._client.list_storage_system()
        except Exception as e:
            msg = "System with controller addresses [%s] is not registered with web service."
            print msg % self.ctrl_ips

        password_not_in_sync = False
        if system.get('status', '').lower() == 'passwordoutofsync':
            password_not_in_sync = True
            new_pwd = self.ctrl_password
            self._client.update_stored_system_password(new_pwd)
            time.sleep (self.SLEEP_SECS)
        sa_comm_timeout = 60
        comm_time = 0
        while True:
            system = self._client.list_storage_system()
            status = system.get('status', '').lower()
            # wait if array not contacted or
            # password was not in sync previously.
            if ((status == 'nevercontacted') or
                    (password_not_in_sync and status == 'passwordoutofsync')):
                print "Waiting for web service array communication."
                time.sleep(self.SLEEP_SECS)
                comm_time = comm_time + self.SLEEP_SECS
                if comm_time >= sa_comm_timeout:
                    msg = "Failure in communication between web service and array. Waited %s seconds. Verify array configuration parameters."
                    raise Exception (msg % sa_comm_timeout)
            else:
                break
        msg_dict = {'id': system.get('id'), 'status': status}
        if (status == 'passwordoutofsync' or status == 'notsupported' or status == 'offline'):
            msg = "System %(id)s found with bad status - %(status)s."
            raise Exception (msg % msg_dict)
        print "System %(id)s has %(status)s status." % msg_dict
        return True
