#!/usr/bin/python
import sys
import os
import shutil
import subprocess
import datetime
import time

#from confparse import properties

import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.database.postgres import pgsql
from time import gmtime, strftime
from ifconfig import ifconfig
dhcp_retry=5
######Transcirrus utils#######

#DESC: Logs and rasies excpetions from the OpenStack REST API
#INPUT: code - https error code
#       reason - message from REST API
#OUTPUT: void
def http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")

def db_connect():
    try:
        #use util.close_db when you no longer need o have the connection open.
        #Try to connect to the transcirrus db
        db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")
    except Exception as e:
        logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
        raise

    return db

#DESC: used to clean up after the server class
#INPUT: self object
#OUTPUT: void
def db_close(db_obj):
    #close any open db connections
    db_obj.pg_close_connection()


def write_new_config_file(file_dict):
    """
    DESC: Write out a config file.
    INPUT: file_dict - file_path - req
                     - file_name - req
                     - file_content - array - req
                     - file_owner - req
                     - file_group - req
                     - file_perm - default 644
                     - file_op - new/append
    OUTPUT: A file written out to the proper location with the proper permissions
            raise exceptions on fail
            OK - file written
            ERROR - file not written
            NA - unknown
    ACCESS: wide open
    NOTES: Note the file permissions come in the bit format, ex. 644
           The defualt file permissions should be sufficient for any config
           file written. Default file operation is write. -Need to add the ability to append to a config file
    """
    #make sure none of the values are empty
    for key, val in file_dict.items():
        #skip over these
        if(key == 'file_permissions'):
            continue
        if(key == 'op'):
            continue
        if(val == ""):
            logger.sys_error("The value %s was left blank" %(val))
            #raise Exception("The value %s was left blank" %(val))
            return 'ERROR'
        if(key not in file_dict):
            logger.sys_error("Required info not specified for file creation.")
            #raise Exception ("Required info not specified for file creation.")
            return 'ERROR'

    permissions = None
    if(('file_permissions' not in file_dict) or (file_dict['file_permissions'])):
        permissions = '644'
    else:
        permissions = file_dict['file_permissions']

    #check if the config file exists in the file system
    path = []
    path.extend([file_dict['file_path'],file_dict['file_name']])
    fqp = "/".join(path)

    spath = []
    spath.extend(['/tmp',file_dict['file_name']])
    scratch = "/".join(spath)

    check_fqp = os.path.exists(fqp)
    config = None
    if(check_fqp == False):
        logger.sys_warning("The file %s does not exists, Creating..." %(fqp))
        os.system('sudo mkdir -p %s' %(file_dict['file_path']))
    else:
        logger.sys_warning("The file %s exists. Creating a backup and building new config." %(fqp))
        date = strftime("%Y-%m-%d", gmtime())
        old = '%s_%s' %(fqp,date)
        os.system('sudo cp -f %s %s' %(fqp,old))

    #decide if we append the scratch file or write it as
    #an entire new file
    ops = None
    config_new = None
    if('op' in file_dict):
        ops = file_dict['op'].lower()
        if(ops == 'new'):
            config = open(scratch, 'w')
        elif((ops == 'append') or (ops == 'update')):
            #need to add automation to move file prototype into place and append on new info
            config = open(fqp, 'r')
            config_new = open(scratch,'w')
    else:
        #config = open(scratch, 'w')
        logger.sys_error("No operation specified in the file descriptor.")
        return 'ERROR'

    #check that the array of lines is not empty
    if(len(file_dict['file_content']) == 0):
        logger.sys_warning("No file input was given. Can not write out the file %s." %(file_dict['file_name']))
        #raise Exception("No file input was given. Can not write out the file.")
        return 'ERROR'

    try:
        if(ops == 'new'):
            for line in file_dict['file_content']:
                config.write(line)
                config.write('\n')
            os.system('sudo mv %s %s' %(scratch,fqp))
            config.close()
            os.system('sudo rm -f %s' %(scratch))

        else:
            for line in config:
                #Set a flag to continue out of the inner loop
                flag = 0
                for x in file_dict['file_content']:
                    split = line.split('=')
                    split2 = x.split('=')
                    if(split[0].rstrip() == split2[0]):
                        flag = 1
                        config_new.write(line.replace(line,x))
                        config_new.write('\n')
                    else:
                        #this will not write new lines to the config file
                        #Enhancement needed to add that functionality.
                        #config_new.write(x)
                        #config_new.write('\n')
                        continue
                if(flag == 1):
                    continue
                else:
                    config_new.write(line)
            os.system('sudo mv %s %s' %(scratch,fqp))
            config.close()
            config_new.close()
            os.system('sudo rm -f %s' %(scratch))

        #set ownership
        os.system('sudo chown %s:%s %s' %(file_dict['file_owner'],file_dict['file_group'],fqp))

        #set permissions
        os.system('sudo chmod %s %s' %(file_dict['file_perm'],fqp))

    except IOError:
        config.close()
        config_new.close()
        #move the backup copy back to the original copy
        #shutil.move('%s_%s','%s') %(fqp,date,fqp)
        logger.sys_error("Could not write the config file at path %s" %(fqp))
        #raise Exception("Could not write the config file at path %s" %(fqp))
        return 'ERROR'

    #confirm the file was written and return OK if it was ERROR if not
    check_new_path = os.path.exists(fqp)
    if(check_new_path == True):
        return 'OK'
    elif(check_new_path == False):
        return 'ERROR'
    else:
        return 'NA'

def delete_config_file(file_dict):
    """
    DESC: Write out a config file.
    INPUT: file_dict - file_path
                     - file_name
                     - file_content
    OUTPUT: OK - file deleted
            ERROR - file could not be deleted
            NA - Unknown
    ACCESS: wide open
    NOTES: This will be used as part fo the cleanup procedure to set the system back to
           the factory state.
    """
    print "not implemented"

