#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json

sys.path.append('../../common')
import logger
import config

from api_caller import caller

sys.path.append(config.DB_PATH)
from postgres import pgsql

class user_ops:
    
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

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

    #DESC: create a new user in both the transcirrus and OpenStack Keystone DB
    #INPUT: self object
    #       new_user_dict - dictionary containg the new user info
    #                       username
    #                       password
    #                       userrole - admin,pu,user
    #                       email
    #                       project_name  name of the project to add the user to OPTIONAL
    #                               if project_name is not set, the admin users project will be used
    #OUTPUT: Dictionary containing the 
    def create_user(self,new_user_dict):
        #Only an admin can create a new user
        #check to make sure that new_user_dict is present
        new_user_proj_id = "NULL"
        if(not new_user_dict):
            logger.sys_error("new_user_dict not specified for create_user operation.")
            raise Exception("new_user_dict not specified for create_user operation.")
        #Check to make sure that the username,password and userrole are valid
        if((not new_user_dict['username'])or(not new_user_dict['password'])or(not new_user_dict['userrole'])):
            logger.sys_error("Blank parametrs passed into create user operation, INVALID.")
            raise Exception("Blank parametrs passed into create user operation, INVALID.")
        #make sure that only the admin pu or user role specifeid
        #if((new_user_dict['userrole'] != "admin") or (new_user_dict['userrole'] != "pu") or (new_user_dict['userrole'] != "user")):
        #    logger.sys_error("INVALID user role passed to create_user operation.")
        #    raise Exception("INVALID user role passed to create_user operation.")
        if('project_name' not in new_user_dict):
            #set the tenant id to the admin users project id
            new_user_proj_id = self.project_id

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

            #need to figure out the group id based on the role given
            group_id = ""
            key_role = ""
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
                #Try to connect to the transcirrus db
                self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
                logger.sql_info("Connected to the Transcirrus DB to do keystone user operations.")
                #get the project ID if not using the admins
                if(new_user_proj_id == "NULL"):
                    select_proj_id = {"select":"proj_id","from":"projects","where":"proj_name='%s'" %(new_user_dict['project_name'])}
                    proj_id = self.db.pg_select(select_proj_id)
                    new_user_proj_id = proj_id[0][0]
            except Exception as e:
                logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
                raise

            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)

                #add the new user to openstack
                body = '{"user": {"email":"%s", "password": "%s", "enabled": true, "name": "%s", "tenantId":"%s"}}' %(new_user_dict['email'],new_user_dict['password'],new_user_dict['username'],new_user_proj_id)
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2.0/users'
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                new_user_id = ""
                #check the response and make sure it is a 200 or 201
                if((rest['response'] == 201) or (rest['response'] == 200)):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    load = json.loads(rest['data'])
                    new_user_id = load['user']['id']
                else:
                    _http_codes(rest['response'],rest['reason'])

                user_role_dict = {"username":new_user_dict['username'],"project_id":new_user_dict['tenant_id'],"role":key_role}
                add_role_to_user(user_role_dict)
            except Exception as e:
                logger.sql_error("Could not get the project_id from the Transcirrus DB.%s" %(e))
                #back the user out of the transcirrus DB if the db works and the REST API fails
                raise
            
            try:
                #get the project id from the transcirrus DB
                get_proj_name = {"select":"proj_name", "from":"projects", "where":"proj_id='%s'" %(new_user_proj_id)}
                proj_name = self.db.pg_select(get_proj_name)
                
                #insert data in transcirrus DB
                ins_dict = {"user_name":new_user_dict['username'],"user_group_membership":new_user_dict['userrole'],"user_group_id":group_id,"user_enabled":'TRUE',"keystone_role":key_role,"user_primary_project":proj_name[0][0],"user_project_id":new_user_proj_id,"keystone_user_uuid":new_user_id}
                insert = self.db.pg_insert("trans_user_info",ins_dict)
                self.db.pg_close_connection()
            except Exception as e:
                logger.sql_error("%s" %(e))
                #back the user out if an exception is thrown
                raise

            r_dict = {"username":new_user_dict['username'],"user_id":new_user_id,"project_id":new_user_proj_id}
            return r_dict

        else:
            logger.sys_error("Admin flag not set, could not create the new user.")


    def remove_user():
        print "yo"
    
    def create_user_role():
        print "not implemented"
    def remove_user_role():
        print "not implemeted"
    def update_user():
        print "yo"
    def update_user_role():
        print "not implemented"
    def list_user_tenants():
        print "not implemented"
    def list_user_roles():
        print "not implemented"

    def add_role_to_user(self, user_role_dict):
        #user_role_dict = {"username":new_user_dict['username'],"project_id":new_user_dict['tenant_id'],"role":key_role}
        #Only an admin can add a role to a user
        if(not user_role_dict):
            logger.sys_error("user_role_dict not specified for add_role_to_user operation.")
            raise Exception("user_role_dict not specified for add_role_to_user operation.")
        #Check to make sure that the username,password and userrole are valid
        if((not user_role_dict['username'])or(not user_role_dict['project_id'])or(not user_role_dict['role'])):
            logger.sys_error("Blank parametrs passed into add roll to user operation, INVALID.")
            raise Exception("Blank parametrs passed into add roll to user operation, INVALID.")
        if((user_role_dict['role'] == 'admin') or (user_role_dict['role'] == 'Member')):
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
            except Exception as e:
                logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
                raise
        
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

                #check if project is valid
                select_proj = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(user_role_dict['project_id'])}
                proj = self.db.pg_select(select_proj)
                if(type(proj[0][0]) is str):
                    logger.sys_info("Project id is valid in the transcirrus DB, for operation add_role_to_user.")
                else:
                    logger.sys_error("Project id is not valid in the transcirrus DB, for operation add_role_to_user Project: %s." %(user_role_dict['project_id']))
                    raise Exception("Project id is not valid in the transcirrus DB, for operation add_role_to_user Project %s." %(user_role_dict['project_id']))
                self.db.pg_close_connection()
            except Exception as e:
                logger.sql_error("Database Operation failed for add_role_to_user.")
                raise

            #Verify that the role and tenant exist in Openstack
            #NOTE: NEED TO MAKE FUNCTION IN THE TENANTS LIB TO DO THIS
            
            #Verify the role
            #NOTE: NEED TO MAKE A FUNCTION TO DO THIS

            #Determin the Keystone role ID
            key_role = ""
            if (user_role_dict['role'] == 'admin'):
                key_role = config.DEFAULT_ADMIN_ROLE_ID
            elif(user_role_dict['role'] == 'Member'):
                key_role = config.DEFAULT_MEMBER_ROLE_ID
            else:
                logger.sys_error("An invalid role name was passed, check your config.")
                raise Esception("An invalid role name was passed, check your config.")
            #add the role to the user
            new_role_name = ""
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)

                #add the new user to openstack
                body = ""
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/v2.0/tenants/%s/users/%s/roles/OS-KSADM/%s' %(user_role_dict['project_id'],user[0][0],key_role)
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                new_user_id = ""
                #check the response and make sure it is a 200 or 201
                if(rest['response'] == 200):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    load = json.loads(rest['data'])
                    new_role_name = load['role']['name']
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                logger.sys_error('%s' %(e))
                raise
            r_dict = {"username":new_role_name,"role":new_role_name}
            return r_dict
        else:
            logger.sys_error("Admin flag not set, could not create the new user.")

    def remove_role_from_user():
        print "not implemented"

        
    def get_user_credentials():
        print "not implemented"
    def update_user_credentials():
        sunday
    def remove_user_credentials():
        sunday