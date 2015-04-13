#!/usr/bin/python
import sys
import os
import subprocess
import time

import transcirrus.common.logger as logger
import transcirrus.common.util as util
import transcirrus.common.config as config
import transcirrus.common.service_control as service

def check_config_type():
    """
    DESC: Check the Transcirrus system DB and see if the system is set to be a single or multi node system
    INPUT: None
    OUTPUT: r_dict -config_type SINGLE
                                MULTI
                                HA
                                NA
                                ERROR
    ACCESS: Wide open
    NOTE: This function will only check the flag, you must call the enable_multi_node utility in
          order to enable the multi node functions. Conversely you must call disable_multi_node in
          order to set back to single node ciac set up.
    """
    db = util.db_connect()

    try:
        single = {'select':"param_value",'from':"trans_system_settings",'where':"parameter='single_node' and host_system='%s'" %(config.CLOUD_CONTROLLER)}
        nodeconfig = db.pg_select(single)
    except:
        logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
        r_dict = {'config_type':'ERROR'}

    r_dict = {}
    if(nodeconfig[0][0] == '1'):
        r_dict = {'config_type':'SINGLE'}
    elif(nodeconfig[0][0] == '0'):
        r_dict = {'config_type':'MULTI'}
    elif(nodeconfig[0][0] == '2'):
        r_dict = {'config_type':'HA'}
    else:
        r_dict = {'config_type':'NA'}

    return r_dict

def enable_multi_node():
    """
    DESC: Enable all of the multinode functionality in the system. This includes starting up dhcp
          enableing the data net adapter.
    INPUT: None
    OUTPUT: OK - success
            ERROR - fail
            NA - unknown
    ACCESS: Wide open
    NOTE: This function will implicitly check the single_node flag in the Transcirrus system db. The Data
          net is 100% controlled by Transcirrus, so all of the default info is in the Transcirrus DB to set up
          the adapter. This info will not change.
    """
    
    check = check_config_type()
    if(check['config_type'] == 'SINGLE'):
        db = util.db_connect()
        try:
            db.pg_transaction_begin()
            update_config = {'table':"trans_system_settings",'set':"param_value='0'",'where':"parameter='single_node'",'and':"host_system='%s'" %(config.CLOUD_CONTROLLER)}
            db.pg_update(update_config)
            #This may be a complete HACK need more research
            dhcp = service.dhcp_server('start')
            if (dhcp == 'OK'):
                db.pg_transaction_commit()
                db.pg_close_connection()
                logger.sys_info("DHCP is now runnig for multi-node setup configs.")
            else:
                return 'NA'
        except:
            db.pg_transaction_rollback()
            logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
            return 'ERROR'

        #turn on the network adapter for datanet
        #bond2 is always the datanet bond
        logger.sys_info("Bringing up Datanet.")
        ifconfig = util.enable_network_card('bond1')
        if(ifconfig == 'OK'):
            logger.sys_info("Datanet successfully brough up.")
            return 'OK'
        else:
            logger.sys_error("Datanet error: datanet interface did not come up.")
            return 'ERROR'
    else:
        logger.sys_error("The node does not appear to be in a single node setup conifg, make sure the system is set to single node")
        return 'ERROR'


