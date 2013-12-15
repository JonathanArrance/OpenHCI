import os
import time
import subprocess

from transcirrus.common.auth import authorization
import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.node_util as node_util
import transcirrus.common.service_control as service

from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.operations.change_adminuser_password import change_admin_password
from transcirrus.component.keystone.keystone_endpoints import endpoint_ops
from transcirrus.database import node_db

auth = authorization("admin","password")
b = auth.get_auth()

node_id = util.get_node_id()
node_name = util.get_system_name()
sys_vars = util.get_system_variables(node_id)
auth_dict['api_ip'] = util.get_api_ip()

#set up openvswitch
logger.sys_info("Setting up br-ex")
os.system("sudo ovs-vsctl add-br br-ex")
os.system("sudo ovs-vsctl add-bond br-ex bond1 eth2 eth3")
logger.sys_info("Setting up the internal br-int")
os.system("sudo ovs-vsctl add-br br-int")

g_input = {'uplink_ip':sys_vars['UPLINK_IP'],'uplink_gateway':sys_vars['UPLINK_GATEWAY'],'uplink_subnet':sys_vars['UPLINK_SUBNET']}
gateway = util.check_gateway_in_range(g_input)
if(gateway != 'OK'):
    logger.sys_error('Uplink gateway is not on the same subnet as the uplink ip.')
    print gateway

#set up br-ex and enable ovs.
net_input = {'node_id':node_id,
             'net_adapter':'uplink',
             'net_ip':sys_vars['UPLINK_IP'],
             'net_subnet':sys_vars['UPLINK_SUBNET'],
             'net_gateway':sys_vars['UPLINK_GATEWAY'],
             'net_dns1':sys_vars['UPLINK_DNS'],
             'net_domain':sys_vars['DOMAIN_NAME'],
             'net_dhcp':'static'
            }

uplink = util.set_network_variables(net_input)
print uplink
write_net_config = util.write_new_config_file(uplink)
time.sleep(1)
if(write_net_config != 'OK'):
    #Exit the setup return to factory default
    print write_net_config
else:
    print "Net config file written."
    logger.sys_info("Net config file written.")

#restart adapters
time.sleep(1)
#reconfig ips
out = subprocess.Popen('ipcalc --class %s/%s'%(sys_vars['UPLINK_IP'],sys_vars['UPLINK_SUBNET']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
process = out.stdout.readlines()
os.system("ip addr add %s/%s dev br-ex" %(sys_vars['UPLINK_IP'],process[0]))

#this may have to be moved to the end
#logger.sys_info("Restarting the network adapters.")
#ints = util.restart_network_card('all')
#if(ints != 'OK'):
#    logger.sys_error("Could not restart network interfaces.")
#    return ints

#add IP tables entries for new bridge - Grizzly only Havanna will do this automatically
logger.sys_info("Setting up iptables entries.")
os.system("sudo iptables -A FORWARD -i bond1 -o br-ex -s 172.38.24.0/24 -m conntrack --ctstate NEW -j ACCEPT")
os.system("sudo iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")
os.system("sudo iptables -A POSTROUTING -s 172.38.24.0/24 -t nat -j MASQUERADE")

logger.sys_info("Saving the iptables entries.")
os.system("sudo iptables-save > /etc/iptables.conf")

#after quantum enabled create the default_public ip range
#check to make sure default public is the same range as the uplink ip
public_dict = {'uplink_ip':sys_vars['UPLINK_IP'],'public_start':sys_vars['VM_IP_MIN'],'public_end':sys_vars['VM_IP_MAX'],'public_subnet':sys_vars['UPLINK_SUBNET']}
pub_check = util.check_public_with_uplink(public_dict)
if(pub_check != 'OK'):
    logger.sys_error('The public network given does not match the uplink subnet.')
    print pub_check

#if in the same range create the default public range in quantum/neutron
time.sleep(2)
neu_net = neutron_net_ops(auth_dict)
p_create_dict = {'net_name':'default_public','admin_state':'true','shared':'true'}
default_public = neu_net.add_public_network(p_create_dict)
if('net_id' not in default_public):
    logger.sys_error("Could not create the default public network.")
    print 'ERROR'
else:
    #add the new public net to the sys_vars_table
    def_array = [{'system_name': sys_vars['NODE_NAME'],'parameter':'default_pub_net_id', 'param_value':default_public['net_id']}]
    update_def_pub_net = util.update_system_variables(def_array)
    if((pdate_def_pub_net == 'ERROR') or (pdate_def_pub_net == 'NA')):
        logger.sys_error("Could not update the default public network id, Setup has failed.")
        print 'ERROR'