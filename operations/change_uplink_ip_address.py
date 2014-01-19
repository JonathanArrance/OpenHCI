#!/usr/bin/python

import transcirrus.common.util as util
import transcirrus.common.config as config
import transcirrus.common.node_util as node_util
import transcirrus.common.logger as logger

from transcirrus.component.neutron.network import neutron_net_ops
from ifconfig import ifconfig

def change_uplink_ip(auth_dict,input_dict):
    """
    DESC: Change the IP address of the uplink adapter.
    INPUT: input_dict - uplink_ip
                      - uplink_subnet - op
                      - uplink_gateway - op
                      - uplink_dns - op
                      - uplink_dns2 - op
                      - uplink_dns3 - op
                      - uplink_domain - op
                      
    OUTPUT: OK - success
            ERROR - fail
    ACCESS:Only the admin can change the Uplink ip address
    NOTE: This def will change the uplink ip - it WILL NOT
          chnage the default public network or any allocated floating ips.
          The admin will have to do that seperatly.
    """
    #get the nodeID from the config file
    node_id = util.get_node_id()
    node_type = util.get_node_type()
    
    for key,value in input_dict.items():
        if(key == 'uplink_ip'):
            logger.sys_info('Uplink ip specified %s'%(input_dict['uplink_ip']))
            if(value == ""):
                logger.sys_error("Missing required param to reset uplink ip.")
                raise Exception("Missing required param to reset uplink ip.")
        elif(key == 'uplink_subnet'):
            logger.sys_info('Uplink subnet specified %s'%(input_dict['uplink_subnet']))
        elif(key == 'uplink_gateway'):
            logger.sys_info('Uplink gateway specified %s'%(input_dict['uplink_gateway']))
        elif(key == 'uplink_dns'):
            logger.sys_info('Uplink dns specified %s'%(input_dict['uplink_dns']))
        elif(key == 'uplink_dns2'):
            logger.sys_info('Uplink dns2 specified %s'%(input_dict['uplink_dns2']))
        elif(key == 'uplink_dns3'):
            logger.sys_info('Uplink dns3 specified %s'%(input_dict['uplink_dns3']))
        elif(key == 'uplink_domain'):
            logger.sys_info('Uplink domain specified %s'%(input_dict['uplink_domain']))
        else:
            logger.sys_error("Missing required param to reset uplink ip.")
            raise Exception("Missing required param to reset uplink ip.")

    #get the current mgmt net info
    mgmt_net = util.get_network_variables({'net_adapter':'mgmt','node_id':node_id})
    if(mgmt_net == 'ERROR'):
        logger.sys_error('Could not get the mgmt netw adapter info. Can not update uplink ip.')
        return 'ERROR'

    # 1. we need to change the network bond1 ip address based on the node type - cc - change it it is uplink
    if(node_type == 'cc'):
        #
    else:
        logger.sys_error("Invalid node type.")
        return 'ERROR'