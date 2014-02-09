#!/usr/bin/python

import transcirrus.common.util as util

#up = util.enable_network_card('bond2')
#print up

#net = util.get_network_variables()
#print net

#set up br-ex and enable ovs.
uplink_dict = {
                'up_ip':'192.168.168.168',
                'up_subnet':'255.255.0.0',
                'up_gateway':'192.168.168.1',
                }

mgmt_dict = {
            'mgmt_ip':'192.168.10.10',
            'mgmt_subnet':'255.255.255.0',
            'mgmt_dhcp':'static'
            }

net_input = {'node_id':'000-10012472-16382',
             'uplink_dict':uplink_dict,
             'mgmt_dict':mgmt_dict
            }


uplink = util.set_network_variables(net_input)
print uplink

#write_net_config = util.write_new_config_file(uplink)
#print write_net_config

#net = util.restart_network_card('all')
#print net

#net = util.get_adapter_ip('eth4')
#print net
