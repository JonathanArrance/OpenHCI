#!/usr/local/lib/python2.7
import subprocess

from transcirrus.database.postgres import pgsql
import transcirrus.common.logger as looger
import transcirrus.common.config as config


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

def display_cluster_ips():
    pass

def kill_cluster_node(cluster_node_id):
    pass

def get_cluster_members():
    pass

def get_cluster_status():
    pass
