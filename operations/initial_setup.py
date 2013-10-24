from celery import Celery
from celery import task

import transcirrus.common.util as util
import transcirrus.common.logger as logger

from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.operations.change_adminuser_password import change_admin_password
from transcirrus.component.keystone.keystone_endpoints import endpoint_ops

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
    endpoint = endpoint_ops(auth_dict)
    key_input = {'service_name':'keystone'}
    del_keystone = endpoint.delete_endpoint(key_input)
    if(del_keystone == 'OK'):
        input_dict = {'cloud_name':sys_vars['cloud_name'],'service_name':'keystone'}
        create_keystone = endpoint.create_endpoint(input_keystone)
    
#undo and redo the keystone endpoint.

#set up all of the other endpoint based on the new mgmt IP address

#re-enable keystone

#enable nova

#enable cinder

#enable glance

#enable quantum

#after quantum enabled create the default_public ip range

def check_setup():
    pass

def get_setup_results():
    pass

