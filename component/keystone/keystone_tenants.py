#!/usr/local/bin/python2.7

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json
import os

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.gluster import gluster_ops
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
        reload(config)
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
            else:
                self.adm_token = 'NULL'

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

        if(self.is_admin == 1 and self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")
            raise Exception("No admin tokens passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        self.keystone_users = user_ops(user_dict)
        self.gluster = gluster_ops(user_dict)

    def create_tenant(self,project_name, is_default=False):
        """
        DESC:   create a new project in Openstack. Only admins can perform this operation.
                calls the rest api in OpenStack and updates applicable fields in Transcirrus
                database
        INPUT:  self object
                project_name    - what you want to call the new project
                is_default      - op - "SHIB" for default shibboleth project, "LDAP" for default ldap project
                                - THERE CAN ONLY BE ONE of each per cloud, TODO below as to where to check for this
        OUTPUT project_id
        """
        logger.sys_info('\n**Creating new Keystone project. Component: Keystone Def: create_tenant**\n')
        if((not project_name) or (project_name == "")):
            logger.sys_error("No project name was specified for the new project.")
            raise Exception("No project name was specified for the new project.")

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

            # added for custom third party configuration, now we can check description to determine cloud behavior
            description = project_name

            # TODO: determine if "THERE CAN ONLY BE ONE" of each check should be done in frontend or backend, currently relying on front-end
            if is_default is not False:
                if is_default != "SHIB" and is_default != "LDAP":
                    logger.sys_error("incorrect value for default project passed")
                    raise Exception("Incorrect value for default project passed, must be 'SHIB' or 'LDAP'.")
                description = is_default

            try:
                #Build the new project in OpenStack
                body = '{"tenant": {"enabled": true, "name": "%s", "description": "%s"}}' %(project_name,description)
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
            description = load['tenant']['description']
            # need to update the project_id info to the relevent transcirrus db tables
            try:
                self.db.pg_transaction_begin()
                #insert the new project into the db
                proj_ins_dict = {"proj_id":project_id,"proj_name":project_name,"host_system_name":self.controller, "host_system_ip":self.api_ip}
                if description != project_name:
                    proj_ins_dict["is_default"] = description
                self.db.pg_insert("projects",proj_ins_dict)
            except Exception as e:
                logger.sql_error("Could not commit the transaction to the Transcirrus DB.%s" %(e))
                self.db.pg_transaction_rollback()
                self.db.pg_close_connection()
                #simple cleanup of failed project create
                raise e
            else:
                gluster_vol_input = {'volume_name':str(project_id),'volume_type':'spindle'}
                self.gluster.create_gluster_volume(gluster_vol_input)

                # Create a process to handle running the create_gluster_swift_ring function because it can take some
                # time to complete.
                logger.sys_info('Forking process to call gluster_swift_ring for project %s' % project_name)
                newpid = os.fork()
                if newpid == 0:
                    # This is the child process running which calls the long running function and then exits.
                    logger.sys_info('Forked process calling gluster_swift_ring for project %s' % project_name)
                    self.gluster.create_gluster_swift_ring()
                    logger.sys_info('Forked process for project %s exiting' % project_name)
                    os._exit(0)

                # This is the parent process which continues to run.
                self.db.pg_transaction_commit()
                self.db.pg_close_connection()

            #add the admin to the project who created the project
            #if(self.username == 'admin'):
            try:
                #add the "cloud" admin to the project as an admin - admin gets added to all projects in the system
                add_admin = {'username':'admin','user_role':'admin','project_id':project_id}
                admin = self.keystone_users.add_user_to_project(add_admin)
                # add the shadow_admin
                add_shadow_admin = {'username':'shadow_admin','user_role':'admin','project_id':project_id}
                shadow_admin = self.keystone_users.add_user_to_project(add_shadow_admin)
            except Exception as e:
                logger.sys_error('Could not add the admin to %s'%(project_id))
                raise Exception('Could not add the admin to %s'%(project_id))
            if(self.username != 'admin' and self.username != "shadow_admin"):
                try:
                    #add the admin user to the project as an admin
                    add_projadmin = {'username':self.username,'user_role':'admin','project_id':project_id}
                    projadmin = self.keystone_users.add_user_to_project(add_projadmin)
                except Exception as e:
                    logger.sys_error('Could not add the project admin to %s'%(project_name))
                    raise Exception('Could not add the project admin to %s'%(project_name))

            return project_id
        else:
            util.http_codes(rest['response'],rest['reason'])

    def remove_tenant(self,project_id):
        """
        DESC: Remove a tenant from the OpenStack system and from the Transcirrus DB
        INPUT: project_id
        ACCESS: Only the admin can remove the project
        OUTPUT: 'OK' if task completed successfully
        """
        logger.sys_info('\n**Deleteing Keystone project. Keystone Def: remove_tenant**\n')
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

            #check the project_id is valid
            try:
                select_dict = {"select":"proj_name", "from":"projects", "where":"proj_id='%s'" %(project_id)}
                select = self.db.pg_select(select_dict)
            except Exception as e:
                logger.sql_error("Could not fine the project in the Transcirrus DB.%s" %(e))
                raise e

            try:
                #build an api connection for the admin user.
                api_dict = {"username":self.username, "password":self.password, "project_id":project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                body = ""
                header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2.0/tenants/%s' %(project_id)
                token = self.adm_token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                logger.sys_error("Could not remove the project %s" %(e))
                raise e

            if((rest['response'] == 201) or (rest['response'] == 200) or (rest['response'] == 204)):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                logger.sys_info("Project: %s has been removed from the Transcirrus DB." %(project_id))
                #delete the project from transcirrus db and update the user account
                try:
                    self.db.pg_transaction_begin()
                    del_dict = {"table":'projects',"where":"proj_id='%s'" %(project_id)}
                    self.db.pg_delete(del_dict)

                    # delete from trans_user_projects as well
                    self.db.pg_transaction_begin()
                    del_dict_tup = {"table":'trans_user_projects',"where":"proj_id='%s'" %(project_id)}
                    self.db.pg_delete(del_dict_tup)

                    user_up_dict = {'table':"trans_user_info",'set':"""user_primary_project='NULL',user_project_id='NULL'""",'where':"user_project_id='%s'" %(project_id)}
                    self.db.pg_update(user_up_dict)
                    self.db.pg_transaction_commit()
                except Exception as e:
                    logger.sql_error("Could not commit the transaction to the Transcirrus DB.%s, Contact an Admin" %(e))
                    self.db.pg_transaction_rollback()
                    raise
                #close all of the db connections that are open
                self.db.pg_close_connection()

                #remove the gluster volume used for object storage
                self.gluster.delete_gluster_volume(project_id)
                logger.sys_info('Forking process to call gluster_swift_ring for project %s' % project_id)

                #re-build the gluster ring after the project vol deleted
                #This needs to be fixed so that it is backgrounded
                #newpid = os.fork()
                #if newpid == 0:
                    # This is the child process running which calls the long running function and then exits.
                    #logger.sys_info('Forked process calling gluster_swift_ring for project %s' % project_id)
                self.gluster.create_gluster_swift_ring()
                    #logger.sys_info('Forked process for project %s exiting' % project_id)
                    #os._exit(0)

                    #return OK if good to go
                return "OK"
                #else:
                #    util.http_codes(rest['response'],rest['reason'],rest['data'])
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
            if(self.username == 'admin' or self.username == 'shadow_admin'):
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
                       - is_default
                - OR -
                None if project does not exist
        ACCESS: Admins can get any project, users can only view the primary project
              they belong to.
        NOTE: If any of the project variables are empty a None will be returned for that variable.
        """
        logger.sys_info('\n**Get project details. Keystone Def: get_tenant**\n')
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
        if len(proj) > 0:
            r_dict = {"project_id":proj[0][0],"project_name":proj[0][1],"def_security_key_name":proj[0][2],"def_security_key_id":proj[0][3],"def_security_group_id":proj[0][4],
                      "def_security_group_name":proj[0][5], "host_system_name":proj[0][6], "host_system_ip":proj[0][7], "def_network_name":proj[0][8], "def_network_id":proj[0][9],
                      "is_default":proj[0][10]}
            if(self.is_admin == 1):
                return r_dict
            else:
                if(self.project_id == proj[0][0]):
                    return r_dict
                else:
                    return None
                    # raise Exception("Users can only get information on their own projects.")
        else:
            return None

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
        logger.sys_info('\n**List the users in a project. Keystone Def: list_tenant_users**\n')
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


    def get_default_tenants(self):
        """
        DESC:   returns the default projects used in third party authentication, or None if none exists
        INPUT:  none
        OUTPUT: array of:
                    tenant_dict:    {
                                        project_id
                                        project_name
                                        def_security_key_name
                                        def_security_key_id
                                        def_security_group_id
                                        def_security_group_name
                                        host_system_name
                                        host_system_ip
                                        def_network_name
                                        def_network_id
                                        is_default
                                    }
                    - OR -
                None
        ACCESS: wide open, but with great power comes great responsibility
        NOTE:
        """
        # try to connect to the transcirrus db
        try:
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

        # get the default project info
        proj = []
        try:
            get = {"select":'*', "from":'projects', "where":"is_default is not null"}
            proj = self.db.pg_select(get)
        except:
            logger.sql_error("Could not get the default project info")
            raise Exception("Could not get the default project info.")

        # make sure a default project exists
        if len(proj) != 0:
            r_array = []
            for p in proj:
                # build the dictionary up
                r_dict = {"project_id":p[0],"project_name":p[1],"def_security_key_name":p[2],"def_security_key_id":p[3],"def_security_group_id":p[4],
                          "def_security_group_name":p[5], "host_system_name":p[6], "host_system_ip":p[7], "def_network_name":p[8], "def_network_id":p[9],
                          "is_default":p[10]}
                r_array.append(r_dict)
            # return default project info
            return r_array

        # else return None
        return None


    def toggle_default_tenant(self, input_dict):
        """
        DESC:   enables or disables default project for shibboleth or ldap
        INPUT:  innput_dict:    {
                                    project_id  - project_id of project to enable/disable - req
                                    type        - tpa flag, either "SHIB" or "LDAP" - req
                                }
        OUTPUT: "OK" - success
        ACCESS: cloud admin only
        NOTE:   need to revisit description handling in create_tenant(), if we want to keep, we'll have to update it here as well
        """
        # only cloud admin or shadow_admin can manage tpa
        if(self.username != 'admin' and self.username != 'shadow_admin'):
            logger.sys_error("Only cloud admin can toggle default third party authentication projects.")
            raise Exception("Only cloud admin can toggle default third party authentication projects.")

        # validate project_id
        target = self.get_tenant(input_dict['project_id'])
        if target is None:
            logger.sys_error("Invalid project_id (%s) given for toggle_default_tenant." %input_dict['project_id'])
            raise Exception("Invalid project_id (%s) given for toggle default third party authentication project." %input_dict['project_id'])

        # if default, disable
        if target['is_default'] is not None:
            try:
                disable = {'table':"projects",'set':"""is_default=NULL""",'where':"proj_id='%s'" %(input_dict['project_id'])}
                self.db.pg_update(disable)
                self.db.pg_transaction_commit()
            except Exception as e:
                logger.sql_error("Could not commit the transaction to the Transcirrus DB.%s, Contact an Admin" %(e))
                self.db.pg_transaction_rollback()
                raise
        # else, enable
        else:
            # shibboleth
            if input_dict['type'] == "SHIB":
                try:
                    enable_shib = {'table':"projects",'set':"""is_default='SHIB'""",'where':"proj_id='%s'" %(input_dict['project_id'])}
                    self.db.pg_update(enable_shib)
                    self.db.pg_transaction_commit()
                except Exception as e:
                    logger.sql_error("Could not commit the transaction to the Transcirrus DB.%s, Contact an Admin" %(e))
                    self.db.pg_transaction_rollback()
                    raise
            # ldap
            elif input_dict['type'] == "LDAP":
                try:
                    enable_ldap = {'table':"projects",'set':"""is_default='LDAP'""",'where':"proj_id='%s'" %(input_dict['project_id'])}
                    self.db.pg_update(enable_ldap)
                    self.db.pg_transaction_commit()
                except Exception as e:
                    logger.sql_error("Could not commit the transaction to the Transcirrus DB.%s, Contact an Admin" %(e))
                    self.db.pg_transaction_rollback()
                    raise
            # invalid
            else:
                logger.sys_error("Invalid type (%s) given for toggle_default_tenant." %input_dict['type'])
                raise Exception("Invalid type (%s) given for toggle default third party authentication project." %input_dict['type'])

        return "OK"
