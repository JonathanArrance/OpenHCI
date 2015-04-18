#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.revert_volume_snapshot import revert_vol_snap

auth = authorization("admin","password")
b = auth.get_auth()

input_dict = {'snapshot_id': 'dfe2a6b8-bcf4-41cd-86c2-97f40047418f','volume_id': '1d4dee9b-8885-40f0-84e4-29b9977b8f8d','project_id':'27e633859b2b46db9b0fc0cbece206ea'}

yo = revert_vol_snap(input_dict,b)

print yo
