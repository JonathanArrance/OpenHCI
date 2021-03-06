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

server = {'sec_group_name':'test','sec_key_name':'test','network_name':'test','image_id':'00afa8ca-103e-47eb-8bba-7a80e77819a8',
          'flavor_id':'1','instance_name':'server_no_vol_info','project_id':'660c9b42c2d945c0a79b32589b16a6bd','boot_from_vol':"False"}

server_no_vol_info = boot_instance(server,b)

print server_no_vol_info

#server2 = {'sec_group_name':'test','sec_key_name':'test','network_name':'test','image_id':'860f9671-0562-4cb6-a5f8-2876fd2a65cb',
#          'flavor_id':'1','instance_name':'server_no_vol','project_id':'ff8fbdc33d83419a8070d2e7577b3a3f','boot_from_vol':"False"}

#server_no_vol = boot_instance(server2,b)

#print server_no_vol

#server3 = {'sec_group_name':'test','sec_key_name':'test','network_name':'test','image_id':'860f9671-0562-4cb6-a5f8-2876fd2a65cb',
#          'flavor_id':'1','instance_name':'server_no_vol','project_id':'ff8fbdc33d83419a8070d2e7577b3a3f','volume_size':'8','volume_name':'volume_with_info','volume_type':'ssd','boot_from_vol':"True"}#

#server_vol_info = boot_instance(server3,b)

#print server_vol_info