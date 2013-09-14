#!/usr/bin/python
#tested and works as of 7-21-2013

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json
import re

sys.path.append('../../common')
import logger
import config
import util

from api_caller import caller

sys.path.append(config.DB_PATH)
from postgres import pgsql

class user_ops:
    def __init__(self,user_dict):
        """
        DESC: Constructor to build out the tokens object
        INPUT: user_dict dictionary containing - built in auth.py
               username
               password
               project_id - could be blank
               token
               status_level
               user_level
               is_admin
               sec - optional - use HTTPS sec = TRUE defaults to FALSE
        """
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        else:
            self.username = user_dict['username']
            self.password = user_dict['password']
            self.project_id = user_dict['project_id']
            if((self.project_id == 'NULL') or (not user_dict['project_id'])):
                logger.sys_error("In order to perform user operations, Admin user must be assigned to project")
                raise Exception("In order to perform user operations, Admin user must be assigned to project")
            self.token = user_dict['token']
            self.status_level = user_dict['status_level']
            self.user_level = user_dict['user_level']
            self.is_admin = user_dict['is_admin']
            self.adm_token = user_dict['adm_token']
            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'
                
            #Retrieve all default values from the DB????
            #Screw a config file????
            #get the default cloud controller info
            self.controller = config.DEFAULT_CLOUD_CONTROLER
            self.api_ip = config.DEFAULT_API_IP
            #self.db = user_dict['db']

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")
            raise Exception("No admin tokens passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

    def create_user(self,new_user_dict):
        """
        DESC: create a new user in both the transcirrus and OpenStack Keystone DB
        INPUT: new_user_dict - username - req
                             - password - req
                             - userrole - req - admin,pu,user
                             - email - req
                             - project_name - op - if project_name is not set, project is set to the NULL state
        OUTPUT: r_dict - user_name
                       - user_id
                       - project_id
                       
        ACCESS: Only an admin can create a new user account.
        NOTE: If the project is not specified then the user project is set to NULL. The user can then be added to a project later.
              If the project name is not specified the user will be default be set to an ordinary user.
        """
        #check to make sure that new_user_dict is present
        if(not new_user_dict):
            logger.sys_error("new_user_dict not specified for create_user operation.")
            raise Exception("new_user_dict not specified for create_user operation.")
        #Check to make sure that the username,password and userrole are valid
        if((not new_user_dict['username'])or(not new_user_dict['password'])or(not new_user_dict['userrole'])):
            logger.sys_error("Blank parametrs passed into create user operation, INVALID.")
            raise Exception("Blank parametrs passed into create user operation, INVALID.")
        if(('username' not in new_user_dict) or ('password' not in new_user_dict) or ('userrole' not in new_user_dict) or ('email' not in new_user_dict)):
            logger.sys_error("Required parametrs not passed into create user operation, INVALID.")
            raise Exception("Required parametrs not passed into create user operation, INVALID.")
        if(not re.match(r"^[A-Za-z0-9\.\+_-]+\@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", new_user_dict['email'])):
            logger.sys_error("Invalid email syntax given.")
            raise Exception("Invalid email syntax given.")
        
        #check if the user creating a new account is an admin
        if(self.is_admin == 1):
            logger.sys_info("User identified as an admin.")
            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient.")
                raise Exception("User status not sufficient.")

            #standard users can create a project
            if(self.user_level >= 1):
                logger.sys_error("Only admins can create a project")
                raise Exception("Only admins can create a project.")

            try:
                #Try to connect to the transcirrus db
                self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
                logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")
            except Exception as e:
                logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
                raise e

            group_id = None
            key_role = None
            if('project_name' in new_user_dict):
                #need to figure out the group id based on the role given
                #NOTE for now we are sticking with the default admin,Member roles in Keystone.
                #all access is controlled with Transcirrus permissions. Later we will add the
                #ability to create and use custom roles in keystone.
                if(new_user_dict['userrole'] == 'admin'):
                    group_id = 0
                    key_role = 'admin'
                elif(new_user_dict['userrole'] == 'pu'):
                    group_id = 1
                    key_role = 'Member'
                else:
                    group_id = 2
                    key_role = 'Member'

                try:
                    #get the project ID if not using the admins
                    select_proj_id = {"select":"proj_id","from":"projects","where":"proj_name='%s'" %(new_user_dict['project_name'])}
                    proj_id = self.db.pg_select(select_proj_id)
                    self.new_user_proj_id = proj_id[0][0]
                except:
                    logger.sql_error("Could not get the project ID for project %s" %(new_user_dict['project_name']))
                    raise Exception("Could not get the project ID for project %s" %(new_user_dict['project_name']))
            else:
                #This is the default case if the user is being created
                #without a project. When we add the user to a project then
                #we can specify if the user will be a power_user or reamin a standard user.
                group_id = 2
                key_role = 'Member'
                self.new_user_proj_id = "NULL"

            try:
                #build an api connection for the admin user. NOTE project ID is the admin user project id
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the new user to openstack
                if('project_name' not in new_user_dict):
                    body = '{"user": {"email":"%s", "password": "%s", "enabled": true, "name": "%s", "tenantId": null}}' %(new_user_dict['email'],new_user_dict['password'],new_user_dict['username'])
                else:
                    body = '{"user": {"email":"%s", "password": "%s", "enabled": true, "name": "%s", "tenantId": "%s"}}' %(new_user_dict['email'],new_user_dict['password'],new_user_dict['username'],self.new_user_proj_id)
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/users'
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                new_user_id = None
                #check the response and make sure it is a 200 or 201
                if((rest['response'] == 201) or (rest['response'] == 200)):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    load = json.loads(rest['data'])
                    new_user_id = load['user']['id']
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                logger.sql_error("Could not get the project_id from the Transcirrus DB.%s" %(e))
                #back the user out of the transcirrus DB if the db works and the REST API fails
                raise e

            if(self.new_user_proj_id != "NULL"):
                self.proj_name = new_user_dict['project_name']
            else:
                self.proj_name = "NULL"

            try:
                self.db.pg_transaction_begin()
                #insert data in transcirrus DB
                ins_dict = {"user_name":new_user_dict['username'],"user_group_membership":new_user_dict['userrole'],"user_group_id":group_id,"user_enabled":'TRUE',"keystone_role":key_role,"user_primary_project":self.proj_name,"user_project_id":self.new_user_proj_id,"keystone_user_uuid":new_user_id,"user_email":new_user_dict['email']}
                insert = self.db.pg_insert("trans_user_info",ins_dict)
                self.db.pg_transaction_commit()
                self.db.pg_close_connection()
            except Exception as e:
                self.db.pg_transaction_rollback()
                logger.sql_error("%s" %(e))
                #back the user out if an exception is thrown
                raise e

            r_dict = {"username":new_user_dict['username'],"user_id":new_user_id,"project_id":self.new_user_proj_id}
            return r_dict

        else:
            logger.sys_error("Admin flag not set, could not create the new user.")
            raise Exception("Admin flag not set, could not create the new user.")

    def remove_user(self,delete_dict):
        """
        DESC: Removes a user from the Keystone Db and th Transcirrus DB
              Admin must be in the same project as user they are removeing
              only admins can remove users includeing other admins
        INPUTS: delete_dict - username - req
                            - userid - req
        OUTPUTS: OK if successful or Exception
        ACCESS: Only an admin can delete a user account.
        NOTE: You will need to get the userid from the database by using the keystone_tenants.tenant_ops.list_tenant_users().
              The userid will be in the form of a UUID.
        """
        #check to make sure that new_user_dict is present
        if(not delete_dict):
            logger.sys_error("delete_dict not specified for remove_user operation.")
            raise Exception("delete_dict not specified for remove_user operation.")
        #Check to make sure that the username,password and userrole are valid
        if((not delete_dict['username'])or(not delete_dict['userid'])):
            logger.sys_error("Blank parametrs passed into remove user operation, INVALID.")
            raise Exception("Blank parametrs passed into remove user operation, INVALID.")
        if(('username' not in delete_dict) or ('userid' not in delete_dict)):
            logger.sys_error("Required parametrs missing for remove user operation, MISSING PARAM.")
            raise Exception("Required parametrs missing for remove user operation, MISSING PARAM.")

        #check if the user creating a new account is an admin
        if(self.is_admin == 1):
            try:
                #Try to connect to the transcirrus db
                self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
                logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")

                #get the project ID of the user you want to remove - Only primary project for the prototype
                get_proj_id = {"select":"user_project_id", "from":"trans_user_info","where":"user_name='%s'" %(delete_dict['username'])}
                proj_id = self.db.pg_select(get_proj_id)
            except Exception as e:
                logger.sys_error("%s" %(e))
                raise

            #Compare the admin project id to the user project id
            #only an admin in the same project can disable a user in a project
            if((self.project_id != proj_id[0][0]) or (self.user_level >= 1)):
                logger.sys_error("Admin and User not in the same project, can not remove user.")
                raise Exception("Admin and User not in the same project, can not remove user.")

            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient for remove user operation.")
                raise Exception("User status not sufficient for remove user operation.")

            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)

                #add the new user to openstack
                body = ""
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/users/%s' %(delete_dict['userid'])
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 200 or 201
                if((rest['response'] == 200) or (rest['response'] == 204)):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))

                    #update the transcirrus db
                    del_dict = {"table":'trans_user_info',"where":"user_name='%s'" %(delete_dict['username'])}
                    self.db.pg_delete(del_dict)
                    self.db.pg_close_connection()
                    return "OK"
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                logger.sql_error("Could not get the project_id from the Transcirrus DB.%s" %(e))
                #back the user out of the transcirrus DB if the db works and the REST API fails
                raise
        else:
            logger.sys_error("Admin flag not set, could not create the new user.")

    #Not sure why I called it disable dict???????
    def toggle_user(self,disable_dict):
        """
        DESC: Disable a user in both the Keystone and Transcirrus DB
        INPUT: disable_dict - username - req - name of the user to toggle
                            - toggle - req - enable/disable
                            - userid - op
        OUTPUT: r_dict - username
                       - userid
                       - toggle status(enable|disable) or exception
        ACCESS: Only an admin can toggle the user status.
        NOTE: The userid input can be given as an optional parameter. If it is not given then it will be
              looked up in the database.
        """
        #Check to make sure required params are given
        if(not disable_dict):
            logger.sys_error("new_user_dict not specified for create_user operation.")
            raise Exception("new_user_dict not specified for create_user operation.")
        #Check to make sure that the username,password and userrole are valid
        if((not disable_dict['username'])or(not disable_dict['toggle'])):
            logger.sys_error("Blank parametrs passed into create user operation, INVALID.")
            raise Exception("Blank parametrs passed into create user operation, INVALID.")
        #make sure that toggle is set to enable or disable only
        if((disable_dict['toggle'] == 'enable') or (disable_dict['toggle'] == 'disable')):
            #HACK
            logger.sys_error("Toggle value is invalid.")
        else:
            logger.sys_error("Toggle value is invalid.")
            raise Exception("Toggle value is invalid.")
        #Set userid to NULL to easily track
        if(('userid' not in disable_dict) or (disable_dict['userid'] == "")):
            disable_dict['userid'] = 'NULL'

        toggle = None
        if(disable_dict['toggle'] == 'enable'):
            toggle = 'true'
        elif(disable_dict['toggle'] == 'disable'):
            toggle = 'false'

        #if the userid is not specified connect to the DB and get it
        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
            logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")
            #get the project ID if not using the admins
            if(disable_dict['userid'] == 'NULL'):
                logger.sql_info("Userid was NULL for toggle user operation, retrieving userid from Transcirrus DB.")
                select_user = {"select":"user_project_id,keystone_user_uuid","from":"trans_user_info","where":"user_name='%s'" %(disable_dict['username'])}
                user = self.db.pg_select(select_user)
                disable_dict['userid'] = user[0][1]
            else:
                logger.sql_info("Userid was not NULL for toggle user operation.")
                select_user = {"select":"user_project_id","from":"trans_user_info","where":"user_name='%s'" %(disable_dict['username'])}
                user = self.db.pg_select(select_user)
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
            raise

        #Create an API connection with the admin
        if(self.is_admin == 1):
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)

                #add the new user to openstack
                body = '{"user": {"enabled": %s, "id":"%s"}}' %(toggle,disable_dict['userid'])
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/users/%s' %(disable_dict['userid'])
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)

                #check the response and make sure it is a 200 or 201
                if(rest['response'] == 200):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    self.db.pg_transaction_begin()
                    #update the transcirrus db
                    update_dict = {'table':"trans_user_info",'set':"user_enabled='%s'" %(toggle.upper()),'where':"keystone_user_uuid='%s'" %(disable_dict['userid'])}
                    self.db.pg_update(update_dict)
                    self.db.pg_transaction_commit()
                    self.db.pg_close_connection()

                    r_dict = {"username":disable_dict['username'],"userid":disable_dict['userid'],"toggle":disable_dict['toggle']}
                    return r_dict
                else:
                    _http_codes(rest['response'],rest['reason'])
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not get the project_id from the Transcirrus DB.")
                #back the user out of the transcirrus DB if the db works and the REST API fails
                raise Exception("Could not get the project_id from the Transcirrus DB.")
        else:
            logger.sys_error("Admin flag not set, could not create the new user.")

    def add_user_to_project(self, user_role_dict):
        """
        DESC: Add a user to a project. Only an admin can perform this operation
        INPUT: user_role_dict - username - req
                              - user_role - req - admin/pu/user
                              - project_name - req - name of the project to add the user to
        OUTPUT: r_dict - project_name
                       - project_id
        ACCESS: Only an admin can add a user to a project.
        NOTE: This call is actually to an API call that addsa a user to an OpenStack role. It implicitly adds
              the user to project specified.
        """
        if(not user_role_dict):
            logger.sys_error("user_role_dict not specified for add_role_to_user operation.")
            raise Exception("user_role_dict not specified for add_role_to_user operation.")
        if((user_role_dict['user_role'] == 'admin') or (user_role_dict['user_role'] == 'user') or (user_role_dict['user_role'] == 'pu')):
            logger.sys_info("Valid Keystone user role passed")
        else:
            logger.sys_info("Invalid Keystone user role passed")
            raise Exception("Invalid Keystone user role passed")

        #check if the user creating a new account is an admin
        if(self.is_admin == 1):
            logger.sys_info("User identified as an admin.")
            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient.")
                raise Exception("User status not sufficient.")

            #standard users can not add roles to users
            if(self.user_level >= 1):
                logger.sys_error("Only admins can add roles to users.")
                raise Exception("Only admins can add roles to users.")

            try:
                #Try to connect to the transcirrus db
                self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
                logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")
            except:
                logger.sql_error("Could not connect to the Transcirrus DB.")
                raise Exception("Could not connect to the Transcirrus DB.")

            #check all of the variables and make sure that they are legit
            #NOTE: the log messages are not includeing the %s specifics.
            try:
                #check if valid username
                select_user = {"select":"keystone_user_uuid","from":"trans_user_info","where":"user_name='%s'" %(user_role_dict['username'])}
                user = self.db.pg_select(select_user)
                if(type(user[0][0]) is str):
                    logger.sys_info("Username is valid in the transcirrus DB, for operation add_role_to_user.")
                else:
                    logger.sys_error("Username is not valid in the transcirrus DB, for operation add_role_to_user USER: %s." %(user_role_dict['username']))
                    raise Exception("Username is not valid in the transcirrus DB, for operation add_role_to_user USER: %s." %(user_role_dict['username']))
            except:
                logger.sql_error("Database Operation failed for add_user_to_project.")
                raise Exception("Database Operation failed for add_user_to_project.")

            try:
                #check if project is valid
                select_proj = {"select":"proj_id","from":"projects","where":"proj_name='%s'" %(user_role_dict['project_name'])}
                proj = self.db.pg_select(select_proj)
                if(type(proj[0][0]) is str):
                    logger.sys_info("Project id is valid in the transcirrus DB, for operation add_role_to_user.")
                else:
                    logger.sys_error("Project id is not valid in the transcirrus DB, for operation add_role_to_user Project: %s." %(user_role_dict['project_id']))
                    raise Exception("Project id is not valid in the transcirrus DB, for operation add_role_to_user Project %s." %(user_role_dict['project_id']))
            except:
                logger.sql_error("Database Operation failed for add_user_to_project.")
                raise Exception("Database Operation failed for add_user_to_project.")

            #Determin the Keystone role ID
            #Query the DB to get the ID for the member role and the admin role
            try:
                #get the role_id for admin or Member from db
                if(user_role_dict['user_role'] == 'admin'):
                    select_id = {"select":"param_value","from":"trans_system_settings","where":"parameter='default_admin_role_id'"}
                else:
                    select_id = {"select":"param_value","from":"trans_system_settings","where":"parameter='default_member_role_id'"}
                key_role = self.db.pg_select(select_id)
            except:
                logger.sql_error("Could not get the default role id for the %s ." %(user_role_dict['user_role']))
                raise Exception("Could not get the default role id for the %s ." %(user_role_dict['user_role']))

            try:
                #build an api connection for the admin user. NOTE project ID is the admin user project id
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the user to the project with the proper keystone Role
                body = ""
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "python-keystoneclient"}
                function = 'PUT'
                api_path = '/v2.0/tenants/%s/users/%s/roles/OS-KSADM/%s' %(proj[0][0],user[0][0],key_role[0][0])
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'35357'}
                rest = api.call_rest(rest_dict)
                new_user_id = ""
                #check the response and make sure it is a 200
                if(rest['response'] == 200):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    load = json.loads(rest['data'])
                    self.db.pg_transaction_begin()
                    #need to update trans_usr_table
                    update_dict = {'table':"trans_user_info",'set':"user_primary_project='%s',user_project_id='%s'" %(user_role_dict['project_name'],proj[0][0]),'where':"keystone_user_uuid='%s'" %(user[0][0])}
                    self.db.pg_update(update_dict)
                    self.db.pg_transaction_commit()
                    #close any open db connections
                    self.db.pg_close_connection()
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                self.db.pg_transaction_rollback()
                logger.sys_error('%s' %(e))
                raise e
            r_dict = {"project":user_role_dict['project_name'],"project_id":proj[0][0]}
            return r_dict
        else:
            logger.sys_error("Admin flag not set, could not create the new user.")

    def remove_user_from_project(self,remove_role):
        """
        DESC: removes a specifc keystone role from a user on a project basis, if a role is not specified
              then all of the roles for that user in the project are removed.
        INPUT: del_dict - username
                        - project_name
        OUTPUT: OK if successful
        ACCESS: Only an admin can remove a user from a project.
        NOTE: When a user is removed from a project by an admin, no matter what the role of that user is,
              they will be switched back to a standard user. When the user is added to a new project the user
              can then be added as a new role, admin/pu/user
        """
        if(not remove_role):
            logger.sys_error("remove_role not specified for remove_role_from_user operation.")
            raise Exception("remove_role not specified for remove_role_from_user operation.")
        #Check to make sure that the username and keystone role are specified
        if((not remove_role['username']) or (not remove_role['project_name'])):
            logger.sys_error("Blank parametrs passed into remove_role_from_user operation, INVALID.")
            raise Exception("Blank parametrs passed into remove_role_from_user, INVALID.")

        #check if the user creating a new account is an admin
        if(self.is_admin == 1):
            logger.sys_info("User identified as an admin.")
            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient.")
                raise Exception("User status not sufficient.")

            #standard users can not add roles to users
            if(self.user_level >= 1):
                logger.sys_error("Only admins can add roles to users.")
                raise Exception("Only admins can add roles to users.")

            #connect to the transcirrus DB and the keystone DB
            try:
                #Try to connect to the transcirrus db
                self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
                logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")

                self.key_db = pgsql(config.OS_DB,config.OS_DB_PORT,config.KEYSTONE_DB_NAME,config.KEYSTONE_DB_USER,config.KEYSTONE_DB_PASS)
                logger.sql_info("Connected to the Keystone DB to do keystone user operations.")
            except:
                logger.sql_error("Could not connect to the DB.")
                raise Exception("Could not connect to the DB.")

            #get the userid and tenant id from the transcirrus db
            try:
                get_user_id = {"select":"keystone_user_uuid,user_project_id,keystone_role","from":"trans_user_info","where":"user_name='%s'" %(remove_role['username'])}
                user_id = self.db.pg_select(get_user_id)

            except:
                logger.sql_error("Could not connect to the DB.")
                raise Exception("Could not connect to the DB.")

            #get the keystone role_id
            try:
                if(user_id[0][2] == 'admin'):
                    param = 'default_admin_role_id'
                else:
                    param = 'default_member_role_id'

                get_key_role_id = {"select":'param_value',"from":'trans_system_settings',"where":"parameter='%s'" %(param)}
                role_id = self.db.pg_select(get_key_role_id)
            except:
                logger.sql_error("Could not find the UUID for Keystone role %s." %(user_id[0][2]))
                raise Exception("Could not find the UUID for Keystone role %s." %(user_id[0][2]))

            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #remove the role from the user on the tenant
                body = ""
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/tenants/%s/users/%s/roles/OS-KSADM/%s' %(user_id[0][1],user_id[0][0],role_id[0][0])
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 200 or 201
                if(rest['response'] == 204):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    try:
                        self.db.pg_transaction_begin()
                        up_dict = {'table':"trans_user_info",'set':"keystone_role='Member',user_project_id='NULL',user_primary_project='NULL'",'where':"user_name='%s'" %(remove_role['username'])}
                        self.db.pg_update(up_dict)
                        self.db.pg_transaction_commit()
                        self.db.pg_close_connection()
                    except:
                        self.db.pg_transaction_rollback()
                        logger.sql_error("Could not update user information in the Transcirrus DB.")
                        raise Exception("Could not update user information in the Transcirrus DB.")
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                logger.sys_error('%s' %(e))
                raise
            r_dict = {"response":rest['response'],"reason":rest['reason']}
            return r_dict
        else:
            logger.sys_error("Admin flag not set, could not create the new user.")

    def get_user_info(self,user_dict):
        """
        DESC: Get information in regards to a specific user.
        INPUT: user_dict - username
                         - project_name
        OUTPUT: r_dict - username
                       - user_id
                       - prinmary_project
                       - primary_proj_id
                       - user_role
                       - email
                       - user_enabled
        ACCESS: Only admins can get specific user information
        NOTE: none
        """
        if(not user_dict):
            logger.sys_error("user_dict not specified for get_user_info operation.")
            raise Exception("user_dict not specified for get_user_info operation.")
        #Check to make sure that the username and keystone role are specified
        if((not user_dict['username']) or (not user_dict['project_name'])):
            logger.sys_error("Blank parametrs passed into get_user_info operation, INVALID.")
            raise Exception("Blank parametrs passed into get_user_info, INVALID.")

        #check if the calling user is an admin and if so proceed
        if(self.is_admin == 1):
            logger.sys_info("User identified as an admin.")
            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient.")
                raise Exception("User status not sufficient.")

            #connect to the transcirrus DB and the keystone DB
            try:
                #Try to connect to the transcirrus db
                self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
                logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")
            except Exception as e:
                logger.sql_error("Could not connect to the DB, %s" %(e))
                raise

            #get the user info from the transcirrus db
            try:
                get_user = {"select":"*","from":"trans_user_info","where":"user_name='%s'" %(user_dict['username']), "and": "user_primary_project = '%s'" %(user_dict['project_name'])}
                user_info= self.db.pg_select(get_user)
            except Exception as e:
                logger.sql_error("Could not find user information in Transcirrus DB., %s" %(e))
                raise

            #call the REST api to get info from keystone - used as a check more then anything else.
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)

                #remove the role from the user on the tenant
                body = ""
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/v2.0/users/%s' %(user_info[0][5])
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 200 or 201
                if((rest['response'] == 200) or (rest['response'] == 203)):
                    #read the json that is returned
                    load = json.loads(rest['data'])
                    r_dict = {"username":user_info[0][1],"user_id":user_info[0][5],"primary_project":user_info[0][6],"primary_proj_id":user_info[0][7],"user_role":user_info[0][2],"email":str(load['user']['email']),"user_enabled":user_info[0][4]}
                    return r_dict
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                logger.sys_error('%s' %(e))
                raise
        else:
            logger.sys_error("Admin flag not set, could not create the new user.")

    def get_user_credentials():
        print "not implemented"
    def update_user_credentials():
        print "not implemented"
    def remove_user_credentials():
        print "not implemented"
        
    def create_user_role():
        #Glabal and tenit based
        print "not implemented"
    def remove_user_role():
        #global and tenant based
        print "not implemeted"

    def update_user(self,update_dict):
        """
        DESC: Update basic user information in the Transcirrus DB and Keystone DB
        INPUT: update_dict - username - req - name of the user to toggle
                           - toggle - op - enable/disable
                           - email - op - new email address
                           - new_username - op - new username if any
                           - new_project - op - add or change user project membership
                           - new_role - op - assign a user to a new roles admin/pu/user
        OUTPUT: r_dict - username
                       - userid
                       - user_email
                       - user_enabled
                       - user_project
                       - user_role
        ACCESS: Only an admin can toggle the user status.
        NOTE: Unless specified the user will remian in the same user role when transfered to a new project.
        """
        #Check to make sure required params are given
        if(not update_dict):
            logger.sys_error("new_user_dict not specified for create_user operation.")
            raise Exception("new_user_dict not specified for create_user operation.")
        #Check to make sure that the username,password and userrole are valid
        if((not update_dict['username']) or ('username' not in update_dict)):
            logger.sys_error("Blank parametrs passed into create user operation, INVALID.")
            raise Exception("Blank parametrs passed into create user operation, INVALID.")

        if(self.is_admin == 1):
            try:
                #Try to connect to the transcirrus db
                self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
                logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")
            except:
                logger.sql_error("Could not connect to the DB.")
                raise Exception("Could not connect to the DB.")

            try:
                select_user = {"select":"*","from":"trans_user_info","where":"user_name='%s'" %(update_dict['username'])}
                user = self.db.pg_select(select_user)
            except:
                logger.sql_error("Could not connect to the Transcirrus DB.")
                raise Exception("Could not connect to the Transcirrus DB.")

            if('toggle' in update_dict):
                if(update_dict['toggle'] == 'enable'):
                    self.toggle = 'true'
                elif(update_dict['toggle'] == 'disable'):
                    self.toggle = 'false'
                else:
                    logger.sys_error("Invalid toggle value given.")
                    raise Exception("Invalid toggle value given.")
            else:
                #alwas defaults to true
                #may have to cahnage this.
                self.toggle = 'true'

            if('email' in update_dict):
                if(not re.match(r"^[A-Za-z0-9\.\+_-]+\@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", update_dict['email'])):
                    logger.sys_error("Invalid email syntax given.")
                    raise Exception("Invalid email syntax given.")
                else:
                    self.email = update_dict['email']
            else:
                self.email = user[0][9]

            if('new_username' in update_dict):
                self.new_username = update_dict['new_username']
            else:
                self.new_username = user[0][1]

            if('new_project' in update_dict):
                self.new_project = update_dict['new_project']
                try:
                    select_proj = {'select':"proj_id",'from':"projects",'where':"proj_name='%s'"%(update_dict['new_project'])}
                    proj = self.db.pg_select(select_proj)
                    self.new_proj_id = proj[0][0]
                except:
                    logger.sys_error("Could not get the project ID for project %s" %(update_dict['new_project']))
                    raise Exception("Could not get the project ID for project %s" %(update_dict['new_project']))
            else:
                self.new_project = user[0][6]
                self.new_proj_id = user[0][7]

            if('new_role' in update_dict):
                if((update_dict['new_role'] == 'admin') or (update_dict['new_role'] == 'pu') or (update_dict['new_role'] == 'user')):
                    self.new_role = update_dict['new_role']
                    if(update_dict['new_role'] == 'admn'):
                        self.new_key_role = 'admin'
                        self.role_id = 0
                    else:
                        if(update_dict['new_role'] == 'pu'):
                            self.role_id = 1
                        else:
                            self.role_id = 2
                        self.new_key_role = 'Member'
                else:
                    logger.sys_error("Invalid role given. Must be admin/pu/user.")
                    raise Exception("Invalid role given. Must be admin/pu/user.")
            else:
                self.new_role = user[0][2]
                self.new_key_role = user[0][8]
                self.role_id = user[0][3]

            #Create an API connection with the admin
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_logger("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the new user to openstack
                body = '{"user": {"enabled": %s, "id":"%s", "username":"%s", "email":"%s","name":"%s"}}' %(self.toggle,user[0][5],self.new_username,self.email,self.new_username)
                print body
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/users/%s' %(user[0][5])
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                print rest
                #check the response and make sure it is a 200 or 201
                if(rest['response'] == 200):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    self.db.pg_transaction_begin()
                    #update the transcirrus db
                    update = {'table':"trans_user_info",'set':"user_name='%s',user_group_membership='%s',user_group_id='%s',user_enabled='%s',user_primary_project='%s',user_project_id='%s',keystone_role='%s',user_email='%s'"
                                   %(self.new_username,self.new_role,self.role_id,self.toggle.upper(),self.new_project,self.new_proj_id,self.new_key_role,self.email),'where':"keystone_user_uuid='%s'" %(user[0][5])}
                    self.db.pg_update(update)
                    self.db.pg_transaction_commit()
                    self.db.pg_close_connection()
                else:
                    util.http_codes(rest['response'],rest['reason'])
            except:
                self.db.pg_transaction_rollback()
                logger.sql_error("Could not get the project_id from the Transcirrus DB.")
                raise Exception("Could not get the project_id from the Transcirrus DB.")

            #add the user to a new project if it needs to be.
            print update_dict
            if('new_project' in update_dict):
                user_info = {'username':self.new_username,'user_role':update_dict['new_role'],'project_name':self.new_project}
                self.add_user_to_project(user_info)

            r_dict = {'username':self.new_username,'userid':user[0][5],'user_email':self.email,'user_enabled':self.toggle, 'user_project':self.new_project, 'user_role':self.new_role}
            return r_dict
        else:
            logger.sys_error("Admin flag not set, could not create the new user.")


    #NOTE this will be added when we add the ability to have users in multiple projects.
    #OpenStack allows it, but for now we will not.
    def list_user_tenants():
        print "not implemented"
    
    #Note at some point we will allow a user to be assigned to multiple Roles,
    #however one role must be the default admin, or Member role.
    def list_user_roles():
        print "not implemented"

######Internal defs#######
def _http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")
