#!/usr/bin/python
import sys
import json
import random

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class nova_image_ops:
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

    #DESC: List the available cloud images that are available to the project
    #      all users can look at the images available to the project
    #INPUT: self object
    #OUTPUT: array of dictionaries containing the name, id, link to available images
    #               - image_name
    #               - image_id
    #               - image_link
    def nova_list_images(self,**kwargs):
        #NOTE: need to use kwargs to build an api_path that allows us to search for images with specific
        # atributes
        
        #connect to the rest api caller.
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
            api_path = '/v2/%s/images' %(self.project_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 201
            if((rest['response'] == 200) or (rest['response'] == 203)):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                img_array = []
                for image in load['images']:
                    line = {"image_name": str(image['name']), "image_id": str(image['id']), "image_link":str(image['links'][1]['href'])}
                    img_array.append(line)
                return img_array
            else:
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not remove the project %s" %(e))

    #DESC: Get the specifics for an available image
    #      all users can look at the image details
    #INPUT: self object, image_id
    #OUTPUT: dictionary containing the information relateing to the image
    #        r_dict - status - image staus
    #               - name
    #               - id
    #               - create_date
    #               - minDisk
    #               - minRam
    #               - image_size (MB)
    #               - image_link
    def nova_get_image(self, image_id):
        #connect to the rest api caller.
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
            api_path = '/v2/%s/images/%s' %(self.project_id,image_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'8774'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 201
            if(rest['response'] == 200):
                #build up the return dictionary and return it if everythig is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                r_dict = {"status":str(load['image']['status']), "name":str(load['image']['name']), "id":str(load['image']['id']), "minDisk":str(load['image']['minDisk']), "minRam":str(load['image']['minRam']), "image_size":str(load['image']['OS-EXT-IMG-SIZE:size']), "image_link":str(load['image']['links'][1]['href'])}
                return r_dict
            else:
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not remove the project %s" %(e))
