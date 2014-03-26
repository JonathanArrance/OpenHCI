#!/usr/bin/python

import transcirrus.common.util as util

#up = util.enable_network_card('bond2')
#print up

#net = util.get_network_variables()
#print net

#resolve = {
#                'dns_server1':'8.8.8.8',
#                'search_domain_int':'rtp.trans.com',
#                'search_domain_ext':'int.trans.com'
#}

#name_service = util.set_nameresolution(resolve)
#print name_service

#write_name_config = util.write_new_config_file(name_service)

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


clust_ip = {
           'clust_ip':'169.168.0.146',
           'clust_subnet':'255.255.0.0'
           }

net_input = {'node_id':'000-10015992-38332',
             'uplink_dict':uplink_dict,
             'mgmt_dict':mgmt_dict
            }

uplink = util.set_network_variables(net_input)

for link in uplink:
    print link
    write_net_config = util.write_new_config_file(link)


#net = util.restart_network_card('all')
#print net

#net = util.get_adapter_ip('eth4')
#print net
