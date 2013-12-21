#!/usr/bin/python

import transcirrus.common.util as util

#up = util.enable_network_card('bond2')
#print up

#net = util.get_network_variables()
#print net

#set up br-ex and enable ovs.
#net_input = {'node_id':'000-12345678-12345',
#             'net_adapter':'uplink',
#             'net_ip':'192.168.10.30',
#             'net_subnet':'255.255.255.0',
#             'net_gateway':'192.168.1.1',
#             'net_dns1':'8.8.8.8',
#             'net_domain':'rtp.transcirrus.com',
#             'net_dhcp':'static'
#            }

#uplink = util.set_network_variables(net_input)
#print uplink

#write_net_config = util.write_new_config_file(uplink)
#print write_net_config

#net = util.restart_network_card('all')
#print net

net = util.get_adapter_ip('eth4')
print net