def insert_system_variables(input_array):
    """
    DESC: Used to take system variables in from the user interface and insert them into the
          Transcirrus system db where they are used for config_files. This is NOT the same
          thing as node config tables. This is for the overall system. These variables
          apply to the ciac node for the most part.
    INPUT: array of input_dict - system_name
                               - parameter
                               - param_value
    OUTPUT: OK - success
            ERROR - fail
    ACCESS: Wide open
    NOTE: This table is very extndable and we can add almost anythng we want in here.
          The input will look like this
          [{'system_name':"jon",parameter:"mgmt_ip",'param_value':"192.168.10.2"},{'system_name':"jon",parameter:"default_region",'param_value':"RegionOne"}]
    """
    for key, val in file_dict.items():
        #skip over these
        if(val == ""):
            logger.sys_error("The value %s was left blank" %(val))
            raise Exception("The value %s was left blank" %(val))
        if(key not in file_dict):
            logger.sys_error("Required info not specified for file creation.")
            raise Exception ("Required info not specified for file creation.")

    db = db_connect()

    for dictionary in input_array:
        try:
            db.pg_transaction_begin()
            insert = {"parameter":value['parameter'],"param_value":value['param_value'],'host_system':value['system_name']}
            db.pg_insert("trans_system_settings",insert)
            db.pg_transaction_commit()
            return 'OK'
        except:
            db.pg_transaction_rollback()
            logger.sgl_error("Could not insert system config into the Transcirrus db.")
            return 'ERROR'

def delete_system_variables(del_dict):
    """
    DESC: Used to delete a variable from the transcirrus systems settings db. This is mostly used when resetting a box to factory.
    INPUT:array of delete_dict - system_name
                               - parameter - op
                               - param_value - op
    OUTPUT: OK - success
            ERROR - fail
            NA - unknown
    ACCESS: Wide open
    NOTE: Note if only the system name is specified all values will be removed from the DB.
          The input will look like this
          [{'system_name':"jon",parameter:"mgmt_ip",'param_value':"192.168.10.2"},{'system_name':"jon",parameter:"default_region",'param_value':"RegionOne"}]
    """
    print "not implemented"

def update_system_variables(update_array):
    """
    DESC: Used to update a variable in the transcirrus systems settings db. 
    INPUT:array of update_dict - system_name
                               - parameter - op
                               - param_value - op
    OUTPUT: OK - success
            ERROR - fail
            NA - unknown
    ACCESS: Wide open
    NOTE: This call will only update system variables. Not the actual system name. YOu need to use update_cloud_controller_name() in order to change the
          cloud controller/ciac node name.
          The update input will look like this
          [{'system_name':"jon",parameter:"mgmt_ip",'param_value':"192.168.10.2"},{'system_name':"jon",parameter:"default_region",'param_value':"RegionOne"}]
    """
    #check if the input is an array
    if(len(update_array) == 0):
        logger.sys_warning("The input array did contain any values")
        return 'NA'

    db = db_connect()

    for value in update_array:
        for key,val in value.items():
            #skip over these
            if(val == ""):
                logger.sys_error("The value %s was left blank" %(val))
                raise Exception("The value %s was left blank" %(val))
            if(key == ""):
                logger.sys_error("The key was left blank")
                raise Exception("The key was left blank")
        if(('parameter' not in value) or ('param_value' not in value) or ('system_name' not in value)):
            logger.sys_error("Required info not specified for file creation.")
            raise Exception ("Required info not specified for file creation.")

        try:
            db.pg_transaction_begin()
            update = {'table':"trans_system_settings",'set':"param_value='%s'"%(value['param_value']),'where':"host_system='%s'" %(value['system_name']),'and':"parameter='%s'" %(value['parameter'])}
            db.pg_update(update)
            db.pg_transaction_commit()
        except:
            db.pg_transaction_rollback()
            logger.sgl_error("Could not insert system config into the Transcirrus db.")
            return 'ERROR'
    return 'OK'

def update_cloud_controller_name(update_dict):
    """
    DESC: Update the cloud controller name.
    INPUT: update_dict - old_name
                       - new_name
    OUTPUT: OK - success
            ERROR - fail
            NA - unknown
    ACCESS: Wide open
    NOTE: Update the cloud controller name on the physical system as well as in the various transcirrsus db tables.
          also regenerate the system config.py file.
    """
    for key,val in update_dict.items():
        #skip over these
        if(val == ""):
            logger.sys_error("The value %s was left blank" %(val))
            raise Exception("The value %s was left blank" %(val))
        if(key == ""):
            logger.sys_error("The key was left blank")
            raise Exception("The key was left blank")
        if((key == 'old_name') or (key == 'new_name')):
            logger.sys_info("The key was valid.")
        else:
            logger.sys_error("The key was invalid.")
            raise Exception("The key was invalid")

    #check if the old name is valid
    #update the host_system colum in the trans_system settings table

    db = db_connect()

    try:
        select_id = {'select':"param_value", 'from':"trans_system_settings", 'where':"parameter='cloud_controller_id'", 'and':"host_system='%s'"%(update_dict['old_name'])}
        nodeid = db.pg_select(select_id)
    except:
        logger.sql_error("Could not validate the cloud controller name.")
        return 'ERROR'

    #update the name in the trans_nodes table
    try:
        db.pg_transaction_begin()
        update_node = {'table':"trans_nodes",'set':"node_name='%s'" %(update_dict['new_name']),'where':"node_id='%s'" %(nodeid[0][0])}
        db.pg_update(update_node)

        update_node_con = {'table':"trans_nodes",'set':"node_controller='%s'" %(update_dict['new_name']),'where':"node_controller='%s'" %(update_dict['old_name'])}
        db.pg_update(update_node_con)

        update_name = {'table':"trans_system_settings",'set':"param_value='%s'" %(update_dict['new_name']),'where':"parameter='cloud_controller'"}
        db.pg_update(update_name)

        update_name = {'table':"trans_system_settings",'set':"host_system='%s'" %(update_dict['new_name']),'where':"host_system='%s'" %(update_dict['old_name'])}
        db.pg_update(update_name)

    except:
        db.pg_transaction_rollback()
        logger.sql_error("Could not update trans system settings table with new host system name.")
        return 'ERROR'
    finally:
        db.pg_transaction_commit()
        #disconnect from db
        db.pg_close_connection()

    #rewrite the default config.py file and save to transcirrus.common
    system_vars = get_system_variables(nodeid[0][0])

    #build a file descriptor for config.py
    #NODE - check quantum version make path based on that.

    config_array = []
    conf = {}
    for key,val in system_vars.items():
        row = key.upper()+"="+'"%s"'%(val)
        print row
        config_array.append(row)
    conf['op'] = 'new'
    conf['file_owner'] = 'transuser'
    conf['file_group'] = 'transystem'
    conf['file_perm'] = '644'
    conf['file_path'] = '/usr/local/lib/python2.7/dist-packages/transcirrus/common/'
    conf['file_name'] = 'config.py'
    conf['file_content'] = config_array

    #build the new config.py out
    write = write_new_config_file(conf)
    
    if(write == 'OK'):
        return 'OK'
    elif(write == 'ERORR'):
        return 'ERROR'
    else:
        return 'NA'


