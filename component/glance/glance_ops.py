#!/usr/bin/python
#Glance v2 api caller
#Refer to http://docs.openstack.org/api/openstack-image-service/2.0/content/
#Refer to http://api.openstack.org/api-ref.html#os-images-2.0
#Refer to http://docs.openstack.org/trunk/openstack-image/content/

#######standard impots#######
import sys
import json
import subprocess

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller

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
            self.adm_token = user_dict['adm_token']
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

    #DESC: Builds out a new empty container for an image binary image file.
    #      The binary image file needs to be created and then uploaded. If the
    #      image binary to use is already created and has a id, the id can be specified.
    #      All users can create an image.
    #INPUT: create_dict - image_name
    #                   - disk_format
    #                   - container_format
    #                   - is_public
    #                   - file_location
    #OUTPUT: r_dict - image_name
    #               - image_id
    #               - image_status
    #               - container_format
    #               - disk_format
    #               - is_public
    #               - min_disk
    #               - size
    #               - min_ram
    def create_image(self,create_dict):
        #print "not implemented"
        #POST v2/images
        #Check user status level for valid range
        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        #connect to the rest api caller.
        #NOTE: read DB for image info
        """
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")

        try:
            body = ""
            header = {"User-Agent": "python/glanceclient", "Content-Type": "application/octet-stream", "X-Auth-Token": self.token, "x-image-meta-name": create_dict['image_name'], "x-image-meta-disk-format": create_dict['disk_format'], "x-image-meta-container-format": create_dict['container_format'], "x-image-meta-is-public": create_dict['is_public']}
            function = 'POST'
            api_path = '/v1/images'
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
            print rest
            #
            #BELOW IS COPIED FROM LIST_IMAGES, working on modifying it for create_image
            #
            #check the response and make sure it is a 200 or 201
            if((rest['response'] == 200) or (rest['response'] == 201)):
                #build up the return dictionary and return it if everything is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                return load
            else:
                util.http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not remove the project %s" %(e))
            raise e
        """
        try:
            #subprocess
            out = subprocess.Popen('glance image-create --is-public %s --disk-format %s --container-format %s --name %s < %s' % (create_dict['is_public'], create_dict['disk_format'], create_dict['container_format'], create_dict['image_name'], create_dict['file_location']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            image = out.stdout.readlines()
            if(image[0]):
                return 'OK'
            else:
                return 'ERROR'
        except Exception as e:
            logger.sys_error("Could not remove the project %s" %(e))
            raise e

    #DESC: Create a new operating system binary from an .iso file. Only admins can build
    #      new binaries and and them to the Glance catalog.
    #INPUT: self object
    #OUTPUT:
    #NOTE:http://docs.openstack.org/trunk/openstack-image/content/ch_creating_images_manually.html
    def create_new_os_binary(self):
        print "not implemented"
        # qemu-img create -f qcow2 /tmp/precise.qcow2 10G
        # virt-install --virt-type kvm --name precise --ram 1024 \
        #--cdrom=/data/isos/precise-64-mini.iso \
        #--disk /tmp/precise.qcow2,format=qcow2 \
        #--network network=default \
        #--graphics vnc,listen=0.0.0.0 --noautoconsole \
        #--os-type=linux --os-variant=ubuntuprecise

    #DESC: Uploads an image created with create_new_os_binary to an image built
    #      with create_image. All users can upload a new binary to the glance catalog.
    #INPUT: upload_dict - os_binary_location
    #                   - image_id
    #                   - file_link
    #OUTPUT: OK if uploaded else http error
    #NOTE: refer to http://docs.openstack.org/api/openstack-image-service/2.0/content/upload-binary-image-data.html
    def upload_image(self,upload_dict):
        print "not implemented"
        """
        #PUT v2/images/{image_id}/file
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
            with open(upload_dict['file_location'], 'rb') as content_file:
                content = content_file.read()
            body = content
            header = {"X-Auth-Token":self.token, "Content-Type": "application/octet-stream"}
            function = 'PUT'
            api_path = '/v1/images/%s' % (upload_dict['image_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 204
            if(rest['response'] == 204):
                return "OK"
            else:
                util.http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not get image %s" %(e))
            raise e
        """

    #DESC: Updates the image information. Only admins and power users can update the image info
    #      for images in their projects.
    #INPUT: update_dict - image_id
    #                   - "update": array of dictionaries of parameters to change and the new values
    #                     example:
    #                     "update": [{"x-image-meta-name": new_name, "x-image-meta-id": new_id, "x-image-meta-property-*": new_custom_property}]
    #OUTPUT: r_dict - image_name
    #               - image_id
    #               - image_status
    #               - container_format
    #               - disk_format
    #               - is_public
    #               - min_disk
    #               - size
    #               - min_ram
    def update_image(self,update_dict):
        #PUT v1/images/{image_id}
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
            #Not validating properties
            for p in update_dict['update']:
                header.update(p)
            function = 'PUT'
            api_path = '/v1/images/%s' % (update_dict['image_id'])
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200
            if(rest['response'] == 200):
                #build up the return dictionary and return it if everything is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                r_dict = {"image_name": str(load['image']['name']), "image_id": str(load['image']['id']),"image_status": str(load['image']['status']), "container_format": str(load['image']['container_format']), "disk_format": str(load['image']['disk_format']), "is_public": str(load['image']['is_public']), "min_disk": str(load['image']['min_disk']), "size": str(load['image']['size']), "min_ram": str(load['image']['min_ram'])}
                return r_dict
            else:
                util.http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not get image %s" %(e))
            raise e

    #DESC: Deletes an image from the Glance catalog.Protected images can not be deleted. Only admins can delete
    #      an image from the catalog for their project.
    #INPUT: image_id
    #OUTPUT: OK if deleted else http error
    def delete_image(self,image_id):
        #DELETE v2/images/{image_id}
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
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'DELETE'
            api_path = '/v1/images/%s' % (image_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200
            if(rest['response'] == 200):
                return "OK"
            else:
                util.http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not get image %s" %(e))
            raise e

    #DESC: List all of the images in a project as well as any images in the Glance
    #      catalog that may be set to public. All users can list the images in a
    #      project.
    #INPUT: self object
    #OUTPUT: array of r_dict - image_name
    #                        - image_id
    def list_images(self):
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
            api_path = '/v1/images/detail'
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200 or 203
            if((rest['response'] == 200) or (rest['response'] == 203)):
                #build up the return dictionary and return it if everything is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                img_array = []
                for image in load['images']:
                    line = {"image_name": str(image['name']), "image_id": str(image['id'])}
                    img_array.append(line)
                return img_array
            else:
                util.http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not list images %s" %(e))
            raise e

    #DESC: Get detailed information about a Glance image. All users can
    #      get information regarding images in their project.
    #INPUT: image_id
    #OUTPUT: r_dict - image_name
    #               - image_id
    #               - image_status
    #               - container_format
    #               - disk_format
    #               - visibility
    #               - min_disk
    #               - size
    #               - min_ram
    #               - schema
    def get_image(self,image_id):
        #GET v2/images/{image_id}
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
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'GET'
            api_path = '/v2/images/%s' % (image_id)
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200
            if(rest['response'] == 200):
                #build up the return dictionary and return it if everything is good to go
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                r_dict = {"image_name": str(load['name']), "image_id": str(load['id']),"image_status": str(load['status']), "container_format": str(load['container_format']), "disk_format": str(load['disk_format']), "visibility": str(load['visibility']), "min_disk": str(load['min_disk']), "size": str(load['size']), "min_ram": str(load['min_ram']), "schema": str(load['schema'])}
                return r_dict
            else:
                util.http_codes(rest['response'],rest['reason'])
        except Exception as e:
            logger.sys_error("Could not get image %s" %(e))
            raise e