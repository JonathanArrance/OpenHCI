#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.initial_setup import run_setup

auth = authorization("admin","builder")
b = auth.get_auth()

new_system_variables = [{"system_name":"ciac-19974","parameter":"api_ip","param_value":"192.168.10.252"},{"system_name":"ciac-19974","parameter":"mgmt_ip","param_value":"192.168.10.252"},
    {"system_name":"ciac-19974","parameter":"admin_api_ip","param_value":"192.168.10.252"},{"system_name":"ciac-19974","parameter":"int_api_ip","param_value":"192.168.10.252"}]

yo = run_setup(new_system_variables,b)

print yo
