#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.initial_setup import run_setup

auth = authorization("admin","password")
b = auth.get_auth()

new_system_variables = [{"system_name":"ciac-25466","parameter":"api_ip","param_value":"192.168.10.247"},{"system_name":"ciac-25466","parameter":"mgmt_ip","param_value":"192.168.10.247"},
    {"system_name":"ciac-25466","parameter":"admin_api_ip","param_value":"192.168.10.247"},{"system_name":"ciac-25466","parameter":"int_api_ip","param_value":"192.168.10.247"},
    {"system_name":"ciac-25466","parameter":"uplink_ip","param_value":"192.168.10.247"},{"system_name":"ciac-25466","parameter":"uplink_dns","param_value":"8.8.8.8"},
    {"system_name":"ciac-25466","parameter":"uplink_gateway","param_value":"192.168.10.1"},{"system_name":"ciac-25466","parameter":"domain_name","param_value":"rtp.transcirrus.com"}]

yo = run_setup(new_system_variables,b)

print yo
