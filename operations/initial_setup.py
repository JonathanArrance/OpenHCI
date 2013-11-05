#from celery import Celery
#from celery import task
#import rollback

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.node_util as node_util
import transcirrus.common.service_control as service

from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.operations.change_adminuser_password import change_admin_password
from transcirrus.component.keystone.keystone_endpoints import endpoint_ops
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
#@celery.task(name='initial_setup')
def run_setup(new_system_variables,auth_dict):
    #retrieve the node_id from the config file before it is rewritten.
    node_id = util.get_node_id()
    node_name = util.get_system_name()
    auth_dict['api_ip'] = util.get_api_ip()
    
    #get the original system vars from the DB - used in case we need to rollback
    #rollback_sys_vars = util.get_system_variables(node_id)

    #add all of the new value from the interface into the db
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
        row = key+"="+val
        content.append(row)

    #build the new config.py file
    config_dict = {'file_path':'/home/builder/common/',
                   'file_name':'config.py',
                   'file_content':content,
                   'file_owner':'transuser',
                   'file_group':'transystem',
                   'file_perm':'644',
                   'file_op':'new'
                   }

    write_config = util.write_new_config_file(config_dict)
    if(write_config != 'OK'):
        logger.sys_error("Could not write the new config file.")
        #Perform the rollback to the original values
        #rollback = util.update_system_variables(rollback_sys_vars)

    #create a sevice controller object
    endpoint = endpoint_ops(auth_dict)
    '''
    #reset the keystone endpoint
    key_input = {'service_name':'keystone'}
    del_keystone = endpoint.delete_endpoint(key_input)
    print del_keystone
    if(del_keystone == 'OK'):
        input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'keystone'}
        create_keystone = endpoint.create_endpoint(input_dict)
        if(create_keystone['endpoint_id']):
            print "Keystone endpoint set up complete."
        else:
            return "Keystone error."

    #set up all of the other endpoint based on the new mgmt IP address
    nova_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'nova'}
    create_nova = endpoint.create_endpoint(nova_input_dict)
    print create_nova
    if(create_nova['endpoint_id']):
        print "Nova endpoint set up complete."
    else:
        return "Nova error."
    cinder_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'cinder'}
    create_cinder = endpoint.create_endpoint(cinder_input_dict)
    print create_cinder
    if(create_cinder['endpoint_id']):
        print "Cinder endpoint set up complete."
    else:
        return "Cinder error."
    glance_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'glance'}
    create_glance = endpoint.create_endpoint(glance_input_dict)
    print create_glance
    if(create_glance['endpoint_id']):
        print "Glance endpoint set up complete."
    else:
        return "Glance error."
    quantum_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'quantum'}
    create_quantum = endpoint.create_endpoint(quantum_input_dict)
    print create_quantum
    if(create_quantum['endpoint_id']):
        print "Quantum endpoint set up complete."
    else:
        return "Quantum error."
    swift_input_dict = {'cloud_name':sys_vars['CLOUD_NAME'],'service_name':'swift'}
    create_swift = endpoint.create_endpoint(swift_input_dict)
    print create_swift
    if(create_glance['endpoint_id']):
        print "Swift endpoint set up complete."
    else:
        return "Swift error."

    #insert the controller info into trans_nodes db table
    cc_insert_dict = {'node_id':node_id,
                      'node_name':node_name,
                      'node_type':'cc',
                      'node_mgmt_ip':sys_vars['MGMT_IP'],
                      'node_data_ip':'172.38.24.10',
                      'node_controller':sys_vars['CLOUD_CONTROLLER'],
                      'node_cloud_name':sys_vars['CLOUD_NAME'],
                      'node_nova_zone':'nova',
                      'node_iscsi_iqn':'NULL'}
    insert_cc = node_db.insert_node(cc_insert_dict)
    if(insert_cc != 'OK'):
        return 'ERROR'

    #enable nova
    #write the nova config files
    nova_configs = node_db.get_node_nova_config(node_id)
    #take the array of nova file decriptors and write the files
    for config in nova_configs:
        write_nova_config = util.write_new_config_file(config)
        if(write_nova_config != 'OK'):
            #Exit the setup return to factory default
            return write_nova_config
        else:
            print "Nova config file written."
    #start the NOVA service
    nova_start = service.nova('restart')
    if(nova_start != 'OK'):
        #fire off revert
        return nova_start
    '''

    #enable cinder
    cinder_configs = node_db.get_node_cinder_config(node_id)
    #take the array of cinder file decriptors and write the files
    for config in cinder_configs:
        write_cinder_config = util.write_new_config_file(config)
        if(write_cinder_config != 'OK'):
            #Exit the setup return to factory default
            return write_cinder_config
        else:
            print "Cinder config file written."
    #start the cinder service
    cinder_start = service.cinder('restart')
    if(cinder_start != 'OK'):
        #fire off revert
        return cinder_start

    #enable glance
    glance_configs = node_db.get_node_glance_config(node_id)
    #take the array of cinder file decriptors and write the files
    for config in glance_configs:
        write_glance_config = util.write_new_config_file(config)
        if(write_glance_config != 'OK'):
            #Exit the setup return to factory default
            return 'ERROR'
        else:
            print "Glance config file written."
    #start the cinder service
    glance_start = service.glance('restart')

    #enable neutron
    neu_configs = node_db.get_node_neutron_config(node_id)
    #take the array of cinder file decriptors and write the files
    for config in neu_configs:
        write_neutron_config = util.write_new_config_file(config)
        if(write_neutron_config != 'OK'):
            #Exit the setup return to factory default
            return 'ERROR'
        else:
            print "Neutron config file written."
    #start the cinder service
    neutron_start = service.neutron('restart')

    #after quantum enabled create the default_public ip range

    #only restart the swift services. We will not write a config as of yet because of the complexity of swift.
    #this is pushed to alpo.1

    #if the node is set as multinode, enable multinode

    

    #call tasks/change_admin_user_password
    #result = change_admin_password.delay(auth_dict,admin_pass)
    #check the status of the task_id
    #if(result.status != 'SUCCESS'):
    #    raise "Could not chnage the admin password, initial setup has failed."

def check_setup():
    pass

def get_setup_results():
    pass

