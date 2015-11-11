#!/usr/local/lib/python2.7
# from celery import Celery
# from celery import task
# import rollback

import os
import time
import subprocess

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.node_util as node_util
import transcirrus.common.service_control as service
import transcirrus.ha.ha_common as ha_common

from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.keystone.keystone_endpoints import endpoint_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops
from transcirrus.component.cinder.cinder_volume import volume_ops

from transcirrus.database import node_db

# get the passed in vars
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


def run_setup(new_system_variables, auth_dict):
    null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)]
    # save the current file descriptors to a tuple
    save = os.dup(1), os.dup(2)
    # put /dev/null fds on 1 and 2
    os.dup2(null_fds[0], 1)
    os.dup2(null_fds[1], 2)

    # retrieve the node_id from the config file before it is rewritten.
    node_id = util.get_node_id()
    #node_name = util.get_system_name()
    #auth_dict['api_ip'] = util.get_api_ip()

    # new_cloud_name = new_system_variables['cloud_name']
    # get the original system vars from the DB - used in case we need to rollback
    # rollback_sys_vars = util.get_system_variables(node_id)

    # add all of the new value from the interface into the db
    logger.sys_info('SETUP0:Updating system variables...')
    update_sys_vars = util.update_system_variables(new_system_variables)

    if ((update_sys_vars == 'ERROR') or (update_sys_vars == 'NA')):
        logger.sys_error("Could not update the system variables, Setup has failed.")
        raise Exception("Could not update the system variables, Setup has failed.")

    # get the current system settings
    sys_vars = util.get_system_variables(node_id)

    if (sys_vars == 'NA'):
        logger.sys_error("Could not retrieve the system_variables.")
        # do the rollback procedure
        # rollback = util.update_system_variables(rollback_sys_vars)
        raise Exception("Could not retrieve the system_variables.")

    boot = node_util.check_first_time_boot()

    if (boot == 'FALSE'):
        logger.sys_info('SETUPERROR:System already set up')
        return "System already set up."

    # properly format the key values to an array.
    content = []
    for key, val in sys_vars.items():
        row = key + '=' + '"' + val + '"'
        content.append(row)

    logger.sys_info('SETUP1:Building the config.py file...')
    # build the new config.py file
    config_dict = {'file_path': '/usr/local/lib/python2.7/transcirrus/common',
                   'file_name': 'config.py',
                   'file_content': content,
                   'file_owner': 'transuser',
                   'file_group': 'transystem',
                   'file_perm': '644',
                   'op': 'new'
                   }

    write_config = util.write_new_config_file(config_dict)

    if (write_config != 'OK'):
        logger.sys_error("SETUPERROR:Could not write the new config file.")
        # Perform the rollback to the original values
        # rollback = util.update_system_variables(rollback_sys_vars)
        return "Could not write the new config file."

    # create an enpoint object
    endpoint = endpoint_ops(auth_dict)

    logger.sys_info('SETUP2:Building endpoints...')
    # Remove the comments when we support Swift
    ##logger.sys_info('SETUP2:Re-building Swift endpoints...')
    ### reset the swift
    ##del_swift = endpoint.delete_endpoint('swift')
    ##
    ##if (del_swift == 'OK'):
    ##    input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 'swift'}
    ##    create_swift = endpoint.create_endpoint(input_dict)
    ##
    ##    if (create_swift['endpoint_id']):
    ##        logger.sys_info("Swift endpoint set up complete.")
    ##    else:
    ##        logger.sys_error("Could not create Swift endpoint - %s, %s" % (input_dict, create_swift))
    ##        logger.sys_error("SETUPERROR:could not create Swift endpoint")
    ##        return "Swift error."

    logger.sys_info('SETUP3:Re-building Keystone endpoints...')
    # reset the keystone endpoint
    del_keystone = endpoint.delete_endpoint('keystone')
    if (del_keystone == 'OK'):
        input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 'keystone'}
        create_keystone = endpoint.create_endpoint(input_dict)
        if (create_keystone['endpoint_id']):
            logger.sys_info("SETUP4:Keystone endpoint set up complete...")
        else:
            logger.sys_error("Could not create Keystone endpoint - %s, %s" % (input_dict, create_keystone))
            logger.sys_error("SETUPERROR:could not create Keystone endpoint")
            return "Keystone error."

    logger.sys_info('SETUP5:Building Nova endpoints...')
    # set up all of the other endpoint based on the new mgmt IP address
    nova_input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 'nova'}
    create_nova = endpoint.create_endpoint(nova_input_dict)
    if (create_nova['endpoint_id']):
        logger.sys_info("SETUP6:Nova endpoint set up complete...")
    else:
        logger.sys_error("SETUPERROR:could not create Nova endpoint")
        return "Nova error."

    logger.sys_info('SETUP7:Building Cinder endpoints...')
    cinder_input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 'cinder'}
    create_cinder = endpoint.create_endpoint(cinder_input_dict)
    if (create_cinder['endpoint_id']):
        logger.sys_info("SETUP8:Cinder endpoint set up complete...")
    else:
        logger.sys_error("SETUPERROR:could not create cinder endpoint")
        return "Cinder error."

    logger.sys_info('SETUP9:Building Cinder V2 endpoints...')
    cinderv2_input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 'cinder_v2'}
    create_cinderv2 = endpoint.create_endpoint(cinderv2_input_dict)
    if (create_cinderv2['endpoint_id']):
        logger.sys_info("SETUP10:Cinder v2 endpoint set up complete...")
    else:
        logger.sys_error("SETUPERROR:could not create cinder v2 endpoint")
        return "Cinder V2 error."

    logger.sys_info('SETUP11:Building Glance endpoints...')
    glance_input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 'glance'}
    create_glance = endpoint.create_endpoint(glance_input_dict)
    if (create_glance['endpoint_id']):
        logger.sys_info("SETUP12:Glance endpoint set up complete...")
    else:
        logger.sys_error("SETUPERROR:could not create glance endpoint")
        return "Glance error."

    logger.sys_info('SETUP13:Building Neutron endpoints...')
    neutron_input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 'neutron'}
    create_neutron = endpoint.create_endpoint(neutron_input_dict)
    if (create_neutron['endpoint_id']):
        logger.sys_info("SETUP14:Neutron endpoint set up complete...")
    else:
        logger.sys_error("SETUPERROR:could not create neutron endpoint")
        return "Neutron error."

    logger.sys_info('SETUP15:Building Heat endpoints...')
    heat_input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 'heat'}
    create_heat = endpoint.create_endpoint(heat_input_dict)
    if (create_heat['endpoint_id']):
        logger.sys_info("SETUP16:Heat endpoint set up complete...")
    else:
        logger.sys_error("SETUPERROR:could not create heat endpoint")
        return "Heat error."

    logger.sys_info('SETUP17:Building Ceilometer endpoints...')
    ceil_input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 'ceilometer'}
    create_ceil = endpoint.create_endpoint(ceil_input_dict)
    if (create_ceil['endpoint_id']):
        logger.sys_info("SETUP18:Ceilometer endpoint set up complete...")
    else:
        logger.sys_error("SETUPERROR:could not create ceilometer endpoint")
        return "Ceilometer error."

    logger.sys_info('SETUP19:Building EC2 endpoints...')
    ec_input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 'ec2'}
    create_ec = endpoint.create_endpoint(ec_input_dict)
    if (create_ec['endpoint_id']):
        logger.sys_info("SETUP20:EC2 endpoint set up complete...")
    else:
        logger.sys_error("SETUPERROR:could not create EC2 endpoint")
        return "EC2 error."

    logger.sys_info('SETUP21:Building S3 endpoints...')
    s3_input_dict = {'cloud_name': sys_vars['CLOUD_NAME'], 'service_name': 's3'}
    create_s3 = endpoint.create_endpoint(s3_input_dict)
    if (create_s3['endpoint_id']):
        logger.sys_info("SETUP22:S3 endpoint set up complete...")
    else:
        logger.sys_error("SETUPERROR:could not create S3 endpoint")
        return "S3 error."

    logger.sys_info('SETUP23:Adding the core node to the trans_nodes table...')
    # insert the controller info into trans_nodes db table
    cc_insert_dict = {'node_id': node_id,
                      'node_name': sys_vars['NODE_NAME'],
                      'node_type': 'cc',
                      'node_mgmt_ip': sys_vars['MGMT_IP'],
                      'node_data_ip': '172.24.24.10',
                      'node_controller': sys_vars['CLOUD_CONTROLLER'],
                      'node_cloud_name': sys_vars['CLOUD_NAME'],
                      'avail_zone': 'nova',
                      'node_gluster_peer': '0',
                      'node_gluster_disks': 'ssd'}
    insert_cc = node_db.insert_node(cc_insert_dict)
    if (insert_cc != 'OK'):
        logger.sys_error("SETUPERROR:could not add core node to the trans_nodes table")
        return 'ERROR'

    # enable nova
    # write the nova config files
    logger.sys_info('SETUP24:Writing the Nova Config files...')
    nova_configs = node_db.get_node_nova_config(node_id)
    # take the array of nova file decriptors and write the files
    for config in nova_configs:
        write_nova_config = util.write_new_config_file(config)
        if (write_nova_config != 'OK'):
            # Exit the setup return to factory default
            logger.sys_error("SETUPERROR:could not write the Nova config files")
            return write_nova_config
        else:
            logger.sys_info("Nova config file written.")
    time.sleep(1)
    # HACK CentOS6.5 may not be needed in the future
    os.system("sudo usermod -G lock nova > /dev/null")
    os.system("sudo nova-manage db sync > /dev/null")
    time.sleep(1)
    # start the NOVA service
    nova_start = service.nova('restart')
    if (nova_start != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not start the Nova service")
        return nova_start

    # enable cinder
    logger.sys_info('SETUP25:Writing the Cinder Config files...')
    cinder_configs = node_db.get_node_cinder_config(node_id)
    # take the array of cinder file decriptors and write the files
    for config in cinder_configs:
        write_cinder_config = util.write_new_config_file(config)
        if (write_cinder_config != 'OK'):
            # Exit the setup return to factory default
            logger.sys_error("SETUPERROR:could not write the Cinder config files")
            return write_cinder_config
        else:
            logger.sys_info("Cinder config file written.")
    time.sleep(1)
    os.system("sudo cinder-manage db sync >> /dev/null")
    time.sleep(1)
    # start the cinder service
    cinder_start = service.cinder('restart')
    if (cinder_start != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not start the Cinder service")
        return cinder_start

    # enable glance
    logger.sys_info('SETUP26:Writing the Glance Config files...')
    glance_configs = node_db.get_glance_config()
    # take the array of cinder file decriptors and write the files
    for config in glance_configs:
        write_glance_config = util.write_new_config_file(config)
        if (write_glance_config != 'OK'):
            # Exit the setup return to factory default
            logger.sys_error("SETUPERROR:could not write the Glance config files")
            return write_glance_config
        else:
            logger.sys_info("Glance config file written.")
    # start the cinder service
    glance_start = service.glance('restart')
    if (glance_start != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not start the Glance service")
        return glance_start
    else:
        time.sleep(1)
        logger.sys_info("SETUP27:Syncing the Glance DB...")
        os.system("sudo glance-manage db_sync > /dev/null")
        # load default glance images shipped on ssd.

    # enable heat
    logger.sys_info('SETUP28:Writing the Heat Config files...')
    heat_configs = node_db.get_node_heat_config()
    # take the array of cinder file decriptors and write the files
    for config in heat_configs:
        write_heat_config = util.write_new_config_file(config)
        if (write_heat_config != 'OK'):
            # Exit the setup return to factory default
            logger.sys_error("SETUPERROR:could not write the Head config files")
            return write_heat_config
        else:
            logger.sys_info("Heat config file written.")
    heat_start = service.heat('restart')
    if (heat_start != 'OK'):
        logger.sys_error("SETUPERROR:could not start the Heat service")
        return heat_start
    else:
        time.sleep(1)
        logger.sys_info("SETUP29:Syncing the Heat DB...")
        os.system("sudo heat-manage db_sync > /dev/null")

    # enable ceilometer
    logger.sys_info('SETUP30:Adding ceilometer to mongo DB...')
    os.system('sudo mongo --host 172.24.24.10 ceilometer /transcirrus/mongo.js')
    logger.sys_info('SETUP31:Writing the Ceilometer Config files...')
    ceil_configs = node_db.get_node_ceilometer_config(node_id)
    # take the array of ceilometer file decriptors and write the files
    for config in ceil_configs:
        write_ceil_config = util.write_new_config_file(config)
        if (write_ceil_config != 'OK'):
            # Exit the setup return to factory default
            logger.sys_error("SETUPERROR:could not write the Ceilometer config files")
            return write_ceil_config
        else:
            logger.sys_info("Ceilometer config file written.")
    ceil_start = service.ceilometer('restart')
    if (ceil_start != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not start the Ceilometer service")
        return ceil_start

    # enable neutron
    logger.sys_info('SETUP32:Writing the Neutron Config files...')
    neu_configs = node_db.get_node_neutron_config(node_id)

    # take the array of cinder file decriptors and write the files
    for config in neu_configs:
        write_neutron_config = util.write_new_config_file(config)
        if (write_neutron_config != 'OK'):
            # Exit the setup return to factory default
            logger.sys_error("SETUPERROR:could not write the Neutron config files")
            return write_neutron_config
        else:
            logger.sys_info("Neutron config file written.")
    # HACK - centOS6.5 - may not be needed in future
    os.system('sudo ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini > /dev/null')
    os.system('sudo chown -R neutron:neutron /var/lib/neutron > /dev/null')
    # start the cinder service
    neutron_start = service.neutron('restart')
    if (neutron_start != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not start the Neutron service")
        return neutron_start

    logger.sys_info('SETUP33:Writing the network config files...')
    g_input = {'uplink_ip': sys_vars['UPLINK_IP'], 'uplink_gateway': sys_vars['UPLINK_GATEWAY'],
               'uplink_subnet': sys_vars['UPLINK_SUBNET']}
    gateway = util.check_gateway_in_range(g_input)
    if (gateway != 'OK'):
        logger.sys_error('SETUPERROR:the uplink gateway is not on the same subnet as the uplink ip.')
        return gateway

    resolve = {
        'dns_server1': sys_vars['UPLINK_DNS'],
        'search_domain_int': sys_vars['UPLINK_DOMAIN_NAME'],
        'search_domain_ext': sys_vars['MGMT_DOMAIN_NAME']
    }
    name_service = util.set_nameresolution(resolve)
    write_name_config = util.write_new_config_file(name_service)
    time.sleep(1)
    if (write_name_config != 'OK'):
        # Exit the setup return to factory default
        logger.sys_error("SETUPERROR:could not write the Name Service config file")
        return write_name_config
    else:
        logger.sys_info("SETUP34:Name service config file written...")

    # set up br-ex and enable ovs.
    uplink_dict = {
        'up_ip': sys_vars['UPLINK_IP'],
        'up_subnet': sys_vars['UPLINK_SUBNET'],
        'up_gateway': sys_vars['UPLINK_GATEWAY'],
    }

    mgmt_dict = {
        'mgmt_ip': sys_vars['MGMT_IP'],
        'mgmt_subnet': sys_vars['MGMT_SUBNET'],
        'mgmt_dhcp': 'static'
    }

    net_input = {'node_id': node_id,
                 'uplink_dict': uplink_dict,
                 'mgmt_dict': mgmt_dict
                 }

    links = util.set_network_variables(net_input)
    for link in links:
        write_net_config = util.write_new_config_file(link)
        time.sleep(1)
        if (write_net_config != 'OK'):
            # Exit the setup return to factory default
            logger.sys_error("SETUPERROR:could not write the Network config files")
            return write_net_config
        else:
            logger.sys_info("Net config file written.")

    # restart postgres
    logger.sys_info('SETUP35:Restarting postgres...')
    pgsql_start = service.postgresql('restart')
    if (pgsql_start != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not start the PgSQL service")
        return pgsql_start
    time.sleep(10)

    # restart keystone so neutron does not go nuts
    logger.sys_info('SETUP36:Restarting Keystone...')
    keystone_restart = service.keystone('restart')
    if (keystone_restart != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not restart the Keystone service")
        return keystone_restart
    time.sleep(10)

    logger.sys_info('SETUP37:Setting OpenStack networking configs and bridges...')
    out = subprocess.Popen('ipcalc -p %s %s' % (sys_vars['UPLINK_IP'], sys_vars['UPLINK_SUBNET']), shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process = out.stdout.readlines()
    cidr = process[0].split("=")
    os.system("sudo ip addr add %s/%s dev br-ex > /dev/null" % (sys_vars['UPLINK_IP'], cidr[1].rstrip()))
    logger.sys_info('SETUP38:OpenStack networking configs and bridges set up...')

    # add the internal bridge
    logger.sys_info("Adding br-int")
    os.system("sudo ovs-vsctl add-br br-int > /dev/null")

    logger.sys_info("SETUP39:Saving the iptables entries...")
    os.system("sudo iptables-save > /transcirrus/iptables.conf")

    # after neutron enabled create the default_public ip range
    # check to make sure default public is the same range as the uplink ip
    logger.sys_info("SETUP40:Building the uplink network...")
    public_dict = {'uplink_ip': sys_vars['UPLINK_IP'], 'public_start': sys_vars['VM_IP_MIN'],
                   'public_end': sys_vars['VM_IP_MAX'], 'public_subnet': sys_vars['UPLINK_SUBNET']}
    pub_check = util.check_public_with_uplink(public_dict)
    if (pub_check != 'OK'):
        logger.sys_error('SETUPERROR:The public network given does not match the uplink subnet.')
        return pub_check

    # if in the same range create the default public range in neutron/neutron
    pg_accept = 1
    while pg_accept != 0:
        time.sleep(1)
        logger.sys_info('SETUP41:Sleeping until postgres accepts connections...')
        pg_accept = os.system('netstat -lnp | grep 5432 > /dev/null')
    logger.sys_info('SETUP42:Postgres accepting connections on port 5432...')
    time.sleep(10)

    # HACK
    neutron_start = service.neutron('restart')
    if (neutron_start != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not start the Neutron service")
        return neutron_start
    time.sleep(10)

    heat_start = service.heat('restart')
    if (heat_start != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not restart the Heat service")
        return heat_start
    time.sleep(10)

    glance_start = service.glance('restart')
    if (glance_start != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not start the Glance service")
        return glance_start

    nova_start = service.nova('restart')
    if (nova_start != 'OK'):
        # fire off revert
        logger.sys_error("SETUPERROR:could not start the Nova service")
        return nova_start

    logger.sys_info('SETUP43:Creating Neutron Default Public Connection...')
    neu_net = neutron_net_ops(auth_dict)
    p_create_dict = {'net_name': 'DefaultPublic', 'admin_state': 'true', 'shared': 'false'}
    default_public = neu_net.add_public_network(p_create_dict)
    if ('net_id' not in default_public):
        logger.sys_error("SETUPERROR:Could not create the default public network.")
        return 'ERROR'
    else:
        # add the new public net to the sys_vars_table
        def_array = [{'system_name': sys_vars['NODE_NAME'], 'parameter': 'default_pub_net_id',
                      'param_value': default_public['net_id']}]
        update_def_pub_net = util.update_system_variables(def_array)
        if ((update_def_pub_net == 'ERROR') or (update_def_pub_net == 'NA')):
            logger.sys_error("SETUPERROR:Could not update the default public network id.")
            return 'ERROR'

    # create a subnet in the public network. Subnet ip range must be on the same subnet as the uplink IP
    # or the vms will not be able to reach the outside.
    time.sleep(1)
    logger.sys_info('SETUP44:Creating the DefaultPublic network...')
    s_create_dict = {
        'net_id': default_public['net_id'],
        'subnet_dhcp_enable': 'true',
        'subnet_dns': [sys_vars['UPLINK_DNS']],
        'subnet_start_range': sys_vars['VM_IP_MIN'],
        'subnet_end_range': sys_vars['VM_IP_MAX'],
        'public_ip': sys_vars['UPLINK_IP'],
        'public_gateway': sys_vars['UPLINK_GATEWAY'],
        'public_subnet_mask': sys_vars['UPLINK_SUBNET']
    }
    default_pub_subnet = neu_net.add_public_subnet(s_create_dict)
    if ('subnet_id' not in default_pub_subnet):
        logger.sys_error("SETUPERROR:Could not create the default public subnet.")
        return 'ERROR'
    else:
        def_sub_array = [{'system_name': sys_vars['NODE_NAME'], 'parameter': 'default_pub_subnet_id',
                          'param_value': default_pub_subnet['subnet_id']}]
        update_def_pub_subnet = util.update_system_variables(def_sub_array)
        if ((update_def_pub_subnet == 'ERROR') or (update_def_pub_subnet == 'NA')):
            logger.sys_error("SETUPERROR:Could not update the default public network id")
            return 'ERROR'

    # build the net content array
    net_content = ['DEFAULT_PUB_NET_ID="%s"' % (default_public['net_id']),
                   'DEFAULT_PUB_SUBNET_ID="%s"' % (default_pub_subnet['subnet_id'])]

    # build the new config.py file
    netconfig_dict = {'file_path': '/usr/local/lib/python2.7/transcirrus/common',
                      'file_name': 'config.py',
                      'file_content': net_content,
                      'file_owner': 'transuser',
                      'file_group': 'transystem',
                      'file_perm': '644',
                      'op': 'append'
                      }

    write_net_config = util.write_new_config_file(netconfig_dict)
    if (write_net_config != 'OK'):
        logger.sys_error("SETUPERROR:Could not write network settings to the config file.")
        return "Error"

    # add ext net id to neutron l3agent.conf
    os.system('sudo chmod 664 /etc/neutron/l3_agent.ini')
    time.sleep(1)
    os.system('sudo echo "gateway_external_network_id = %s" >> /etc/neutron/l3_agent.ini' % (default_public['net_id']))

    logger.sys_info("SETUP45:Restarting the Mgmt network adapter...")
    card_restart = util.restart_network_card("bond0")
    if (card_restart == 'OK'):
        logger.sys_info("SETUP46:Mgmt network adapter has been restarted...")
    else:
        logger.sys_warn("Mgmt adapter may not have been restarted.")

    logger.sys_info("SETUP47:Restarting the uplink network adapter...")
    card_restart = util.restart_network_card("br-ex")
    if (card_restart == 'OK'):
        logger.sys_info("SETUP48:Uplink network adapter has been restarted...")
        os.system('sudo /transcirrus/promisc')

    # add the spindle and SSD vol types
    volumes = volume_ops(auth_dict)
    ssd = volumes.create_volume_type("ssd")
    spindle = volumes.create_volume_type("spindle")

    # add the volume backings
    logger.sys_info('SETUP49:Setting up cloud storage...')
    ssd_input = {"volume_type_id": "%s" % (ssd['volume_type_id']), "volume_backend_name": "ssd"}
    spindle_input = {"volume_type_id": "%s" % (spindle['volume_type_id']), "volume_backend_name": "spindle"}
    ssd_back = volumes.assign_volume_type_to_backend(ssd_input)
    if (ssd_back == 'ERROR'):
        logger.sys_error("SETUPERROR:Could not assign the ssd volume backend type")
        return 'ERROR'
    else:
        logger.sys_info("Volume type SSD added to the backings")

    spindle_back = volumes.assign_volume_type_to_backend(spindle_input)
    if (spindle_back == 'ERROR'):
        logger.sys_error("SETUPERROR:Could not assign the spindle volume backend type")
        return 'ERROR'
    else:
        logger.sys_info("Volume type spindle added to the backings")

    # setup the pre-installed images
    logger.sys_info('SETUP50:Importing Default Glance images...')
    glance = glance_ops(auth_dict)
    logger.sys_info('SETUP51:Importing Cirros image...')
    cirros_input = {
        'image_name': "Cirros-x86_64-0-3-1",
        'container_format': "bare",
        'disk_format': "qcow2",
        'visibility': 'public',
        'image_type': 'image_file',
        'image_location': "/transcirrus/cirros-0.3.1-x86_64-disk.img",
        'os_type': "linux"
    }
    import_cirros = glance.import_image(cirros_input)
    if ('image_id' not in import_cirros):
        logger.sys_warning('Could not import the default cirros image.')
    else:
        logger.sys_info("SETUP:Added the cirros image...")

    logger.sys_info('SETUP52:Importing Ubuntu 12.04 image...')
    ubuntu_input = {
        'image_name': "Ubuntu-12-04-x86_64",
        'container_format': "bare",
        'disk_format': "qcow2",
        'visibility': 'public',
        'image_type': 'image_file',
        'image_location': "/transcirrus/precise-server-cloudimg-amd64-disk1.img",
        'os_type': "linux"
    }
    import_ubuntu = glance.import_image(ubuntu_input)
    if ('image_id' not in import_ubuntu):
        logger.sys_warning('Could not import the default Ubuntu Precise image.')
    else:
        logger.sys_info("SETUP:Added the Ubuntu 12.04 image...")

    logger.sys_info('SETUP53:Importing CentOS 6.5 image...')
    fedora_input = {
        'image_name': "CentOS-65-x86_64",
        'container_format': "bare",
        'disk_format': "qcow2",
        'visibility': 'public',
        'image_type': 'image_file',
        'image_location': "/transcirrus/centos-6.5-20140117.0.x86_64.qcow2",
        'os_type': "linux"
    }
    import_fedora = glance.import_image(fedora_input)
    if ('image_id' not in import_fedora):
        logger.sys_warning('Could not import the default Fedora image.')
    else:
        logger.sys_info("SETUP:Added the CentOS 6.5 image...")

    # set the first time boot flag
    first_boot = node_util.set_first_time_boot('UNSET')
    if(first_boot == 'ERROR'):
       logger.sys_error("Could not set the first time boot flag to the UNSET status.")
    else:
       logger.sys_info("First time boot flag unset.")

    # logger.sys_info("Restarting all services")

    # restart all of the services and return the statuses
    # checkpoint = restart_services()
    # checkpoint['status'] = 'OK'
    # print checkpoint
    # logger.sys_info("Service status: %s"%(checkpoint))
    os.system('sudo chmod 775 /var/lib/glance/images')
    os.system('source /home/transuser/factory_creds;openstack-status >> /transcirrus/first_time_status.txt')

    # restart rabbitmq using new hostname
    util.restart_rabbitmq()

    logger.sys_info("SETUP54:END")

    # restore file descriptors so I can print the results
    os.dup2(save[0], 1)
    os.dup2(save[1], 2)
    # close the temporary fds
    os.close(null_fds[0])
    os.close(null_fds[1])

    return 'OK'


def check_setup():
    pass


def get_setup_results():
    pass