def disable_multi_node():
    """
    DESC: Disable all of the multinode functionality in the system. This includes stoping dhcp
          and disableing the data net adapter.
    INPUT: None
    OUTPUT: OK - success
            ERROR - fail
            NA - unknown
    ACCESS: Wide open
    NOTE: This function will implicitly check the single_node flag in the Transcirrus system setting db.
    """
    check = check_config_type()
    if(check['config_type'] == 'MULTI'):
        db = util.db_connect()
        try:
            #isc-dhcp-server stop/waiting
            db.pg_transaction_begin()
            update_config = {'table':"trans_system_settings",'set':"param_value='1'",'where':"parameter='single_node'"}
            db.pg_update(update_config)
            dhcp = service.dhcp_server('stop')
            time.sleep(1)
            if (dhcp == 'OK'):
                db.pg_transaction_commit()
                db.pg_close_connection()
                logger.sys_info("DHCP is now off for single setup configs.")
            else:
                return 'NA'
        except:
            db.pg_transaction_rollback()
            logger_sql("Could not set the node back to single node. Returning ERROR.")
            return 'ERROR'
        
        #turn datanet network off
        logger.sys_info("Bringing down the Datanet")
        ifconfig = util.disable_network_card('bond1')
        if(ifconfig == 'OK'):
            logger.sys_info("Datanet successfully brought down.")
            return 'OK'
        else:
            logger.sys_error("Datanet could not be brought down")
            return 'ERROR'
    else:
        logger.sys_error("The node does not appear to be in a single node setup conifg, make sure the system is set to single node")
        return 'ERROR'

def enable_ha():
    print "not implemented"
    
def disable_ha():
    print "not implemented"

def check_first_time_boot():
    """
    DESC: Check to see if this is the "first" time the system has been booted so the
          user can be forced to setup. This is set back to 0 if the system is reset.
    INPUT: None
    OUTPUT: r_dict -first_time_boot TRUE
                                    FASLE
                                    NA
    ACCESS: Wide open
    NOTE: FALSE - system has been booted and set up, TRUE - system is new or freshly reset.
    """

    db = util.db_connect()

    r_dict = None
    try:
        single = {'select':"param_value",'from':"trans_system_settings",'where':"parameter='first_time_boot'", 'and':"host_system='%s'" %(config.CLOUD_CONTROLLER)}
        nodeconfig = db.pg_select(single)
    except:
        logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
        r_dict = {'first_time_boot':'ERROR'}

    if(nodeconfig[0][0] == '0'):
        r_dict = {'first_time_boot':'FALSE'}
    elif(nodeconfig[0][0] == '1'):
        r_dict = {'first_time_boot':'TRUE'}
    else:
        r_dict = {'first_time_boot':'NA'}

    db.pg_close_connection()
    return r_dict

def set_first_time_boot(set_flag):
    """
    DESC: Set the "first" time system boot flag in the Transcirrsu db.
    INPUT: SET/UNSET
    OUTPUT: r_dict -set_first_time_boot OK
                                        ERROR
                                        NA
    ACCESS: Wide open
    NOTE: SET - set the flag(new node/rollback) , UNSET - unset the flag(node already set up)
    """
    db = util.db_connect()

    r_dict = {}
    value = None

    if(set_flag == 'SET'):
        value = '1'
    elif(set_flag == 'UNSET'):
        value = '0'
    else:
        r_dict = {'first_time_boot':'NA'}

    try:
        db.pg_transaction_begin()
        update_config = {'table':"trans_system_settings",'set':"param_value='%s'" %(value),'where':"parameter='first_time_boot'",'and':"host_system='%s'" %(config.CLOUD_CONTROLLER)}
        db.pg_update(update_config)
        db.pg_transaction_commit()
        r_dict = {'first_time_boot':'OK'}
    except:
        db.pg_transaction_rollback()
        logger.sql_error("FIRST_TIME_BOOT_FLAG: Could not connect to the Transcirrus setting db to set . Returning ERROR.")
        r_dict = {'first_time_boot':'ERROR'}

    db.pg_close_connection()
    return r_dict

def check_admin_pass_status():
    """
    DESC: Check the flag to see if the admin pass has been changed from the default 'password' to something more secure.
    INPUT: None
    OUTPUT: r_dict -admin_pass_set TRUE
                                   FASLE
                                   NA
    ACCESS: Wide open
    NOTE: TRUE - admin password has been set, FALSE - admin pass is still default
    """
    db = util.db_connect()

    r_dict = {}
    try:
        single = {'select':"param_value",'from':"trans_system_settings",'where':"parameter='admin_pass_set'", 'and':"host_system='%s'" %(config.CLOUD_CONTROLLER)}
        nodeconfig = db.pg_select(single)
    except:
        logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
        r_dict = {'first_time_boot':'ERROR'}

    if(nodeconfig[0][0] == '1'):
        r_dict = {'admin_pass_set':'TRUE'}
    elif(nodeconfig[0][0] == '0'):
        r_dict = {'admin_pass_set':'FALSE'}
    else:
        r_dict = {'admin_pass_set':'NA'}

    db.pg_close_connection()
    return r_dict

