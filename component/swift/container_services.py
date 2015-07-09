import sys
import json
import subprocess

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token
from transcirrus.database.postgres import pgsql

class container_service_ops:
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

            if(self.is_admin == 1):
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

        if(self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")
            #raise Exception("No admin tokens passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        #attach to the DB
        self.db = util.db_connect()

    def list_container_objects(self,input_dict):
        """
        DESC: List all of the objects inside of a container
        INPUT input_dict - container_name
                         - project_id
        OUTPUT: r_array - list of container objects
        ACCESS: Admin - can get the objects in any container
                PU - can get the objects from any container in their project
                User - can get the objects in the containers they own
        NOTE:
        """
        logger.sys_info('\n**Getting Swift container objects. Component: Swift Def: list_container_objects**\n')
        #check if the continer can be accesed by the user.
        try:
            get_container = None
            if(self.user_level == 0):
                get_container = {'select':"index",'from':"trans_swift_containers",'where':"container_name='%s'"%(input_dict['container_name'])}
            elif(self.user_level == 1):
                get_container = {'select':"index",'from':"trans_swift_containers",'where':"proj_id='%s'"%(self.project_id),'and':"container_name='%s'"%(input_dict['container_name'])}
            elif(self.user_level == 2):
                if(self.project_id == input_dict['project_id']):
                    get_container = {'select':"index",'from':"trans_swift_containers",'where':"container_user_id='%s'"%(self.user_id),'and':"container_name='%s'"%(input_dict['container_name'])}
                else:
                    logger.sys_error("Container specified does not belong to the user.")
                    raise Exception("Container specified does not belong to the user.")
            container = self.db.pg_select(get_container)
        except:
            logger.sys_error("Container could not be found.")
            raise Exception("Container could not be found.")

        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":input_dict['project_id']}
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            #add the new user to openstack
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v1/AUTH_%s/%s' %(input_dict['project_id'],input_dict['container_name'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8080'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sql_error("Could not get the Swift account info.")
            raise Exception("Could not get the Swift account info.")

        #check the response and make sure it is a 204
        if(rest['response'] == 204 or rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            objects = rest['data']
            objects = objects.split("\n")
            return objects
        else:
            util.http_codes(rest['response'],rest['reason'])

    def create_container(self,input_dict):
        """
        DESC: Create a new container in a project
        INPUT input_dict - container_name
                         - project_id
        OUTPUT: 'OK' - success
        ACCESS: Admin - can create a container in any project
                PU - can create a container in their project
                User - can create a container their project
        NOTE:
        """
        logger.sys_info('\n**Creating a new container. Component: Swift Def: create_container**\n')
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":input_dict['project_id']}
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            #add the new user to openstack
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'PUT'
            api_path = '/v1/AUTH_%s/%s' %(input_dict['project_id'],input_dict['container_name'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8080'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sql_error("Could not get the Swift account info.")
            raise Exception("Could not get the Swift account info.")

        #check the response and make sure it is a 204
        if(rest['response'] == 204 or rest['response'] == 201):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            try:
                put_container = None
                self.db.pg_transaction_begin()
                if(self.user_level == 0):
                    put_container = {"proj_id":input_dict['project_id'],"container_name":input_dict['container_name'],"container_user_id":self.user_id}
                elif(self.user_level >= 1):
                    if(self.project_id == input_dict['project_id']):
                        put_container = {"proj_id":input_dict['project_id'],"container_name":input_dict['container_name'],"container_user_id":self.user_id}
                    else:
                        logger.sys_error("Container specified does not belong to the user.")
                        raise Exception("Container specified does not belong to the user.")
                container = self.db.pg_insert('trans_swift_containers',put_container)
            except:
                self.db.pg_transaction_rollback()
                logger.sys_error("Container could not be created.")
                raise Exception("Container could not be created.")
            else:
                self.db.pg_transaction_commit()
                return 'OK'
        else:
            util.http_codes(rest['response'],rest['reason'],rest['data'])

    def delete_container(self,input_dict):
        """
        DESC: Delete a container
        INPUT input_dict - container_name
                         - project_id
        OUTPUT: 'OK' - success
                Exception
        ACCESS: Admin - can delete a container in any project
                PU - can delete a container in their project
                User - can delete a container their project they own
        NOTE: This will fail if there are objects in the container.
        """
        logger.sys_info('\n**Creating a new container. Component: Swift Def: create_container**\n')
        #check if the continer can be accesed by the user.
        try:
            get_container = None
            if(self.user_level == 0):
                get_container = {'select':"index",'from':"trans_swift_containers",'where':"container_name='%s'"%(input_dict['container_name'])}
            elif(self.user_level == 1):
                get_container = {'select':"index",'from':"trans_swift_containers",'where':"proj_id='%s'"%(self.project_id),'and':"container_name='%s'"%(input_dict['container_name'])}
            elif(self.user_level == 2):
                if(self.project_id == input_dict['project_id']):
                    get_container = {'select':"index",'from':"trans_swift_containers",'where':"container_user_id='%s'"%(self.user_id),'and':"container_name='%s'"%(input_dict['container_name'])}
                else:
                    logger.sys_error("Container specified does not belong to the user.")
                    raise Exception("Container specified does not belong to the user.")
            container = self.db.pg_select(get_container)
        except:
            logger.sys_error("Container could not be found.")
            raise Exception("Container could not be found.")

        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":input_dict['project_id']}
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            #add the new user to openstack
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'DELETE'
            api_path = '/v1/AUTH_%s/%s' %(input_dict['project_id'],input_dict['container_name'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8080'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sql_error("Could not get the Swift account info.")
            raise Exception("Could not get the Swift account info.")

        #check the response and make sure it is a 204
        if(rest['response'] == 204):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            try:
                self.db.pg_transaction_begin()
                delete = {"table":'trans_swift_containers',"where":"container_name='%s'"%(input_dict['container_name']), "and":"proj_id='%s'"%(input_dict['project_id'])}
                self.db.pg_delete(delete)
            except:
                self.db.pg_transaction_rollback()
                logger.sys_error('Could not delete container from Transcirus DB.')
                raise Exception('Could not delete container from Transcirus DB.')
            else:
                self.db.pg_transaction_commit()
                print 'OK'
        else:
            util.http_codes(rest['response'],rest['reason'],rest['data'])
    def update_container_info(self):
        pass
        #pushed out to starkist