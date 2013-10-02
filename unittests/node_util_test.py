#!/usr/bin/python

import transcirrus.common.node_util as node_util
import time


print "Checking admin password set to new password"
check_admin = node_util.check_admin_pass_status()
print check_admin
print "------------------------------------------"

status = None
time.sleep(1)
if(check_admin['admin_pass_set'] == 'FALSE'):
    print "Admin pass was not set ,Setting status flag to True"
    status = node_util.set_admin_pass_status('SET')
    print status
print "-------------------------------------------"

time.sleep(1)
print "Setting admin pass flag back to false"
unset = node_util.set_admin_pass_status('UNSET')
print unset
print "--------------------------------------------"

time.sleep(1)
print "Check first time boot flag"
fboot = node_util.check_first_time_boot();
print fboot
print "---------------------------------------------"

time.sleep(1)
print "checking fboot"
if(fboot['first_time_boot'] == 'TRUE'):
    print "setting first time boot flag to FALSE"
    setboot = node_util.set_first_time_boot('SET')
    print setboot
print "----------------------------------------------"

time.sleep(1)
print "Setting boot flag back to TRUE"
setboot =node_util.set_first_time_boot('UNSET')
print setboot
print "----------------------------------------------"

time.sleep(1)


print "Check node config flag"
flag = node_util.check_config_type();
print flag
print "-----------------------------------------------"


time.sleep(1)
if(flag['config_type'] == 'SINGLE'):
    print "setting node to multinode"
    setmode = node_util.enable_multi_node()
    print setmode
print "----------------------------------------------"

time.sleep(1)
print "setting back to single node"
if(setmode == 'OK'):
    unsetmode = node_util.disable_multi_node()
    print unsetmode
print "------------------------------------------------"

time.sleep(1)
flag2 = node_util.check_config_type();
print flag2
