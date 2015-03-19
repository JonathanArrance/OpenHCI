#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.revert_volume_snapshot import revert_vol_snap

auth = authorization("admin","password")
b = auth.get_auth()

input_dict = {'snapshot_id': '52bcdaed-b05d-4fa2-a341-500f00dcff2e','volume_id': '58201843-b421-47d7-86a8-cf76e4c42a5d','project_id':'d4b29af44660474da7d5f884ec107f76'}

yo = revert_vol_snap(input_dict,b)

print yo
