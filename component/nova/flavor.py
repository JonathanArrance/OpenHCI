#!/usr/bin/python
import sys
import json
import random

sys.path.append('../../common')
import logger
import config

#get the transcirrus api caller
from api_caller import caller

#get the db library path from the config file
sys.path.append(config.DB_PATH)
from postgres import pgsql

class flavor_ops:
    #DESC:
    #INPUT:
    #OUTPUT:
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

    #DESC: Get a list of all flavors associated with a project
    #      users and admin can only get flavors associated with their
    #      projects
    #INPUT: self object
    #OUTPUT: An array of dictionaries
    #        r_dict - flavor_name
    #               - flav_id
    def list_flavors(self):
        #connec to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v2/%s/flavors' %(self.project_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 201
            if((rest['response'] == 200) or (rest['response'] == 203)):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                flav_array = []
                for flavor in load['flavors']:
                    line = {"flavor_name": str(flavor['name']), "flav_id": str(flavor['id'])}
                    flav_array.append(line)
                return flav_array
            else:
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not remove the project %s" %(e))

    #DESC: Get the information for a specific flavor users and admins can only
    #      get flavor info for flavors in their project
    #INPUT: flavor_id - id of the flavor
    #OUTPUT: r_dict - flavor_name
    #               - flav_id
    #               - memory(MB)
    #               - disk_space(GB)
    #               - ephemeral(GB)
    #               - swap(GB)
    #               - cpus
    #               - flav_link
    def get_flavor(self,flavor_id):
        #connec to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v2/%s/flavors/%s' %(self.project_id, flavor_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 201
            if((rest['response'] == 200) or (rest['response'] == 203)):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                r_dict = {"flavor_name": str(load['flavor']['name']), "flav_id": str(load['flavor']['id']), "memory(MB)": str(load['flavor']['ram']), "disk_space(GB)": str(load['flavor']['disk']), "ephemeral(GB)": str(load['flavor']['OS-FLV-EXT-DATA:ephemeral']), "swap(GB)": str(load['flavor']['swap']), "cpus": str(load['flavor']['vcpus']), "link": str(load['flavor']['links'][1]['href'])}
                return r_dict
            else:
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not remove the project %s" %(e))

    #DESC: create a new flavor in the openstack cloud
    #      only an admin can create a flavor
    #      if the admin sets public to FALSE the flavor is
    #      only visable to the admins primary project
    #INPUT: flav_dict - name - req
    #                - ram - req
    #                - boot_disk - req (GB)
    #                - cpus - req
    #                - swap - op - default 0 (MB)
    #                - ephemeral - op - default 0 (GB)
    #                - public - op - default false (true/false)
    #OUTPUT: r_dict - status - ok (may change after proto)
    #                 flav_name
    #                 flav_id
    def create_flavor(self,flav_dict):
        #connect to the rest api caller.
        if(self.is_admin == 1):
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API caller")
                raise Exception("Could not connect to the API caller")

            #NOTE: this needs to be fixed everything will be set to true by default
            #determin if flavor is public
            #public = ""
            #if('public' in flav_dict):
            #    if((str(flav_dict['public']).lower == 'true') or (str(flav_dict['public']).lower == 'false')):
            #        pulic = str(flav_dict['public']).upper
            #        print public
            #    else:
            #        public = 'true'
            #else:
            #    public = 'true'

            #check for disks
            swap = '0'
            if('swap' in flav_dict):
                swap = flav_dict['swap']

            ephemeral = '0'
            if('ephemeral' in flav_dict):
                ephemeral = flav_dict['ephemeral']

            #generate a random ID for the flavor
            random.seed()
            flav_id = random.randrange(0,1000)

            try:
                #body = '{"flavor": {"vcpus": 2, "disk": 40, "name": "jontest5", "os-flavor-access:is_public": true, "rxtx_factor": 1.0, "OS-FLV-EXT-DATA:ephemeral": 5, "ram": 256, "id": 205, "swap": 5}}'
                body = '{"flavor": {"vcpus": %s, "disk": %s, "name": "%s", "rxtx_factor": 1.0, "OS-FLV-EXT-DATA:ephemeral": %s, "ram": %s, "id": %s, "swap": %s}}' %(flav_dict['cpus'],flav_dict['boot_disk'],flav_dict['name'],ephemeral,flav_dict['ram'],flav_id,swap)
                print body
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2/%s/flavors' %(self.project_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 200 or 201
                if((rest['response'] == 200) or (rest['response'] == 203)):
                    #build up the return dictionary and return it if everythig is good to go
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    load = json.loads(rest['data'])
                    print load
                    r_dict = {"flavor_name": str(load['flavor']['name']), "flav_id": str(load['flavor']['id']), "status": "OK"}
                    return r_dict
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                logger.sys_error("Could not remove the project %s" %(e))
        else:
            logger.sys_error("Only admin can create a flavor user: %s" %(self.username))
            raise Exception("Only admin can create a flavor user: %s" %(self.username))

    #DESC: Remove a flavor from the openstack cloud. Only admins
    #      can remove a flavor
    #INPUT: the id of the flavor to delete
    #OUTPUT: OK if deleted
    def delete_flavor(self,flavor_id):
        #connect to the rest api caller.
        if(self.is_admin == 1):
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API caller")
                raise Exception("Could not connect to the API caller")

            try:
                body = ""
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'DELETE'
                api_path = '/v2/%s/flavors/%s' %(self.project_id,flavor_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 200 or 202
                if((rest['response'] == 200) or (rest['response'] == 202)):
                    #build up the return dictionary and return it if everythig is good to go
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    return "OK"
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                logger.sys_error("Could not remove the project %s" %(e))
        else:
            logger.sys_error("Only admin can create a flavor user: %s" %(self.username))
            raise Exception("Only admin can create a flavor user: %s" %(self.username))
        
######Internal defs#######
def _http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")