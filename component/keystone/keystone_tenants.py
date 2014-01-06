#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.common.api_caller import caller
from transcirrus.database.postgres import pgsql

class tenant_ops:
    #UPDATED/UNIT TESTED
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

            if('adm_token' in user_dict):
                self.adm_token = user_dict['adm_token']

            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'
                
            #get the default cloud controller info
            self.controller = config.CLOUD_CONTROLLER
            self.api_ip = config.API_IP

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

        self.keystone_users = user_ops(user_dict)

    #DESC: create a new project in Openstack. Only admins can perform this operation.
    #      calls the rest api in OpenStack and updates applicable fields in Transcirrus
    #      database
    #INPUT: self object
    #       project_name - what you want to call the new project - Required
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

            try:
                #build an api connection for the admin user. NOTE project ID is the admin user project id
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #Build the new project in OpenStack
                body = '{"tenant": {"enabled": true, "name": "%s", "description": "%s project"}}' %(project_name,project_name)
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/tenants'
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
            except:
                logger.sys_logger("Could not build the new project %s"%(project_name))
                raise Exception("Could not build the new project %s"%(project_name))
        else:
            logger.sys_error("Admin flag not set, could not create the new project ")

        #check the response and make sure it is a 200 or 201
        tenant_id = None
        if((rest['response'] == 201) or (rest['response'] == 200)):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            tenant_id = load['tenant']['id']
            # need to update the project_id info to the relevent transcirrus db tables
            try:
                self.db.pg_transaction_begin()
                #insert the new project into the db
                proj_ins_dict = {"proj_id":tenant_id,"proj_name":project_name,"host_system_name":self.controller, "host_system_ip":self.api_ip}
                self.db.pg_insert("projects",proj_ins_dict)
            except Exception as e:
                logger.sql_error("Could not commit the transaction to the Transcirrus DB.%s" %(e))
                self.db.pg_transaction_rollback()
                self.db.pg_close_connection()
                #simple cleanup of failed project create
                raise e
            else:
                self.db.pg_transaction_commit()
                self.db.pg_close_connection()
        else:
            util.http_codes(rest['response'],rest['reason'])


        try:
            #add the admin to the project as an admin - admingets added to all projects in the system
            add_admin = {'username':'admin','user_role':'pu','project_name':project_name}
            admin = self.keystone_users.add_user_to_project(add_admin)
        except Exception as e:
            logger.sys_error('Could not add the admin to %s'%(project_name))
            raise Exception('Could not add the admin to %s'%(project_name))

        r_dict = {"response":200,"reason":"OK","project_name":project_name,"tenant_id":tenant_id}
        return r_dict

    def remove_tenant(self,project_name):
        """
        DESC: Remove a tenant from the OpenStack system and from the Transcirrus DB
        INPUT: project_name
        ACCESS: Only the admin can remove the project
        OUTPUT: r_dict -response
                       -reason
                       -status - 'OK' if task completed successfully
        """
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
                print select
            except Exception as e:
                logger.sql_error("Could not get the project_id from the Transcirrus DB.%s" %(e))
                raise

            try:
                #build an api connection for the admin user.
                api_dict = {"username":self.username, "password":self.password, "project_id":select[0][0]}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                body = ""
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/tenants/%s' %(select[0][0])
                print api_path
                token = self.adm_token
                sec = 'FALSE'
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 200 or 201
                if((rest['response'] == 201) or (rest['response'] == 200) or (rest['response'] == 204)):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    logger.sys_info("Project: %s has been removed from the Transcirrus DB." %(select[0][0]))
                    #delete the project from transcirrus db and update the user account
                    try:
                        self.db.pg_transaction_begin()
                        del_dict = {"table":'projects',"where":"proj_id='%s'" %(select[0][0])}
                        self.db.pg_delete(del_dict)

                        user_up_dict = {'table':"trans_user_info",'set':"""user_primary_project='NULL',user_project_id='NULL'""",'where':"user_project_id='%s'" %(select[0][0])}
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
            except Exception as e:
                logger.sys_error("Could not remove the project %s" %(e))
        else:
            logger.sys_error("Admin flag not set, could not create the new project ")

    def list_all_tenants(self):
        """
        DESC: Get all of the project names and IDs from the Transcirrus Db
        INPUT: None
        Output: Dictionary containing all of the projects and project ids
        ACCESS: This operation is only available to admins
        """
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

    def get_tenant(self,project_name):
        """
        DESC: Get the information for a specific project from the Transcirrus DB
        INPUT: project_name
        OUTPUT: dictionary containing the project info
        ACCESS: Admins can get any project, users can only view the primary project
              they belong to.
        NOTE: If any of the project variables are empty a None will be returned for that variable.
        """
        
        if(not project_name):
            logger.sys_error("Did not pass a project name to the get_tenant operation.")
            raise Exception ("Did not pass a project name to the get_tenant operation.")

        #connect to the db
        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        #get the project info
        try:
            get = {"select":'*', "from":'projects', "where":"proj_name='%s'" %(project_name)}
            proj = self.db.pg_select(get)
        except:
            logger.sql_error("Could not get the project info for project: %s" %(project_name))
            raise Exception("Could not get the project info for project: %s" %(project_name))

        #build the dictionary up
        r_dict = {"project_id":proj[0][0],"project_name":proj[0][1],"def_security_key_name":proj[0][2],"def_security_key_id":proj[0][3],"def_security_group_id":proj[0][4],
                  "def_security_group_name":proj[0][5], "host_system_name":proj[0][6], "host_system_ip":proj[0][7], "def_network_name":proj[0][8], "def_network_id":proj[0][9]}
        if(self.is_admin == 1):
            return r_dict
        else:
            if(self.project_id == proj[0][0]):
                return r_dict
            else:
                raise Exception("Users can only get information on their own projects.")

    def list_tenant_users(self,project_name):
        """
        DESC: list the users that are members of the project. Admins and power users can do this.
        INPUT: project_name
        OUTPUT: array of r_dict - username
                                - user_id
        ACCESS: All users can list project users in the project they belong to. Admins can list users
                in any project.
        NOTE:none
        """
        if(project_name == ""):
            logger.sys_error("Must specify the project name.")
            raise Exception("Must specify the project name.")

        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        try:
            if(self.is_admin == 1):
                self.get_users = {'select':'user_name,keystone_user_uuid','from':'trans_user_info','where':"user_primary_project='%s'"%(project_name)}
            else:
                self.get_users = {'select':'user_name,keystone_user_uuid','from':'trans_user_info','where':"user_primary_project='%s'"%(project_name),'and':"user_project_id='%s'"%(self.project_id)}
            self.users = self.db.pg_select(self.get_users)
        except:
            logger.sys_error("Could not get user list for %s."%(project_name))
            raise Exception("Could not get user list for %s."%(project_name))

        r_array = []
        for user in self.users:
            r_dict = {'username':user[0],'user_id':user[1]}
            r_array.append(r_dict)
        return r_array

    def update_tenant(self):
        pass
        
######Internal defs#######
def _http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")
