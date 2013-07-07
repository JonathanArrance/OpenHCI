#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json
import numpy as np

sys.path.append('../../common')
import logger
import config

from api_caller import caller

sys.path.append(config.DB_PATH)
from postgres import pgsql

class tenant_ops:
    
    #DESC: Constructor to build out the tokens object
    #INPUT: user_dict dictionary containing - built in auth.py
    #           username
    #           password
    #           project_id - could be blank
    #           token
    #           status_level
    #           user_level
    #           is_admin
    #           sec - optional - use HTTPS sec = TRUE defaults to FALSE
    def __init__(self,user_dict):
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        # user_dict = {"username":self.username,"password":self.user_pass,"project_id":exist[0][7],"status_level":status_level,"user_level":user_level,"is_admin": is_admin,"token":token}
        else:
            self.username = user_dict['username']
            self.password = user_dict['password']
            self.project_id = user_dict['project_id']
            self.token = user_dict['token']
            self.status_level = user_dict['status_level']
            self.user_level = user_dict['user_level']
            self.is_admin = user_dict['is_admin']
            self.adm_token = user_dict['adm_token']
            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'
                
            #get the default cloud controller info
            self.controller = config.DEFAULT_CLOUD_CONTROLER
            self.api_ip = config.DEFAULT_API_IP

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")
            raise Exception("No admin tokens passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

    #DESC: create a new project in Openstack. Only admins can perform this operation.
    #      calls the rest api in OpenStack and updates applicable fields in Transcirrus
    #      database
    #INPUT: self object
    #       project_name - what you want to call it - Required
    #OUTPUT tenant ID
    def create_tenant(self,project_name):
        # create a new project in OpenStack. This can only be done by and Admin
        # we need to make sure that the user is a transcirrus admin and an openstack admin.
        # if not reject and throw an exception

        if((not project_name) or (project_name == "")):
            logger.sys_error("No project name was specified for the new project.")
            raise EXception("No project name was specified for the new project.")

        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        #declare tenant_id
        tenant_id = ""

        #Need to create the new project then find the new project in OS then update transcirrus db

        #check if the is_admin flag set to 1 - sanity check
        if(self.is_admin == 1):
            logger.sys_error("User not identified as a user or an admin.")
            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient, can not list endpoints.")
                raise Exception("User status not sufficient, can not list endpoints.")
    
            #standard users can not create a project
            if(self.user_level >= 1):
                logger.sys_error("Only admins and power users can may list endpoints.")
                raise Exception("Only admins and power users can may list endpoints.")
    
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)

            body = '{"tenant": {"enabled": true, "name": "%s", "description": "%s dev project"}}' %(project_name,project_name)
            header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
            function = 'POST'
            api_path = '/v2.0/tenants'
            token = self.adm_token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
            rest = api.call_rest(rest_dict)

            #check the response and make sure it is a 200 or 201
            if((rest['response'] == 201) or (rest['response'] == 200)):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                tenant_id = load['tenant']['id']
            else:
                _http_codes(rest['response'],rest['reason'])

        else:
            logger.sys_error("Admin flag not set, could not create the new project ")

        # need to update the project_id info to the relevent transcirrus db tables
        try:
            self.db.pg_transaction_begin()
            #insert the new project into the db
            proj_ins_dict = {"proj_id":tenant_id,"proj_name":project_name,"host_system_name":self.controller, "host_system_ip":self.api_ip}
            self.db.pg_insert("projects",proj_ins_dict)

            #Update the user table
            #user_up_dict = {'table':"trans_user_info",'set':"""user_primary_project='%s',user_project_id='%s'"""%(project_name,tenant_id),'where':"user_name='%s'" %(self.username)}
            #self.db.pg_update(user_up_dict)

            self.db.pg_transaction_commit()
            self.db.pg_close_connection()
        except Exception as e:
            logger.sql_error("Could not commit the transaction to the Transcirrus DB.%s" %(e))
            self.db.pg_transaction_rollback()
            #simple cleanup of failed project create
            raise
        r_dict = {"response":200,"reason":"OK","project_name":project_name,"tenant_id":tenant_id}
        return r_dict

    #DESC: remove a tenant from the OpenStack system and from the Transcirrus DB
    #INPUT: self object
    #       project_name
    #OUTPUT: dictionary containg the rest API response,reason and status of "OK' if task completed successfully
    def remove_tenant(self,project_name):
        
        if((not project_name) or (project_name == "")):
            logger.sys_error("No project name was specified for the new project.")
            raise EXception("No project name was specified for the new project.")

        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        #check if the is_admin flag set to 1 - sanity check
        if(self.is_admin == 1):
            logger.sys_error("User not identified as a user or an admin.")
            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient, can not list endpoints.")
                raise Exception("User status not sufficient, can not list endpoints.")

            #standard users can not delete a project
            if(self.user_level >= 1):
                logger.sys_error("Only admins and power users can may list endpoints.")
                raise Exception("Only admins and power users can may list endpoints.")

            #need to get the project ID from the Transcirrus DB
            try:
                select_dict = {"select":"proj_id", "from":"projects", "where":"proj_name='%s'" %(project_name)}
                select = self.db.pg_select(select_dict)
            except Exception as e:
                logger.sql_error("Could not get the project_id from the Transcirrus DB.%s" %(e))
                raise

            api_dict = {"username":self.username, "password":self.password, "project_id":select[0][0]}
            api = caller(api_dict)

            #body = '{"tenant": {"enabled": true, "name": "%s", "description": "%s dev project", "id": "%s"}}' %(project_name,project_name,select[0][0])
            body = ""
            header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
            function = 'DELETE'
            api_path = '/v2.0/tenants/%s' %(self.project_id)
            token = self.adm_token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 201
            if((rest['response'] == 201) or (rest['response'] == 200) or (rest['response'] == 204)):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                logger.sys_info("Project: %s has been removed from the Transcirrus DB." %(self.project_id))
                #delete the project from transcirrus db and update the user account
                try:
                    self.db.pg_transaction_begin()
                    del_dict = {"table":'projects',"where":"proj_id='%s'" %(self.project_id)}
                    self.db.pg_delete(del_dict)

                    user_up_dict = {'table':"trans_user_info",'set':"""user_primary_project='NULL',user_project_id='NULL'""",'where':"user_project_id='%s'" %(self.project_id)}
                    self.db.pg_update(user_up_dict)

                    self.db.pg_transaction_commit()
                except Exception as e:
                    logger.sql_error("Could not commit the transaction to the Transcirrus DB.%s, Contact an Admin" %(e))
                    self.db.pg_transaction_rollback()
                    raise
                #close all of the db connections that are open
                self.db.pg_close_connection()
                #build up the return dictionary and return it if everythig is good to go
                r_dict = {"response":rest['response'],"reason":rest['reason'],"status":"OK"}
                return r_dict
            else:
                _http_codes(rest['response'],rest['reason'])
        else:
            logger.sys_error("Admin flag not set, could not create the new project ")

    #DESC: Get all of the project names and IDs from the Transcirrus Db
    #INPUT: self - object
    #Output:dictionary containing all of the projects and project ids
    #This operation is only available to admins
    def list_all_tenants(self):
        
        # create a new project in OpenStack. This can only be done by and Admin
        # we need to make sure that the user is a transcirrus admin and an openstack admin.
        # if not reject and throw an exception

        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        #check if the is_admin flag set to 1 - sanity check
        if(self.is_admin == 1):
            logger.sys_error("User not identified as a user or an admin.")
            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient, can not list endpoints.")
                raise Exception("User status not sufficient, can not list endpoints.")
    
            #standard users can not create a project
            if(self.user_level >= 1):
                logger.sys_error("Only admins and power users can may list endpoints.")
                raise Exception("Only admins and power users can may list endpoints.")

            #query the DB and get the list of projects in the OpenStack Environment
            try:
                #insert the new project into the db
                select_dict = {"select":'proj_name,proj_id',"from":'projects'}
                projects = self.db.pg_select(select_dict)
                
                #initialize the projects dict
                proj_dict = {}
                for project in projects:
                    proj_dict[project[0]] = project[1]
                self.db.pg_close_connection()
                return proj_dict
            except Exception as e:
                logger.sql_error("Could not commit the transaction to the Transcirrus DB.%s" %(e))
                raise
        else:
            logger.sys_error("Admin flag not set, could not create the new project ")
        

    def list_tenant_users(self):
        print "yo"
    def update_tenant(self):
        print "yo"
        
######Internal defs
def _http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")