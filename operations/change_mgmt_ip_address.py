#!/usr/bin/python

import transcirrus.common.util as util
import transcirrus.common.config as config
import transcirrus.common.node_util as node_util
import transcirrus.common.logger as logger
from ifconfig import ifconfig

def change_mgmt_ip(auth_dict,input_dict):
    """
    DESC: Change the IP address of the uplink adapter.
    INPUT: input_dict - mgmt_ip - op
                      - mgmt_subnet - op
                      - mgmt_gateway - op (only nodes)
                      - mgmt_dns - op
                      - mgmt_dns2 - op
                      - mgmt_dns3 - op
                      - mgmt_domain - op
                      - mgmt_dhcp - op static/dhcp
                      
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
    node_name = util.get_node_name()

    print input_dict

    for key,value in input_dict.items():
        if(key == 'mgmt_ip'):
            logger.sys_info('Management ip specified %s'%(input_dict['mgmt_ip']))
        elif(key == 'mgmt_gateway' and node_type == 'cc'):
            logger.sys_error("The cloud controller can not have a gateway set on the management port.")
            raise Exception("The cloud controller can not have a gateway set on the management port.")
        elif(key == 'mgmt_subnet'):
            logger.sys_info('Management subnet specified %s'%(input_dict['mgmt_subnet']))
        elif(key == 'mgmt_dns'):
            logger.sys_info('Management dns specified %s'%(input_dict['mgmt_dns']))
        elif(key == 'mgmt_dns2'):
            logger.sys_info('Uplink dns2 specified %s'%(input_dict['mgmt_dns2']))
        elif(key == 'mgmt_dns3'):
            logger.sys_info('Management dns3 specified %s'%(input_dict['mgmt_dns3']))
        elif(key == 'mgmt_domain'):
            logger.sys_info('Management domain specified %s'%(input_dict['mgmt_domain']))
        else:
            logger.sys_error("Missing required param to reset mgmt ip.")
            raise Exception("Missing required param to reset mgmt ip.")

    if('mgmt_dhcp' in input_dict):
        if(input_dict['mgmt_dhcp'] == 'static' and input_dict['mgmt_ip'] == ''):
            logger.sys_error("Missing param to reset mgmt ip. Specify ip with dhcp set to static.")
            raise Exception("Missing param to reset mgmt ip.Specify ip with dhcp set to static.")

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
    if('mgmt_ip' not in input_dict and input_dict['mgmt_dhcp'] != 'dhcp'):
        input_dict['mgmt_ip'] = mgmt_net['net_ip']
    if('mgmt_subnet' not in input_dict):
        input_dict['mgmt_subnet'] = mgmt_net['net_mask']
    
    if('uplink_gateway' not in input_dict and node_type != 'cc'):
        input_dict['mgmt_gateway'] = uplink_net['net_gateway']
    
    if('mgmt_dns' not in input_dict):
        input_dict['mgmt_dns'] = mgmt_net['net_dns1']
    if('mgmt_dns2' not in input_dict):
        input_dict['mgmt_dns2'] = mgmt_net['net_dns2']
    if('mgmt_dns3' not in input_dict):
        input_dict['mgmt_dns3'] = mgmt_net['net_dns3']
    if('mgmt_domain' not in input_dict):
        input_dict['mgmt_domain'] = mgmt_net['net_dns_domain']
    if('mgmt_dhcp' not in input_dict):
        input_dict['mgmt_dhcp'] = mgmt_net['inet_setting']

    #change the ip with the given info
    uplink_dict = {
                   'up_ip':uplink_net['net_ip'],
                   'up_subnet':uplink_net['net_mask'],
                   'up_gateway':uplink_net['net_gateway'],
                   'up_dns1':uplink_net['net_dns1'],
                   'up_dns2':uplink_net['net_dns2'],
                   'up_dns3':uplink_net['net_dns3'],
                   'up_domain':uplink_net['net_dns_domain']
                   }
    mgmt_dict = {
                'mgmt_ip':input_dict['mgmt_ip'],
                'mgmt_subnet':input_dict['mgmt_subnet'],
                'mgmt_dns1':input_dict['mgmt_dns'],
                'mgmt_dns2':input_dict['mgmt_dns2'],
                'mgmt_dns3':input_dict['mgmt_dns3'],
                'mgmt_domain':input_dict['mgmt_domain'],
                'mgmt_dhcp':input_dict['mgmt_dhcp']
                }
    if(node_type != 'cc'):
        mgmt_dict['mgmt_gateway'] = input_dict['mgmt_gateway']

    input_dict = {
                  'node_id':node_id,
                  'uplink_dict':uplink_dict,
                  'mgmt_dict':mgmt_dict
                  }
    change_uplink = util.set_network_variables(input_dict)
    if(change_uplink == 'ERROR' or change_uplink == 'NA'):
        return change_uplink
    else:
        logger.sys_info("writing the network config file.")
        write_up_net = util.write_new_config_file(change_uplink)
        if(write_up_net == 'OK'):
            #write the sysconfigs and the new config.py
            mg_info = [{'host_system':node_name,'parameter':"mgmt_ip",'param_value':input_dict['mgmt_ip']},
                        {'host_system':node_name,'parameter':"mgmt_subnet",'param_value':input_dict['mgmt_subnet']},
                        {'host_system':node_name,'parameter':"mgmt_dns",'param_value':input_dict['mgmt_dns']},
                        {'host_system':node_name,'parameter':"mgmt_domain_name",'param_value':input_dict['mgmt_domain']}
                       ]
            manage = update_system_variables(mg_info)
            if(manage == 'OK'):
                #restart the network card
                restart_card = util.restart_network_card("bond0")
                if(restart_card != 'OK'):
                    logger.sys_error("Could not restart adapter: bond0(mgmt)")
                    return restart_card
        else:
            logger.sys_info("Network config file not written, new uplnk not written, rolling back old config.")
            #Rollback the netconfig file
            date = strftime("%Y-%m-%d", gmtime())
            os.system('sudo cp /etc/network/interfaces_%s /etc/network/interfaces'%(date))