def set_admin_pass_status(pass_flag):
    """
    DESC: Set the admin pass flag when the password is reset during setup in the Transcirrsu db.
    INPUT: SET/UNSET
    OUTPUT: r_dict -pass_flag OK
                              ERROR
                              NA
    ACCESS: Wide open
    NOTE: OK - admin pass flag has been set, ERROR - password flag could not be set.
    """
    db = util.db_connect()

    value = None
    r_dict = {}

    if(pass_flag == 'SET'):
        value = '1'
    elif(pass_flag == 'UNSET'):
        value = '0'
    else:
        r_dict = {'pass_flag_set':'NA'}

    try:
        db.pg_transaction_begin()
        update = {'table':"trans_system_settings",'set':"param_value='%s'" %(value),'where':"parameter='admin_pass_set'",'and':"host_system='%s'" %(config.CLOUD_CONTROLLER)}
        db.pg_update(update)
        db.pg_transaction_commit()
        r_dict = {'pass_flag_set':'OK'}
    except:
        db.pg_transaction_rollback()
        logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
        r_dict = {'pass_flag_set':'ERROR'}

    db.pg_close_connection()
    return r_dict

def set_node_ready_flag(node_id):
    """
    DESC: Set the node ready flag when the node is ready to use in the Transcirrsu db.
    INPUT: node_id
    OUTPUT: r_dict -ready_flag_set SET
                                   ERROR
    ACCESS: Wide open
    NOTE: SET - node ready flag has been set, ERROR - node ready could not be set.
    """
    db = util.db_connect()
    r_dict = {}

    try:
        db.pg_transaction_begin()
        update = {'table':"trans_nodes",'set':"node_ready_flag='SET'",'where':"node_id='%s'" %(node_id)}
        db.pg_update(update)
        db.pg_transaction_commit()
        r_dict = {'ready_flag_set':'SET'}
    except:
        db.pg_transaction_rollback()
        logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
        r_dict = {'ready_flag_set':'ERROR'}

    db.pg_close_connection()
    return r_dict
    
def clear_node_ready_flag(node_id):
    """
    DESC: Unset the node ready flag when the node is not ready to use in the Transcirrsu db.
          Can also be used to set the flag if there is an error during setup.
    INPUT: node_id
    OUTPUT: r_dict -ready_flag_set UNSET
                                   ERROR
    ACCESS: Wide open
    NOTE: UNSET - node ready flag has been unset, ERROR - node ready could not be set.
    """
    db = util.db_connect()
    r_dict = {}

    try:
        db.pg_transaction_begin()
        update = {'table':"trans_nodes",'set':"node_ready_flag='UNSET'",'where':"node_id='%s'" %(node_id)}
        db.pg_update(update)
        db.pg_transaction_commit()
        r_dict = {'ready_flag_set':'UNSET'}
    except:
        db.pg_transaction_rollback()
        logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
        r_dict = {'ready_flag_set':'ERROR'}

    db.pg_close_connection()
    return r_dict
    
