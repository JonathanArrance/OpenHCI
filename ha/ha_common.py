#!/usr/local/lib/python2.7
import subprocess
import fileinput
import os
import time

from transcirrus.database.postgres import pgsql
import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util


def add_cluster_node():
    pass

def remove_cluster_node():
    pass

def check_cluster():
    out = subprocess.Popen('sudo service %s status'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pass

def reset_cluster_ring_state():
    pass

def load_cluster_service():
    pass

def unload_cluster_service():
    pass

def list_cluster_ips():
    pass

def kill_cluster_node(cluster_node_id):
    pass

def get_cluster_members():
    """
    DESC: Get a list of corosync cluster members
    INPUT: None
    OUTPUT: r_array - node_id
                    - node_name
                    - node_status
                    - node_cluster_ip
                    - corosync_id
                    - node_id
    ACCESS: wide open
    NOTES:
    """
    out = subprocess.Popen('corosync-objctl runtime.totem.pg.mrp.srp.members', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process = out.stdout.readlines()
    print process

def get_cluster_status():
    pass

def get_cluster_node_ha_ip():
    """
    DESC: Get the cluster node cluster ip 169.254.x.x
    INPUT: None
    OUTPUT: cluster_ip or 'ERROR'
    ACCESS: wide open
    NOTES:
    """
    cluster_ip = util.get_cluster_ip()
    if(cluster_ip == 'ERROR'):
        logger.sys_info('Could not get the ha cluster ip address.')
        return 'ERROR'
    return cluster_ip

def set_cluster_node_ha_ip():
    """
    DESC: Set the cluster bond IP.
    INPUT: None
    OUTPUT: r_dict - node_name
                   - cluster_ip
    ACCESS: wide open
    NOTES:
    """
    out = os.system('sudo avahi-autoipd --force-bind -D bond3')
    # this is BS we need to see if we can lower this time out
    time.sleep(10)
    if (out != 0):
        logger.sys_info("Cluster IP already set.")
        node_name = util.get_system_name()
        net = get_cluster_node_ha_ip()
        r_dict = {'node_name':node_name,'cluster_ip':net}
        return r_dict
    else:
        node_name = util.get_system_name()
        net = get_cluster_node_ha_ip()
        os.system("""sudo sed -i 's/IPADDR=/IPADDR='${IP}'/g' /etc/sysconfig/network-scripts/ifcfg-bond3""")
        os.system("""sudo sed -i 's/NETMASK=/NETMASK="255.255.0.0"/g' /etc/sysconfig/network-scripts/ifcfg-bond3""")
        db = util.db_connect()
        adapter = {'table':'net_adapter_settings','set':"net_ip='%s'"%(net),'where':"index='1'"}
        insert = db.pg_update(adapter)
        r_dict = {'node_name':node_name,'cluster_ip':net}
        return r_dict

def get_cluster_vip():
    pass

def set_cluster_vip():
    # pcs resource create ClusterIP IPaddr2 ip=192.168.0.120 cidr_netmask=32
    pass

def set_cluster_data_vip():
    # pcs resource create ClusterIP IPaddr2 ip=192.168.0.120 cidr_netmask=32
    pass