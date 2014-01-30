import transcirrus.common.logger as logger
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.nova.server import server_ops
from transcirrus.component.neutron.layer_three import layer_three_ops


def destroy_project(auth_dict, proj_dict):
    """
    DESC: Destroy project.
    INPUT: auth_dict
           proj_dict - project_id - req
                     - project_name - req
                     - keep_users - req
    OUTPUT:
    ACCESS:
    NOTES:
    """
    tenant = tenant_ops(auth_dict)
    logger.sys_info("Instantiated tenant_ops object")
    user = user_ops(auth_dict)
    logger.sys_info("Instantiated user_ops object")
    neutron_net = neutron_net_ops(auth_dict)
    logger.sys_info("Instantiated neutron_net_ops object")
    nova = server_ops(auth_dict)
    logger.sys_info("Instantiated server_ops object")
    neutron_router = layer_three_ops(auth_dict)
    logger.sys_info("Instantiated layer_three_ops object")

    router_list = neutron_router.list_routers(proj_dict['project_id'])
    for router in router_list:
        router_dict = neutron_router.get_router(router['router_id'])
        remove_gateway = neutron_router.delete_router_gateway_interface(router_dict)
        if(remove_gateway == "OK"):
            logger.sys_info("Router %s gateway removed." % router_dict['router_id'])
        else:
            logger.sys_info("ERROR, Router %s gateway not removed." % router_dict['router_id'])
            return "ERROR"
        remove_internal_interface = neutron_router.delete_router_internal_interface(router_dict)
        if(remove_internal_interface == "OK"):
            logger.sys_info("Router %s internal interface removed." % router_dict['router_id'])
        else:
            logger.sys_info("ERROR, Router %s internal interface not removed." % router_dict['router_id'])
            return "ERROR"
        remove_router = neutron_router.delete_router(router_dict['router_id'])
        if(remove_router == "OK"):
            logger.sys_info("Router %s removed." % router_dict['router_id'])
        else:
            logger.sys_info("ERROR, Router %s not removed." % router_dict['router_id'])
            return "ERROR"

    sec_key_list = nova.list_sec_keys(proj_dict['project_id'])
    for sec_key in sec_key_list:
        #sec_key_dict = nova.get_sec_keys(sec_key['key_id'])
        #sec_key_dict['project_id'] = proj_dict['project_id']
        sec_key_dict = {'sec_key_name': sec_key['key_name'], 'project_id': proj_dict['project_id']}
        remove_sec_key = nova.delete_sec_keys(sec_key_dict)
        if(remove_sec_key == "OK"):
            logger.sys_info("sec_key %s removed." % sec_key_dict['sec_key_name'])
        else:
            logger.sys_info("ERROR, sec_key %s not removed." % sec_key_dict['sec_key_name'])
            return "ERROR"

    sec_group_list = nova.list_sec_group(proj_dict['project_id'])
    for sec_group in sec_group_list:
        sec_group['project_id'] = proj_dict['project_id']
        remove_sec_group = nova.delete_sec_group(sec_group)
        if(remove_sec_group == "OK"):
            logger.sys_info("sec_group %s removed." % sec_group['sec_group_name'])
        else:
            logger.sys_info("ERROR, sec_group %s not removed." % sec_group['sec_group_name'])
            return "ERROR"

    internal_network_list = neutron_net.list_internal_networks(proj_dict['project_id'])
    for network in internal_network_list:
        subnet_list = neutron_net.list_net_subnet(network['net_id'])
        for subnet in subnet_list:
            subnet['project_id'] = proj_dict['project_id']
            remove_subnet = neutron_net.remove_net_subnet(subnet)
            if(remove_subnet == "OK"):
                logger.sys_info("Subnet %s removed." % subnet['subnet_id'])
            else:
                logger.sys_info("ERROR, subnet %s not removed." % subnet['subnet_id'])
                return "ERROR"
        remove_network = neutron_net.remove_network(network)
        if(remove_network == "OK"):
                logger.sys_info("Network %s removed." % network['net_id'])
        else:
            logger.sys_info("ERROR, network %s not removed." % network['net_id'])
            return "ERROR"

    user_list = tenant.list_tenant_users(proj_dict['project_name'])
    for usr in user_list:
        if(proj_dict['keep_users']):
            usr['project_id'] = proj_dict['project_id']
            remove_user = user.remove_user_from_project(usr)
            if(remove_user == "OK"):
                logger.sys_info("User %s removed." % usr['user_id'])
            else:
                logger.sys_info("ERROR, user %s not removed." % usr['user_id'])
                return "ERROR"
        else:
            usr['userid'] = usr['user_id']
            remove_user = user.delete_user(usr)
            if(remove_user == "OK"):
                logger.sys_info("User %s deleted." % usr['user_id'])
            else:
                logger.sys_info("ERROR, user %s not deleted." % usr['user_id'])
                return "ERROR"

    remove_tenant = tenant.remove_tenant(proj_dict['project_name'])
    if(remove_tenant['status'] == "OK"):
        logger.sys_info("Project %s removed." % proj_dict['project_name'])
    else:
        logger.sys_info("ERROR, project %s not removed." % proj_dict['project_name'])
        return "ERROR"

    return "OK"