def get_cloud_controller_name():
    """
    DESC: get the cloud controller name from the transcirrus db
    INPUT: None
    OUTPUT: cloud_controller
    ACCESS: Wide open
    NOTE: The cloud controller is also the ciac node system name. These are human readable names. This
          is not the same as the node id.
    """
    '''
    db = db_connect()
    try:
        get_name = {'select':"param_value",'from':"trans_system_settings",'where':"parameter='default_cloud_controller'"}
        name = db.pg_select(get_name)
        r_dict = {'cloud_controller':name[0][0]}
    except:
        logger.sql_error("Could not retrieve cloud controller name from the Transcirrus db.")
        raise Exception("Could not retrieve cloud controller name from the Transcirrus db.")
    '''
    return config.CLOUD_CONTROLLER

def get_cloud_controller_id():
    """
    DESC: get the system name from the config.py file.
    INPUT: None
    OUTPUT: node_name
    ACCESS: Wide open
    NOTE: The cloud controller name and the system name on a ciac node will be the same.
    """
    return config.CLOUD_CONTROLLER_ID

def get_node_name():
    """
    DESC: get the node name from the config.py file.
    INPUT: None
    OUTPUT: node_name
    ACCESS: Wide open
    NOTE: node name is the factory default, which can be changed later.
    """
    return config.NODE_NAME

def get_node_id():
    """
    DESC: get the node id from the config.py file.
    INPUT: None
    OUTPUT: node_id
    ACCESS: Wide open
    NOTE: node id is the factory default unique which can NOT be changed later.
    """
    return config.NODE_ID

def get_node_type():
    """
    DESC: get the node type from the config.py file.
    INPUT: None
    OUTPUT: node type
    ACCESS: Wide open
    NOTE: node type may be compute(cn)/storage(sn)/hybrid(hd) and its a
    factory default
    """
    return config.NODE_TYPE

def get_api_ip():
    """
    DESC: get the system name from the config.py file.
    INPUT: None
    OUTPUT: node_name
    ACCESS: Wide open
    NOTE: The cloud controller name and the system name on a ciac node will be the same.
    """
    return config.API_IP

def get_cloud_name():
    """
    DESC: get the cloud name from the transcirrus db
    INPUT: None
    OUTPUT: cloud_name
    ACCESS: Wide open
    NOTE: The cloud controller is also the ciac node system name. These are human readable names.
          The cloud name is needed when setting up api endpoints.
    """
    '''
    db = db_connect()
    try:
        get_name = {'select':"param_value",'from':"trans_system_settings",'where':"parameter='cloud_name'"}
        name = db.pg_select(get_name)
        r_dict = {'cloud_name':name[0][0]}
    except:
        logger.sql_error("Could not retrieve cloud name from the Transcirrus db.")
        raise Exception("Could not retrieve cloud name from the Transcirrus db.")
    '''
    return config.CLOUD_NAME

def get_system_name():
    """
    DESC: get the system name from the config.py file.
    INPUT: None
    OUTPUT: node_name
    ACCESS: Wide open
    NOTE: The cloud controller name and the system name on a ciac node will be the same.
    """
    return config.NODE_NAME

def get_node_id():
    """
    DESC: get the system id from the config.py file.
    INPUT: None
    OUTPUT: node_name
    ACCESS: Wide open
    NOTE: The cloud controller id and the system id on a ciac node will be the same.
    """
    return config.NODE_ID

def get_system_defaults(node_id):
    """
    DESC: Return the system settings from the transcirrus system settings db.
    INPUT: system_name
    OUTPUT: r_dict - TRANSCIRRUS_DB
                   - TRAN_DB_USER
                   - TRAN_DB_PASS
                   - TRAN_DB_NAME
                   - TRAN_DB_PORT
                   - ADMIN_TOKEN
                   - API_IP - "public api ip"
                   - MGMT_IP
                   - INT_API_IP
                   - ADMIN_API_IP
                   - CLOUD_CONTROLLER
                   - CLOUD_CONTROLLER_ID
                   - CLOUD_NAME
                   - OS_DB
                   - OS_DB_USER
                   - OS_DB_PASS
                   - OS_DB_PORT
                   - MEMBER_ROLE_ID
                   - ADMIN_ROLE_ID
                   - NODE_ID
    ACCESS: Wide open
    NOTE: This returns the variables in regarding the transcirrus system. It is used for information and to create the
          config.py file descriptor to write out the config.py that is in transcirrus.common by calling write_new_config.py
    """
    if(node_id == ""):
        logger.sys_error("System node_id can not be blank when getting system variables.")
        raise Exception("System node_id can not be blank when getting system variables.")

    db = db_connect()
    #get the system name
    #try:
    #    get_sys_name = {'select':'host_system', 'from':'trans_system_settings','where':"parameter='node_id'", 'and':"param_value='%s'"%(node_id)}
    #    node_name = db.pg_select(get_sys_name)
    #except:
    #    logger.sql_error("Could not get the system name/node name for node id %s" %(node_id))
    #    raise Exception("Could not get the system name/node name for node id %s" %(node_id))

    node_name = get_system_name()
    try:
        find_node_dict = {'select':"parameter,param_value",'from':"factory_defaults",'where':"host_system='%s'" %(node_name)}
        sys = db.pg_select(find_node_dict)
    except:
        logger.sql_error("Could not find the system with name %s in the Transcirrus DB." %(system_name))
        return 'NA'
    db.pg_close_connection()

    r_dict = {}
    for x in sys:
        r = iter(x)
        key = r.next()
        val = r.next()
        r_dict[key] = val

    return r_dict

