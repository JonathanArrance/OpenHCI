from celery import Celery
from celery import task

import transcirrus.common.util as util
import transcirrus.common.logger as logger

from transcirrus.common.service_control import service_controller
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
@celery.task(name='initial_setup')
def run_setup(new_system_variables,auth_dict,admin_pass):
    #create a sevice controller object
    controller = service_controller(auth_dict)
    endpoint = endpoint_ops(auth_dict)

    #call tasks/change_admin_user_password
    result = change_admin_password.delay(auth_dict,admin_pass)
    #check the status of the task_id
    if(result.status != 'SUCCESS'):
        raise "Could not chnage the admin password, initial setup has failed."

    #add all of the new value from the interface into the db
    update_sys_vars = util.update_system_variables(new_system_variables)
    if((update_sys_vars == 'ERROR') or (update_sys_vars == 'NA')):
        logger.sys_error("Could not update the system variables, Setup has failed.")
        raise Exception("Could not update the system variables, Setup has failed.")

    #get the current system settings
    #retrieve the node_id from the config file before it is rewritten.
    node_id = util.get_node_id()
    sys_vars = util.get_system_variables(node_id)
    if(sys_vars == 'NA'):
        logger.sys_error("Could not retrieve the system_variables.")
        raise Exception("Could not retrieve the system_variables.")

    #build the new config.py file
    config_dict = {'file_path':'/usr/local/lib/python/dist-packages/transcirrus/common/',
                   'file_name':'config.py',
                   'file_content':sys_vars,
                   'file_owner':'transuser',
                   'file_group':'transystem',
                   'file_perm':'644'}
    write_config = util.write_new_config_file(config_dict)

    #reset the keystone endpoint
    key_input = {'service_name':'keystone'}
    del_keystone = endpoint.delete_endpoint(key_input)
    if(del_keystone == 'OK'):
        input_dict = {'cloud_name':sys_vars['cloud_name'],'service_name':'keystone'}
        create_keystone = endpoint.create_endpoint(input_dict)
        if(create_keystone['endpoint_id']):
            print "Keystone endpoint set up complete."
        else:
            return "Keystone error."

    #set up all of the other endpoint based on the new mgmt IP address
    nova_input_dict = {'cloud_name':sys_vars['cloud_name'],'service_name':'nova'}
    create_nova = endpoint.create_endpoint(nova_input_dict)
    if(create_nova['endpoint_id']):
        print "Nova endpoint set up complete."
    else:
        return "Nova error."
    cinder_input_dict = {'cloud_name':sys_vars['cloud_name'],'service_name':'cinder'}
    create_cinder = endpoint.create_endpoint(cinder_input_dict)
    if(create_cinder['endpoint_id']):
        print "Cinder endpoint set up complete."
    else:
        return "Cinder error."
    glance_input_dict = {'cloud_name':sys_vars['cloud_name'],'service_name':'glance'}
    create_glance = endpoint.create_endpoint(glance_input_dict)
    if(create_glance['endpoint_id']):
        print "Glance endpoint set up complete."
    else:
        return "Glance error."
    quantum_input_dict = {'cloud_name':sys_vars['cloud_name'],'service_name':'quantum'}
    create_quantum = endpoint.create_endpoint(quantum_input_dict)
    if(create_quantum['endpoint_id']):
        print "Quantum endpoint set up complete."
    else:
        return "Quantum error."
    swift_input_dict = {'cloud_name':sys_vars['cloud_name'],'service_name':'swift'}
    create_swift = endpoint.create_endpoint(swift_input_dict)
    if(create_glance['endpoint_id']):
        print "Swift endpoint set up complete."
    else:
        return "Swift error."
'''
    #enable nova
    #write the nova config files
    nova_configs = node_db.get_node_nova_config(node_id)
    #take the array of nova file decriptors and write the files
    for config in nova_configs:
        write_nova_config = util.write_new_config_file(config)
        if(write_nova_config != 'OK'):
            #Exit the setup return to factory default
            return 'ERROR'
        else:
            print "Nova config file written."
    #start the NOVA service
    nova_start = controller.nova(restart)
'''
    #enable cinder

    #enable glance

    #enable quantum

    #after quantum enabled create the default_public ip range

def check_setup():
    pass

def get_setup_results():
    pass

