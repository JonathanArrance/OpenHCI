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
            #NOTE for now we are sticking with the default admin,Member roles in Keystone.
            #all access is controlled with Transcirrus permissions. Later we will add the
            #ability to create and use custom roles in keystone.
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
            except Exception as e:
                logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
                raise

            try:
                #get the project ID if not using the admins
                if('project_name' in new_user_dict):
                    select_proj_id = {"select":"proj_id","from":"projects","where":"proj_name='%s'" %(new_user_dict['project_name'])}
                    proj_id = self.db.pg_select(select_proj_id)
                    new_user_proj_id = proj_id[0][0]
            except:
                logger.sql_error("Could not get the project ID, %s" %(e))
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

            #add the role to the new user
            #NOTE: adding a role throws a 404 error on the REST call.
            #Maybe a bug in the new devstack?
            #user_role_dict = {"username":new_user_dict['username'],"project_id":new_user_proj_id,"role":key_role}
            #self.add_role_to_user(user_role_dict)

            r_dict = {"username":new_user_dict['username'],"user_id":new_user_id,"project_id":new_user_proj_id}
            return r_dict

        else:
            logger.sys_error("Admin flag not set, could not create the new user.")

    #DESC: Removes a user from the Keystone Db and th Transcirrus DB
    #      Admin must be in the same project as user they are removeing
    #      only admins can remove users includeing other admins
    #INPUTS: self object
    #        delete_dict - dictionary containg the user info
    #                    username
    #                    userid
    #OUTPUTS: OK if successful or Exception
    def remove_user(self,delete_dict):
        #Only an admin can create a new user
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

    #DESC: Disable a user in both the Keystone and Transcirrus DB
    #INPUT:self object
    #      disable_dict - dictionary containg the parameters for the user account
    #                    username - name of the user to toggle
    #                    toggle - enable/disable
    #                    userid - OPTIONAL
    #OUTPUT: dictionary conating the username,userid,toggle status(enable|disable) or exception
    def toggle_user(self,disable_dict):
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

        toggle = ""
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
            #only an admin in the same project can disable a user in a project
            if((self.project_id != user[0][0]) or (self.user_level >= 1)):
                logger.sys_error("Admin and User not in the same project, can not toggle user.")
                raise Exception("Admin and User not in the same project, can not toggle user.")

            #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
            if(self.status_level <= 1):
                logger.sys_error("User status not sufficient for toggle operation.")
                raise Exception("User status not sufficient for toggle operation.")

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

                    #update the transcirrus db
                    update_dict = {'table':"trans_user_info",'set':"user_enabled='%s'" %(toggle.upper()),'where':"keystone_user_uuid='%s'" %(disable_dict['userid'])}
                    self.db.pg_update(update_dict)
                    self.db.pg_close_connection()

                    r_dict = {"username":disable_dict['username'],"userid":disable_dict['userid'],"toggle":disable_dict['toggle']}
                    return r_dict
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                logger.sql_error("Could not get the project_id from the Transcirrus DB.%s" %(e))
                #back the user out of the transcirrus DB if the db works and the REST API fails
                raise
        else:
            logger.sys_error("Admin flag not set, could not create the new user.")

    def create_user_role():
        #Glabal and tenit based
        print "not implemented"
    def remove_user_role():
        #global and tenant based
        print "not implemeted"

    def update_user():
        #updates keystone and the transcirrus db
        print "not implemneted"

    #NOTE this will be added when we add the ability to have users in multiple projects.
    #OpenStack allows it, but for now we will not.
    def list_user_tenants():
        print "not implemented"
    
    #Note at some point we will allow a user to be assigned to multiple Roles,
    #however one role must be the default admin, or Member role.
    def list_user_roles():
        print "not implemented"

    #DESC: Add a new user to a role in the keystone DB
    #INPUT: self object
    #       new_role_dict - dictionary containg the user_role_info
    #                       username
    #                       project_id - id of the project to user is in
    #                       role - keystone role can only be admin or Member at this time
    #OUTPUT: Dictionary containing the username and keystone role
    #NOTE: need to add ability to add global role to user
    #NOTE: getting 404 error when calling REST
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
                print api_path
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

    #DESC: removes a specifc keystone role from a user on a project basis, if a role is not specified
    #then all of the roles for that user in the project are removed.
    #INPUT: Dictionary containing the username and keystone role to remove
    #OUTPUT: OK if successful
    #NOTE: used for internal admin for now. The ability to create add,remove custom user roles
    #will NOT be available in the prototype
    def remove_role_from_user(self,remove_role):
        if(not remove_role):
            logger.sys_error("remove_role not specified for remove_role_from_user operation.")
            raise Exception("remove_role not specified for remove_role_from_user operation.")
        #Check to make sure that the username and keystone role are specified
        if((not remove_role['username']) or (not remove_role['key_role'])):
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
            except Exception as e:
                logger.sql_error("Could not connect to the DB, %s" %(e))
                raise

            #HACK - Should use rest api. get the role id from keystone DB
            try:
                get_role_id = {"select":"id","from":"role","where":"name='%s'" %(remove_role['key_role'])}
                key_role_id = self.key_db.pg_select(get_role_id)
                self.key_db.pg_close_connection()
            except Exception as e:
                logger.sql_error("Could not connect to the DB, %s" %(e))
                raise

            #get the userid and tenant id from the transcirrus db
            try:
                get_user_id = {"select":"keystone_user_uuid,user_project_id","from":"trans_user_info","where":"user_name='%s'" %(remove_role['username'])}
                user_id = self.db.pg_select(get_user_id)
            except:
                logger.sql_error("Could not connect to the DB, %s" %(e))
                raise

            #if we remove the built in admin or Member set the DB to NULL
            if(remove_role['key_role'] == 'admin' or remove_role['key_role'] == 'Member'):
                try:
                    up_dict = {'table':"trans_user_info",'set':"keystone_role='NULL'",'where':"username='%s'" %(remove_role['username'])}
                    self.db.pg_update(up_dict)
                    self.db.pg_close_connection()
                except Exception as e:
                    logger.sql_error("Could not connect to the Transcirrus DB, %s" %(e))
                    raise

            # NOTE at some point need to check if the role exists in openstack
            try:
                #build an api connection for the admin user
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)

                #remove the role from the user on the tenant
                body = ""
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/tenants/%s/users/%s/roles/OS-KSADM/%s' %(user_id[0][1],user_id[0][0],key_role_id[0][0])
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
                print rest
                #check the response and make sure it is a 200 or 201
                if((rest['response'] == 200) or (rest['response'] == 204)):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    #load = json.loads(rest['data'])
                    #new_role_name = load['role']['name']
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                logger.sys_error('%s' %(e))
                raise
            r_dict = {"response":rest['response'],"reason":rest['reason']}
            return r_dict
        else:
            logger.sys_error("Admin flag not set, could not create the new user.")

    def get_user_credentials():
        print "not implemented"
    def update_user_credentials():
        print "not implemented"
    def remove_user_credentials():
        print "not implemented"
        
######Internal defs#######
def _http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")