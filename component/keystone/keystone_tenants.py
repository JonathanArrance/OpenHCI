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
            self.user_id = user_dict['user_id']

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

    def create_tenant(self,project_name):
        """
        DESC: create a new project in Openstack. Only admins can perform this operation.
              calls the rest api in OpenStack and updates applicable fields in Transcirrus
              database
        INPUT: self object
               project_name - what you want to call the new project - Required
        OUTPUT project_id
        """
        logger.sys_info('\n**Creating new Keystone project. Component: Keystone Def: create_tenant**\n')
        if((not project_name) or (project_name == "")):
            logger.sys_error("No project name was specified for the new project.")
            raise EXception("No project name was specified for the new project.")

        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        #declare project_id
        project_id = None

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
                logger.sys_error("Could not connect to the API")
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
                logger.sys_error("Could not build the new project %s"%(project_name))
                raise Exception("Could not build the new project %s"%(project_name))
        else:
            logger.sys_error("Admin flag not set, could not create the new project ")

        #check the response and make sure it is a 200 or 201
        project_id = None
        if((rest['response'] == 201) or (rest['response'] == 200)):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            project_id = load['tenant']['id']
            # need to update the project_id info to the relevent transcirrus db tables
            try:
                self.db.pg_transaction_begin()
                #insert the new project into the db
                proj_ins_dict = {"proj_id":project_id,"proj_name":project_name,"host_system_name":self.controller, "host_system_ip":self.api_ip}
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

        #add the admin to the project who created the project
        if(self.username == 'admin'):
            try:
                #add the "cloud" admin to the project as an admin - admin gets added to all projects in the system
                add_admin = {'username':'admin','user_role':'admin','project_id':project_id}
                admin = self.keystone_users.add_user_to_project(add_admin)
            except Exception as e:
                logger.sys_error('Could not add the admin to %s'%(project_id))
                raise Exception('Could not add the admin to %s'%(project_id))
        else:
            #try:
            #add the admin user to the project as an admin
            add_projadmin = {'username':self.username,'user_role':'admin','project_id':project_id}
            projadmin = self.keystone_users.add_user_to_project(add_projadmin)
            #except Exception as e:
            #    logger.sys_error('Could not add the project admin to %s'%(project_name))
            #    raise Exception('Could not add the project admin to %s'%(project_name))
        return project_id

    def remove_tenant(self,project_id):
        """
        DESC: Remove a tenant from the OpenStack system and from the Transcirrus DB
        INPUT: project_id
        ACCESS: Only the admin can remove the project
        OUTPUT: 'OK' if task completed successfully
        """
        if((not project_id) or (project_id == "")):
            logger.sys_error("No project id was specified for the new project.")
            raise EXception("No project id was specified for the new project.")

        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        #check if the is_admin flag set to 1 - sanity check
        if(self.is_admin == 1):
            #logger.sys_error("User is identified as a user or an admin.")
            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient, can not list endpoints.")
                raise Exception("User status not sufficient, can not list endpoints.")

            #standard users can not delete a project
            if(self.user_level >= 1):
                logger.sys_error("Only admins and power users can may list endpoints.")
                raise Exception("Only admins and power users can may list endpoints.")
            """
            #need to get the project ID from the Transcirrus DB
            try:
                select_dict = {"select":"proj_id", "from":"projects", "where":"proj_name='%s'" %(project_name)}
                select = self.db.pg_select(select_dict)
                print select
            except Exception as e:
                logger.sql_error("Could not get the project_id from the Transcirrus DB.%s" %(e))
                raise
            """
            try:
                #build an api connection for the admin user.
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                body = ""
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/tenants/%s' %(project_id)
                print "API Path is:"
                print api_path
                token = self.adm_token
                sec = 'FALSE'
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 200 or 201
                if((rest['response'] == 201) or (rest['response'] == 200) or (rest['response'] == 204)):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    logger.sys_info("Project: %s has been removed from the Transcirrus DB." %(project_id))
                    #delete the project from transcirrus db and update the user account
                    try:
                        self.db.pg_transaction_begin()
                        del_dict = {"table":'projects',"where":"proj_id='%s'" %(project_id)}
                        self.db.pg_delete(del_dict)

                        user_up_dict = {'table':"trans_user_info",'set':"""user_primary_project='NULL',user_project_id='NULL'""",'where':"user_project_id='%s'" %(project_id)}
                        self.db.pg_update(user_up_dict)
                        self.db.pg_transaction_commit()
                    except Exception as e:
                        logger.sql_error("Could not commit the transaction to the Transcirrus DB.%s, Contact an Admin" %(e))
                        self.db.pg_transaction_rollback()
                        raise
                    #close all of the db connections that are open
                    self.db.pg_close_connection()
                    #return OK if good to go
                    return "OK"
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except Exception as e:
                logger.sys_error("Could not remove the project %s" %(e))
        else:
            logger.sys_error("Admin flag not set, could not create the new project ")

    def list_all_tenants(self):
        """
        DESC: Get all of the project names and IDs from the Transcirrus Db
        INPUT: None
        Output:array of r_dict - project_name
                               - project_id
        ACCESS: This operation is only available to admins
        """
        logger.sys_info('\n**Listing projects. Component: Keystone Def: list_all_tenants**\n')
        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        #check if the is_admin flag set to 1 - sanity check
        if(self.is_admin == 1):
            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient, can not list projects.")
                raise Exception("User status not sufficient, can not list projects.")
    
            #standard users can not create a project
            if(self.user_level >= 1):
                logger.sys_error("Only admins can list projects.")
                raise Exception("Only admins can list projects.")

            #query the DB and get the list of projects in the OpenStack Environment
            projects=None
            if(self.username == 'admin'):
                try:
                    #insert the new project into the db
                    select_dict = {"select":'proj_name,proj_id',"from":'projects'}
                    projects = self.db.pg_select(select_dict)
                except Exception as e:
                    logger.sql_error("Could not retrieve the tenants." %(e))
                    raise
            else:
                try:
                    select_dict = {"select":'proj_name,proj_id',"from":'trans_user_projects','where':"user_id='%s'"%(self.user_id)}
                    projects = self.db.pg_select(select_dict)
                except Exception as e:
                    logger.sql_error("Could not retrieve the tenants." %(e))
                    raise

            #initialize the r_array
            r_array = []
            for project in projects:
                r_dict = {}
                r_dict['project_name'] = project[0].rstrip()
                r_dict['project_id'] = project[1].rstrip()
                r_array.append(r_dict)
            return r_array
        else:
            logger.sys_error("Admin flag not set, could not list projects")

    def get_tenant(self,project_id):
        """
        DESC: Get the information for a specific project from the Transcirrus DB
        INPUT: project_id
        OUTPUT: r_dict - project_id
                       - project_name
                       - def_security_key_name
                       - def_security_key_id
                       - def_security_group_id
                       - def_security_group_name
                       - host_system_name
                       - host_system_ip
                       - def_network_name
                       - def_network_id
        ACCESS: Admins can get any project, users can only view the primary project
              they belong to.
        NOTE: If any of the project variables are empty a None will be returned for that variable.
        """
        
        if(not project_id):
            logger.sys_error("Did not pass a project id to the get_tenant operation.")
            raise Exception ("Did not pass a project id to the get_tenant operation.")

        #connect to the db
        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        #get the project info
        try:
            get = {"select":'*', "from":'projects', "where":"proj_id='%s'" %(project_id)}
            proj = self.db.pg_select(get)
        except:
            logger.sql_error("Could not get the project info for project: %s" %(project_id))
            raise Exception("Could not get the project info for project: %s" %(project_id))

        logger.sys_info('%s proj stuff' %(proj))
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

    def list_tenant_users(self,project_id):
        """
        DESC: list the users that are members of the project. Admins and power users can do this.
        INPUT: project_id
        OUTPUT: array of r_dict - username
                                - user_id
        ACCESS: All users can list project users in the project they belong to. Admins can list users
                in any project.
        NOTE:none
        """
        if(project_id == ""):
            logger.sys_error("Must specify the project id.")
            raise Exception("Must specify the project id.")

        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        try:
            """
            if(self.is_admin == 1):
                self.get_users = {'select':'user_name,keystone_user_uuid','from':'trans_user_info','where':"user_project_id='%s'"%(project_id)}
            else:
            """
            self.get_users = {'select':'user_name,keystone_user_uuid','from':'trans_user_info','where':"user_project_id='%s'"%(project_id)}
            self.users = self.db.pg_select(self.get_users)
        except:
            logger.sys_error("Could not get user list for %s."%(project_id))
            raise Exception("Could not get user list for %s."%(project_id))

        r_array = []
        for user in self.users:
            r_dict = {'username':user[0],'user_id':user[1]}
            r_array.append(r_dict)
        return r_array

    def update_tenant(self):
        pass
