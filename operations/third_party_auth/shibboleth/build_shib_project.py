#!/usr/local/bin/python2.7
import transcirrus.common.logger as logger
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.nova.server import server_ops
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.nova.quota import quota_ops
from transcirrus.component.neutron.admin_actions import admin_ops

def build_project(auth_dict, project_dict):
    """
    DESC: Build complete project.
    INPUT: auth_dict
           project_dict - project_name - req
                     - user_dict - username - req
                                 - password - req
                                 - user_role - must be "admin"
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
                     - advanced_ops - quota - op
    OUTPUT:
    ACCESS:
    NOTE:
    """
    tenant = tenant_ops(auth_dict)
    logger.sys_info("Instantiated tenant_ops object")
    user = user_ops(auth_dict)
    logger.sys_info("Instantiated user_ops object")

    proj = None
    r_user = None
    net = None
    router = None
    subnet = None
    ext_net_id = None
    try:
        proj = tenant.create_tenant(project_dict['project_name'])
        logger.sys_info("Created project with project name: %s" % project_dict['project_name'])
    except Exception as e:
        logger.sys_error("Couldn't create a project, %s" %(str(e)))

    # List out the current cloud users
    cloud_users = user.list_orphaned_users()
    x = []
    for y in cloud_users:
        x.append(y['username'])

    userset = set(x)
    #If the user specifed already exists and is not attached to another project just add him to the project as adminr.
    if('%s'%(project_dict['user_dict']['username']) in userset):
        try:
            user_dict = {'username': project_dict['user_dict']['username'],'user_role': 'admin','project_id': proj}
            user.add_user_to_project(user_dict)
            r_user_info_dict = {'username': project_dict['user_dict']['username'], 'project_name': project_dict['project_name']}
            r_user_info = user.get_user_info(r_user_info_dict)
            r_user = {'username': r_user_info['username'], 'user_id': r_user_info['user_id'], 'project_id': r_user_info['project_id']}
        except Exception as e:
            logger.sys_error("Couldn't add an existing project admin to the project, %s" %(str(e)))
    else:
        #If the user does not exist create a new project power user.
        try:
            project_dict['user_dict']['project_id'] = proj
            r_user = user.create_user(project_dict['user_dict'])
            logger.sys_info("Created project admin named %s for project named %s " % (project_dict['user_dict']['username'], project_dict['project_name']))
        except Exception as e:
            logger.sys_error("Couldn't create a project admin for the project, %s" %(str(e)))
    
    a = authorization(project_dict['user_dict']['username'], project_dict['user_dict']['password'])
    auth = a.get_auth()
    neutron_net = neutron_net_ops(auth)
    logger.sys_info("Instantiated neutron_net_ops object")
    nova = server_ops(auth)
    logger.sys_info("Instantiated server_ops object")
    neutron_router = layer_three_ops(auth)
    logger.sys_info("Instantiated layer_three_ops object")

    try:
        net_dict = {'net_name': project_dict['net_name'],'admin_state':"true", 'shared':"false",'project_id':proj}
        net = neutron_net.add_private_network(net_dict)
        logger.sys_info("Created private netowrk with net name: %s" % project_dict['net_name'])
    except Exception as e:
        logger.sys_error("Couldn't create a private network, %s" %(str(e)))

    try:
        subnet_dict = {'net_id': net['net_id'],'subnet_dhcp_enable':'true','subnet_dns': project_dict['subnet_dns']}
        subnet = neutron_net.add_net_subnet(subnet_dict)
        logger.sys_info("Created subnet with subnet dns: %s" % project_dict['subnet_dns'])
    except Exception as e:
        logger.sys_error("Couldn't create a subnet, %s" %(str(e)))

    try:
        ports = ['22','80','443','3389']
        project_dict['sec_group_dict']['project_id'] = proj
        project_dict['sec_group_dict']['ports'] = ports
        sec_group = nova.create_sec_group(project_dict['sec_group_dict'])
        logger.sys_info("Created security group")
    except Exception as e:
        logger.sys_error("Couldn't create a security group, %s" %(str(e)))

    try:
        sec_keys_dict = {'key_name': project_dict['sec_keys_name'], 'project_id': proj}
        sec_keys = nova.create_sec_keys(sec_keys_dict)
        logger.sys_info("Created security keys")
    except Exception as e:
        logger.sys_error("Couldn't create security keys, %s" %(str(e)))

    try:
        router_dict = {'router_name': project_dict['router_name'], 'project_id': proj}
        router = neutron_router.add_router(router_dict)
        logger.sys_info("Created router with router name: %s" % project_dict['router_name'])
    except Exception as e:
        logger.sys_error("Couldn't create a router, %s" %(str(e)))
        
    try:
        inside_port_dict = {'router_id': router['router_id'], 'subnet_id': subnet['subnet_id'], 'project_id': proj}
        inside_port = neutron_router.add_router_internal_interface(inside_port_dict)
        logger.sys_info("Created router internal interface")
    except Exception as e:
        logger.sys_error("Couldn't create a router internal interface, %s" %(str(e)))

    try:
        ext_net_dict = neutron_net.list_external_networks()
        for ext_net in ext_net_dict:
            if(ext_net['net_name'] == "DefaultPublic"):
                ext_net_id = ext_net['net_id']
                break

        outside_port_dict = {'router_id': router['router_id'], 'ext_net_id': ext_net_id, 'project_id': proj}
        outside_port = neutron_router.add_router_gateway_interface(outside_port_dict)
        logger.sys_info("Created router gateway")
    except Exception as e:
        logger.sys_error("Couldn't create a router gateway, %s" %(str(e)))

    #advanced options
    if(('advanced_ops' in project_dict) and (project_dict['advanced_ops'] is not None)):
        qo = quota_ops(auth_dict)
        ao = admin_ops(auth_dict)

        try:
            proj_out = qo.update_project_quotas(project_dict['advanced_ops']['quota'])
            net_out = ao.update_net_quota(project_dict['advanced_ops']['quota'])
        except Exception as e:
            logger.sys_error("Could not add quotas to the bew project, %s" %(str(e)))

    return proj, r_user