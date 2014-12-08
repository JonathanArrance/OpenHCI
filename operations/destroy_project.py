import transcirrus.common.logger as logger
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.neutron.network import neutron_net_ops
import transcirrus.operations.delete_server as ds
from transcirrus.component.nova.server import server_ops
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.component.cinder.cinder_snapshot import snapshot_ops


def destroy_project(auth_dict, project_dict):
    """
    DESC: Destroy project.
    INPUT: auth_dict
           project_dict - project_id - req
                        - project_name - req
                        - keep_users - req (boolean)
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
    cinder_vol = volume_ops(auth_dict)
    logger.sys_info("Instantiated volume_ops object")
    cinder_snap = snapshot_ops(auth_dict)
    logger.sys_info("Instantiated snapshot_ops object")

    #instances
    server_list = nova.list_servers(project_dict['project_id'])
    for server in server_list:
        input_dict = {'project_id': project_dict['project_id'], 'server_id': server['server_id']}
        remove_server = ds.delete_server(auth_dict, input_dict)
        if(remove_server['delete'] == "OK"):
            logger.sys_info("Destroy project: Server %s removed." % server['server_id'])
        else:
            logger.sys_error("Destroy project: Server %s not removed." % server['server_id'])
            #return "inst ERROR"
            raise Exception("Destroy project: Can not remove server %s."%(server['server_name']))

    #floating ips
    floating_ip_list = neutron_router.list_floating_ips(project_dict['project_id'])
    for floating_ip in floating_ip_list:
        floating_ip['project_id'] = project_dict['project_id']
        remove_floating_ip = neutron_router.deallocate_floating_ip(floating_ip)
        if(remove_floating_ip == "OK"):
            logger.sys_info("Destroy project: Floating IP %s deallocated." % floating_ip['floating_ip_id'])
        else:
            logger.sys_error("Destroy project: floating IP %s not deallocated." % floating_ip['floating_ip_id'])
            #return "fip ERROR"
            raise Exception("Destroy project: Can not deallocate floating ip %s."%(floating_ip_id))

    #snapshots
    snapshot_list = cinder_snap.list_snapshots(project_dict['project_id'])
    for snapshot in snapshot_list:
        snapshot_dict = {'snap_id': snapshot['snapshot_id'], 'project_id': project_dict['project_id']}
        remove_snapshot = cinder_snap.delete_snapshot(snapshot_dict)
        if(remove_snapshot == "OK"):
            logger.sys_info("Destroy project: Snapshot %s removed." % snapshot['snapshot_id'])
        else:
            logger.sys_error("Destroy project: snapshot %s not removed." % snapshot['snapshot_id'])
            return "snap ERROR"
            #raise Exception("Can not remove server %s from project %s."%(server['server_name'],project_dict['project_name']))

    #volumes
    volume_list = cinder_vol.list_volumes(project_dict['project_id'])
    for volume in volume_list:
        remove_volume = cinder_vol.delete_volume(volume)
        if(remove_volume == "OK"):
            logger.sys_info("Destroy project: Volume %s removed." % volume['volume_id'])
        else:
            logger.sys_error("Destroy project: volume %s not removed." % volume['volume_id'])
            #return "volume ERROR"
            raise Exception("Destroy project: Can not remove volume %s."%(volume['volume_name']))

    #object storage containers (future)

    #routers
    router_list = neutron_router.list_routers(project_dict['project_id'])
    for router in router_list:
        router_dict = neutron_router.get_router(router['router_id'])
        remove_gateway = neutron_router.delete_router_gateway_interface(router_dict)
        if(remove_gateway == "OK"):
            logger.sys_info("Destroy project: Router %s gateway removed." % router_dict['router_id'])
        else:
            logger.sys_error("Destroy project: Router %s gateway not removed." % router_dict['router_id'])
            #return "gateway ERROR"
            raise Exception("Destroy project: Can not remove gateway interface from router %s."%(router['router_name']))
        remove_internal_interface = neutron_router.delete_router_internal_interface(router_dict)
        if(remove_internal_interface == "OK"):
            logger.sys_info("Destroy project: Router %s internal interface removed." % router_dict['router_id'])
        else:
            logger.sys_error("Destroy project: Router %s internal interface not removed." % router_dict['router_id'])
            #return "internal interface ERROR"
            raise Exception("Destroy project: Can not remove internal interface from router %s."%(router['router_name']))
        del_dict = {'router_id': router_dict['router_id'],'project_id': project_dict['project_id']}
        remove_router = neutron_router.delete_router(del_dict)
        if(remove_router == "OK"):
            logger.sys_info("Router %s removed." % router_dict['router_id'])
        else:
            logger.sys_error("Destroy project: Router %s not removed." % router_dict['router_id'])
            #return "router ERROR"
            raise Exception("Destroy project: Can not remove router %s."%(router['router_name']))

    #security keys
    sec_key_list = nova.list_sec_keys(project_dict['project_id'])
    for sec_key in sec_key_list:
        #sec_key_dict = nova.get_sec_keys(sec_key['key_id'])
        #sec_key_dict['project_id'] = project_dict['project_id']
        sec_key_dict = {'sec_key_name': sec_key['key_name'], 'project_id': project_dict['project_id']}
        remove_sec_key = nova.delete_sec_keys(sec_key_dict)
        if(remove_sec_key == "OK"):
            logger.sys_info("Destroy project: sec_key %s removed." % sec_key_dict['sec_key_name'])
        else:
            logger.sys_error("Destroy project: sec_key %s not removed." % sec_key_dict['sec_key_name'])
            #return "sec_key ERROR"
            raise Exception("Destroy project: Can not remove security key %s."%(sec_key['key_name']))

    #security groups
    sec_group_list = nova.list_sec_group(project_dict['project_id'])
    for sec_group in sec_group_list:
        sec_group['project_id'] = project_dict['project_id']
        remove_sec_group = nova.delete_sec_group(sec_group)
        if(remove_sec_group == "OK"):
            logger.sys_info("Destroy project: sec_group %s removed." % sec_group['sec_group_name'])
        else:
            logger.sys_error("Destroy project: sec_group %s not removed." % sec_group['sec_group_name'])
            #return "sec_group ERROR"
            raise Exception("Destroy project: Can not remove security group %s."%(sec_group['sec_group_name']))

    #internal networks
    internal_network_list = neutron_net.list_internal_networks(project_dict['project_id'])
    for network in internal_network_list:
        subnet_list = neutron_net.list_net_subnet(network['net_id'])
        for subnet in subnet_list:
            subnet['project_id'] = project_dict['project_id']
            remove_subnet = neutron_net.remove_net_subnet(subnet)
            if(remove_subnet == "OK"):
                logger.sys_info("Destroy project: Subnet %s removed." % subnet['subnet_id'])
            else:
                logger.sys_error("Destroy project: subnet %s not removed." % subnet['subnet_id'])
                #return "subnet ERROR"
                raise Exception("Destroy project: Can not remove subnet %s."%(subnet['subnet_id']))
        remove_network = neutron_net.remove_network(network)
        if(remove_network == "OK"):
                logger.sys_info("Network %s removed." % network['net_id'])
        else:
            logger.sys_error("Destroy project: network %s not removed." % network['net_id'])
            #return "net ERROR"
            raise Exception("Destroy project: Can not remove network %s."%(network['net_id']))

    #users
    user_list = tenant.list_tenant_users(project_dict['project_id'])
    for usr in user_list:
        if(project_dict['keep_users']):
            usr['project_id'] = project_dict['project_id']
            remove_user = user.remove_user_from_project(usr)
            if(remove_user == "OK"):
                logger.sys_info("Destroy project: User %s removed." % usr['user_id'])
            else:
                logger.sys_error("Destroy project: user %s not removed." % usr['user_id'])
                #return "user ERROR"
                raise Exception("Destroy project: Can not remove user %s."%(usr['username']))
        else:
            usr['userid'] = usr['user_id']
            remove_user = user.delete_user(usr)
            if(remove_user == "OK"):
                logger.sys_info("Destroy project: User %s deleted." % usr['user_id'])
            else:
                logger.sys_error("Destroy project: user %s not deleted." % usr['user_id'])
                #return "user ERROR"
                raise Exception("Destroy project: Can not delete user %s."%(usr['username']))

    #tenant
    remove_tenant = tenant.remove_tenant(project_dict['project_id'])
    logger.sys_error('%s'%(remove_tenant))
    if(remove_tenant == "OK"):
        logger.sys_info("Destroy project: Project %s removed." % project_dict['project_id'])
    else:
        logger.sys_error("Destroy project: project %s not removed." % project_dict['project_id'])
        #return "tenant ERROR"
        raise Exception("Destroy project: Can not delete tenant %s."%(project_dict['project_name']))

    return "OK"