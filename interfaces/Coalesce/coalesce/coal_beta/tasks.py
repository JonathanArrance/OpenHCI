from celery import task
from transcirrus.common.util import get_cloud_controller_name, update_system_variables
from transcirus.component.keystone.keystone_users import update_admin_password

@task()
def send_setup_info(management_ip, uplink_ip, vm_ip_min, vm_ip_max, cloud_name, single_node, admin_password):
    # call mortar script to setup the box
    print "calling box setup with the following parameters: %s | %s |%s |%s |%s |%s |%s" % (management_ip, uplink_ip, min_vm_ip, max_vm_ip,
                                                                                            cloud_name, single_node, admin_password)
    logger = send_setup_info.get_logger()
    logger.info("calling box setup with the following parameters: %s | %s |%s |%s |%s |%s |%s" % (management_ip, uplink_ip, min_vm_ip, max_vm_ip,
                                                                                         cloud_name, single_node, admin_password))

    system = get_cloud_controller_name()
    system_var_array = [
                        {"system_name": system, "parameter": "api_ip",          "parameter_value": management_ip},
                        {"system_name": system, "parameter": "mgmt_ip",         "parameter_value": management_ip},
                        {"system_name": system, "parameter": "admin_api_ip",    "parameter_value": management_ip},
                        {"system_name": system, "parameter": "int_api_id",      "parameter_value": management_ip},
                        {"system_name": system, "parameter": "uplink_ip",       "parameter_value": uplink_ip},
                        {"system_name": system, "parameter": "vm_ip_min",       "parameter_value": vm_ip_min},
                        {"system_name": system, "parameter": "vm_ip_max",       "parameter_value": vm_ip_max},
                        {"system_name": system, "parameter": "cloud_name",      "parameter_value": cloud_name},
                        {"system_name": system, "parameter": "single_node",     "parameter_value": single_node},
                        ]

    update_system_variables(system_var_array)
    #update_admin_password (admin_password)

    return "box setup complete"