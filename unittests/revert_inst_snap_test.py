#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.revert_instance_snapshot import revert_inst_snap

auth = authorization("admin","password")
b = auth.get_auth()

input_dict = {'snapshot_id': 'c0a70c4a-f82d-410b-bc63-7f20b42c2f49','instance_id': 'c0cc70ea-ced0-4149-b4f2-dc413a052c7e','project_id':'57944987bd224ac497534f6c875553f9'}

yo = revert_inst_snap(input_dict,b)

print yo
