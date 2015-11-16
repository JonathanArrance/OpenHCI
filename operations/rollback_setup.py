#!/usr/local/bin/python2.7
import os, time, subprocess

from fnmatch import fnmatch

import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.node_util as node_util
import transcirrus.common.service_control as service

from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.operations.change_adminuser_password import change_admin_password
from transcirrus.component.keystone.keystone_endpoints import endpoint_ops
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.glance.glance_ops import glance_ops
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.database import node_db

#app = Celery('rollback_setup')
#@app.task()
def rollback(auth_dict):
    null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)]
    # save the current file descriptors to a tuple
    save = os.dup(1), os.dup(2)
    # put /dev/null fds on 1 and 2
    os.dup2(null_fds[0], 1)
    os.dup2(null_fds[1], 2)

    net = neutron_net_ops(auth_dict)
    glance = glance_ops(auth_dict)
    auth_dict['api_ip'] = util.get_api_ip()
    endpoint = endpoint_ops(auth_dict)
    tenants = tenant_ops(auth_dict)
    volumes = volume_ops(auth_dict)

    #get the projects that may be on the system.
    cloud_projects = tenants.list_all_tenants()
    if(len(cloud_projects) > 0):
        for cp in cloud_projects:
            project_info = tenants.get_tenant(cp['project_id'])
            if(project_info['project_name'] == 'trans_default'):
                logger.sys_info('Could not remove project trans_default. It can not be removed.')
            else:
                proj_dict = {'project_name': project_info['project_name'], 'project_id':project_info['project_id'] , 'keep_users': True}
                remove = tenants.remove_tenant(project_info['project_id'])
                if(remove == 'OK'):
                    logger.sys_info('Removed project %s completed during rollback.'%(project_info['project_name']))
                else:
                    logger.sys_error('Removed project %s failed during rollback.'%(project_info['project_name']))
                    pass
    else:
        logger.sys_info('No projects to roll back.')

    #remove the ssd and spindle vol types
    ssd = volumes.delete_volume_type("ssd")
    spindle = volumes.delete_volume_type("spindle")

    #connect to the DB
    db = util.db_connect()

    #get all of the variables from the factory defaults table
    logger.sys_info('Getting the node ID and factory default settings.')
    factory_defaults = None
    try:
        factory_defaults = util.get_system_defaults()
        logger.sys_info("factory_defaults: %s" % str(factory_defaults))
    except Exception as e:
        logger.sys_error('Could not get the factory_defaults')
        raise e

    #get trans_default
    try:
        get_project = {'select':"*",'from':"projects",'where':"proj_name='trans_default'"}
        proj_info = db.pg_select(get_project)
    except:
        logger.sys_error('Could not get the trans_default')
        pass
    """
    logger.sys_info("Removing the default glance images.")
    try:
        #remove the default glance images if they were created
        images = glance.list_images()
        for image in images:
            glance.delete_image(image['image_id'])
    except:
        logger.sys_info("No Glance images to remove.")
        pass

    #remove the iptables settings and the config file
    logger.sys_info("Removing iptables entries.")
    try:
        os.system('sudo iptables -F')
        os.system('sudo rm /transcirrus/iptables.conf')
    except:
        logger.sys_info("No iptables entries to remove.")
        pass
    """

    #get the default public info
    t = None
    try:
        t = net.list_external_networks()
    except:
        logger.sys_error('Could not get the external networks')
        pass

    #get default subnet and net id
    try:
        get_net = {'select':"subnet_id",'from':"trans_public_subnets",'where':"net_id='%s'"%(t[0]['net_id'])}
        network = db.pg_select(get_net)
        logger.sys_info("%s" %(network))
    except:
        logger.sys_error('Could not get the default subnet and net id')
        pass

    #remove the public subnet
    logger.sys_info("Removing the public subnet.")
    try:
        pub_sub = net.remove_net_pub_subnet(network[0][0])
        logger.sys_info("%s"%(pub_sub))
    except:
        logger.sys_error("No public subnet to remove.")
        pass

    #remove the public network
    logger.sys_info("Removing the public net.")
    try:
        net_dict = {'net_id':t[0]['net_id'],'project_id':proj_info[0][0]}
        pub_net = net.remove_network(net_dict)
        logger.sys_info("%s"%(pub_net))
    except:
        logger.sys_error("No public net to remove.")
        pass

    #set all of the netadpters to default IPS
    #set up br-ex and enable ovs.
    uplink_dict = {
                'up_ip':'192.168.0.2',
                'up_subnet':'255.255.255.0',
                'up_gateway':'192.168.10.1',
                }

    mgmt_dict = {
                'mgmt_ip':'192.168.0.3',
                'mgmt_subnet':'255.255.255.0',
                'mgmt_dhcp':'static'
                }

    net_input = {'node_id':config.NODE_ID,
                 'uplink_dict':uplink_dict,
                 'mgmt_dict':mgmt_dict
                }

    logger.sys_info('Reseting the network cards to factory default.')
    try:
        links = util.set_network_variables(net_input)
        logger.sys_info(str(links))
        for link in links:
            write_net_config = util.write_new_config_file(link)
            time.sleep(1)
            if (write_net_config != 'OK'):
                # Exit the setup return to factory default
                return write_net_config
            else:
                logger.sys_info("Net config file written.")
    except:
        logger.sys_error('Could not reset network')
        pass

    #remove all of the endpoints except keystone
    logger.sys_info('Deleting the OpenStack API endpoints.')
    try:
        endpoint.delete_endpoint('nova')
        endpoint.delete_endpoint('cinder')
        endpoint.delete_endpoint('cinder_v2')
        endpoint.delete_endpoint('glance')
        endpoint.delete_endpoint('neutron')
        endpoint.delete_endpoint('ceilometer')
        endpoint.delete_endpoint('heat')
        endpoint.delete_endpoint('ec2')
        endpoint.delete_endpoint('s3')
    except:
        logger.sys_error('Could not delete endpoints')
        pass

    #stop all of the openstack services
    logger.sys_info('Stopping the OpenStack services.')
    try:
        nova_stop = service.nova('stop')
        cinder_stop = service.cinder('stop')
        glance_stop = service.glance('stop')
        heat_stop = service.heat('stop')
        ceilometer_stop = service.ceilometer('stop')
        neutron_stop = service.neutron('stop')
    except:
        logger.sys_error('Could not stop services')
        pass

    #set nova,glance,cinder,neutron config files to defaults
    logger.sys_info('Removing the OpenStack configs.')
    try:
        os.system('sudo rm -rf /etc/nova')
        os.system('sudo rm -rf /etc/cinder')
        os.system('sudo rm -rf /etc/glance')
        os.system('sudo rm -rf /etc/heat')
        os.system('sudo rm -rf /etc/ceilometer')
        os.system('sudo rm -rf /etc/neutron')
        for f in os.listdir('/etc'):
            if fnmatch(f, 'os_configs*.tar'):
                os.system('sudo tar -xvf %s -C /etc' %f)
        os.system('sudo chown -R nova:nova /etc/nova')
        os.system('sudo chown -R cinder:cinder /etc/cinder')
        os.system('sudo chown -R glance:glance /etc/glance')
        os.system('sudo chown -R heat:heat /etc/heat')
        os.system('sudo chown -R ceilometer:ceilometer /etc/ceilometer')
        os.system('sudo chown -R neutron:neutron /etc/neutron')
        os.system('sudo chmod -R 770 /etc/nova /etc/neutron /etc/glance /etc/cinder /etc/ceilometer /etc/heat')
    except:
        logger.sys_error('Could not remove configs')
        pass

    #remove the node entry
    logger.sys_info('Removing the node from the Transcirrus DB.')
    try:
        del_node = node_db.delete_node(config.NODE_ID)
        logger.sys_info("delnode: %s" %(str(del_node)))
    except:
        logger.sys_error('Could not remove node entry')
        pass


    #copy all of the factory defaults to trans_system_settings
    logger.sys_info("\n   ---   config.NODE_NAME: %s   ---\n" %(str(config.NODE_NAME)))
    rollback_array = []
    for key,value in factory_defaults.items():
        dictionary = {"system_name":config.NODE_NAME,"parameter":key,"param_value":value}
        rollback_array.append(dictionary)

    logger.sys_info("\n   ---   rollback_array: %s   ---\n" %(str(rollback_array)))
    logger.sys_info('Resetting the factory system defaults.')
    try:
        up = util.update_system_variables(rollback_array)
        util.update_cloud_controller_name({"old_name":config.NODE_NAME,"new_name":factory_defaults['node_name']})
    except:
        logger.sys_error('Could not reset factory defaults')
        pass

    try:
        logger.sys_info('Resetting OpenStack Keystone.')
        #move the default config file back in place
        del_keystone = endpoint.delete_endpoint('keystone')
        if(del_keystone == 'OK'):
            input_dict = {'cloud_name':'TransCirrusCloud','service_name':'keystone'}
            create_keystone = endpoint.create_endpoint(input_dict)
            if(create_keystone['endpoint_id']):
                logger.sys_info("Keystone endpoint set up complete.")
            else:
                return "Keystone error."
    except:
        logger.sys_error('Could not reset keystone')
        pass

    #may have to hack endpoint not deleted for some reason, however the default endpoint is created ???????
    try:
        logger.sys_info('Resetting OpenStack Swift.')
        #move the default config file back in place
        del_swift = endpoint.delete_endpoint('swift')
        if(del_swift == 'OK'):
            input_dict = {'cloud_name':'TransCirrusCloud','service_name':'swift'}
            create_swift = endpoint.create_endpoint(input_dict)
            if(create_swift['endpoint_id']):
                logger.sys_info("Swift endpoint set up complete.")
            else:
                return "Swift error."
    except:
        logger.sys_error('Could not reset swift')
        pass

    #reset the config file
    sys_vars = None
    os.system('sudo mv /usr/local/lib/python2.7/transcirrus/common/config.py /usr/local/lib/python2.7/transcirrus/common/config.orig')
    try:
        #get the current system settings
        sys_vars = util.get_system_variables(config.NODE_ID)
        #properly format the key values to an array.
        content = []
        for key, val in sys_vars.items():
            row = key+'='+ '"'+ val + '"'
            content.append(row)
        #build the new config.py file
        config_dict = {'file_path':'/usr/local/lib/python2.7/transcirrus/common',
                       'file_name':'config.py',
                       'file_content':content,
                       'file_owner':'transuser',
                       'file_group':'transystem',
                       'file_perm':'644',
                       'op':'new'
                       }
        util.write_new_config_file(config_dict)
    except:
        logger.sys_error('Could not reset config file')
        pass

    #set the admin password back to password
    reset_password = change_admin_password(auth_dict,'password')
    if('OK'):
        logger.sys_info('Admin password reset to "password"')
    else:
        logger.sys_warn('Admin password was not reset, password may still be set.')
    os.system('sudo rm /usr/local/lib/python2.7/transcirrus/common/config.pyc')

    os.system('sudo rm /usr/local/lib/python2.7/transcirrus/common/config.pyc')
    os.system('sudo mv /var/log/caclogs/system.log /var/log/caclogs/system.log.pre_rollback')
    os.system('sudo touch /var/log/caclogs/system.log')
    os.system('sudo chmod 777 /var/log/caclogs/system.log')

    # restore file descriptors so I can print the results
    os.dup2(save[0], 1)
    os.dup2(save[1], 2)
    # close the temporary fds
    os.close(null_fds[0])
    os.close(null_fds[1])
    return 'OK'