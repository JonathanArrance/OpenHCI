#get the libs needed
#from celery import Celery
#from celery import task
import os
import time
import subprocess

import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.node_util as node_util
import transcirrus.common.service_control as service

from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.operations.change_adminuser_password import change_admin_password
from transcirrus.component.keystone.keystone_endpoints import endpoint_ops
from transcirrus.database import node_db

#app = Celery('rollback_setup')
#@app.task()
def rollback(auth_dict):
    net = neutron_net_ops(auth_dict)
    auth_dict['api_ip'] = util.get_api_ip()
    endpoint = endpoint_ops(auth_dict)

    #get all of the variables from the factory defaults table
    logger.sys_info('Getting the node ID and factory default settings.')
    try:
        factory_defaults = util.get_system_defaults(config.NODE_ID)
    except:
        logger.sys_error('Could not get the factory_defaults')
        raise Exception('Could not get the factory_defaults')

    #connect to the DB
    try:
        db = util.db_connect()
    except:
        pass

    #set the node back to single
    logger.sys_info("Disableing muli-node support.")
    try:
        status = node_util.disable_multi_node()
    except:
        pass

    #set the first time boot flag
    logger.sys_info("Reseting first time boot flag.")
    try:
        first_boot = node_util.set_first_time_boot('UNSET')
    except:
        pass

    #get trans_default
    try:
        get_project = {'select':"*",'from':"projects",'where':"proj_name='trans_default'"}
        proj_info = db.pg_select(get_project)
    except:
        pass

    #remove the iptables settings and the config file
    logger.sys_info("Removeing iptables entries.")
    try:
        os.system('sudo rm -rf /transcirrus/iptables.conf')
        os.system("sudo iptables -D FORWARD -i bond1 -o br-ex -s 172.38.24.0/24 -m conntrack --ctstate NEW -j ACCEPT")
        os.system("sudo iptables -D FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")
        os.system("sudo iptables -D POSTROUTING -s 172.38.24.0/24 -t nat -j MASQUERADE")
    except:
        logger.sys_info("No iptables entries to remove.")
        pass

    #get default subnet and net id
    try:
        net_id = util.get_default_pub_net_id()
        subnet_id = util.get_default_pub_subnet_id()
    except:
        pass

    #remove the public subnet
    logger.sys_info("Removeing the public subnet.")
    try:
        net.remove_net_pub_subnet(subnet_id)
    except:
        logger.sys_info("No public subnet to remove.")
        pass

    #remove the public network
    logger.sys_info("Removeing the public net.")
    try:
        net_dict = {'net_id':net_id,'project_id':proj_info[0][0]}
        net.remove_network(net_dict)
    except:
        logger.sys_info("No public net to remove.")
        pass

    #set all of the netadpters to default IPS
    #set up br-ex and enable ovs.
    uplink_dict = {
                'up_ip':'192.168.0.3',
                'up_subnet':'255.255.255.0',
                'up_gateway':'192.168.0.1',
                'up_dns1':'8.8.8.8',
                'up_domain':'localhost.pubnet'
                }

    mgmt_dict = {
                'mgmt_ip':'192.168.0.2',
                'mgmt_subnet':'255.255.255.0',
                'mgmt_dns1':'8.8.8.8',
                'mgmt_domain':'localhost.localnet',
                'mgmt_dhcp':'static'
                }

    net_input = {'node_id':config.NODE_ID,
                 'uplink_dict':uplink_dict,
                 'mgmt_dict':mgmt_dict
                }

    logger.sys_info('Reseting the network cards to factory default.')
    try:
        uplink = util.set_network_variables(net_input)
        write_net_config = util.write_new_config_file(uplink)
    except:
        pass

    #remove all of the endpoints except keystone
    logger.sys_info('Deleteing the OpenStack API endpoints.')
    try:
        endpoint.delete_endpoint({'service_name':'nova'})
        endpoint.delete_endpoint({'service_name':'cinder'})
        endpoint.delete_endpoint({'service_name':'glance'})
        endpoint.delete_endpoint({'service_name':'quantum'})
    except:
        pass

    #set nova,glance,cinder,quantum config files to defaults
    logger.sys_info('Removeing the OpenStack configs.')
    try:
        os.system('sudo rm -rf /etc/nova')
        os.system('sudo rm -rf /etc/cinder')
        os.system('sudo rm -rf /etc/glance')
        os.system('sudo rm -rf /etc/quantum')
        os.system('sudo tar -xvf /etc/os_configs.tar -C /etc')
    except:
        pass

    #stop all of the openstack services
    logger.sys_info('Stopping the OpenStack services.')
    try:
        nova_stop = service.nova('stop')
        cinder_stop = service.cinder('stop')
        glance_stop = service.glance('stop')
        neutron_start = service.neutron('stop')
    except:
        pass
    
    #remove the node entry
    logger.sys_info('Removeing the node from the Transcirrus DB.')
    node_id = util.get_node_id()
    try:
        del_node = node_db.delete_node(node_id)
    except:
        pass


    try:
        logger.sys_info('Resetting OpenStack Keystone.')
        #move the default config file back in place
        key_input = {'service_name':'keystone'}
        del_keystone = endpoint.delete_endpoint(key_input)
        print del_keystone
        if(del_keystone == 'OK'):
            input_dict = {'cloud_name':'TransCirrusCloud','service_name':'keystone'}
            create_keystone = endpoint.create_endpoint(input_dict)
            if(create_keystone['endpoint_id']):
                print "Keystone endpoint set up complete."
            else:
                return "Keystone error."
    except:
        pass

    #copy all of the factory defaults to trans_system_settings
    logger.sys_info('Resetting the factory system defaults.')
    try:
        util.update_system_variables(factory_defaults)
    except:
        pass

    #restart postgres
    logger.sys_info('Reseting the postgres DB.')
    try:
        os.system('sudo cp /etc/postgresql/9.1/main/pg_hba.proto /etc/postgresql/9.1/main/pg_hba.conf')
        psql_stop = service.postgresql('restart')
    except:
        pass

    #reset the config file
    sys_vars = None
    try:
        #get the current system settings
        sys_vars = util.get_system_variables(node_id)
        #properly format the key values to an array.
        content = []
        for key, val in sys_vars.items():
            row = key+'='+ '"'+ val + '"'
            content.append(row)
        #build the new config.py file
        config_dict = {'file_path':'/usr/local/lib/python2.7/dist-packages/transcirrus/common',
                       'file_name':'config.py',
                       'file_content':content,
                       'file_owner':'transuser',
                       'file_group':'transystem',
                       'file_perm':'644',
                       'op':'new'
                       }
        util.write_new_config_file(config_dict)
    except:
        pass

    #set the admin password back to password
    reset_password = change_admin_password(auth_dict,'password')
    if('OK'):
        logger.sys_info('Admin password reset to "password"')
    else:
        logger.sys_warn('Admin password was not reset, password may still be set.')