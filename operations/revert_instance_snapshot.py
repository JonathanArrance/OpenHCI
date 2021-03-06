#!/usr/bin/python2.7
import sys
import json
import time
import random

from delete_instance import delete_instance
import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.component.nova.error as ec
from transcirrus.component.nova.server import server_ops
from transcirrus.component.nova.storage import server_storage_ops
from transcirrus.component.nova.server_action import server_actions
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops

def revert_inst_snap(input_dict,auth_dict):
    """
    DESC: Revert to an earlier instance state from a snapshot.
    INPUTS: input_dict - snapshot_id - snapshot to revert from- REQ
                       - instance_id - instance you want to revert - REQ
                       - project_id - the project you are working in - REQ
    OUTPUTS: r_dict of new instance info
    ACCESS: Admins can revert any instance
            PU - can revert instances from snapshots in their project
            Users - can only revert instances they own with snapshots they own
    NOTE: You can not create two volumes with the same name in the same project.
    """
    logger.sys_info('\n**Revet to instance snapshot. Component: Operations: revert_inst_snap**\n')
    glance = glance_ops(auth_dict)

    net = neutron_net_ops(auth_dict)
    sa = server_actions(auth_dict)
    server = server_ops(auth_dict)
    storage = server_storage_ops(auth_dict)
    three = layer_three_ops(auth_dict)
    rannum = random.randrange(1000,9000)

    if(input_dict['snapshot_id'] == "" or 'snapshot_id' not in input_dict):
        logger.sys_error('Snapshot id is required to revert an instance snapshot.')
        raise Exception('Snapshot id is required to revert an instance snapshot.')

    if(input_dict['instance_id'] == "" or 'instance_id' not in input_dict):
        logger.sys_error('Instance id is required to revert an instance snapshot.')
        raise Exception('Instance id is required to revert an instance snapshot.')

    if(input_dict['project_id'] == "" or 'project_id' not in input_dict):
        logger.sys_error('Project id is required to revert an instance snapshot.')
        raise Exception('Project id is required to revert an instance snapshot.')

    #get the "snapshot" image info
    snap_input = {'snapshot_id':input_dict['snapshot_id'],'project_id':input_dict['project_id']}
    inst_snap_info = sa.get_instance_snap_info(snap_input)

    #get the instance info
    inst_input = {'server_id':input_dict['instance_id'],'project_id':input_dict['project_id']}
    inst_info = server.get_server(inst_input)

    #check to see if snap and inst are in the same project
    if(inst_info['project_id'] != inst_snap_info['project_id']):
        logger.sys_error('Instance and Snapshot are not in the same project.')
        raise Exception('Instance and Snapshot are not in the same project.')

    #get the network name the instance is attached to
    network = net.get_network(inst_info['server_net_id'])

    #get the volumes attached if any
    att_dict = {'instance_id':inst_info['server_id'],'project_id':input_dict['project_id']}
    attached = storage.list_attached_vols(att_dict)

    # You may wonder why in the hell we have a sleep here! That is a good damn question!!
    # After a lot of trial and error, this is the location I found. The problem is this:
    # If a user creates a snapshot and then immediately tries to revert it, the REST call
    # to create_server errors with a 400 (image not ready) error. BUT you can't wait before
    # that call, you have to wait all the way back here. The other option is to put the wait
    # in create_inst_snapshot but I decided to put it here. If you put the wait after the
    # call to delete_instance (below), it won't work! Very f'ing strange!!
    time.sleep(30)

    #delete original instance
    del_input = {'project_id':input_dict['project_id'],'server_id':inst_info['server_id']}
    del_instance = delete_instance(auth_dict,del_input)

    #Should we just power off original instance? This would prevent 400 errors if the new reverted instance did not boot, however the reverted instance would not be able to have the
    #original name since the original instance still exisits in the system. Maybe we can leverage the Nova rename API call? Rename the new instance after the original is deleted.
    #pow_input = {'project_id':input_dict['project_id'],'server_id':inst_info['server_id'],'power_state':'off'}
    #power_instance = sa.server_power_control(pow_input)

    time.sleep(2)

    #create a new virtual machine with the snapshot image anf the info from the original instance
    logger.sys_info('Createing a new instance from snapshot %s'%(input_dict['snapshot_id']))
    create_dict = {'project_id':input_dict['project_id'],
                   'instance_name': inst_info['server_name'],
                   'sec_group_name':inst_info['server_group_name'],
                   'sec_key_name': inst_info['server_key_name'],
                   'avail_zone':inst_info['server_zone'],
                   'network_name': network['net_name'],
                   'image_name': inst_snap_info['snapshot_name'],
                   'image_id': inst_snap_info['snapshot_id'],
                   'flavor_name': inst_info['server_flavor'],
                   'flavor_id': inst_info['flavor_id'],
                   'name': inst_info['server_name']
    }
    create = server.create_server(create_dict)

    #We could delete the original only after we are sure the new instance is created and then rename the new instance to the original name.
    #if('vm_id' in create):
    #    #remove the original vm if new vm created
    #    del_input = {'project_id':input_dict['project_id'],'server_id':inst_info['server_id']}
    #    del_instance = delete_instance(auth_dict,del_input)
    # rename new reverted instance
    #    sa.rename_instance(blah)

    #    time.sleep(5)

    #add back the float ip
    if(inst_info['server_public_ips'] == 'None'):
        logger.sys_info("Instance %s does not have a floating ip."%(inst_info['server_name']))
    else:
        assign_dict = {'floating_ip':inst_info['server_public_ips'],'instance_id': create['vm_id'],'project_id':input_dict['project_id'],'action':'add'}
        assign = three.update_floating_ip(assign_dict)

    #reattach the volumes
    if(len(attached) >= 1):
        for vol in attached:
            attach = {'project_id':input_dict['project_id'],'instance_id':create['vm_id'],'volume_id':vol['vol_id'],'mount_point':vol['vol_mount_location']}
            att_vol = storage.attach_vol_to_server(attach)

    r_dict = {'instance':create,'volumes':attached,'network':network}
    return r_dict