def check_node_ready_flag(node_id):
    """
    DESC: Get the node ready flag in the Transcirrsu db.
    INPUT: None
    OUTPUT: r_dict -node_ready_set SET
                                   UNSET
                                   ERROR
                                   NA
    ACCESS: Wide open
    NOTE: SET - Node is ready to use, UNSET - Node not ready to use.
    """
    db = util.db_connect()
    r_dict = {}

    try:
        get = {'select':"node_ready_flag", 'from':"trans_nodes", 'where':"node_id='%s'" %(node_id)}
        get_flag = db.pg_select(get)
        if((get_flag[0][0] == '') or (get_flag[0][0] == 'NULL')):
            r_dict = {'ready_flag_set':'NA'}
        else:
            r_dict = {'ready_flag_set':'%s' %(get_flag[0][0])}
    except:
        logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
        r_dict = {'ready_flag_set':'ERROR'}

    db.pg_close_connection()
    return r_dict

def set_node_fault_flag(node_id):
    """
    DESC: Set the node fault flag when the node is ready to use in the Transcirrsu db.
    INPUT: node_id
    OUTPUT: r_dict -fault_flag_set SET
                                   ERROR
    ACCESS: Wide open
    NOTE: SET - node fault flag has been set, ERROR - node fault could not be set.
    """
    db = util.db_connect()
    r_dict = {}

    try:
        db.pg_transaction_begin()
        update = {'table':"trans_nodes",'set':"node_fault_flag='SET'",'where':"node_id='%s'" %(node_id)}
        db.pg_update(update)
        db.pg_transaction_commit()
        r_dict = {'fault_flag_set':'SET'}
    except:
        db.pg_transaction_rollback()
        logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
        r_dict = {'fault_flag_set':'ERROR'}

    db.pg_close_connection()
    return r_dict

def clear_node_fault_flag(node_id):
    """
    DESC: Unset the node falt flag when the node is not in a fault state in the Transcirrsu db.
    INPUT: node_id
    OUTPUT: r_dict -fault_flag_set UNSET
                                   ERROR
    ACCESS: Wide open
    NOTE: UNSET - node fault flag has been unset, ERROR - node ready could not be set.
    """
    db = util.db_connect()
    r_dict = {}

    try:
        db.pg_transaction_begin()
        update = {'table':"trans_nodes",'set':"node_fault_flag='UNSET'",'where':"node_id='%s'" %(node_id)}
        db.pg_update(update)
        db.pg_transaction_commit()
        r_dict = {'fault_flag_set':'UNSET'}
    except:
        db.pg_transaction_rollback()
        logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
        r_dict = {'fault_flag_set':'ERROR'}

    db.pg_close_connection()
    return r_dict

def check_node_fault_flag(node_id):
    """
    DESC: Get the node fault flag in the Transcirrsu db.
    INPUT: None
    OUTPUT: r_dict -node_fault_flag SET
                                    UNSET
                                    ERROR
                                    NA
    ACCESS: Wide open
    NOTE: SET - Node fault flag is set, UNSET - Node fault is not set.
    """
    db = util.db_connect()
    r_dict = {}

    try:
        get = {'select':"node_fault_flag", 'from':"trans_nodes", 'where':"node_id='%s'" %(node_id)}
        get_flag = db.pg_select(get)
        if((get_flag[0][0] == '') or (get_flag[0][0] == 'NULL')):
            r_dict = {'fault_flag_set':'NA'}
        else:
            r_dict = {'fault_flag_set':'%s' %(get_flag[0][0])}
    except:
        logger.sql_error("Could not connect to the Transcirrus setting db. Returning ERROR.")
        r_dict = {'ready_flag_set':'ERROR'}

    db.pg_close_connection()
    return r_dict

def get_all_storage_nodes():
    """
    DESC: Get all of the dedicated storage nodes in the cloud.
    INPUT: None
    OUTPUT: array of r_dict - sn_name
                            - sn_id
                            - sn_data_ip
    ACCESS: Wide open
    NOTE: none
    """
    db = util.db_connect()
    get_sn = {'select':'node_name,node_id,node_data_ip','from':'trans_nodes','where':"node_type='sn'"}
    nodes = db.pg_select(get_sn)
    r_array = []
    for node in nodes:
        r_dict = {'sn_name':node[0],'sn_id':node[1],'sn_data_ip':node[2]}
        r_array.append(r_dict)
    return r_array