#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.server_volume_ops import server_vol_ops

auth = authorization("admin","password")
b = auth.get_auth()

input_dict = {'instance_id': 'd69170a7-a071-4311-86af-553a5aae378c','project_id':'6492cba476994153800c5220a2f51bc2','mount_point':'/dev/vdc','action':'mount','volume_id':'89da0ca5-df09-4005-b7f4-474b6b3019b5'}

yo = server_vol_ops(b,input_dict)

print yo