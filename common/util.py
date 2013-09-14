#!/usr/bin/python
import sys
import logger
import config

sys.path.append(config.DB_PATH)
from postgres import pgsql

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


#######System level calls used to run linux commands#######

#DESC: ping an ip
#INPUT: ip
#OUTPUT: SUCCESS - ip pingable
#        FAIL - ip not pingable
def ping_ip(ip):
    print "not implemented"

#DESC: Change the ip address for the given adapter. Only cloud admins can
#      perform this operation.
#INPUT: input_dict - user_level
#                  - net_adapter
#                  - new_ip
#                  - new_subnet - op
#                  - new_gateway - op
#OUTPUT: r_dict - net_adapter
#               - new_p
#               - ping SUCCESS/FAIL
def set_adapter_ip():
    print "not implemented"
    

#DESC: Set a system adapter to DHCP. Only cloud admin can perform this operation.
#INPUT: net_adapter
#OUTPUT: r_dict - net_adapter
#               - dhcp_ip
#               - dhcp_net_mask
#               - dhcp_net_gateway
def set_adapter_dhcp(net_adapter):
    print "not implemented"

#DESC: Get the ip info associated with a specific network adapter. Only cloud admin can
#      perform this operation.
#INPUT: net_adapter
#OUTPUT: r_dict - net_adapter
#               - net_ip
#               - net_mask
#               - net_gateway
def get_adapter_ip(net_adapter):
    print "not implemeted"

#DESC: Halt, but do not power off the linux system. Only cloud admins
#      can perform this task.
#INPUT: 
#OUTPUT: 
def halt_system():
    print "not implememted"
    
def reboot_system():
    print "not implemeted"
    
def power_off_system():
    print "not implemented"