def get_system_variables(node_id):
    """
    DESC: Return the system settings from the transcirrus system settings db.
    INPUT: system_name
    OUTPUT: r_dict - all system vas in the trans_system_settings table
    ACCESS: Wide open
    NOTE: This returns the variables in regarding the transcirrus system. It is used for information and to create the
          config.py file descriptor to write out the config.py that is in transcirrus.common by calling write_new_config.py
    """
    if(node_id == ""):
        logger.sys_error("System node_id can not be blank when getting system variables.")
        raise Exception("System node_id can not be blank when getting system variables.")

    db = db_connect()
    #get the system name
    try:
        #change to use config.py
        get_sys_name = {'select':'host_system', 'from':'trans_system_settings','where':"parameter='node_id'", 'and':"param_value='%s'"%(node_id)}
        node_name = db.pg_select(get_sys_name)
    except:
        logger.sql_error("Could not get the system name/node name for node id %s" %(node_id))
        raise Exception("Could not get the system name/node name for node id %s" %(node_id))

    try:
        find_node_dict = {'select':"parameter,param_value",'from':"trans_system_settings",'where':"host_system='%s'" %(node_name[0][0])}
        sys = db.pg_select(find_node_dict)
    except:
        logger.sql_error("Could not find the system with name %s in the Transcirrus DB." %(node_name[0][0]))
        return 'NA'
    db.pg_close_connection()

    r_dict = {}
    for x in sys:
        r = iter(x)
        key = r.next().upper()
        val = r.next()
        r_dict[key] = val

    return r_dict

def add_network_adapter():
    pass


