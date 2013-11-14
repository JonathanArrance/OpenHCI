#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.initial_setup import run_setup

auth = authorization("admin","builder")
b = auth.get_auth()

new_system_variables = [{"system_name":"integration","parameter":"api_ip","param_value":"192.168.10.41"},{"system_name":"integration","parameter":"mgmt_ip","param_value":"192.168.10.41"},
    {"system_name":"integration","parameter":"admin_api_ip","param_value":"192.168.10.41"},{"system_name":"integration","parameter":"int_api_ip","param_value":"192.168.10.41"}]

yo = run_setup(new_system_variables,b)

print yo
