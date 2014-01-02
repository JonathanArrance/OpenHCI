from celery import task
from transcirrus.operations.initial_setup import run_setup
from transcirrus.operations.change_adminuser_password import change_admin_password

@task()
def send_setup_info(management_ip, uplink_ip, vm_ip_min, vm_ip_max, uplink_dns, uplink_gateway, uplink_domain_name, uplink_subnet, mgmt_domain_name, mgmt_subnet, mgmt_dns, cloud_name, single_node, admin_password):
    # call mortar script to setup the box
    print "calling box setup with the following parameters: %s | %s |%s |%s |%s |%s |%s" % (management_ip, uplink_ip, min_vm_ip, max_vm_ip,
                                                                                            cloud_name, single_node, admin_password)
    #logger = send_setup_info.get_logger()
    #logger.info("calling box setup with the following parameters: %s | %s |%s |%s |%s |%s |%s" % (management_ip, uplink_ip, min_vm_ip, max_vm_ip,
                                                                                         #cloud_name, single_node, admin_password))
                                                                                         
    auth = request.session['auth']

    system = get_cloud_controller_name()
    system_var_array = [
                        {"system_name": system, "parameter": "api_ip",             "param_value": management_ip},
                        {"system_name": system, "parameter": "mgmt_ip",            "param_value": management_ip},
                        {"system_name": system, "parameter": "admin_api_ip",       "param_value": management_ip},
                        {"system_name": system, "parameter": "int_api_id",         "param_value": management_ip},
                        {"system_name": system, "parameter": "uplink_ip",          "param_value": uplink_ip},
                        {"system_name": system, "parameter": "vm_ip_min",          "param_value": vm_ip_min},
                        {"system_name": system, "parameter": "vm_ip_max",          "param_value": vm_ip_max},
                        {"system_name": system, "parameter": "cloud_name",         "param_value": cloud_name},
                        {"system_name": system, "parameter": "single_node",        "param_value": single_node},
                        {"system_name": system, "parameter": "uplink_dns",         "param_value": uplink_dns},
			{"system_name": system, "parameter": "uplink_gateway",     "param_value": "192.168.10.1"},
			{"system_name": system, "parameter": "uplink_domain_name", "param_value": "rtp.transcirrus.com"},
			{"system_name": system, "parameter": "uplink_subnet",      "param_value": "255.255.255.0"},
			{"system_name": system, "parameter": "mgmt_domain_name",   "param_value": "int.transcirrus.com"},
			{"system_name": system, "parameter": "mgmt_subnet",        "param_value": "255.255.255.0"},
			{"system_name": system, "parameter": "mgmt_dns",           "param_value": "8.8.8.8"},
                        ]

    run_setup(system_var_array, auth)
    change_admin_password (admin_password)

    return "box setup complete"