def set_network_variables(input_dict):
    """
    DESC: Change the ip address for the given adapter. Only cloud admins can
          perform this operation.
    INPUT: input_dict - node_id
                      - uplink_dict - dictionary of uplink params
                            - up_ip - req
                            - up_subnet - req
                            - up_gateway - req
                            - up_dns1 - req default 8.8.8.8
                            - up_dns2 - op default 8.8.4.4
                            - up_dns3 - op default 204.85.3.3
                            - up_domain - op default localhost
                      - mgmt_dict - dictionary of mgmt_net params
                            - mgmt_ip - op
                            - mgmt_subnet - op
                            - mgmt_dns1 -  op
                            - mgmt_dns2 - op
                            - mgmt_dns3 - op
                            - mgmt_domain - op
                            - mgmt_dhcp - dhcp/static - def dhcp
    OUTPUT: file descriptor used to write the interfaces file
            ERROR - fail
            NA - unknown
    ACCESS - wide open
    NOTE: This is used to set the net adapters on the physical machines - neutron libs for virtual environments
          The defualt subnet is 255.255.255.0 and the gateway will be set to None if a gateway is not specified.
          This is cumbersome but it just builds descriptors to re-rite the entire interface file. THIS WILL REWRITE THE
          /ETC/NETWORK/INTERFACE FILE EVERY TIME.
    """

    #do this today!
    #make sure none of the values are empty
    for key, value in input_dict.items():
        if((value == '') or (value == None)):
            logger.sys_error('%s was empty, required value.' %(key))
            raise Exception('%s was empty, required value.' %(key))

    mgmt_dict = input_dict['mgmt_dict']
    uplink_dict = input_dict['uplink_dict']
    print mgmt_dict
    print uplink_dict

    up_inet = 'static'
    for key,value in uplink_dict.items():
        if('up_ip' not in uplink_dict):
            logger.sys_error('No net adapter was specified.')
            raise Exception('No net adapter was specified.')
        if('up_subnet' not in uplink_dict):
            logger.sys_error('No uplink subnet was specified.')
            raise Exception('No uplink subnet was specified.')
        if('up_gateway' not in uplink_dict):
            logger.sys_error('No uplink gateway was specified.')
            raise Exception('No uplink gateway was specified.')
        #dns stuff
        if((uplink_dict['up_dns1'] == '') or ('up_dns1' not in uplink_dict)):
            uplink_dict['up_dns1'] = '8.8.8.8'
        if('up_dns2' not in uplink_dict):
            uplink_dict['up_dns2'] = '8.8.4.4'
        if('up_dns3' not in uplink_dict):
            uplink_dict['up_dns3'] = '204.85.3.3'
        if('up_domain' not in uplink_dict):
            uplink_dict['up_domain'] = 'localdomain'

    mgmt_inet = None
    for key,value in mgmt_dict.items():
        if('mgmt_dhcp' in mgmt_dict):
            if(mgmt_dict['mgmt_dhcp'].lower() == 'dhcp'):
                mgmt_inet = 'dhcp'
                break
            if(mgmt_dict['mgmt_dhcp'].lower() == 'static'):
                mgmt_inet = 'static'
            if('mgmt_ip' not in mgmt_dict):
                logger.sys_error('No mgmt ip was specified.')
                raise Exception('No mgmt ip was specified.')
            if('mgmt_subnet' not in mgmt_dict):
                logger.sys_error('No mgmt subnet was specified.')
                raise Exception('No mgmt subnet was specified.')
            if('mgmt_gateway' in mgmt_dict):
                logger.sys_error('No gateway used on mgmt network.')
            #dns stuff
            if((mgmt_dict['mgmt_dns1'] == '') or ('mgmt_dns1' not in mgmt_dict)):
                mgmt_dict['mgmt_dns1'] = '8.8.8.8'
            if('mgmt_dns2' not in mgmt_dict):
                mgmt_dict['mgmt_dns2'] = '8.8.4.4'
            if('mgmt_dns3' not in mgmt_dict):
                mgmt_dict['mgmt_dns3'] = '204.85.3.3'
            if('mgmt_domain' not in mgmt_dict):
                mgmt_dict['mgmt_domain'] = 'localdomain'

    #connect to the db
    db = db_connect()

    #check if the adapter already exsists on the system
    #Note - no try block - this is meerly a check to see if the adapter is in the db 
    get_upadpt = {'select':"net_alias",'from':"net_adapter_settings",'where':"node_id='%s'"%(input_dict['node_id']),'and':"net_alias='uplink'"}
    up_adapter = db.pg_select(get_upadpt)

    get_madpt = {'select':"net_alias",'from':"net_adapter_settings",'where':"node_id='%s'"%(input_dict['node_id']),'and':"net_alias='mgmt'"}
    m_adapter = db.pg_select(get_madpt)


    try:
        get_node = {'select':'node_type,node_mgmt_ip','from':'trans_nodes','where':"node_id='%s'"%(input_dict['node_id'])}
        node = db.pg_select(get_node)
    except:
        logger.sys_error("Could not get the node type from the Transcirrus db.")
        raise Exception("Could not get the node type from the Transcirrus db.")

    #add new config to the DB - This is a freaking hack but it is going away when the redhat switch happens
    try:
        db.pg_transaction_begin()
        if(up_adapter == None):
            #insert the new adapter
            ins_adpt = {'net_ip':"%s",'net_alias':"%s",'net_mask':"%s",'net_gateway':"%s",'net_adapter':"%s",'inet_setting':"%s",'net_dns1':"%s",'net_dns2':"%s",'net_dns3':"%s",'net_dns_domain':"%s",'net_mtu':"%s"
                        %(uplink_dict['up_ip'],'br-ex',uplink_dict['up_subnet'],uplink_dict['up_gateway'],'br-ex',up_inet,uplink_dict['up_dns1'],uplink_dict['up_dns2'],uplink_dict['up_dns3'],uplink_dict['up_domain'],'9000')}
    
            db.pg_insert("net_adapter_settings",ins_adpt)
        elif(up_adapter[0][0] == 'uplink'):
            #update the adapter row
            update = {'table':"net_adapter_settings",'set':"net_ip='%s',net_mask='%s',net_gateway='%s',inet_setting='%s',net_dns1='%s',net_dns2='%s',net_dns3='%s',net_dns_domain='%s',net_mtu='%s'"
                      %(uplink_dict['up_ip'],uplink_dict['up_subnet'],uplink_dict['up_gateway'],up_inet,uplink_dict['up_dns1'],uplink_dict['up_dns2'],uplink_dict['up_dns3'],uplink_dict['up_domain'],'9000'),'where':"net_adapter='br-ex'",
                      'and':"node_id='%s'"%(input_dict['node_id'])}
    
            db.pg_update(update)
        else:
            return 'NA'
    
        if(m_adapter == None):
            #insert the new adapter
            ins_adpt = {'net_ip':"%s",'net_alias':"%s",'net_mask':"%s",'net_gateway':"%s",'net_adapter':"%s",'inet_setting':"%s",'net_dns1':"%s",'net_dns2':"%s",'net_dns3':"%s",'net_dns_domain':"%s",'net_mtu':"%s"
                        %(mgmt_dict['mgmt_ip'],mgmt_dict['mgmt_adapter'],mgmt_dict['mgmt_subnet'],'NULL',bond0,mgmt_inet,mgmt_dict['mgmt_dns1'],mgmt_dict['mgmt_dns2'],mgmt_dict['mgmt_dns3'],mgmt_dict['mgmt_domain'],'1500')}
    
            db.pg_insert("net_adapter_settings",ins_adpt)
        elif(m_adapter[0][0] == 'mgmt'):
            #update the adapter row
            update = {'table':"net_adapter_settings",'set':"net_ip='%s',net_mask='%s',inet_setting='%s',net_dns1='%s',net_dns2='%s',net_dns3='%s',net_dns_domain='%s',net_mtu='%s'"
                      %(mgmt_dict['mgmt_ip'],mgmt_dict['mgmt_subnet'],mgmt_inet,mgmt_dict['mgmt_dns1'],mgmt_dict['mgmt_dns2'],mgmt_dict['mgmt_dns3'],mgmt_dict['mgmt_domain'],'1500'),'where':"net_adapter='bond0'",
                      'and':"node_id='%s'"%(input_dict['node_id'])}
    
            db.pg_update(update)
        else:
            return 'NA'

    #update the node_mgmt_ip field in trans_nodes
    #if(link == 'bond0'):
    #update_node_table = {'table':'trans_nodes','set':"node_mgmt_ip='%s'"%(input_dict['net_ip']),'where':"node_id='%s'"%(input_dict['node_id'])}
    #db.pg_update(update_node_table)
    except:
        db.pg_transaction_rollback()
        logger.sql_error("Could not set the network adapter settings.")
        return 'ERROR'
    finally:
        db.pg_transaction_commit()
        #disconnect from db
        db.pg_close_connection()

    #"net adapters" are always bonds unless noted, uplink will be a bridge adapter
    get_up_adapter = {'node_id':input_dict['node_id'],'net_adapter':'uplink'}
    up_netadpt = get_network_variables(get_up_adapter)

    get_m_adapter = {'node_id':input_dict['node_id'],'net_adapter':'mgmt'}
    m_netadpt = get_network_variables(get_m_adapter)

    config_array = []
    bond0 = []
    #bond0 is the mgmt interface on the nodes and the ciac
    #if(input_dict['net_adapter'] == 'mgmt'):
    bond = 'auto bond0'
    bond0.append(bond)
    if(m_netadpt['inet_setting'] == 'static'):
        iface = 'iface bond0 inet static'
        bond0.append(iface)
        address = '    address %s'%(m_netadpt['net_ip'])
        bond0.append(address)
        netmask = '    netmask %s' %(m_netadpt['net_mask'])
        bond0.append(netmask)
        if(m_netadpt['net_gateway'] != 'NULL' or m_netadpt['net_gateway'] != ''):
            logger.sys_info("No gateway set for Bond0")
    else:
        iface = 'iface bond0 inet dhcp'
        bond0.append(iface)
    slaves = '    slaves none'
    bond0.append(slaves)
    mtu = '    mtu %s' %(m_netadpt['net_mtu'])
    bond0.append(mtu)
    bondmode = '    bond-mode active-backup'
    bond0.append(bondmode)
    miimon = '    bond-miimon 100'
    bond0.append(miimon)
    downdelay = '    bond-downdelay 200'
    bond0.append(downdelay)
    updelay = '    bond-updelay 200'
    bond0.append(updelay)
    dns = '    dns-nameservers %s %s %s' %(m_netadpt['net_dns1'],m_netadpt['net_dns2'],m_netadpt['net_dns3'])
    bond0.append(dns)
    search = '    dns-search %s'%(m_netadpt['net_dns_domain'])
    bond0.append(search)
    bond0.append('')

    #we know the node type based on the ID
    #000 - ciac
    #001 - compute
    #002 - storage
    br = []
    eth = []
    data_bond = []
    up_bond = []
    if(node[0][0] == 'cc'):
        #if(input_dict['net_adapter'] == 'uplink'):
        bridge = 'auto %s' %(up_netadpt['net_phy_adapter'])
        br.append(bridge)
        if(up_netadpt['inet_setting'] == 'static'):
            iface = 'iface %s inet static' %(up_netadpt['net_phy_adapter'])
            br.append(iface)
            address = '    address %s'%(up_netadpt['net_ip'])
            br.append(address)
            netmask = '    netmask %s' %(up_netadpt['net_mask'])
            br.append(netmask)
            if(up_netadpt['net_gateway'] != 'NULL' or up_netadpt['net_gateway'] != ''):
                gateway = '    gateway %s' %(up_netadpt['net_gateway'])
                br.append(gateway)
        else:
            iface = 'iface %s inet dhcp' %(up_netadpt[0][1])
            br.append(iface)
        bridge_ports = '    bridge_ports bond1'
        br.append(bridge_ports)
        dns = '    dns-nameservers %s %s %s' %(up_netadpt['net_dns1'],up_netadpt['net_dns2'],up_netadpt['net_dns3'])
        br.append(dns)
        if(up_netadpt['net_dns_domain'] != 'NULL' or up_netadpt['net_dns_domain'] != ''):
            search = '    dns-search %s'%(up_netadpt['net_dns_domain'])
            br.append(search)
        br.append('')


        eth = ['auto eth0','iface eth0 inet manual','    bond-master bond0','','auto eth1','iface eth1 inet manual','    bond-master bond0','','auto eth2','iface eth2 inet manual','    bond-master bond1','',
               'auto eth3','iface eth3 inet manual','    bond-master bond1','','auto eth4','iface eth4 inet manual','    bond-master bond2','','auto eth5','iface eth5 inet manual','    bond-master bond2','']

        #uplink bonded interface for br-ex
        up_bond = ['auto bond1','iface bond1 inet manual','    up ifconfig $IFACE 0.0.0.0 up','    up ip link set $IFACE up','    down ip link set $IFACE promisc off','    down ifconfig $IFACE down','    slaves none',
                   '    bond-mode active-backup', '    bond-miimon 100', '    bond-downdelay 200', '    bond-updelay 200','']
        #datanet config for ciac node
        data_bond = ['auto bond2','iface bond2 inet static','    address 172.38.24.10','    netmask 255.255.255.0','    network 172.38.24.0','    slaves none', '    bond-mode active-backup', '    bond-miimon 100', '    bond-downdelay 200', '    bond-updelay 200','']

        #concat the big arrays
        config_array = eth + bond0 + up_bond + br + data_bond

        #apend on the new mgmt_ip and the new uplink_ip to pg_hba.conf
        os.system('sudo cp -f /etc/postgresql/9.1/main/pg_hba.proto /etc/postgresql/9.1/main/pg_hba.conf')
        #get the current ip settings
        b0 = get_adapter_ip('bond0')
        b1 = get_adapter_ip('bond1')
        os.system('sudo echo "host all all %s/32 md5" >> /etc/postgresql/9.1/main/pg_hba.conf'%(b0['net_ip']))
        os.system('sudo echo "host all all %s/32 md5" >> /etc/postgresql/9.1/main/pg_hba.conf'%(b1['net_ip']))
        os.system('sudo echo "host all all %s/32 md5" >> /etc/postgresql/9.1/main/pg_hba.conf'%(mgmt_dict['mgmt_ip']))
        os.system('sudo echo "host all all %s/32 md5" >> /etc/postgresql/9.1/main/pg_hba.conf'%(uplink_dict['up_ip']))

    if((node[0][0] == 'cn') or (node[0][0] == 'sn')):
        eth = ['auto eth0','iface eth0 inet manual','    bond-master bond0','','auto eth1','iface eth1 inet manual','    bond-master bond0','','auto eth2','iface eth2 inet manual','    bond-master bond1','',
               'auto eth3','iface eth3 inet manual','    bond-master bond1','']

        data_bond = ['auto bond1','iface bond1 inet dhcp','    slaves none', '    bond-mode active-backup', '    bond-miimon 100', '    bond-downdelay 200', '    bond-updelay 200','']
        #concat the big arrays
        config_array = eth + bond0 + data_bond

    conf = {}
    conf['op'] = 'new'
    conf['file_owner'] = 'root'
    conf['file_group'] = 'root'
    conf['file_perm'] = '644'
    conf['file_path'] = '/etc/network'
    conf['file_name'] = 'interfaces'
    conf['file_content'] = config_array

    return conf

