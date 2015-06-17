#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.delete_instance import delete_instance

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

#server = {'project_id':'660c9b42c2d945c0a79b32589b16a6bd','server_id':'70aabf53-ad48-40d6-a877-37a40b0f6b83','delete_boot_vol':'False'}

#delete = delete_instance(b,server)

#print delete

server = {'project_id':'660c9b42c2d945c0a79b32589b16a6bd','server_id':'6f2d9650-46d9-4150-8bce-95bde366611d'}
delete = delete_instance(b,server)

print delete
