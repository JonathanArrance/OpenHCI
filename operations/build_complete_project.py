import transcirrus.common.logger as logger
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.nova.server import server_ops
from transcirrus.component.neutron.layer_three import layer_three_ops


def build_complete_project(auth_dict, proj_dict):
    """
    DESC: Build complete project.
    INPUT: auth_dict
           proj_dict - proj_name - req
                     - user_dict - username - req
                                 - password - req
                                 - userrole - must be "pu"
                                 - email - req
                                 - project_id - leave NULL
                     - net_name - req
                     - subnet_dns - req
                     - sec_group_dict - ports[] - op
                                      - group_name - req
                                      - group_desc - req
                                      - project_id - leave NULL
                     - sec_keys_name - req
                     - router_name - req
    OUTPUT:
    ACCESS:
    NOTES:
    """
    tenant = tenant_ops(auth_dict)
    logger.sys_info("Instantiated tenat_ops object")
    user = user_ops(auth_dict)
    logger.sys_info("Instantiated user_ops object")
    neutron_net = neutron_net_ops(auth_dict)
    logger.sys_info("Instantiated neutron_net_ops object")
    nova = server_ops(auth_dict)
    logger.sys_info("Instantiated server_ops object")
    neutron_router = layer_three_ops(auth_dict)
    logger.sys_info("Instantiated layer_three_ops object")

    proj = tenant.create_tenant(proj_dict['proj_name'])
    logger.sys_info("Created project with project name: %s") %(proj_dict['proj_name'])

    user_dict['project_id'] = proj['tenant_id']
    pu = user.create_user(proj_dict['user_dict'])
    logger.sys_info("Created power user named %s for project named %s ") %(proj_dict['user_dict']['username'])

    net_dict = {'net_name': proj_dict['net_name'],'admin_state':"true", 'shared':"true",'project_id':proj['tenant_id']}
    net = neutron_net.add_private_network(net)
    logger.sys_info("Created private netowrk with net name: %s") %(proj_dict['net_name'])

    subnet_dict = {'net_id': net['net_id'],'subnet_dhcp_enable':'true','subnet_dns': proj_dict['subnet_dns']}
    subnet = neutron_net.add_net_subnet(subnet_dict)
    logger.sys_info("Created subnet with subnet dns: %s") %(proj_dict['subnet_dns'])

    proj_dict['sec_group_dict']['project_id'] = proj['tenant_id']
    sec_group = nova.create_sec_group(proj_dict['sec_group_dict'])
    logger.sys_info("Created security group")

    sec_keys_dict = {'key_name': proj_dict['sec_keys_name'], 'project_id': proj['tenant_id']}
    sec_keys = nova.create_sec_keys(sec_keys_dict)
    logger.sys_info("Created security keys")

    router_dict = {'router_name': proj_dict['router_name'], 'project_id': proj['tenant_id']}
    router = neutron_router.add_router(router_dict)
    logger.sys_info("Created router with router name: %s") %(proj_dict['router_name'])

    inside_port_dict = {'router_id': router['router_id'], 'subnet_name': subnet['subnet_name'], 'project_id': proj['tenant_id']}
    inside_port = neutron_router.add_router_internal_interface(inside_port_dict)
    logger.sys_info("Created router internal interface")

    ext_net_dict = neutron_net.list_external_networks()
    for net in ext_net_dict:
        if(net['net_name'] == "DefaultPublic"):
            ext_net_id = net['net_id']
            break

    outside_port_dict = {'router_id': router['router_id'], 'ext_net_id': ext_net_id}
    outside_port = neutron_router.add_router_gateway_interface(outside_port_dict)
    logger.sys_info("Created router gateway")