#check to make sure that a user has an account in the transcirrus system
# and that the account corresponds to an account in keystone
# get the user level from the transcirrus system DB
#passes the user level out
#tested and works as of 7-21-2013
import sys
import json
from transcirrus.common.api_caller import caller

import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.database.postgres import pgsql

#username is an email address
#should be checked by fron end django
#application befor passed into the
#auth mechanism
class authorization:
    #DESC: Initialize the connection to the DB and set the username
    #INPUT: Username in the form of an email address
    #OUTPUT: none
    def __init__(self,username,user_pass):
        #connect to the database
        try:
            #try to connect to the transcirrus db
            #INFO: DB will never move from the root CiaC system so 127 address can be used.
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
            #INFO: connect directly to the keystone DB
            self.key = pgsql("192.168.10.30","5432","keystone","root","builder")
        except StandardError as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise
    
        #assign the username
        self.username = username
        self.user_pass = user_pass

    #DESC: Return the authorization level for the user and the auth token
    #      from openstack if the user is enabled and allowed to login to the
    #      openstack environment
    #INPUT: self.username
    #OUTPUT: Dictionary containing the user level, status level, auth token, and is_admin switch
    def get_auth(self):
        #check to see if the user exists in the DB
        #exist = user array of array
        exist = _get_user_info(self.db,self.username)
        #INFO: status levels determin user activity on the system
        #0 - User is not allowed to login to transcirus interface or Openstack
        #1 - User only has access to the transcirrus interface can not run anything
        #    doing with openstack
        #2 - User has access and use both transcirrus and Openstack stuff
        status_level = 0
        if (exist != 1):
            #check if the user is enabled in the keystone DB
            enabled = _check_user_enabled(self.key,exist)
            #Need to possibly add checks for False and False
            if (enabled):
                if (enabled['trans'] == 'TRUE' and enabled['keystone'] == 'TRUE'):
                    status_level = 2
                    logger.sys_info("User: %s has access status of 2")
                elif (enabled['trans'] == 'TRUE' and enabled['keystone'] == 'FALSE'):
                    status_level = 1
                    logger.sys_info("User: %s has access status of 1")
                else:
                    status_level = 0
                    logger.sys_info("User: %s has access status of 0")
            #get the user level
            #We only use Memeber and admin built in OpenStack roles
            #INFO: 0 - Admin
            #      1 - power user
            #      2 - user
            user_level = exist[0][3]
            user_keystone_role = exist[0][8]
            #if a user has a transcirrus level of 0(admin) and is part of the admin
            #role in keystone for the primary project then set the admin flag to 0
            #if there is any other combination set the flag to 1
            is_admin = 0
            if ((user_level == 0) and (str(user_keystone_role) == "admin")):
                is_admin = 1
            #get user access token (PKI key) from openstack if
            #user has a status level of 2 or higher and user level of 1 or greater
            token = ""
            adm_token = ""
            if (status_level == 0):
                token = ""
                logger.sys_info("User: %s had a status level of 0. Could not get a token." %(self.username))
            elif (status_level == 2 and user_level >= 1 and exist[0][7] != ""):
                token = _get_token(self.username,self.user_pass,exist[0][7])
                logger.sys_info("User: %s had a status level of %s. Retrieving API token." %(self.username,status_level))
            elif (status_level == 2 and user_level == 0 and is_admin == 1):
                if(exist[0][7] == 'NULL'):
                    adm_token = config.DEFAULT_ADMIN_TOKEN
                    logger.sys_info("User: %s had a status level of %s. Using default OpenStack admin token for port 35357." %(self.username,status_level))
                else:
                    logger.sys_info("User: %s had a status level of %s. Retrieving OpenStack admin token for port 35357." %(self.username,status_level))
                    adm_token = _get_admin_token(self.db,exist[0][7])
                    logger.sys_info("User: %s had a status level of %s. Retrieving OpenStack token for port 5000." %(self.username,status_level))
                    token = _get_token(self.username,self.user_pass,exist[0][7])
            else:
                token = "error"
                logger.sys_error("Could not get a token for the the user: %s. Check the system." %(self.username))

            #dictionary containing the user login info. permissions, token and status
            #need to set PKI token and ADMIN token
            user_dict = {"username":self.username,"password":self.user_pass,"project_id":exist[0][7],"status_level":status_level,"user_level":user_level,"is_admin": is_admin,"token":token,"adm_token":adm_token,"db_object":self.db}

            #close open db connections
            #self.db.pg_close_connection()
            self.key.pg_close_connection()
            return user_dict
        else:
            logger.sys_error("The user: %s, does not appear to hava an account." %(self.username))
            raise Exception("The user: %s, does not appear to hava an account." %(self.username))


    def check_first_time_boot():
        print "not implemented"
    
    def check_admin_pass_set():
        print "not implemeted"
        
    def set_admin_pass():
        print "not implemeted"
    
    def set_first_time_boot():
        print "not implemeted"

    def delete_admin_pass():
        print "not implemeted"
    
    def delete_first_time_boot():
        print "not implemeted"

#DESC: Check if the user exists in the database
#INPUT: self object
#OUTPUT: Array of array containing user info from the Transcirrus database on success
#        Return 1 on failure
def _get_user_info(db,username):
    #try to get the user info from the database
    try:
        get_user_dict = {'select':"*", 'from':"trans_user_info", 'where':"user_name='%s'" %(username)}
        user = db.pg_select(get_user_dict)
    except Exception as e:
        logger.sql_error("Could not get user info from Transcirrus db for user: %s with exception %s" %(username,e))
        raise

    if (not user):
        logger.sys_warning("Could not find user: %s in the Transcirrus database." %(username))
        return 1
    else:
        #ex: user[0][1] = user_name
        #    user[0][2] = user_enabled_in_keystone
        return user

