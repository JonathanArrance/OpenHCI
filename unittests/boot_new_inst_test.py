#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.boot_new_instance import boot_instance

auth = authorization("admin","password")
b = auth.get_auth()

#from transcirrus.component.nova.flavor import flavor_ops
#flavor = flavor_ops(b)
#flav_info = flavor.get_flavor("2")
#print flav_info

#input_dict - project_id - REQ
#- sec_group_name - REQ
#- sec_key_name - REQ
#- avail_zone - default availability zone - nova
#- network_name - default project net used if none specified
#                       - image_name - REQ
#                       - flavor_name - REQ
#                       - instance_name - REQ
#                       - volume_size - OP
#                       - volume_name - OP
#                       - volume_type - OP
#                       - boot_from_vol - OP(True/False) - default False

#server = {'sec_group_name':'test','sec_key_name':'test','network_name':'test','image_id':'615f30ee-7708-4a97-9c7d-d5b0c189780c',
#          'flavor_id':'1','instance_name':'server_no_vol_info','project_id':'c417abbb61014f2a8d330a0f7c0210a1','boot_from_vol':"True"}

#server_no_vol_info = boot_instance(server,b)

#print server_no_vol_info

server2 = {'sec_group_name':'test','sec_key_name':'test','network_name':'test','image_id':'615f30ee-7708-4a97-9c7d-d5b0c189780c',
          'flavor_id':'1','instance_name':'server_no_vol','project_id':'c417abbb61014f2a8d330a0f7c0210a1','boot_from_vol':"False"}

server_no_vol = boot_instance(server2,b)

print server_no_vol

server3 = {'sec_group_name':'test','sec_key_name':'test','network_name':'test','image_id':'615f30ee-7708-4a97-9c7d-d5b0c189780c',
          'flavor_id':'1','instance_name':'server_no_vol','project_id':'c417abbb61014f2a8d330a0f7c0210a1','volume_size':'8','volume_name':'volume_with_info','volume_type':'ssd','boot_from_vol':"True"}

server_vol_info = boot_instance(server3,b)

print server_vol_info