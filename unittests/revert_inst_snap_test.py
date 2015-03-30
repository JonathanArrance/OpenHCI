#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.revert_instance_snapshot import revert_inst_snap

auth = authorization("admin","password")
b = auth.get_auth()

input_dict = {'snapshot_id': '1307be5a-8886-44df-9b25-1e6036fdd732','instance_id': '101320f0-c5b4-445d-94e5-2441c2cf2991','project_id':'d4b29af44660474da7d5f884ec107f76'}

yo = revert_inst_snap(input_dict,b)

print yo