#DESC: Initialize the connection to the DB and set the username
#INPUT: user_array containg the info for a user from trans_user_info
#OUTPUT: Dictionary containg the enable status from transcirrus and keystone DB
def _check_user_enabled(key,user_array):
    #check if the user is enabled in the DB
    transcirrus_enabled = 'FALSE'
    if (user_array[0][4] == 'TRUE'):
        logger.sys_info("User: %s is enabled in the Transcirrus database." %(user_array[0][1]))
        transcirrus_enabled = 'TRUE'
    elif (user_array[0][4] == 'FALSE'):
        logger.sys_warning("User: %s is not enabled in the Transcirrus database." %(user_array[0][1]))
    else:
        logger.sys_error("No user array was passed into auth.check_user_enabled")

    #query the keystone DB dirctly to get the user status
    keystone_enabled = 'FALSE'
    try:
        get_user_status = {'select':"enabled", 'from':"public.user", "where":"id='%s'" %(user_array[0][5])}
        key_user = key.pg_select(get_user_status)
        #why did I have to convert this to string to get it to work???? Investigate
        if ((str(key_user[0][0]) == 'True') or (str(key_user[0][0]) == 'TRUE')):
            logger.sys_info("User: %s is enabled in the Keystone DB" %(user_array[0][1]))
            keystone_enabled = 'TRUE'
        else:
            logger.sys_info("User: %s is enabled in the Keystone DB" %(user_array[0][1]))
    except:
        logger.sql_error("Could not find user: %s in the Keystone database." %(user_array[0][1]))
        logger.sys_error("Could not find user: %s in the Keystone database." %(user_array[0][1]))
        raise

    enable_dict = {"trans": transcirrus_enabled, "keystone":keystone_enabled}
    return enable_dict

#DESC: get the user auth token from openstack so that api commands can be run aginst the
#      cloud environment
#INPUT: username
#       password
#       project_id
#OUTPUT: api_token used to run REST API commands
def _get_token(username,password,project_id):
    #submit the values passed in 
    api_dict = {"username":username, "password":password, "project_id":project_id}
    api = caller(api_dict)
    #       body - body of the rest call
    #       Function - POST,PUT,GET,HEAD,DELETE,INSERT
    #       api_path - ex /v2.0/tenants
    #       token - auth or admin token
    #       sec - TRUE/FALSE, use https = True
    logger.sys_info("Tenant id was passwed in %s." %(username))
    body = '{"auth":{"passwordCredentials":{"username": "%s", "password":"%s"}, "tenantId":"%s"}}' %(username,password,project_id)
    header = {"Content-Type": "application/json"}
    function = 'POST'
    api_path = '/v2.0/tokens'
    token = ""
    sec = 'FALSE'
    rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
    rest = api.call_rest(rest_dict)

    if ((rest['response'] == 200) or (rest['response'] == 203)):
        #read the json that is returned
        logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
        load = json.loads(rest['data'])
        apitoken = load['access']['token']['id']
        return apitoken
    elif (rest['response'] == 403):
        logger.sys_warning("Response %s with Reason %s" %(rest['response'],rest['reason']))
        raise Exception("Response %s with Reason %s" %(rest['response'],rest['reason']))
    elif (rest['response'] == 400):
        logger.sys_error("Response %s with Reason %s" %(rest['response'],rest['reason']))
        raise Exception("Response %s with Reason %s" %(rest['response'],rest['reason']))
    elif (rest['response'] == 401):
        logger.sys_error("Response %s with Reason %s" %(rest['response'],rest['reason']))
        raise Exception("Response %s with Reason %s" %(rest['response'],rest['reason']))
    elif (rest['response'] == 405):
        logger.sys_error("Response %s with Reason %s" %(rest['response'],rest['reason']))
        raise Exception("Response %s with Reason %s" %(rest['response'],rest['reason']))
    elif (rest['response'] == 413):
        logger.sys_error("Response %s with Reason %s" %(rest['response'],rest['reason']))
        raise Exception("Response %s with Reason %s" %(rest['response'],rest['reason']))
    elif (rest['response'] == 503):
        logger.sys_error("Response %s with Reason %s" %(rest['response'],rest['reason']))
        raise Exception("Response %s with Reason %s" %(rest['response'],rest['reason']))
    elif (rest['response'] == 404):
        logger.sys_error("Response %s with Reason %s" %(rest['response'],rest['reason']))
        raise Exception("Response %s with Reason %s" %(rest['response'],rest['reason']))
    else:
        logger.sys_error("Could not get apitoken for unknown reason.")
        raise Exception("Could not get apitoken for unknown reason.")

def _get_admin_token(db,project_id):
    #retrieve the default system token from the Transcirrus DB
    #get the host system where the prject lives
    host_dict = {"select":"host_system_name", "from":"projects", "where":"proj_id='%s'" %(project_id)}
    host = db.pg_select(host_dict)

    #get the admin token from the db.
    #get the admin token in case it needs to be verified aginst a passed in "token"
    adm_dict = {"select":"param_value", "from":"trans_system_settings", "where":"parameter='admin_token'", "and":"host_system='%s'" %(host[0][0])}
    adm_token = db.pg_select(adm_dict)

    return adm_token[0][0]
