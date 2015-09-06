#!/usr/bin/python
import sys
import json
import random

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.component.nova.error as nova_ec
from transcirrus.common.auth import get_token
from transcirrus.common.api_caller import caller
from transcirrus.database.postgres import pgsql

class flavor_ops:
    #UPDATED/UNIT TESTED
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

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

    def list_flavors(self):
        """
        DESC: Get a list of all flavors associated with a project
              users and admin can only get flavors associated with their
              projects
        INPUT: self object
        OUTPUT: array of r_dict - name
                                - id
        ACCESS: All users can use this function
        """
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
        except Exception as e:
            logger.sys_error("Could not get the defined instance flavors: %s" %(e))
            raise Exception("Could not get the defined instance flavors: %s" %(e))

        #check the response and make sure it is a 200 or 203
        if((rest['response'] == 200) or (rest['response'] == 203)):
            #build up the return dictionary and return it if everythig is good to go
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            flav_array = []
            for flavor in load['flavors']:
                line = {"name": str(flavor['name']), "id": str(flavor['id'])}
                flav_array.append(line)
            return flav_array
        else:
            #util.http_codes(rest['response'],rest['reason'])
            nova_ec.error_codes(rest)

    def get_flavor(self,flavor_id):
        """
        DESC: Get the information for a specific flavor users and admins can only
              get flavor info for flavors in their project
        INPUT: flav_id of the flavor
        OUTPUT: r_dict - flavor_name
                       - flav_id
                       - memory(MB)
                       - disk_space(GB)
                       - ephemeral(GB)
                       - swap(GB)
                       - cpus
                       - flav_link
                       - metadata - dict
        """
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
        except Exception as e:
            logger.sys_error("Could not get the flavor info %s" %(e))
            raise e

        if((rest['response'] == 200) or (rest['response'] == 203)):
            #build up the return dictionary and return it if everythig is good to go
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            #get description
            meta = self.get_flavor_metadata(str(load['flavor']['id']))
            r_dict = {"flavor_name": str(load['flavor']['name']), "flav_id": str(load['flavor']['id']), "memory(MB)": str(load['flavor']['ram']), "disk_space(GB)": str(load['flavor']['disk']), "ephemeral(GB)": str(load['flavor']['OS-FLV-EXT-DATA:ephemeral']), "swap(GB)": str(load['flavor']['swap']), "cpus": str(load['flavor']['vcpus']), "link": str(load['flavor']['links'][1]['href']), "metadata":str(meta)}
            return r_dict
        else:
            #util.http_codes(rest['response'],rest['reason'])
            nova_ec.error_codes(rest)

    def create_flavor(self,flav_dict):
        """
        DESC: create a new flavor in the openstack cloud
              only an admin can create a flavor
              if the admin sets public to FALSE the flavor is
              only visable to the admins primary project
        INPUT: flav_dict - name - req
                        - ram - req
                        - boot_disk - req (GB)
                        - cpus - req
                        - swap - op - default 0 (MB)
                        - ephemeral - op - default 0 (GB)
                        - public - op - default false (true/false)
                        - description - op
        OUTPUT: r_dict - status - ok (may change after proto)
                         flav_name
                         flav_id
        """
        #connect to the rest api caller.
        if(self.is_admin == 1):
            if(('name' not in flav_dict) or (flav_dict['name'] == "")):
                raise Exception("VM flavor name not given.")
            if(('boot_disk' not in flav_dict) or (flav_dict['boot_disk'] == "") or (flav_dict['boot_disk'] == "0")):
                raise Exception("Boot disk size, in GB, not given.")
            if(('ram' not in flav_dict) or (flav_dict['ram'] == "") or (flav_dict['ram'] == "0")):
                raise Exception("RAM, in MB, not given.")
            if(('cpus' not in flav_dict) or (flav_dict['cpus'] == "") or (flav_dict['cpus'] == "0")):
                raise Exception("Number of CPUs not specified.")

            #determin if flavor is public
            self.public = "TRUE"
            if("public" in flav_dict):
                stuff = str(flav_dict['public']).lower()
                if(stuff == 'false'):
                    self.public = str(flav_dict['public']).upper()

            #check for disks
            swap = '0'
            if('swap' in flav_dict):
                swap = flav_dict['swap']

            ephemeral = '0'
            if('ephemeral' in flav_dict):
                ephemeral = flav_dict['ephemeral']

            #generate a random ID for the flavor
            random.seed()
            flav_id = random.randrange(0,100000)

            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API caller")
                raise Exception("Could not connect to the API caller")

            try:
                #body = '{"flavor": {"vcpus": 2, "disk": 40, "name": "jontest5", "os-flavor-access:is_public": true, "rxtx_factor": 1.0, "OS-FLV-EXT-DATA:ephemeral": 5, "ram": 256, "id": 205, "swap": 5}}'
                body = '{"flavor": {"vcpus": %s, "disk": %s, "name": "%s", "rxtx_factor": 1.0, "OS-FLV-EXT-DATA:ephemeral": %s, "ram": %s, "id": %s, "swap": %s,"os-flavor-access:is_public":"%s"}}' %(flav_dict['cpus'],flav_dict['boot_disk'],flav_dict['name'],ephemeral,flav_dict['ram'],flav_id,swap,self.public)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2/%s/flavors' %(self.project_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                logger.sys_error("%s" %(e))
                raise e

            if((rest['response'] == 200) or (rest['response'] == 203)):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                if('description' in flav_dict):
                    input_dict = {'key':'description', 'value':"%s",'flavor_id':"%s"}%(flav_dict['description'],str(load['flavor']['id']))
                    self.add_flavor_metadata(input_dict)
                load = json.loads(rest['data'])
                r_dict = {"flavor_name": str(load['flavor']['name']), "flav_id": str(load['flavor']['id']), "status": "OK"}
                return r_dict
            else:
                nova_ec.error_codes(rest)
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
            except Exception as e:
                logger.sys_error("Could not remove the flavor %s" %(e))
                raise e

            #check the response and make sure it is a 200 or 202
            if((rest['response'] == 200) or (rest['response'] == 202)):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                return "OK"
            else:
                #util.http_codes(rest['response'],rest['reason'])
                nova_ec.error_codes(rest)
        else:
            logger.sys_error("Only admin can create a flavor user: %s" %(self.username))
            raise Exception("Only admin can create a flavor user: %s" %(self.username))

    def add_flavor_metadata(self,input_dict):
        """
        DESC: Add new metadata to the flavor. An example would be a description.
        INPUT: input_dict - key - req
                          - value - req
                          - flavor_id - req
        OUTPUT: r_dict - key
        NOTE: The output is the rest API output extra_specs:{key:value}
        ACCESS: Only admins can add metadata.
        """
        if(self.is_admin == 1):
            if(('key' not in input_dict) or (input_dict['key'] == "")):
                logger.sys_error("Requiered parameter not specified.")
                raise Exception("Requiered parameter not specified.")
            if(('value' not in input_dict) or (input_dict['value'] == "")):
                logger.sys_error("Requiered parameter not specified.")
                raise Exception("Requiered parameter not specified.")
            if(('flavor_id' not in input_dict) or (input_dict['flavor_id'] == "")):
                logger.sys_error("Requiered parameter not specified.")
                raise Exception("Requiered parameter not specified.")

            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API caller")
                raise Exception("Could not connect to the API caller")

            try:
                body = '{"extra_specs": {"%s": "%s"}}'%(input_dict['key'],input_dict['value'])
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'POST'
                api_path = '/v2/%s/flavors/%s/os-extra_specs' %(self.project_id,input_dict['flavor_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                logger.sys_error("%s" %(e))
                raise e

            #check the response and make sure it is a 200 or 202
            if(rest['response'] == 200):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                return "OK"
            else:
                #util.http_codes(rest['response'],rest['reason'])
                nova_ec.error_codes(rest)
        else:
            logger.sys_error("Only admin can add flavor flavor metadata, user: %s" %(self.username))
            raise Exception("Only admin can add flavor flavor metadata, user: %s" %(self.username))

    def get_flavor_metadata(self,flavor_id=None):
        """
        DESC: Get the metadata attached to a flavor
        INPUT: flavor_id
        OUTPUT: r_dict of specs
        NOTE: The output is the rest API output extra_specs:{key:value}
        ACCESS: Admin can get metadata for any flavor
                PU can get metadata for flavor in their project.
                User can get metadata for flavor in their project.
        """
        if(flavor_id):

            #connec to the rest api caller.
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API caller")
                raise Exception("Could not connect to the API caller")
    
            try:
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/v2/%s/flavors/%s/os-extra_specs' %(self.project_id,flavor_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                logger.sys_error("%s" %(e))
                raise e
    
            #check the response and make sure it is a 200 or 202
            if(rest['response'] == 200):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                return load['extra_specs']
            else:
                #util.http_codes(rest['response'],rest['reason'])
                nova_ec.error_codes(rest)
        else:
            logger.sys_error('Flavor ID not specified')
            raise Exception('Flavor ID not specified')

    def delete_flavor_metadata(self,input_dict):
        """
        DESC: Del
        INPUT: input_dict - flavor_id - req
                          - metadat_key - req
        OUTPUT: metadata
        NOTE: The output is the rest API output extra_specs:{key:value}
        ACCESS: Admin can get metadata for any flavor
                PU can get metadata for flavor in their project.
                User can get metadata for flavor in their project.
        """
        if(('flavor_id' not in input_dict) or (input_dict['flavor_id'] == "")):
            logger.sys_error("Requiered parameter not specified.")
            raise Exception("Requiered parameter not specified.")
        if(('metadata_key' not in input_dict) or (input_dict['metadata_key'] == "")):
            logger.sys_error("Requiered parameter not specified.")
            raise Exception("Requiered parameter not specified.")

        #connec to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'DELETE'
            api_path = '/v2/%s/flavors/%s/os-extra_specs/%s' %(self.project_id,input_dict['flavor_id'],input_dict['metadata_key'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("%s" %(e))
            raise e

        #check the response and make sure it is a 200 or 202
        if(rest['response'] == 200):
            #build up the return dictionary and return it if everythig is good to go
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            return 'OK'
        else:
            #util.http_codes(rest['response'],rest['reason'])
            nova_ec.error_codes(rest)