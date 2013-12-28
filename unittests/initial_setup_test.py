#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.operations.initial_setup import run_setup

auth = authorization("admin","password")
b = auth.get_auth()

new_system_variables = [
    {"system_name":"ciac-25779","parameter":"api_ip","param_value":"192.168.10.243"},
    {"system_name":"ciac-25779","parameter":"mgmt_ip","param_value":"192.168.3.4"},
    {"system_name":"ciac-25779","parameter":"admin_api_ip","param_value":"192.168.10.243"},
    {"system_name":"ciac-25779","parameter":"int_api_ip","param_value":"192.168.10.243"},
    {"system_name":"ciac-25779","parameter":"uplink_ip","param_value":"192.168.10.243"},
    {"system_name":"ciac-25779","parameter":"uplink_dns","param_value":"8.8.8.8"},
    {"system_name":"ciac-25779","parameter":"uplink_gateway","param_value":"192.168.10.1"},
    {"system_name":"ciac-25779","parameter":"uplink_domain_name","param_value":"rtp.transcirrus.com"},
    {"system_name":"ciac-25779","parameter":"uplink_subnet","param_value":"255.255.255.0"},
    {"system_name":"ciac-25779","parameter":"mgmt_domain_name","param_value":"int.transcirrus.com"},
    {"system_name":"ciac-25779","parameter":"mgmt_subnet","param_value":"255.255.255.0"},
    {"system_name":"ciac-25779","parameter":"mgmt_dns","param_value":"8.8.8.8"},
    {"system_name":"ciac-25779","parameter":"vm_ip_min","param_value":"192.168.10.10"},
    {"system_name":"ciac-25779","parameter":"vm_ip_max","param_value":"192.168.10.20"}
    ]

yo = run_setup(new_system_variables,b)

print yo
