#!/usr/local/bin/python2.7
import transcirrus.common.logger as logger
import transcirrus.common.util as util

from transcirrus.component.nova.server import server_ops
from transcirrus.component.nova.storage import server_storage_ops
from transcirrus.component.neutron.layer_three import layer_three_ops

def delete_server(auth_dict, delete_dict):
    """
    DESC: Deletes a virtual server. Users can only delete the servers they own.
          Admins can delete any server in their project.
    INPUT:  auth_dict
            delete_dict - server_id
                        - project_id
    OUTPUT: OK if deleted or error
    """
    nova = server_ops(auth_dict)
    layer_three = layer_three_ops(auth_dict)
    server_storage = server_storage_ops(auth_dict)
    db = util.db_connect()

    #remove the volumes attached to the instance.
    try:
        get_vols = {'select':'vol_id','from':'trans_system_vols','where':"vol_attached_to_inst='%s'"%(delete_dict['server_id'])}
        vols = db.pg_select(get_vols)
    except:
        logger.sys_error("Volume could not be found.")
        raise Exception("Volume could not be found.")
    #this will have to be forked some how, maybe use qpid to run in the back ground.
    if(vols):
        for vol in vols:
            vol_dict = {'project_id':delete_dict['project_id'] ,'instance_id': delete_dict['server_id'],'volume_id':vol[0]}
            server_storage.detach_vol_from_server(vol_dict)

    #remove the floating ips from the instance
    try:
        get_float_id = {'select':'floating_ip_id','from':'trans_instances','where':"inst_id='%s'"%(delete_dict['server_id'])}
        floater = db.pg_select(get_float_id)
    except:
        logger.sys_error("Floating ip id could not be found.")
        raise Exception("Floating ip id could not be found.")
    try:
        get_float_ip = {'select':'floating_ip','from':'trans_floating_ip','where':"floating_ip_id='%s'"%(floater[0][0])}
        floatip = db.pg_select(get_float_ip)
    except:
        logger.sys_error("Floating ip could not be found.")
        raise Exception("Floating ip could not be found.")

    if(len(floatip) >= 1):
        float_dict = {'project_id':delete_dict['project_id'] ,'instance_id': delete_dict['server_id'],'floating_ip':floatip[0][0],'action':'remove'}
        layer_three.update_floating_ip(float_dict)

    #finally remove the server(Instance)
    remove_server = nova.delete_server(server_dict)

    return remove_server