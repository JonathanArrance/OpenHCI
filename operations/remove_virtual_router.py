#!/usr/local/bin/python2.7
from fnmatch import fnmatch
from vpn_manager import delete_vpn_tunnel

import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.common.logger as logger

from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.neutron.vpn import vpn_ops

def remove_virt_router(auth_dict, input_dict):
    """
    DESC: List the routers that are present in a project.
    INPUT: input_dict - project_id
                      - router_id
            auth_dict - authentication
    OUTPUT: 'OK' - success
            'ERROR' - fail
    ACCESS: Admins can remove a router from any project, power users can only remove a router from their own project.
            If any networks are attached an error will occure.
    NOTE: none
    """
    vo = vpn_ops(auth_dict)
    lto = layer_three_ops(auth_dict)

    #list the vpn tunnels in the project and find the ones attached to the router in question.
    tunnels = vo.list_vpn_service(input_dict['project_id'])
    if(len(tunnels['vpnservices']) >= 1):
        for tunnel in tunnels['vpnservices']:
            logger.sys_info('Deleting vpn tunnel %s'%(tunnel['id']))
            if(tunnel['router_id'] == input_dict['router_id']):
                delete_vpn_tunnel(auth_dict, input_dict['project_id'], tunnel['id'])
    else:
        logger.sys_info('No VPNaaS tunnels present.')

    #remove the router
    del_router = lto.delete_router(input_dict)

    return del_router