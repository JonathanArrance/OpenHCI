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

server = {'sec_group_name':'test2','sec_key_name':'test2','network_name':'test2','image_id':'32778bb7-e6ab-4568-a110-8e7573df0f3b',
          'flavor_id':'1','instance_name':'server_no_vol_info','project_id':'29dd2759d3a442b595b63cdc2d6ef8c5','boot_from_vol':"True"}

server_no_vol_info = boot_instance(server,b)

print server_no_vol_info