def get_network_variables(input_dict):
    """
    DESC: Return the network settings from the transcirrus system settings db.
    INPUT: input_dict - net_adapter - uplink/mgmt/data
                      - node_id
    OUTPUT: r_dict - net_ip
                   - net_mask
                   - net_gateway
                   - net_dns1
                   - net_dns2
                   - net_dns3
                   - net_mtu
                   - net_inet
                   - net_phy_adapter
                   - net_dns_domain
    ACCESS: Wide open
    NOTE: This only returns the network interface settings of the system. It is used for information puposes
          and to build file descriptors to write the /etc/network/interfaces file
    """
    for value in input_dict.itervalues():
        if((value == None) or (value == '')):
            logger.sys_error('A required value was not passed.')
            raise Exception('A required value was not passed.')

    if((input_dict['net_adapter'] == 'uplink') or (input_dict['net_adapter'] == 'mgmt') or (input_dict['net_adapter'] == 'data')):
        logger.sys_info("Net adapter passed")
    else:
        logger.sys_error("Net adapter not passed in.")
        raise Exception("Net adapter not passed in.")

    #pull the config info from the db and build a new file descriptor
    db = db_connect()
    r_dict = {}
    if(input_dict['net_adapter'] != 'data'):
        try:
            get_net_config = {'select':'net_adapter,net_ip,net_mask,net_gateway,net_dns1,net_dns2,net_dns3,net_mtu,net_dns_domain,inet_setting','from':'net_adapter_settings',
                              'where':"node_id='%s'" %(input_dict['node_id']),'and':"net_alias='%s'"%(input_dict['net_adapter'])}
            net_config = db.pg_select(get_net_config)
            r_dict = {'net_ip':net_config[0][1],'net_mask':net_config[0][2],'net_gateway':net_config[0][3],'net_dns1':net_config[0][4],'net_dns2':net_config[0][5],
                      'net_dns3':net_config[0][6],'net_mtu':net_config[0][7],'inet_setting':net_config[0][9],'net_phy_adapter':net_config[0][0],'net_dns_domain':net_config[0][8]}
        except:
            logger.sys_error('Could not get the network config for node %s' %(input_dict['node_id']))
            raise Exception('Could not get the network config for node %s' %(input_dict['node_id']))
    elif(input_dict['net_adapter'] == 'data'):
        try:
            get_uplink_ip = {'select':'node_data_ip','from':'trans_nodes','where':"node_id='%s'"%(input_dict['node_id'])}
            net_config = db.pg_select(get_uplink_ip)
            r_dict = {'net_ip':net_config[0][0],'net_mask':'255.255.255.0','net_gateway':'NULL','net_dns1':'NULL','net_dns2':'NULL',
                      'net_dns3':'NULL','net_mtu':'9000','inet_setting':'dhcp','net_phy_adapter':'bond2','net_dns_domain':'NULL'}
        except:
            logger.sys_error('Could not get the network config for node %s' %(input_dict['node_id']))
            raise Exception('Could not get the network config for node %s' %(input_dict['node_id']))
    else:
        return 'ERROR'

    return r_dict

