#!/usr/bin/python
#Glance v2 api caller
#Refer to http://docs.openstack.org/api/openstack-image-service/2.0/content/
#Refer to http://api.openstack.org/api-ref.html#os-images-2.0
#Refer to http://docs.openstack.org/trunk/openstack-image/content/

#######standard impots#######
import sys
import json
import subprocess
import time

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token
from transcirrus.database.postgres import pgsql


class glance_ops:
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
        try:
            #Try to connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sys_error("Could not connect to db with error: %s" %(e))
            raise Exception("Could not connect to db with error: %s" %(e))

    #DESC: used to clean up after the server class
    #INPUT: self object
    #OUTPUT: void
    def destructor(self):
        #close any open db connections
        self.db.close_connection()

    def import_image(self,input_dict):
        """
        DESC: Import a pre-made glance image .img file
        INPUT: input_dict - image_name - req
                          - container_format - req (bare, ovf, aki, ari, ami)
                          - disk_format - req (raw, vhd, vmdk, vdi, iso, qcow2, aki, ari, ami)
                          - image_file -
                                        \ must specify EITHER image_file OR image_url NOT BOTH
                                        / image_file used for local, image_url used for remote
                          - image_url - 
                          - visibility - op ("public" or "private", will default to "public" if not provided)
        OUTPUT: OK - success
                ERROR - fail
        ACCESS: Admins will be able to create universal images and images in projects
                Power users will only be able to create images in their project, images are not
                visible to other projects
                Users can not import images.
        NOTE: Either image_url or image_file need to be specified if neither are specified and ERROR will be
              thrown. If you specify both a file location and a url error will be thrown
        """
        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        if(self.user_level == 2):
            logger.sys_error('Users can not import images.')
            return 'ERROR'

        if(('image_name' not in input_dict) or (input_dict['image_name'] == '')):
            logger.sys_error('Image name not specified')
            raise Exception('Image name not specified')
        
        if(('container_format' not in input_dict) or (input_dict['container_format'] == '')):
            logger.sys_error('Image container format not specified')
            raise Exception('Image container format not specified')
        
        if(('disk_format' not in input_dict) or (input_dict['disk_format'] == '')):
            logger.sys_error('Image disk format not specified')
            raise Exception('Image disk format not specified')
        
        if(('image_file' in input_dict) and ('image_url' in input_dict)):
            logger.sys_error('Cannot specify both an image_file and an image_url')
            raise Exception('Cannot specify both an image_file and an image_url')
        
        if(('image_file' not in input_dict) and ('image_url' not in input_dict)):
            logger.sys_error('Must specify an image_file or an image_url')
            raise Exception('Must specify an image_file or an image_url')
        
        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")
        
        if('visibility' in input_dict):
            body_json = json.dumps({"name": input_dict['image_name'], "container_format": input_dict['container_format'], "disk_format": input_dict['disk_format'], "visibility": input_dict['visibility']})
        else:
            body_json = json.dumps({"name": input_dict['image_name'], "container_format": input_dict['container_format'], "disk_format": input_dict['disk_format'], "visibilitiy": "public"})
        try:
            body = body_json
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "User-Agent": "python/glanceclient"}
            function = 'POST'
            api_path = '/v2/images'
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not reserve image, %s" %(e))
            raise e

        if((rest['response'] == 201)):
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            image_id = load['id']
            if('image_file' in input_dict):
                file_open = open(input_dict['image_file'], 'rb')
            else:
                out = subprocess.Popen('sudo wget -O /var/lib/glance/images/import.img %s' %(input_dict['image_url']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                if(out != None):
                    time.sleep(5)
                    file_open = open('/var/lib/glance/images/import.img', 'rb')
                else:
                    util.http_codes(out,"Unable to open remote file %s" %(input_dict['image_url']))
                    return "ERROR"
            try:
                body = file_open
                header = {"X-Auth-Token":self.token, "Content-Type": "application/octet-stream"}
                function = 'PUT'
                api_path = '/v2/images/%s/file' %(image_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                logger.sys_error("Could not upload image data, %s" %(e))
                raise e
    
            if((rest['response'] == 201 or rest['response'] == 204)):
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                file_open.close()
                if('image_file' not in input_dict):
                    out = subprocess.Popen('sudo rm -f /var/lib/glance/images/import.img %s' %(input_dict['image_url']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                return "OK"
            else:
                util.http_codes(rest['response'],rest['reason'])
                return "ERROR"
        else:
            util.http_codes(rest['response'],rest['reason'])
            return "ERROR"
       
    
    def delete_image(self, image_id):
        """
        DESC: Delete specific image given by image_id.
        INPUT: image_id - req
        OUTPUT: "OK" upon success or "ERROR" upon failure
        ACCESS:
        NOTE:
        """
        #Check user status level for valid range
        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "User-Agent": "python/glanceclient"}
            function = 'DELETE'
            api_path = '/v2/images/%s' %(image_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not list images %s" %(e))
            raise e

        if((rest['response'] == 204)):
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            return "OK"
        else:
            util.http_codes(rest['response'],rest['reason'])
            return "ERROR"
        
        
    def list_images(self):
        """
        DESC: List all of the images in a project as well as any images in the Glance
              catalog that may be set to public. All users can list the images in a
              project.
        INPUT: self object
        OUTPUT: array of r_dict - image_name
                                - image_id
        """
        #GET v2/images
        #Check user status level for valid range
        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "User-Agent": "python/glanceclient"}
            function = 'GET'
            api_path = '/v2/images'
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not list images %s" %(e))
            raise e

        if((rest['response'] == 200)):
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            img_array = []
            for image in load['images']:
                line = {"image_name": str(image['name']), "image_id": str(image['id'])}
                img_array.append(line)
            return img_array
        else:
            util.http_codes(rest['response'],rest['reason'])

    def get_image(self,image_id):
        """
        DESC: Get detailed information about a Glance image. All users can
              get information regarding images in their project.
        INPUT: image_id
        OUTPUT: r_dict - image_name
                       - image_id
                       - status
                       - visibility
                       - size
                       - checksum
                       - tags[]
                       - created_at
                       - updated_at
                       - image_file
                       - schema
        """
        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        #connect to the rest api caller.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        try:
            body = ""
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "User-Agent": "python/glanceclient"}
            function = 'GET'
            api_path = '/v2/images/%s' %(image_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not list images %s" %(e))
            raise e

        if((rest['response'] == 200)):
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            r_dict = {'image_id':load['id'], 'image_name':load['name'], 'status':load['status'], 'visibility':load['visibility'], 'size':load['size'], 'checksum':load['checksum'], 'tags':load['tags'], 'created_at':load['created_at'], 'updated_at':load['updated_at'], 'image_file':load['file'], 'schema':load['schema']}
            return r_dict
        else:
            util.http_codes(rest['response'],rest['reason'])


    def create_new_os_binary(self):
        """
        DESC: Create a new operating system binary from an .iso file. Only admins can build
              new binaries and and them to the Glance catalog.
        INPUT: self object
        OUTPUT:
        NOTE:http://docs.openstack.org/trunk/openstack-image/content/ch_creating_images_manually.html
        """
        print "not implemented"

    def upload_image(self,upload_dict):
        """
        DESC: Uploads an image created with create_new_os_binary to an image built
              with create_image. All users can upload a new binary to the glance catalog.
        INPUT: upload_dict - os_binary_location
                           - image_id
                           - file_link
        OUTPUT: OK if uploaded else http error
        NOTE: refer to http://docs.openstack.org/api/openstack-image-service/2.0/content/upload-binary-image-data.html
        """
        print "not implemented"

    def update_image(self,update_dict):
        """
        DESC: Updates the image information. Only admins and power users can update the image info
              for images in their projects.
        INPUT: update_dict - image_id
                           - "update": array of dictionaries of parameters to change and the new values
                             example:
                             "update": [{"x-image-meta-name": new_name, "x-image-meta-id": new_id, "x-image-meta-property-*": new_custom_property}]
        OUTPUT: r_dict - image_name
                       - image_id
                       - image_status
                       - container_format
                       - disk_format
                       - is_public
                       - min_disk
                       - size
                       - min_ram
        """
        print "not implemented"