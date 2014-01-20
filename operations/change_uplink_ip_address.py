#!/usr/bin/python

import transcirrus.common.util as util
import transcirrus.common.config as config
import transcirrus.common.node_util as node_util
import transcirrus.common.logger as logger
from ifconfig import ifconfig

def change_uplink_ip(auth_dict,input_dict):
    """
    DESC: Change the IP address of the uplink adapter.
    INPUT: input_dict - uplink_ip - req
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

    # 1. we need to change the network bond1 ip address based on the node type - cc - change it it is uplink
    if(node_type == 'cc'):
        #get the current net settings from the db
        #get the current mgmt net info
        mgmt_net = util.get_network_variables({'net_adapter':'mgmt','node_id':node_id})
        if(mgmt_net == 'ERROR'):
            logger.sys_error('Could not get the mgmt net adapter info. Can not update uplink ip.')
            return 'ERROR'

        uplink_net = util.get_network_variables({'net_adapter':'uplink','node_id':node_id})
        if(uplink_net == 'ERROR'):
            logger.sys_error('Could not get the uplink net adapter info. Can not update uplink ip.')
            return 'ERROR'

        #get the existing vals
        if('uplink_subnet' not in input_dict):
            input_dict['uplink_subnet'] = uplink_net['net_mask']
        if('uplink_gateway' not in input_dict):
            input_dict['uplink_gateway'] = uplink_net['net_gateway']
        if('uplink_dns' not in input_dict):
            input_dict['uplink_dns'] = uplink_net['net_dns1']
        if('uplink_dns2' not in input_dict):
            input_dict['uplink_dns2'] = uplink_net['net_dns2']
        if('uplink_dns3' not in input_dict):
            input_dict['uplink_dns3'] = uplink_net['net_dns3']
        if('uplink_domain' not in input_dict):
            input_dict['uplink_domain'] = uplink_net['net_dns_domain']

        #change the ip with the given info
        uplink_dict = {
                       'up_ip':input_dict['uplink_ip'],
                       'up_subnet':input_dict['uplink_subnet'],
                       'up_gateway':input_dict['uplink_gateway'],
                       'up_dns1':input_dict['uplink_dns'],
                       'up_dns2':input_dict['uplink_dns2'],
                       'up_dns3':input_dict['uplink_dns3'],
                       'up_domain':input_dict['uplink_domain']
                       }
        mgmt_dict = {
                    'mgmt_ip':mgmt_net['net_ip'],
                    'mgmt_subnet':mgmt_net['net_mask'],
                    'mgmt_dns1':mgmt_net['net_dns1'],
                    'mgmt_dns2':['net_dns2'],
                    'mgmt_dns3':['net_dns3'],
                    'mgmt_domain':['net_dns_domain'],
                    'mgmt_dhcp':['inet_setting']
                    }
        input_dict = {
                      'node_id':node_id,
                      'uplink_dict':uplink_dict,
                      'mgmt_dict':mgmt_dict
                      }
        change_uplink = util.set_network_variables(input_dict)
    else:
        logger.sys_error("Invalid node type.")
        return 'ERROR'