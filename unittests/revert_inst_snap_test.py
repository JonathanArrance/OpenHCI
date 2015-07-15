#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.revert_instance_snapshot import revert_inst_snap

auth = authorization("admin","password")
b = auth.get_auth()

input_dict = {'snapshot_id': '85bd1140-ef6e-48b8-b944-fe91ee9236a3','instance_id': 'edd840c5-0714-4288-abbb-0150743e63ea','project_id':'ed9dbabaf2a54f13871d477d4a4f2d1e'}

yo = revert_inst_snap(input_dict,b)

print yo