def list_network_variables():
    return 1


#######System level calls used to run linux commands#######

def ping_ip(ip):
    """
    DESC: Ping an ip
    INPUT: ip
    OUTPUT: OK - success
            ERROR - fail
            NA - unknown
    """
    out = os.system('sudo ping %s'  %(ip))
    if(out):
        return 'OK'
    elif(not out):
        return 'ERROR'
    else:
        return 'NA'

def change_phy_system_name(sys_name):
    """
    DESC: Change the physical system name.
    INPUT: sys_name
    OUTPUT: OK - success
            ERROR - fail
    ACCESS: Wide open
    NOTE: 
    """
    #NOT sure if we should do this or not.

def restart_network_card(net_adapter):
    """
    DESC: Perform the ifdown/ifup command in order to apply the new nework card settings.
    INPUT: net_adapter
    OUTPUT: OK - success
            ERROR - fail
    ACCESS: Wide open
    NOTE: This should be used after the network card config files have been written.
          If all is given as net_adapter then all net adapters are restarted.
    """

    if(net_adapter.lower() == 'all'):
        os.system('sudo /etc/init.d/networking restart')
    else:
        down = os.system('sudo ifdown %s' %(net_adapter))
        print down
        #if(down == ''):
        #    return 'ERROR'
    
        up = os.system('sudo ifup %s' %(net_adapter))
        print up
        if(up != 0):
            return 'ERROR'

    return 'OK'

