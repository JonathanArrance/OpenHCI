#!/usr/bin/python2.7

import os
import sys
import socket
from thread import *
import pickle
import select
from time import sleep

import transcirrus.common.util as util
import transcirrus.database.node_db as node_db
import transcirrus.common.node_util as node_util
import transcirrus.common.logger as logger
import transcirrus.common.service_control as service_controller


_server_port=6161
count=0
keep_alive_sec=10
timeout_sec = 1
retry_count = 5
recv_buffer = 4096
dhcp_retry = 5
services_retry = 5

connect_pkt = {
'Type' : 'connect',
'Length': '1',
'Value': 1
}

status_ready = {
'Type':'status',
'Length':'1',
'Value':'node_ready'
}

status_halt = {
'Type':'status',
'length':'1',
'Value':'node_halt'
}

node_info = {
'Type': 'Node_info', 
'Length': 10, 
'Value': {
    'node_name':'box15',
    'node_type':'cn',
    'node_mgmt_ip':'',
    'node_data_ip':'',
    'node_controller':'',
    'node_cloud_name':'',
    'node_nova_zone':'',
    'node_iscsi_iqn':'',
    'node_swift_ring':'',
    'node_id':'trans01'
    }
}

reply_alive = {
'Type' : 'status',
'Length': '1',
'Value': 'alive'
}

pkt_len = {
'Type' : 'pkt_len',
'Length': '1',
'Value': 1
}


