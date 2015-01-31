#!/usr/local/lib/python2.7
#from celery import Celery
#from celery import task
#import rollback

import os
import time
import subprocess

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.node_util as node_util
import transcirrus.common.service_control as service
import transcirrus.ha.ha_common as ha_common

from transcirrus.component.neutron.network import neutron_net_ops
#from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.operations.change_adminuser_password import change_admin_password
from transcirrus.component.keystone.keystone_endpoints import endpoint_ops
from transcirrus.component.glance.glance_ops import glance_ops
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.operations.restart_all_services import restart_services

from transcirrus.database import node_db

#get the passed in vars
'''
Uplink IP
Management IP
VM range start
vm range end
cloud name
Admin password

node = get_node_id()
system = get_cloud_controller_name()
system_variables = get_system_variables(node)
new_system_variables = []
fields=("api_ip","mgmt_ip","admin_api_ip","int_api_ip","uplink_ip","vm_ip_min","vm_ip_max","cloud_name","single_node")
for field in fields:
    if system_variables[field] != form.cleaned_data[field]:
        updated_field_dict = {"system_name": system, "parameter": field, "parameter_value": form.cleaned_data[field]}
        new_system_variables.append(updated_field_dict)
run_setup(new_system_variables,auth_dict)
'''
def run_setup(new_system_variables,auth_dict):
    #retrieve the node_id from the config file before it is rewritten.
    node_id = util.get_node_id()
    node_name = util.get_system_name()
    auth_dict['api_ip'] = util.get_api_ip()

    #new_cloud_name = new_system_variables['cloud_name']
    #get the original system vars from the DB - used in case we need to rollback
    #rollback_sys_vars = util.get_system_variables(node_id)

    #add all of the new value from the interface into the db
    logger.sys_info('Updateing system variables.')
    update_sys_vars = util.update_system_variables(new_system_variables)
    if((update_sys_vars == 'ERROR') or (update_sys_vars == 'NA')):
        logger.sys_error("Could not update the system variables, Setup has failed.")
        raise Exception("Could not update the system variables, Setup has failed.")

    #get the current system settings
    sys_vars = util.get_system_variables(node_id)

    if(sys_vars == 'NA'):
        logger.sys_error("Could not retrieve the system_variables.")
        #do the rollback procedure
        #rollback = util.update_system_variables(rollback_sys_vars)
        raise Exception("Could not retrieve the system_variables.")

    boot = node_util.check_first_time_boot()
    if(boot == 'FALSE'):
        return "System already set up."

    #properly format the key values to an array.
    content = []
    for key, val in sys_vars.items():
        row = key+'='+ '"'+ val + '"'
        content.append(row)

    logger.sys_info('Building the config.py file.')
    #build the new config.py file
    config_dict = {'file_path':'/usr/local/lib/python2.7/transcirrus/common',
                   'file_name':'config.py',
                   'file_content':content,
                   'file_owner':'transuser',
                   'file_group':'transystem',
                   'file_perm':'644',
                   'op':'new'
                   }

    write_config = util.write_new_config_file(config_dict)
    if(write_config != 'OK'):
        logger.sys_error("Could not write the new config file.")
        #Perform the rollback to the original values
        #rollback = util.update_system_variables(rollback_sys_vars)

    #create an enpoint object
    endpoint = endpoint_ops(auth_dict)
    logger.sys_info('Re-building Swift endpoints')
    #reset the swift
    del_swift = endpoint.delete_endpoint('swift')
    if(del_swift == 'OK'):
        input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'swift'}
        create_swift = endpoint.create_endpoint(input_dict)
        if(create_swift['endpoint_id']):
            logger.sys_info("Swift endpoint set up complete.")
        else:
            return "Swift error."

    logger.sys_info('Re-building Keystone endpoints')
    #reset the keystone endpoint
    del_keystone = endpoint.delete_endpoint('keystone')
    if(del_keystone == 'OK'):
        input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'keystone'}
        create_keystone = endpoint.create_endpoint(input_dict)
        if(create_keystone['endpoint_id']):
            logger.sys_info("Keystone endpoint set up complete.")
        else:
            return "Keystone error."

    logger.sys_info('Building Nova endpoints')
    #set up all of the other endpoint based on the new mgmt IP address
    nova_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'nova'}
    create_nova = endpoint.create_endpoint(nova_input_dict)
    if(create_nova['endpoint_id']):
        logger.sys_info("Nova endpoint set up complete.")
    else:
        return "Nova error."

    logger.sys_info('Building Cinder endpoints')
    cinder_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'cinder'}
    create_cinder = endpoint.create_endpoint(cinder_input_dict)
    if(create_cinder['endpoint_id']):
        logger.sys_info("Cinder endpoint set up complete.")
    else:
        return "Cinder error."

    logger.sys_info('Building Glance endpoints')
    glance_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'glance'}
    create_glance = endpoint.create_endpoint(glance_input_dict)
    if(create_glance['endpoint_id']):
        logger.sys_info("Glance endpoint set up complete.")
    else:
        return "Glance error."

    logger.sys_info('Building Neutron endpoints')
    neutron_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'neutron'}
    create_neutron = endpoint.create_endpoint(neutron_input_dict)
    if(create_neutron['endpoint_id']):
        logger.sys_info( "Neutron endpoint set up complete.")
    else:
        return "Neutron error."

    logger.sys_info('Building Heat endpoints')
    heat_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'heat'}
    create_heat = endpoint.create_endpoint(heat_input_dict)
    if(create_heat['endpoint_id']):
        logger.sys_info( "Heat endpoint set up complete.")
    else:
        return "Heat error."

    logger.sys_info('Building Ceilometer endpoints')
    ceil_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'ceilometer'}
    create_ceil = endpoint.create_endpoint(ceil_input_dict)
    if(create_ceil['endpoint_id']):
        logger.sys_info( "Ceilometer endpoint set up complete.")
    else:
        return "Ceilometer error."

    logger.sys_info('Building EC2 endpoints')
    ec_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'ec2'}
    create_ec = endpoint.create_endpoint(ec_input_dict)
    if(create_ec['endpoint_id']):
        logger.sys_info( "EC2 endpoint set up complete.")
    else:
        return "EC2 error."

    logger.sys_info('Building S3 endpoints')
    s3_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'s3'}
    create_s3 = endpoint.create_endpoint(s3_input_dict)
    if(create_s3['endpoint_id']):
        logger.sys_info( "S3 endpoint set up complete.")
    else:
        return "S3 error."

    logger.sys_info('Adding the core node to the trans_nodes table.')
    #insert the controller info into trans_nodes db table
    cc_insert_dict = {'node_id':node_id,
                      'node_name':node_name,
                      'node_type':'cc',
                      'node_mgmt_ip':sys_vars['MGMT_IP'],
                      'node_data_ip':'172.24.24.10',
                      'node_controller':sys_vars['CLOUD_CONTROLLER'],
                      'node_cloud_name':sys_vars['CLOUD_NAME'],
                      'avail_zone':'nova',
                      'node_gluster_peer':'0',
                      'node_gluster_disks':'ssd'}
    insert_cc = node_db.insert_node(cc_insert_dict)
    if(insert_cc != 'OK'):
        return 'ERROR'

    #enable nova
    #write the nova config files
    logger.sys_info('Writing the Nova Config files.')
    nova_configs = node_db.get_node_nova_config(node_id)
    #take the array of nova file decriptors and write the files
    for config in nova_configs:
        write_nova_config = util.write_new_config_file(config)
        if(write_nova_config != 'OK'):
            #Exit the setup return to factory default
            return write_nova_config
        else:
            logger.sys_info("Nova config file written.")
    time.sleep(1)
    #HACK CentOS6.5 may not be needed in the future
    os.system('sudo usermod -G lock nova')
    os.system("sudo nova-manage db sync")
    time.sleep(1)
    #start the NOVA service
    nova_start = service.nova('restart')
    if(nova_start != 'OK'):
        #fire off revert
        return nova_start

    #enable cinder
    logger.sys_info('Writing the Cinder Config files.')
    cinder_configs = node_db.get_node_cinder_config(node_id)
    #take the array of cinder file decriptors and write the files
    for config in cinder_configs:
        write_cinder_config = util.write_new_config_file(config)
        if(write_cinder_config != 'OK'):
            #Exit the setup return to factory default
            return write_cinder_config
        else:
            logger.sys_info("Cinder config file written.")
    time.sleep(1)
    os.system("sudo cinder-manage db sync")
    time.sleep(1)
    #start the cinder service
    cinder_start = service.cinder('restart')
    if(cinder_start != 'OK'):
        #fire off revert
        return cinder_start

    #enable glance
    logger.sys_info('Writing the Glance Config files.')
    glance_configs = node_db.get_glance_config()
    #take the array of cinder file decriptors and write the files
    for config in glance_configs:
        write_glance_config = util.write_new_config_file(config)
        if(write_glance_config != 'OK'):
            #Exit the setup return to factory default
            return write_glance_config
        else:
            logger.sys_info("Glance config file written.")
    #start the cinder service
    glance_start = service.glance('restart')
    if(glance_start != 'OK'):
        #fire off revert
        return glance_start
    else:
        time.sleep(1)
        logger.sys_info("Syncing the Glance DB.")
        os.system("sudo glance-manage db_sync")
        #load default glance images shipped on ssd.

    #enable heat
    logger.sys_info('Writing the Heat Config files.')
    heat_configs = node_db.get_node_heat_config()
    #take the array of cinder file decriptors and write the files
    for config in heat_configs:
        write_heat_config = util.write_new_config_file(config)
        if(write_heat_config != 'OK'):
            #Exit the setup return to factory default
            return write_heat_config
        else:
            logger.sys_info("Heat config file written.")
    heat_start = service.heat('restart')
    if(heat_start != 'OK'):
        return heat_start
    else:
        time.sleep(1)
        logger.sys_info("Syncing the Heat DB.")
        os.system("sudo heat-manage db_sync")

    #enable ceilometer
    logger.sys_info('Writing the Ceilometer Config files.')
    ceil_configs = node_db.get_node_ceilometer_config(node_id)
    #take the array of cinder file decriptors and write the files
    for config in ceil_configs:
        write_ceil_config = util.write_new_config_file(config)
        if(write_ceil_config != 'OK'):
            #Exit the setup return to factory default
            return write_ceil_config
        else:
            logger.sys_info("Ceilometer config file written.")
    ceil_start = service.ceilometer('restart')
    if(ceil_start != 'OK'):
        #fire off revert
        return ceil_start

    #enable neutron
    logger.sys_info('Writing the Neutron Config files.')
    neu_configs = node_db.get_node_neutron_config(node_id)
    #take the array of cinder file decriptors and write the files
    for config in neu_configs:
        write_neutron_config = util.write_new_config_file(config)
        if(write_neutron_config != 'OK'):
            #Exit the setup return to factory default
            return write_neutron_config
        else:
            logger.sys_info("Neutron config file written.")
    #HACK - centOS6.5 - may not be needed in future
    os.system('sudo ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini')
    os.system('sudo chown -R neutron:neutron /var/lib/neutron')
    #start the cinder service
    neutron_start = service.neutron('restart')
    if(neutron_start != 'OK'):
        #fire off revert
        return neutron_start

    logger.sys_info('Writing the network config files.')
    g_input = {'uplink_ip':sys_vars['UPLINK_IP'],'uplink_gateway':sys_vars['UPLINK_GATEWAY'],'uplink_subnet':sys_vars['UPLINK_SUBNET']}
    gateway = util.check_gateway_in_range(g_input)
    if(gateway != 'OK'):
        logger.sys_error('Uplink gateway is not on the same subnet as the uplink ip.')
        return gateway

    resolve = {
                'dns_server1':sys_vars['UPLINK_DNS'],
                'search_domain_int':sys_vars['UPLINK_DOMAIN_NAME'],
                'search_domain_ext':sys_vars['MGMT_DOMAIN_NAME']
            }
    name_service = util.set_nameresolution(resolve)
    write_name_config = util.write_new_config_file(name_service)
    time.sleep(1)
    if(write_name_config != 'OK'):
        #Exit the setup return to factory default
        return write_name_config
    else:
        logger.sys_info("Name service config file written.")

    #set up br-ex and enable ovs.
    uplink_dict = {
                'up_ip':sys_vars['UPLINK_IP'],
                'up_subnet':sys_vars['UPLINK_SUBNET'],
                'up_gateway':sys_vars['UPLINK_GATEWAY'],
                }

    mgmt_dict = {
                'mgmt_ip':sys_vars['MGMT_IP'],
                'mgmt_subnet':sys_vars['MGMT_SUBNET'],
                'mgmt_dhcp':'static'
                }

    net_input = {'node_id':node_id,
                 'uplink_dict':uplink_dict,
                 'mgmt_dict':mgmt_dict
                }

    links = util.set_network_variables(net_input)
    for link in links:
        write_net_config = util.write_new_config_file(link)
        time.sleep(1)
        if(write_net_config != 'OK'):
            #Exit the setup return to factory default
            return write_net_config
        else:
            logger.sys_info("Net config file written.")

    #restart postgres
    logger.sys_info('Restarting postgres.')
    pgsql_start = service.postgresql('restart')
    if(pgsql_start != 'OK'):
        #fire off revert
        return pgsql_start
    time.sleep(10)

    #restart keystone so neutron does not go nuts
    logger.sys_info('Restarting Keystone.')
    keystone_restart = service.keystone('restart')
    if(keystone_restart != 'OK'):
        #fire off revert
        return keystone_restart
    time.sleep(10)


    logger.sys_info('Setting OpenStack networking configs and bridges.')
    out = subprocess.Popen('ipcalc -p %s %s'%(sys_vars['UPLINK_IP'],sys_vars['UPLINK_SUBNET']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process = out.stdout.readlines()
    cidr = process[0].split("=")
    os.system("sudo ip addr add %s/%s dev br-ex" %(sys_vars['UPLINK_IP'],cidr[1].rstrip()))

    #add the internal bridge
    logger.sys_info("Adding br-int")
    os.system("sudo ovs-vsctl add-br br-int")

    #add IP tables entries for new bridge - Grizzly only Havanna will do this automatically
    #logger.sys_info("Setting up iptables entries.")
    #os.system("sudo iptables -A FORWARD -i bond1 -o br-ex -s 172.12.24.0/24 -m conntrack --ctstate NEW -j ACCEPT")
    #os.system("sudo iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")
    #os.system("sudo iptables -A POSTROUTING -s 172.12.24.0/24 -t nat -j MASQUERADE")
    #os.system("sudo iptables -t mangle -A POSTROUTING -o br-ex -p udp -m udp --dport 68 -j CHECKSUM --checksum-fill")

    logger.sys_info("Saving the iptables entries.")
    os.system("sudo iptables-save > /transcirrus/iptables.conf")

    #after neutron enabled create the default_public ip range
    #check to make sure default public is the same range as the uplink ip
    logger.sys_info("Building the uplink network")
    public_dict = {'uplink_ip':sys_vars['UPLINK_IP'],'public_start':sys_vars['VM_IP_MIN'],'public_end':sys_vars['VM_IP_MAX'],'public_subnet':sys_vars['UPLINK_SUBNET']}
    pub_check = util.check_public_with_uplink(public_dict)
    if(pub_check != 'OK'):
        logger.sys_error('The public network given does not match the uplink subnet.')
        return pub_check

    #if in the same range create the default public range in neutron/neutron
    pg_accept = 1
    while pg_accept != 0:
        time.sleep(1)
        logger.sys_info('Sleeping until postgres accepts connections.')
        pg_accept = os.system('netstat -lnp | grep 5432')
    logger.sys_info('Postgres accepting connections on port 5432.')
    time.sleep(10)

    #HACK
    neutron_start = service.neutron('restart')
    if(neutron_start != 'OK'):
        #fire off revert
        return neutron_start
    time.sleep(10)

    heat_start = service.heat('restart')
    if(heat_start != 'OK'):
        #fire off revert
        return heat_start
    time.sleep(10)

    logger.sys_info('Creating Neutron Connection.')
    neu_net = neutron_net_ops(auth_dict)
    p_create_dict = {'net_name':'DefaultPublic','admin_state':'true','shared':'false'}
    default_public = neu_net.add_public_network(p_create_dict)
    if('net_id' not in default_public):
        logger.sys_error("Could not create the default public network.")
        return 'ERROR'
    else:
        #add the new public net to the sys_vars_table
        def_array = [{'system_name': sys_vars['NODE_NAME'],'parameter':'default_pub_net_id', 'param_value':default_public['net_id']}]
        update_def_pub_net = util.update_system_variables(def_array)
        if((update_def_pub_net == 'ERROR') or (update_def_pub_net == 'NA')):
            logger.sys_error("Could not update the default public network id, Setup has failed.")
            return 'ERROR'

    #create a subnet in the public network. Subnet ip range must be on the same subnet as the uplink IP
    #or the vms will not be able to reach the outside.
    time.sleep(1)
    logger.sys_info('Creating the DefaultPublic network..')
    s_create_dict = {
                     'net_id': default_public['net_id'],
                     'subnet_dhcp_enable':'true',
                     'subnet_dns':[sys_vars['UPLINK_DNS']],
                     'subnet_start_range':sys_vars['VM_IP_MIN'],
                     'subnet_end_range':sys_vars['VM_IP_MAX'],
                     'public_ip':sys_vars['UPLINK_IP'],
                     'public_gateway':sys_vars['UPLINK_GATEWAY'],
                     'public_subnet_mask':sys_vars['UPLINK_SUBNET']
                     }
    default_pub_subnet = neu_net.add_public_subnet(s_create_dict)
    if('subnet_id' not in default_pub_subnet):
        logger.sys_error("Could not create the default public subnet.")
        return 'ERROR'
    else:
        def_sub_array = [{'system_name': sys_vars['NODE_NAME'],'parameter':'default_pub_subnet_id', 'param_value':default_pub_subnet['subnet_id']}]
        update_def_pub_subnet = util.update_system_variables(def_sub_array)
        if((update_def_pub_subnet == 'ERROR') or (update_def_pub_subnet == 'NA')):
            logger.sys_error("Could not update the default public network id, Setup has failed.")
            return 'ERROR'

    #build the net content array
    net_content = ['DEFAULT_PUB_NET_ID="%s"'%(default_public['net_id']),'DEFAULT_PUB_SUBNET_ID="%s"'%(default_pub_subnet['subnet_id'])]

    #build the new config.py file
    netconfig_dict = {'file_path':'/usr/local/lib/python2.7/transcirrus/common',
                   'file_name':'config.py',
                   'file_content':net_content,
                   'file_owner':'transuser',
                   'file_group':'transystem',
                   'file_perm':'644',
                   'op':'append'
                   }

    write_net_config = util.write_new_config_file(netconfig_dict)
    if(write_net_config != 'OK'):
        logger.sys_error("Could not write network setting to the config file.")

    #add ext net id to neutron l3agent.conf
    os.system('sudo chmod 664 /etc/neutron/l3_agent.ini')
    time.sleep(1)
    os.system('sudo echo "gateway_external_network_id = %s" >> /etc/neutron/l3_agent.ini'%(default_public['net_id']))

    #if the node is set as multinode, enable multinode
    #if(sys_vars['SINGLE_NODE'] == '0'):
    #    status = node_util.enable_multi_node()
    #    if(status != 'OK'):
    #        logger.sys_error("Could not enable multi-node. Check the interface and try again.")
    #    else:
    #        logger.sys_info("Multi-node configuration enabled.")

    logger.sys_info("Restarting the uplink network adapter.")
    card_restart = util.restart_network_card("br-ex")
    if(card_restart == 'OK'):
        logger.sys_info("Uplink has been restarted.")
        os.system('sudo /transcirrus/promisc')

    #add the spindle and SSD vol types
    volumes = volume_ops(auth_dict)
    ssd = volumes.create_volume_type("ssd")
    
    spindle = volumes.create_volume_type("spindle")

    #add the volume backings
    ssd_input = {"volume_type_id":"%s"%(ssd['volume_type_id']),"volume_backend_name":"ssd"}
    spindle_input = {"volume_type_id":"%s"%(spindle['volume_type_id']),"volume_backend_name":"spindle"}
    ssd_back = volumes.assign_volume_type_to_backend(ssd_input)
    if(ssd_back == 'ERROR'):
        logger.sys_error("Could not assign the backing to the ssd volume type.")
        return 'ERROR'
    else:
        logger.sys_info("Volume type SSD added to the backings")

    spindle_back = volumes.assign_volume_type_to_backend(spindle_input)
    if(spindle_back == 'ERROR'):
        logger.sys_error("Could not assign the backing to the spindle volume type.")
        return 'ERROR'
    else:
        logger.sys_info("Volume type spindle added to the backings")

    #setup the pre-installed images
    logger.sys_info('Importing Default images.')
    glance = glance_ops(auth_dict)
    logger.sys_info('Importing Cirros image.')
    cirros_input = {
                    'image_name':"Cirros-x86_64-0-3-1",
                    'image_disk_format':"qcow2",
                    'image_is_public':'True',
                    'image_is_protected':'True',
                    'project_id':auth_dict['project_id'],
                    'file_location':"/transcirrus/cirros-0.3.1-x86_64-disk.img"
                    }
    import_cirros = glance.import_image(cirros_input)
    if(import_cirros != 'OK'):
        logger.sys_warning('Could not import the default cirros image.')
    else:
        logger.sys_info("Added the cirros image.")

    logger.sys_info('Importing Ubuntu 12.04 image.')
    ubuntu_input = {
                    'image_name':"Ubuntu-12-04-x86_64",
                    'image_disk_format':"qcow2",
                    'image_is_public':'True',
                    'image_is_protected':'True',
                    'project_id':auth_dict['project_id'],
                    'file_location':"/transcirrus/precise-server-cloudimg-amd64-disk1.img"
                    }
    import_ubuntu = glance.import_image(ubuntu_input)
    if(import_ubuntu != 'OK'):
        logger.sys_warning('Could not import the default Ubuntu Precise image.')
    else:
        logger.sys_info("Added the ubuntu image.")

    logger.sys_info('Importing CentOS 6.5 image.')
    fedora_input = {
                    'image_name':"CentOS-65-x86_64",
                    'image_disk_format':"qcow2",
                    'image_is_public':'True',
                    'image_is_protected':'True',
                    'project_id':auth_dict['project_id'],
                    'file_location':"/transcirrus/centos-6.5-20140117.0.x86_64.qcow2"
                    }
    import_fedora = glance.import_image(fedora_input)
    if(import_fedora != 'OK'):
        logger.sys_warning('Could not import the default Fedora image.')
    else:
        logger.sys_info("Added the CentOS 6.5 image.")

    #set the first time boot flag
    #first_boot = node_util.set_first_time_boot('UNSET')
    #if(first_boot == 'ERROR'):
    #    logger.sys_error("Could not set the first time boot flag to the UNSET status.")
    #else:
    #    logger.sys_info("First time boot flag unset.")

    #logger.sys_info("Restarting all services")

    #restart all of the services and return the statuses
    #checkpoint = restart_services()
    #checkpoint['status'] = 'OK'
    #print checkpoint
    #logger.sys_info("Service status: %s"%(checkpoint))
    return 'OK'

def check_setup():
    pass

def get_setup_results():
    pass

