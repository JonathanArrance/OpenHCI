#import transcirrus.database.node_db as node
import transcirrus.common.util as util
import time

#print "get all of system variables"
#sys = util.get_system_variables('000-12345678-12345')
#print sys

#update_dict = {'old_name':'jon-newdevstack','new_name':'jon-devstack'}
#sys = util.update_cloud_controller_name(update_dict)
#print sys
'''
time.sleep(1)
print "Get Network settings for management adapter"
input_dict = {'node_id':'001-12345678-12345','net_adapter':'mgmt'}
getadpt = util.get_network_variables(input_dict)
print getadpt
print "--------------------------------------------------"

time.sleep(1)
print "Get Network settings for management adapter"
input_dict2 = {'node_id':'001-12345678-12345','net_adapter':'data'}
getadpt2 = util.get_network_variables(input_dict2)
print getadpt2
print "--------------------------------------------------"

#time.sleep(1)
#print "Setting a compute node net config file and changeing network settings"
#input_dict = {'node_id':'001-12345678-12345','net_adapter':'MGMT','net_ip':'192.168.168.3','net_subnet':'255.255.0.0','net_gateway':'192.168.168.1','net_dhcp':'static','net_dns1':'8.8.8.8'}
#net = util.set_network_variables(input_dict)
#print net
#print "---------------------------------------------------"

time.sleep(1)
print "Setting a compute node net config file and changeing network settings"
input_dict = {'node_id':'000-12345678-12345','net_adapter':'uplink','net_ip':'192.168.168.3','net_subnet':'255.255.0.0','net_gateway':'192.168.168.1','net_dhcp':'static','net_dns1':'8.8.8.8'}
net = util.set_network_variables(input_dict)
print net
print "---------------------------------------------------"

time.sleep(1)
print "Writing the file"
write = util.write_new_config_file(net)
print write
'''

#print "Non-exsistant adapter"
stuff = util.restart_network_card("yo")
print stuff

#print "Exsistant adapter bond2"
stuff2 = util.restart_network_card("bond2")
print stuff2
update_dict = {'old_name':'cloud','new_name':'integration'}
sys = util.update_cloud_controller_name(update_dict)
print sys


print "Test compare_vm_range..."
node = util.get_node_id();
system_variables = util.get_system_variables(node)
sys_vm_ip_min = system_variables['VM_IP_MIN']
sys_vm_ip_max = system_variables['VM_IP_MAX']
print "Current range: %s to %s" % (sys_vm_ip_min, sys_vm_ip_max)
new_min = "0.0.0.1"
new_max = "0.0.0.10"
print "Test using %s to %s" % (new_min, new_max)
invalid_range = util.compare_vm_range(util, new_min, new_max)
print invalid_range