def enable_network_card(net_adapter):
    """
    DESC: Perform the ifconfig up command on the given net adapter.
    INPUT: net_adapter
    OUTPUT: OK - success
            ERROR - fail
    ACCESS: Wide open
    NOTE:
    """
    os.system("sudo ifconfig %s up" %(net_adapter))
    out = subprocess.Popen('sudo ifconfig -s | grep "%s"' %(net_adapter), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ifconfig = out.stdout.readlines()
    if(ifconfig[0]):
        return 'OK'
    else:
        return 'ERROR'
    
def disable_network_card(net_adapter):
    """
    DESC: Perform the ifconfig down command on the given net adapter.
    INPUT: net_adapter
    OUTPUT: OK - success
            ERROR - fail
            NA - unknown
    ACCESS: Wide open
    NOTE:
    """
    os.system("sudo ifconfig %s down" %(net_adapter))
    out = subprocess.Popen('sudo ifconfig -s | grep "%s"' %(net_adapter), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ifconfig = out.stdout.readlines()
    if(len(ifconfig) == 0):
        return 'OK'
    else:
        return 'ERROR'
'''
IMPLEMENT LATER alpo.1
def ovs_add_br(br_input):
    """
    DESC: Set up the bridges needed in openstack.
    INPUT: br_input - br_name
                    - br_port - array of ports
                    - port_type bond/port
    OUTPUT: OK - success
            ERROR - fail
    ACCESS: Wide Open
    NOTE: br_port is the port to add. If none is given the bridge is set up and no port
          is added.
    """
    if('br_name' not in br_input):
        logger.sys_error("Bridge name is requird when setting up a bridge.")
        return 'ERROR'
    os.system("ovs-vsctl add-br %s" %(br_input['br_name']))
    if('br_port' in br_input):
        ports = br_port['br_port']
        if('port_type' in br_input):
            if(br_input['br_type'] == 'bond'):
                logger.sys_info("Adding bond %s to bridge %s" %(br_input['br_port'],br_input['br_name']))
                os.system("ovs-vsctl add-bond %s %s %s %s" %(br_input['br_name'],br_input['br_port']))
            elif(br_input['br_type'] == 'port'):
                logger.sys_info("Adding port %s to bridge %s" %(ports[0],br_input['br_name']))
                os.system("ovs-vsctl add-port %s %s" %(br_input['br_name'],ports[0]))
    return 'OK'
'''


def ovs_update_br(br_input):
    pass

def ovs_delete_br(br):
    pass

def get_adapter_ip(net_adapter):
    """
    DESC: Get the ip info associated with a specific network adapter.
    INPUT: net_adapter
    OUTPUT: r_dict - net_adapter
                   - net_ip
                   - net_mask
                   - net_mac
    """
    out = ifconfig('%s' %(net_adapter))
    r_dict = {'net_adapter':net_adapter,'net_ip':out['addr'],'net_mask':out['netmask'],'net_mac':out['hwaddr']}
    return r_dict

def halt_system():
    """
    DESC: Halt the local system.
    INPUT: none
    OUTPUT: none
    NOTE: VERY DANGEROUS. THIS IS WIDE OPEN AS OF NOW
    """
    os.system('sudo shutdown -H')

def reboot_system():
    """
    DESC: Reboot the local system.
    INPUT: none
    OUTPUT:
    NOTE: VERY DANGEROUS. THIS IS WIDE OPEN AS OF NOW
    """
    os.system('sudo reboot')

def power_off_system():
    """
    DESC: Power off the local system.
    INPUT: none
    OUTPUT: none
    NOTE: VERY DANGEROUS. THIS IS WIDE OPEN AS OF NOW
    """
    os.system('sudo shutdown -P')

def compare_vm_range(new_start, new_end):
    """
    DESC: Checks to see if new ip endpoints will conflict with current state
    INPUT: new vm ip endpoints
    OUTPUT: current vm range that will become invalid given new endpoints or -1 if no conflicts
            form is array of dictionaries [{'start': -1, 'end': -1}]
    NOTE: Returns only the last part of the address, example: 192.168.10.XXX <- the XXX part
          This does not validate if the ip addresses are in valid ip format or not
    """
    node = get_node_id()

    system_variables = get_system_variables(node)

    sys_vm_ip_min = system_variables['VM_IP_MIN']
    sys_vm_ip_max = system_variables['VM_IP_MAX']

    problem_start = -1
    problem_end = -1
    problem_mid_1 = -1
    problem_mid_2 = -1

    new_start_bytes = new_start.split('.')
    new_end_bytes = new_end.split('.')
    sys_vm_ip_min_bytes = sys_vm_ip_min.split('.')
    sys_vm_ip_max_bytes = sys_vm_ip_max.split('.')

    new_start_parts = [int(b) for b in new_start_bytes]
    new_end_parts = [int(b) for b in new_end_bytes]
    sys_vm_ip_min_parts = [int(b) for b in sys_vm_ip_min_bytes]
    sys_vm_ip_max_parts = [int(b) for b in sys_vm_ip_max_bytes]

    start = new_start_parts[3]
    end = new_end_parts[3]
    vm_min = sys_vm_ip_min_parts[3]
    vm_max = sys_vm_ip_max_parts[3]

    for x in range(0, 3):
        if(new_start_parts[x] != sys_vm_ip_min_parts[x] or
           new_end_parts[x] != sys_vm_ip_max_parts[x]):
            return [{'start': vm_min, 'end': vm_max}]

    for x in range(vm_min, vm_max + 1):
        if(x < start or x > end):
            if(problem_start == -1):
                problem_start = x
            problem_end = x
    if(problem_start < start and problem_end > end):
        problem_mid_1 = start - 1
        problem_mid_2 = end + 1
    if(problem_mid_1 == -1):
        return [{'start': problem_start, 'end': problem_end}]
    else:
        return [{'start': problem_start, 'end': problem_mid_1}, {'start': problem_mid_2, 'end': problem_end}]

def check_gateway_in_range(input_dict):
    """
    DESC: Check if the uplink ip gateway is on the same network as the uplink ip
    INPUT: input_dict - uplink_ip
                        uplink_gateway
                        uplink_subnet
    OUTPUT: OK - success
            ERROR - fail
            NA
    NOTE: All veriables are rquiered.
    """
    return 'OK'

def check_public_with_uplink(input_dict):
    """
    DESC: Check to make sure that the default public ip range is on the same subnet as the uplink ip.
    INPUT: input_dict - uplink_ip
                        public_start
                        public_end
                        public_subnet
    OUTPUT: OK - success
            ERROR - fail
            NA
    NOTE: All veriables are required.
    """
    return 'OK'

def time_stamp():
    raw = datetime.datetime.now()
    julian = time.mktime(raw.timetuple())
    stamp = {'raw':datetime.datetime.now(), 'julian':julian}
    return stamp

def restart_dhclient():
    """
    DESC: restart dhclient service
    INPUT: 
    OUTPUT: 
    NOTE: 
    """

    out = subprocess.Popen('sudo dhclient', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    console = out.stdout.readlines()
    logger.sys_info(console)

def getDhcpServer():
    '''
    @author         : Shashaa
    comment         : get DHCP server IP address from dhcp.bond1.leases
                      file. bond1 interface of the machine connects to
                      data network of the cloud.
    return value    : dhcp_server ip
    create date     :
    ----------------------
    modify date     :
    @author         :
    comments        : should be used by cn/sn client process
    '''

    dhcp_file = "/var/lib/dhcp/dhclient.bond1.leases"
    dhcp_server = ""
    global dhcp_retry

    while dhcp_retry:

        out = subprocess.Popen('grep dhcp-server-identifier %s' % (dhcp_file), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        data = out.stdout.readlines()
        if (data):
            #print data[0].split(" ")
            data = data[0].split(" ")
            dhcp_server = data[4].strip()
            dhcp_server = dhcp_server.strip(";")
            logger.sys_info("dhcp_server IP: %s" % dhcp_server)
            dhcp_retry=0
            #sys.exit()
        else:
            logger.sys_warning("Trying to get DHCP server IP")
            restart_dhclient()
            dhcp_retry = dhcp_retry-1
            time.sleep(1)

    if (dhcp_server == ""):
        logger.sys_error("Error in getting DHCP server IP")
        sys.exit()
    else:
        return dhcp_server

