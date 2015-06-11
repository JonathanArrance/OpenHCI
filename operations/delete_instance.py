#!/usr/local/bin/python2.7
import transcirrus.common.logger as logger
import transcirrus.common.util as util
import transcirrus.common.config as config

from transcirrus.component.nova.server import server_ops
from transcirrus.component.nova.server_action import server_actions
from transcirrus.component.nova.storage import server_storage_ops
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.cinder.cinder_volume import volume_ops

def delete_instance(auth_dict, delete_dict):
    """
    DESC: Deletes a virtual server. Users can only delete the servers they own.
          Admins can delete any server in their project.
    INPUT:  auth_dict
            delete_dict - server_id - REQ
                        - project_id - REQ
                        - delete_boot_vol -OP (True/False)
    OUTPUT: OK if deleted or error
    NOTE: If the delete_boot_vol is not set default is False, if it is set and there is no boot vol
          then nothing will happen. 
    """
    logger.sys_info('\n**Deleteing an instance. Component: Operations: delete_instance**\n')
    nova = server_ops(auth_dict)
    sa = server_actions(auth_dict)
    layer_three = layer_three_ops(auth_dict)
    server_storage = server_storage_ops(auth_dict)
    cinder = volume_ops(auth_dict)
    db = util.db_connect()
    remove_server = {}

    snaps = sa.list_instance_snaps(delete_dict['server_id'])
    if(len(snaps) > 0):
        raise Exception("Instance snapshots must be deleted.")

    #if the flag not set default to false
    if('delete_boot_vol' not in delete_dict):
        delete_dict['delete_boot_vol'] = 'false'
    elif(delete_dict['delete_boot_vol'] == None):
        delete_dict['delete_boot_vol'] = 'false'

    #normalize input
    raw = delete_dict['delete_boot_vol']
    delete_boot_vol = raw.lower()

    #remove the volumes attached to the instance.
    try:
        get_vols = {'select':'vol_id,vol_set_bootable','from':'trans_system_vols','where':"vol_attached_to_inst='%s'"%(delete_dict['server_id'])}
        vols = db.pg_select(get_vols)
    except:
        logger.sys_error("Volume could not be found.")
        raise Exception("Volume could not be found.")
    #this will have to be forked some how, maybe use rabbit to run in the back ground.
    boot_vol = []
    remove_server['vols'] = vols
    if(vols):
        for vol in vols:
            #do not detach the boot vol if it is bootable
            if(vol[1] == 'false'):
                vol_dict = {'project_id':delete_dict['project_id'] ,'instance_id': delete_dict['server_id'],'volume_id':vol[0]}
                server_storage.detach_vol_from_server(vol_dict)
            else:
                boot_vol = vol

    #remove the floating ips from the instance
    try:
        get_float_id = {'select':'floating_ip_id','from':'trans_instances','where':"inst_id='%s'"%(delete_dict['server_id'])}
        floater = db.pg_select(get_float_id)
    except:
        logger.sys_error("Floating ip id could not be found.")
        raise Exception("Floating ip id could not be found.")

    if(floater):
        try:
            get_float_ip = {'select':'floating_ip','from':'trans_floating_ip','where':"floating_ip_id='%s'"%(floater[0][0])}
            floatip = db.pg_select(get_float_ip)
        except:
            logger.sys_error("Floating ip could not be found.")
            raise Exception("Floating ip could not be found.")

        if(len(floatip) >= 1):
            float_dict = {'project_id':delete_dict['project_id'] ,'instance_id': delete_dict['server_id'],'floating_ip':floatip[0][0],'action':'remove'}
            layer_three.update_floating_ip(float_dict)

        remove_server['floating_ip_id'] = floater
        remove_server['floating_ip'] = floatip

    #finally remove the server(Instance)
    remove_server['delete'] = nova.delete_server(delete_dict)

    #if booted from vol and flag set
    if(len(boot_vol) >= 1):
        #This is a HACK to get around a bug in ICEHOUSE: It is in regards to deleteing a volume that a vm was booted from:
        #the instance gets deleted however the volme does not and stays in the in-use state. The solution was found here
        #http://www.florentflament.com/blog/openstack-volume-in-use-although-vm-doesnt-exist.html
        from transcirrus.database.postgres import pgsql
        try:
            #use util.close_db when you no longer need o have the connection open.
            #Try to connect to the transcirrus db
            cin = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,'cinder',config.TRAN_DB_USER,config.TRAN_DB_PASS)
            logger.sql_info("Connected to the Cinder DB to set bootable volume to available.")
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
            raise e

        try:
            update = {'table':"volumes",'set':"status='available',attach_status='detached',mountpoint=NULL,instance_uuid=NULL",'where':"id='%s'" %(boot_vol[0])}
            cin.pg_transaction_begin()
            cin.pg_update(update)
        except:
            cin.pg_transaction_rollback()
        else:
            cin.pg_transaction_commit()
            cin.pg_close_connection()

        if(delete_boot_vol == 'true'):
            #delete the volume
            delete_vol={'volume_id':boot_vol[0],'project_id':delete_dict['project_id']}
            cinder.delete_volume(delete_vol)
        elif(delete_boot_vol == 'false'):
            try:
                update2 = {'table':"trans_system_vols",'set':"vol_attached='false',vol_attached_to_inst=NULL,vol_mount_location=NULL",'where':"vol_id='%s'" %(boot_vol[0])}
                db.pg_transaction_begin()
                db.pg_update(update2)
            except:
                db.pg_transaction_rollback()
            else:
                db.pg_transaction_commit()
                db.pg_close_connection()

    return remove_server