import sys
import json
import subprocess

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token
from transcirrus.database.postgres import pgsql

class object_service_ops:
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
        
    def get_object_details(self,input_dict):
        """
        DESC: Get the specifics of an object.
        INPUT input_dict - container_name
                         - object_name
                         - project_id
        OUTPUT: r_array - list of container objects
        ACCESS: Admin - can get the object details in any container
                PU - can get the object details from any container in their project
                User - can get the object details in the containers they own
        NOTE:
        """
        logger.sys_info('\n**Get object details. Component: Swift Def: get_object_details**\n')
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
            api_path = '/v1/AUTH_%s/%s/%s' %(input_dict['project_id'],input_dict['container_name'],input_dict['object_name'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8080'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sql_error("Could not get the Swift object info.")
            raise Exception("Could not get the Swift object info.")

        #check the response and make sure it is a 200
        if(rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            print rest
            #r_array = rest['data'].split('\n')
            #r_array.pop()
            #return r_array
        else:
            util.http_codes(rest['response'],rest['reason'],rest['data'])
    
    def create_object(self,input_dict):
        """
        DESC: Create a new object in a container.
        INPUT input_dict - container_name
                         - object_path
                         - project_id
        OUTPUT: 'OK' - success
                Exception
        ACCESS: Admin - can create an object in any container
                PU - can create an object in any container in their project
                User - can creae a new object in a container they own.
        NOTE:
        """
        print "--create_object:: starting"
        logger.sys_info('\n**Create a new object. Component: Swift Def: create_object**\n')
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
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        print "--create_object:: calling subprocess.Popen"

        command = "cd /home/transuser; swift --auth-version 2 -A http://%s:5000/v2.0 -U %s:%s -K %s upload %s test.txt" % (util.get_uplink_ip(), input_dict['project_name'], self.username, self.password, input_dict['container_name'])

        subproc = subprocess.Popen (command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        std_out, std_err = subproc.communicate()

        if subproc.returncode != 0:
            print "Error calling swift to upload object, exit status: %d" % subproc.returncode
            print "Error message: %s" % std_err
            logger.sys_error("Error calling swift to upload object, exit status: %d" % subproc.returncode)
            logger.sys_error("Error message: %s" % std_err)
            raise Exception("Error calling swift to upload object, exit status: %d" % subproc.returncode)
        
        print "   ---   object_services: create_object   ---"
        
        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Length": "0", "X-Detect-Content-Type": "true"}
            header = {"X-Auth-Token":self.token, "Content-Length": "0"}
            function = 'PUT'
            api_path = '/v1/AUTH_%s/%s%s' %(input_dict['project_id'],input_dict['container_name'],input_dict['object_path'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8080'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sql_error("Could not get the Swift object info.")
            raise Exception("Could not get the Swift object info.")

        #check the response and make sure it is a 200
        if(rest['response'] == 200 or rest['response'] == 201):
            #read the json that is returned
            load = json.loads(rest['data'])
            print "load data: %s" % load
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            return
        else:
            print "Upload file/object data via swift - bad status: %s - %s" % (rest['response'], rest['reason'])
            logger.sys_error("Upload file/object data via swift - bad status: %s - %s" % (rest['response'], rest['reason']))
            raise Exception("Upload file/object data via swift - bad status: %s - %s" % (rest['response'], rest['reason']))


    def update_object(self):
        pass
        #most likey we can use create_object
    
    def create_chunked_object(self):
        pass

    def delete_object(self,input_dict):
        """
        DESC: Create a new object in a container.
        INPUT input_dict - container_name
                         - object_name
                         - project_id
        OUTPUT: 'OK' - success
                Exception
        ACCESS: Admin - can create an object in any container
                PU - can create an object in any container in their project
                User - can creae a new object in a container they own.
        NOTE:
        """
        logger.sys_info('\n**Delete an object. Component: Swift Def: delete_object**\n')
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
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(self.project_id != input_dict['project_id']):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Length": "0"}
            function = 'DELETE'
            api_path = '/v1/AUTH_%s/%s/%s' %(input_dict['project_id'],input_dict['container_name'],input_dict['object_name'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8080'}
            rest = api.call_rest(rest_dict)
        except:
            logger.sql_error("Could not delete the Swift object info.")
            raise Exception("Could not delete the Swift object info.")

        #check the response and make sure it is a 200
        if(rest['response'] == 200 or rest['response'] == 204):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s Data %s" %(rest['response'],rest['reason'],rest['data']))
            print rest
            return 'OK'
        else:
            util.http_codes(rest['response'],rest['reason'],rest['data'])

    def get_object_metadata(self):
        pass
    
    def update_object_metadata(self):
        pass