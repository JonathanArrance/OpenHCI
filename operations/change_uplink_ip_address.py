#!/usr/bin/python

import transcirrus.common.util as util
import transcirrus.common.config as config
import transcirrus.common.node_util as node_util
import transcirrus.common.logger as logger
import datetime
from ifconfig import ifconfig
from transcirrus.component.keystone.keystone_endpoints import endpoint_ops

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
            NA - unknown
    ACCESS:Only the admin can change the Uplink ip address
    NOTE: This def will change the uplink ip - it WILL NOT
          chnage the default public network or any allocated floating ips.
          The admin will have to do that seperatly.
    """
    #get the nodeID from the config file
    node_id = util.get_node_id()
    node_type = util.get_node_type()
    node_name = util.get_node_name()
    cloud_name = util.get_cloud_name()

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
                    'mgmt_dns2':mgmt_net['net_dns2'],
                    'mgmt_dns3':mgmt_net['net_dns3'],
                    'mgmt_domain':mgmt_net['net_dns_domain'],
                    'mgmt_dhcp':mgmt_net['inet_setting']
                    }
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
                uplink_info = [{'host_system':node_name,parameter:"api_ip",'param_value':input_dict['uplink_ip']},
                                {'host_system':node_name,parameter:"admin_api_ip",'param_value':input_dict['uplink_ip']},
                                {'host_system':node_name,parameter:"int_api_ip",'param_value':input_dict['uplink_ip']},
                                {'host_system':node_name,parameter:"uplink_ip",'param_value':input_dict['uplink_ip']},
                                {'host_system':node_name,parameter:"uplink_subnet",'param_value':input_dict['uplink_subnet']},
                                {'host_system':node_name,parameter:"uplink_gateway",'param_value':input_dict['uplink_gateway']},
                                {'host_system':node_name,parameter:"uplink_dns",'param_value':input_dict['uplink_dns']},
                                {'host_system':node_name,parameter:"uplink_domain_name",'param_value':input_dict['uplink_domain']}
                                ]
                uplink = update_system_variables(uplink_info)
                #recreate the openstack API endpoints
                if(uplink == 'OK'):
                    endpoint = endpoint_ops(auth_dict)
                    #reset the keystone endpoint
                    key_input = {'service_name':'keystone'}
                    del_keystone = endpoint.delete_endpoint(key_input)
                    print del_keystone
                    if(del_keystone == 'OK'):
                        input_dict = {'cloud_name':cloud_name,'service_name':'keystone'}
                        create_keystone = endpoint.create_endpoint(input_dict)
                        if(create_keystone['endpoint_id']):
                            print "Keystone endpoint set up complete."
                        else:
                            return "ERROR"
    
                    #reset swift endpoint
                    swift_input = {'service_name':'swift'}
                    del_swift = endpoint.delete_endpoint(swift_input)
                    print del_swift
                    if(del_swift == 'OK'):
                        input_dict = {'cloud_name':cloud_name,'service_name':'swift'}
                        create_swift = endpoint.create_endpoint(input_dict)
                        if(create_swift['endpoint_id']):
                            print "Swift endpoint set up complete."
                        else:
                            return "ERROR"
    
                    #reset nova endpoint
                    nova_input = {'service_name':'nova'}
                    del_nova = endpoint.delete_endpoint(nova_input)
                    print del_nova
                    if(del_nova == 'OK'):
                        input_dict = {'cloud_name':cloud_name,'service_name':'nova'}
                        create_nova = endpoint.create_endpoint(input_dict)
                        if(create_nova['endpoint_id']):
                            print "Nova endpoint set up complete."
                        else:
                            return "ERROR"
    
                    #reset quantum endpoint
                    quant_input = {'service_name':'quantum'}
                    del_quant = endpoint.delete_endpoint(quant_input)
                    print del_quant
                    if(del_quant == 'OK'):
                        input_dict = {'cloud_name':cloud_name,'service_name':'quantum'}
                        create_quant = endpoint.create_endpoint(input_dict)
                        if(create_quant['endpoint_id']):
                            print "Quantum endpoint set up complete."
                        else:
                            return "ERROR"
    
                    #reset cinder endpoint
                    cinder_input = {'service_name':'cinder'}
                    del_cinder = endpoint.delete_endpoint(cinder_input)
                    print del_cinder
                    if(del_cinder == 'OK'):
                        input_dict = {'cloud_name':cloud_name,'service_name':'cinder'}
                        create_cinder = endpoint.create_endpoint(input_dict)
                        if(create_cinder['endpoint_id']):
                            print "Cinder endpoint set up complete."
                        else:
                            return "ERROR"
    
                    #reset glance endpoint
                    glance_input = {'service_name':'glance'}
                    del_glance = endpoint.delete_endpoint(glance_input)
                    print del_glance
                    if(del_glance == 'OK'):
                        input_dict = {'cloud_name':cloud_name,'service_name':'glance'}
                        create_glance = endpoint.create_endpoint(input_dict)
                        if(create_glance['endpoint_id']):
                            print "Glance endpoint set up complete."
                        else:
                            return "ERROR"

                    #restart the network card
                    restart_card = util.restart_network_card("br-ex")
                    if(restart_card != 'OK'):
                        logger.sys_error("Could not restart adapter: Bridge 1(uplink)")
                        return restart_card
            else:
                logger.sys_info("Network config file not written, new uplnk not written, rolling back old config.")
                #Rollback the netconfig file
                date = strftime("%Y-%m-%d", gmtime())
                os.system('sudo cp /etc/network/interfaces_%s /etc/network/interfaces'%(date))
    else:
        logger.sys_error("Invalid node type.")
        return 'ERROR'