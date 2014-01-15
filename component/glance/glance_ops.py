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
        INPUT: input_dict - img_name
                          - img_disk_format
                          - img_is_public (True/False)
                          - img_is_protected(True/False)
                          - project_id
                          - url - op
                          - file_location - op
        OUTPUT: OK - success
                ERROR - fail
        ACCESS: Admins will be able to create universal images and images in projects
                Power users will only be able to create images in their project, images are not
                visible to other projects
                Users can not import images.
        NOTE: Either URL or file_location need to be specified it neither are specified and ERROR will be
              thrown. Power users have defaults set for img_is_public,img_is_protected,img_disk_format,project_id.
              If you specify both a file location and a url error will be thrown
        """
        #print "not implemented"
        #POST v2/images
        #Check user status level for valid range
        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        if(self.user_level == 2):
            logger.sys_error('Users can not import images.')
            return 'ERROR'

        #make the project exists
        try:
            get_proj = {'select':'proj_name','from':'projects','where':"proj_id='%s'"%(input_dict['project_id'])}
            project = self.db.pg_select(get_proj)
        except:
            logger.sql_error('Could not get the project')
            raise Exception('Could not get the project')

        if(self.user_level == 1):
            if(self.project_id != input_dict['project_id']):
                logger.sys_error('Power users can only create an image in their project.')
                raise Exception('Power users can only create an image in their project.')
            input_dict['img_is_public'] == 'false'
            input_dict['img_is_protected'] == 'false'
            input_dict['img_disk_format'] == 'qcow2'

        if(('img_name' not in input_dict) or (input_dict['img_name'] == '')):
            logger.sys_error('Image name not specified')
            raise Exception('Image name not specified')
        if(('img_disk_format' not in input_dict) or (input_dict['img_disk_format'] == '')):
            logger.sys_error('Image disk format not specified')
            raise Exception('Image disk format not specified')
        if(('project_id' not in input_dict) or (input_dict['project_id'] == '')):
            logger.sys_error('Image project not specified')
            raise Exception('Image project not specified')

        if(('img_is_public' not in input_dict) or (input_dict['img_is_public'] == '')):
            logger.sys_error('Image public not specified.')
            raise Exception('Image public not specified.')
        elif((input_dict['img_is_public'] == 'True') or (input_dict['img_is_public'] == 'False')):
            logger.sys_info('Image public value valid.')
        else:
            logger.sys_error('Image public value invalid.')
            raise Exception('Image public value invalid.')

        if(('img_is_protected' not in input_dict) or (input_dict['img_is_protected'] == '')):
            logger.sys_error('Image project not specified')
            raise Exception('Image project not specified')
        elif((input_dict['img_is_protected'] == 'True') or (input_dict['img_is_protected'] == 'False')):
            logger.sys_info('Image protected value valid.')
        else:
            logger.sys_error('Image public value invalid.')
            raise Exception('Image public value invalid.')

        if(('url' not in input_dict) or (input_dict['url'] == '')):
            input_dict['url'] = ''
        
        if(('file_location' not in input_dict) or (input_dict['file_location'] == '')):
            input_dict['file_location'] = ''

        if(input_dict['file_location'] == input_dict['url']):
            logger.sys_error('Can not specify both file location and a url for the same image.')
            raise Exception('Can not specify both file location and a url for the same image.')

        if(input_dict['file_location'] and input_dict['url']):
            logger.sys_error('Can not specify both file location and a url for the same image.')
            raise Exception('Can not specify both file location and a url for the same image.')

        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":input_dict['project_id']}
            if(input_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API caller")
            raise Exception("Could not connect to the API caller")
        #really need to figure out how to use the API
        #cli stuff is ghetto
        #here is the api error
        #'reason': 'Bad Request', 'data': "400 Bad Request\n\nSupplied size (13147648) and size generated from uploaded image (4) did not match. Setting image status to 'killed'.\n\n   ", 'response': 400
        '''
        try:
            body = None
            if(input_dict['url']):
                body = 'None'
            else:
                body = ''
            header = {"User-Agent": "python-glanceclient",
                      "Content-Type": "application/octet-stream",
                      "X-Auth-Token": self.token,
                      "x-image-meta-name": input_dict['img_name'],
                      "x-image-meta-disk_format": input_dict['img_disk_format'],
                      "x-image-meta-container-format": 'bare',
                      "x-image-meta-is_public": input_dict['img_is_public'],
                      "x-image-meta-location": input_dict['url'],
                      "x-image-meta-owner": input_dict['project_id'],
                      "x-image-meta-protected":input_dict['img_is_protected'],
                      "x-image-meta-size": 0
                    }
            function = 'POST'
            api_path = '/v1/images'
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
            print rest
        except Exception as e:
            logger.sys_error("Could not remove the project %s" %(e))
            raise e

        if(rest['response'] == 201):
            #build up the return dictionary and return it if everything is good to go
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            #load = json.loads(rest['data'])
            return 'OK'
        else:
            util.http_codes(rest['response'],rest['reason'])
        '''
        try:
            #subprocess
            if(input_dict['url'] != ''):
                out = subprocess.Popen('glance image-create --name %s --disk-format %s --container-format bare --owner %s\
                                       --is-public %s  --is-protected %s --location %s'\
                                       % (input_dict['img_name'], input_dict['img_disk_format'], input_dict['project_id'], input_dict['img_is_public'], input_dict['img_is_protected'],input_dict['url']),
                                          shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            elif(input_dict['file_location'] != ''):
                out = subprocess.Popen('glance image-create --name %s --disk-format %s --container-format bare --owner %s\
                                       --is-public %s  --is-protected %s --file %s'\
                                       % (input_dict['img_name'], input_dict['img_disk_format'], input_dict['project_id'], input_dict['img_is_public'], input_dict['img_is_protected'],input_dict['file_location']),
                                          shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            image = out.stdout.readlines()
            if(image[0]):
                return 'OK'
            else:
                return 'ERROR'
        except Exception as e:
            logger.sys_error("Could not remove the project %s" %(e))
            raise e

    def delete_image(self,image_id):
        """
        DESC: Deletes an image from the Glance catalog.Protected images can not be deleted. Only admins can delete
              an image from the catalog for their project.
        INPUT: image_id
        OUTPUT: OK if deleted else http error
        """
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
        except Exception as e:
            logger.sys_error("Could not get image %s" %(e))
            raise e

        if(rest['response'] == 200):
                return "OK"
        else:
            util.http_codes(rest['response'],rest['reason'])

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
            api_path = '/v1/images/detail'
            token = self.token
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":'9292'}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not list images %s" %(e))
            raise e

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

    def get_image(self,image_id):
        """
        DESC: Get detailed information about a Glance image. All users can
              get information regarding images in their project.
        INPUT: image_id
        OUTPUT: r_dict - image_name
                       - image_id
                       - image_status
                       - container_format
                       - disk_format
                       - visibility
                       - min_disk
                       - size
                       - min_ram
                       - schema
        """
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
        except Exception as e:
            logger.sys_error("Could not get image %s" %(e))
            raise e

        #check the response and make sure it is a 200
        if(rest['response'] == 200):
            #build up the return dictionary and return it if everything is good to go
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
            #r_dict = {"image_name": str(load['image_name']), "image_id": image_id,"image_status": str(load['status']), "container_format": str(load['container_format']), "disk_format": str(load['disk_format']), "visibility": str(load['visibility']), "min_disk": str(load['min_disk']), "size": str(load['size']), "min_ram": str(load['min_ram']), "schema": str(load['schema'])}
            #return r_dict
        else:
            util.http_codes(rest['response'],rest['reason'])

    '''

    def create_new_os_binary(self):
        """
        DESC: Create a new operating system binary from an .iso file. Only admins can build
              new binaries and and them to the Glance catalog.
        INPUT: self object
        OUTPUT:
        NOTE:http://docs.openstack.org/trunk/openstack-image/content/ch_creating_images_manually.html
        """
        print "not implemented"
        # qemu-img create -f qcow2 /tmp/precise.qcow2 10G
        # virt-install --virt-type kvm --name precise --ram 1024 \
        #--cdrom=/data/isos/precise-64-mini.iso \
        #--disk /tmp/precise.qcow2,format=qcow2 \
        #--network network=default \
        #--graphics vnc,listen=0.0.0.0 --noautoconsole \
        #--os-type=linux --os-variant=ubuntuprecise

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
    '''