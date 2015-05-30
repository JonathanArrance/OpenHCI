#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.delete_server import delete_server

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

#server = {'project_id':'c417abbb61014f2a8d330a0f7c0210a1','server_id':'a9e66e59-3f85-48d3-94a5-74308461123e','delete_boot_vol':'True'}

#delete = delete_server(b,server)

#print delete

server = {'project_id':'c417abbb61014f2a8d330a0f7c0210a1','server_id':'e06ba0ed-58da-425b-9212-f2195ad192e5'}

delete = delete_server(b,server)

print delete
