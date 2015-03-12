#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.revert_volume_snapshot import revert_vol_snap

auth = authorization("admin","password")
b = auth.get_auth()

input_dict = {'snapshot_id': 'c4486248-d6e1-44f1-8378-3d4a22434a92','volume_id': '5753992f-0c6f-4201-ac3c-3b36a0501b97','project_id':'57944987bd224ac497534f6c875553f9'}

yo = revert_vol_snap(input_dict,b)

print yo
