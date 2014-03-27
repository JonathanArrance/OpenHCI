#!/usr/local/lib/python2.7
import subprocess

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
    pass

def get_cluster_status():
    pass

def get_cluster_ha_ip():
    cluster_ip = util.get_cluster_ip()
    if(cluster_ip == 'ERROR'):
        logger.sys_info('Could not get the ha cluster ip address.')
        raise Exception('Could not get the ha cluster ip address.')
    return cluster_ip

def set_cluster_ha_ip(input_dict):
    

def get_cluster_vip():
    pass