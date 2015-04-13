#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json
import time
import random

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.component.cinder.error as ec

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token

from transcirrus.database.postgres import pgsql


class volume_ops:
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

            self.rannum = random.randrange(1000,9000)

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        #get the db object
        self.db = util.db_connect()

    def create_volume(self,create_vol):
        """
        DESC: Create a new volume in a project
        All user levels can spin up new volumes.
        INPUTS: self object
                create_vol - dictionary containing the
                        volume_name - REQ
                        volume_size - REQ
                        project_id - REQ
                        volume_type - Optional default is ssd
                        volume_zone - Optional default is nova
                        description - Optional
        OUTPUTS: r_dict - volume_name
                        - volume_type
                        - volume_id
                        - volume_size
        ACCESS: Admins can create a volume in any project, Users can only create
                volumes in their primary projects
        NOTE: You can not create two volumes with the same name in the same project.
        """
        logger.sys_info('\n**Create Volume. Component: Cinder Def: create_volume**\n')
        #check to make sure all params have been passed
        if(not create_vol):
            logger.sys_error("Did not pass in create_vol dictionary to create volume operation.")
            raise Exception("Did not pass in create_vol dictionary to create volume operation.")
        if(('volume_name' not in create_vol) or ('volume_size' not in create_vol)):
            logger.sys_error("Did not pass required params to create volume operation.")
            raise Exception("Did not pass required params to create volume operation.")
        if('description' not in create_vol):
            logger.sys_warning("Did not pass in a volume description setting the defaut description.")
            create_vol['description'] = "%s volume" %(create_vol['project_id'])
         #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to create volumes.")
            raise Exception("Status level not sufficient to create volumes.")

        create_flag = 0
        if(self.is_admin == 0):
            if(self.project_id == create_vol['project_id']):
                create_flag = 1
        elif(self.is_admin == 1):
            if(create_vol['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,create_vol['project_id'])
            create_flag = 1

        #default to ssd
        voltype = None
        if('volume_type' not in create_vol):
            voltype = 'ssd'
        elif('volume_type' in create_vol):
            voltype = create_vol['volume_type']

        ## DEBUG ONLY!! Need to determine why list_volume_types is not working in this case.
        vol_type_found = True
        #voltype_list = self.list_volume_types()
        #vol_type_found = False
        #for vol_type in voltype_list:
        #    if vol_type['name'].lower() == voltype.lower():
        #        vol_type_found = True
        #        break

        if not vol_type_found:
            raise Exception ("Volume Type %s was not found for volume creation" % voltype)

        #get the name of the project based on the id
        try:
            select = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(create_vol['project_id'])}
            proj_name = self.db.pg_select(select)
        except:
            logger.sql_error("Could not get the project name from Transcirrus DB.")
            raise Exception("Could not get the project name from Transcirrus DB.")

        try:
            select_uuid = {"select":"keystone_user_uuid","from":"trans_user_info","where":"user_name='%s'" %(self.username)}
            keystone_user = self.db.pg_select(select_uuid)
        except:
            logger.sql_error("Could not get the user uuid from Transcirrus DB.")
            raise Exception("Could not get the user uuid from Transcirrus DB.")

        #check to see if a vol in the project with same name already exists
        try:
            select_vol = {"select":"vol_id","from":"trans_system_vols","where":"proj_id='%s'" %(create_vol['project_id']),"and":"vol_name='%s'"%(create_vol['volume_name'])}
            volume = self.db.pg_select(select_vol)
        except:
            logger.sql_error("Could not get the volume name from Transcirrus DB.")
            raise Exception("Could not get the volume name from Transcirrus DB.")

        if(len(volume) >= 1):
            logger.sql_error("Volume with the name %s already exists."%(create_vol['volume_name']))
            create_vol['volume_name'] = create_vol['volume_name']+'_%s'%(str(self.rannum))

        if('description' not in create_vol) or (create_vol['description'] == 'none'):
            logger.sys_warning("Did not pass in a volume description setting the default description.")
            if('snapshot_id' in create_vol):
                create_vol['description'] = "%s volume from snapshot %s." %(create_vol['volume_name'],create_vol['snapshot_id'])
            elif('source_vol_id' in create_vol):
                create_vol['description'] = "%s volume clone from volume %s." %(create_vol['volume_name'],create_vol['source_vol_id'])
            else:
                create_vol['description'] = "%s volume" %(create_vol['project_id'])
            raise Exception("Volume with the name %s already exists."%(create_vol['volume_name']))
        
        #check the project capacity
        # nned to impliment quatas

        if(create_flag == 1):
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                if(create_vol['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,create_vol['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")
    
            try:
                #add the new user to openstack 
                body = '{"volume":{"status": "creating", "availability_zone": null, "source_volid": null, "display_description": null, "snapshot_id": null, "user_id": null, "size": %s, "display_name": "%s", "imageRef": null,"attach_status": "detached","volume_type": "%s", "project_id": null, "metadata": {}}}'%(create_vol['volume_size'],create_vol['volume_name'],voltype)
                token = self.token
                #NOTE: if token is not converted python will pass unicode and not a string
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": token}
                function = 'POST'
                api_path = '/v1/%s/volumes' %(create_vol['project_id'])
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
            except Exception, e:
                logger.sys_error("Error creating new volume - %s" % e)
                raise Exception("Error creating new volume - %s" % e)

            load = json.loads(rest['data'])
            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s Data: %s" %(rest['response'],rest['reason'],rest['data']))
                volname = str(load['volume']['display_name'])
                volid = str(load['volume']['id'])
                volsize = int(load['volume']['size'])

                input_dict = {'volume_id':volid,'project_id':create_vol['project_id']}
                while(True):
                    status = self.get_volume(input_dict)
                    if(status['volume']['status'] == 'available'):
                        logger.sys_info('Volume with id %s provisioned.'%(volid))
                        break
                    elif(status['volume']['status'] == 'creating'):
                        logger.sys_info('Volume with ID %s creating.'%(volid))
                        time.sleep(2)
                    elif(status['volume']['status'] == 'unknown'):
                        logger.sys_info('Volume with ID %s in unknown state.'%(volid))
                        raise Exception("Could not create a new volume. Unknown error occurred.")
                    elif(status['volume']['status'] == 'error'):
                        logger.sys_info('Volume with ID %s failed to provision.'%(volid))
                        raise Exception("Could not create a new volume. ERROR: 555")

                try:
                    #insert the volume info into the DB
                    self.db.pg_transaction_begin()
                    insert_vol = {"vol_id": volid,"proj_id": create_vol['project_id'],"keystone_user_uuid": keystone_user[0][0],"vol_name": volname,"vol_size": volsize,"vol_type":create_vol['volume_type'],"vol_attached_to_inst":"NONE"}
                    self.db.pg_insert("trans_system_vols",insert_vol)
                except Exception, e:
                    self.db.pg_transaction_rollback()
                    logger.sql_error("Could not enter in volume %s information into Transcirrus DB" %(volname))
                    raise e
                else:
                    self.db.pg_transaction_commit()
                    r_dict = {"volume_id": volid, "volume_type": voltype,"volume_name": volname, "volume_size": volsize}
                    return r_dict
            else:
                logger.sys_error("Could not create a new volume - %s: %s" % (rest['response'], rest['reason']))
                raise Exception("Could not create a new volume - %s: %s" % (rest['response'], rest['reason']))
                #ec.error_codes(rest)
        else:
            logger.sys_error("Could not create a new volume. Unknown error occurred. ERROR: 555")
            raise Exception("Could not create a new volume. Unknown error occurred. ERROR: 555")

    def create_vol_from_snapshot(self,input_dict):
        """
        DESC: Create a new volume in a project from an existing snapshot in the project.
        All user levels can spin up new volumes.
        INPUTS: volume_size - REQ
                project_id - REQ
                snapshot_id - REQ
                volume_name - OP
                volume_zone - Optional default is nova
                description - Optional
        OUTPUTS: r_dict - volume_name
                        - volume_type
                        - volume_id
                        - volume_size
        ACCESS: Admins can create a volume with any snapshot, Users can only create
                volumes with snapshots they own.
        NOTE: You can not create two volumes with the same name in the same project.
        """
        #create = {'volume_name':'test111','volume_size':'1','project_id':"bf54175ff7594e23b8f320c74fb05d68",'volume_type':'ssd','snapshot_id':'a32d8390-1df0-445a-b560-f38697dd3d8f'}
        #make sure snapshot id is given.
        if(('snapshot_id' not in input_dict) or (input_dict['snapshot_id'] == '')):
            logger.sys_error("Snapshot ID is required.")
            raise Exception("Snapshot ID is required.")

        if(('volume_zone' not in input_dict) or (input_dict['volume_zone'] == '')):
            input_dict['volume_zone'] = 'nova'

        if(('project_id' not in input_dict) or (input_dict['project_id'] == '')):
            logger.sys_error("Project ID is required.")
            raise Exception("Project ID is required.")

        if(('volume_name' not in input_dict) or (input_dict['volume_name'] == 'none')):
            input_dict['volume_name'] = input_dict['snapshot_id'] + '_vol_from_snap_%s'%(str(self.rannum))

        if('description' not in input_dict) or (input_dict['description'] == 'none'):
            logger.sys_warning("Did not pass in a volume description setting the default description.")
            input_dict['description'] = "%s volume from snapshot" %(input_dict['project_id'])

        if(self.is_admin == 0):
            if(self.user_level == 1):
                self.select_snap = {'select':'proj_id','from':'trans_system_snapshots','where':"snap_id='%s'"%(input_dict['snapshot_id']),'and':"proj_id='%s'"%(input_dict['project_id'])}
            elif(self.is_admin == 2):
                self.select_snap = {'select':'proj_id','from':'trans_system_snapshots','where':"snap_id='%s'"%(input_dict['snapshot_id']),'and':"user_id='%s'"%(self.user_id)}
        else:
            self.select_snap = {'select':'proj_id','from':'trans_system_snapshots','where':"snap_id='%s'"%(input_dict['snapshot_id'])}

        #check if the snapshot exists in the project and that the user can use it
        try:
            get_snap = self.db.pg_select(self.select_snap)
        except:
            logger.sys_error("The snapshot does not exist in this project, or you may not have permission to use it.")
            raise Exception("The snapshot does not exist in this project, or you may not have permission to use it.")

        input_dict2 = {'volume_name':input_dict['volume_name'],'volume_size':input_dict['volume_size'],'project_id':input_dict['project_id'],
                      'volume_zone':input_dict['volume_zone'],'description':input_dict['description'],'snapshot_id':input_dict['snapshot_id']}

        output = self.create_volume(input_dict)

        return output

    def create_vol_clone(self,input_dict):
        """
        DESC: Create a new volume in a project from an existing snapshot in the project.
        All user levels can spin up new volumes.
        INPUTS: volume_id - REQ
                project_id - REQ
                volume_name - OP
                volume_zone - Optional default is nova
                description - Optional
        OUTPUTS: r_dict - volume_name
                        - volume_type
                        - volume_id
                        - volume_size
        ACCESS: Admins can create a volume with any snapshot, Users can only create
                volumes with snapshots they own.
        NOTE: You can not create two volumes with the same name in the same project.
        """

        #make sure snapshot id is given.
        if(('volume_id' not in input_dict) or (input_dict['volume_id'] == '')):
            logger.sys_error("Volume ID is required.")
            raise Exception("Volume ID is required.")

        if(('project_id' not in input_dict) or (input_dict['project_id'] == '')):
            logger.sys_error("Project ID is required.")
            raise Exception("Project ID is required.")

        if(('volume_zone' not in input_dict) or (input_dict['volume_zone'] == '')):
            input_dict['volume_zone'] = 'nova'

        if(('volume_name' not in input_dict) or (input_dict['volume_name'] == 'none')):
            input_dict['volume_name'] = input_dict['volume_id'] + '_clone_%s'%(str(self.rannum))

        if('description' not in input_dict) or (input_dict['description'] == 'none'):
            logger.sys_warning("Did not pass in a volume description setting the default description.")
            input_dict['description'] = "%s volume from snapshot" %(input_dict['project_id'])

        if(self.is_admin == 0):
            if(self.user_level == 1):
                self.select_vol = {'select':'proj_id,vol_size','from':'trans_system_vols','where':"vol_id='%s'"%(input_dict['volume_id']),'and':"proj_id='%s'"%(input_dict['project_id'])}
            elif(self.is_admin == 2):
                self.select_vol = {'select':'proj_id,vol_size','from':'trans_system_vols','where':"vol_id='%s'"%(input_dict['volume_id']),'and':"user_id='%s'"%(self.user_id)}
        else:
            self.select_vol = {'select':'proj_id,vol_size','from':'trans_system_vols','where':"vol_id='%s'"%(input_dict['volume_id'])}

        #check if the snapshot exists in the project and that the user can use it
        try:
            get_vol= self.db.pg_select(self.select_vol)
        except:
            logger.sys_error("The volume does not exist in this project, or you may not have permission to clone it.")
            raise Exception("The volume does not exist in this project, or you may not have permission to clone it.")

        #if no vol size given
        if(('volume_size' not in input_dict) or (input_dict['volume_size'] == '')):
            input_dict['volume_size'] = get_vol[0][1]

        input_dict = {'volume_name':input_dict['volume_name'],'volume_size':input_dict['volume_size'],'project_id':input_dict['project_id'],
                      'volume_zone':input_dict['volume_zone'],'description':input_dict['description'],'volume_id':input_dict['volume_id']}

        output = self.create_volume(input_dict)

        return output

    def get_volume(self,input_dict):
        """
        DESC: Strictly call the v1 cinder API to get real time vol info
        INPUTS: self object
                input_dict - dictionary containing the
                        volume_id - REQ
                        project_id - REQ
        OUTPUTS: rest_api_output
        ACCESS: Admins can create a volume in any project, Users can only create
                volumes in their primary projects
        NOTE: Admins can list all volumes, users can only list the volumes in their project.
            This will need to be combined with get_volume_info in the future.
        """
        if(not input_dict):
            logger.sys_error("Did not pass in input_dict dictionary to get volume operation.")
            raise Exception("Did not pass in input_dict dictionary to get volume operation.")
        if(('volume_id' not in input_dict) or ('project_id' not in input_dict)):
            logger.sys_error("Did not pass required params to get volume operation.")
            raise Exception("Did not pass required params to get volume operation.")

        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(input_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            #add the new user to openstack 
            body = ''
            token = self.token
            #NOTE: if token is not converted python will pass unicode and not a string
            header = {"Content-Type": "application/json", "X-Auth-Token": token}
            function = 'GET'
            api_path = '/v1/%s/volumes/%s' %(input_dict['project_id'],input_dict['volume_id'])
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error('%s'%(e))
            #back the user out of the transcirrus DB if the db works and the REST API fails
            raise e

        if(rest['response'] == 200):
            load = json.loads(rest['data'])
        else:
            ec.error_codes(rest)

        return load



    def create_vol_from_snapshot(self):
        print "not implemented"

    def delete_volume(self,delete_vol):
        """
        DESC: Delete a volume from the environmnet.
        INPUT delete_vol - volume_id - req
                         - project_id - req
        OUTPUT 'OK' - success
        ACCESS: Users and power users can only delete the volumes they created in a project
                admins can delete any vol or a fault if there is an error
        """
        logger.sys_info('\n**Delete a volume. Component: Cinder Def: delete_volume**\n')
        #NOTE: we will get all info from the Transcirrus DB
        if((not delete_vol) or delete_vol['volume_id'] == ""):
            logger.sys_error("Delete vol parameter was not given or is blank.")
            raise Exception("Delete vol parameter was not given or is blank.")
        if('volume_id' not in delete_vol):
            logger.sys_error("Requiered parameter volume_id not given for delete vol operation.")
            raise Exception("Requiered parameter volume_id not given for delete vol operation.")
        if(('project_id' not in delete_vol) or (delete_vol['project_id'] == '')):
            logger.sys_error("Requiered parameter project_id not given for delete vol operation.")
            raise Exception("Requiered parameter project_id not given for delete vol operation.")

        #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to delete volumes.")
            raise Exception("Status level not sufficient to delete volumes.")

        #get the name of the project based on the id
        try:
            select = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(delete_vol['project_id'])}
            proj_name = self.db.pg_select(select)
        except Exception as e:
            logger.sql_error("Could not get the project name from Transcirrus DB.")
            raise e

        #make sure the volume is in the DB
        try:
            get_vol_id = {'select':"vol_name,keystone_user_uuid", 'from':"trans_system_vols", 'where':"vol_id='%s'"%(delete_vol['volume_id']),'and':"proj_id='%s'"%(delete_vol['project_id'])}
            vol_id = self.db.pg_select(get_vol_id)
            if(not vol_id[0][0]):
                logger.sys_error("Volume not found for given volume id: %s." %(delete_vol['volume_id']))
                raise Exception("Volume not found for given volume id: %s." %(delete_vol['volume_id']))
        except Exception as e:
            logger.sql_error("Could not query the Transcirrus DB ")
            raise e

        #default the del_status to 0 - DO NOT delete
        del_status = 0
        #if the user proj id matches the volume proj_id they can delete the volume
        if(self.user_level >=1):
            if((self.project_id == delete_vol['project_id']) and (self.user_id == vol_id[0][1])):
                #del_status = 1 - DELETE volume
                logger.sys_info("The user can delete volume with id %s"%(delete_vol['volume_id']))
                del_status = 1
            else:
                logger.sys_error("Users can not delete volumes outside of their project.")
                raise Exception("Users can not delete volumes outside of their project.")
        elif(self.is_admin == 1):
            logger.sys_info("The user is an admin and can delete any volume.")
            if(delete_vol['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,delete_vol['project_id'])
            del_status = 1
        else:
            logger.sys_error("The user level is invalid, can not delete the volume.")
            raise Exception("The user level is invalid, can not delete the volume.")

        if(del_status == 1):
            try:
                #api_dict = {"username":self.username, "password":self.password, "project_id":delete_vol['project_id']}
                #api = caller(api_dict)
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                if(delete_vol['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,delete_vol['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the Keystone API")
                raise Exception("Could not connect to the Keystone API")

            try:
                #add the new user to openstack 
                body = ""
                token = self.token
                #NOTE: if token is not converted python will pass unicode and not a string
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": token}
                function = 'DELETE'
                api_path = '/v1/%s/volumes/%s' %(delete_vol['project_id'],delete_vol['volume_id'])
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                logger.sql_error("Could not get the project_id from the Transcirrus DB.%s" %(e))
                #back the user out of the transcirrus DB if the db works and the REST API fails
                raise e

            if(rest['response'] == 202):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                try:
                    #insert the volume info into the DB
                    self.db.pg_transaction_begin()
                    del_vol = {"table":'trans_system_vols',"where":"vol_id='%s'" %(delete_vol['volume_id'])}
                    self.db.pg_delete(del_vol)
                except:
                    self.db.pg_transaction_rollback()
                    logger.sql_error("Could not delete volume %s information from Transcirrus DB" %(vol_id[0][0]))
                    raise Exception("Could not delete volume %s information from Transcirrus DB" %(vol_id[0][0]))
                else:
                    self.db.pg_transaction_commit()
                    return 'OK'
            else:
                #util.http_codes(rest['response'],rest['reason'])
                ec.error_codes(rest)
        else:
            logger.sys_error("The user level is invalid, can not delete the volume.")
            raise Exception("The user level is invalid, can not delete the volume.")

    def list_volumes(self,project_id=None):
        """
        DESC: list the volumes for a particular project if the user is a member
              only admins can list all volumes on the system
        INPUT: project_id - op
        OUTPUT - array of volumes dict {"volume_id":'',"volume_name":'', "volume_type": "","project_id":''}
        ACCESS: Admins can list all volumes, users can only list the volumes in their project
        """
        logger.sys_info('\n**List volums. Component: Cinder Def: list_volumes**\n')
        #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to list volumes.")
            raise Exception("Status level not sufficient to list volumes.")

        #build the select statement
        select_vol = ""
        if(self.user_level == 0):
            if(project_id):
                select_vol = {"select":'*',"from":'trans_system_vols',"where":"proj_id='%s'" %(project_id)}
            else:
                select_vol = {"select":'*',"from":'trans_system_vols'}
        elif(self.user_level == 1):
            select_vol = {"select":'*',"from":'trans_system_vols',"where":"proj_id='%s'" %(self.project_id)}
        elif(self.user_level == 2):
            select_vol = {"select":'*',"from":'trans_system_vols',"where":"proj_id='%s'" %(self.project_id),"and":"keystone_user_uuid='%s'"%(self.user_id)}
        else:
            raise Exception("Could not list volumes, invalid user level.")

        volumes = self.db.pg_select(select_vol)

        vol_array = []
        for vol in volumes:
            vol_dict = {"volume_id":vol[0],"volume_name":vol[3],"volume_type":vol[10],"project_id":vol[1]}
            vol_array.append(vol_dict)

        return vol_array

    def get_volume_info(self,vol_dict):
        """
        DESC: Get all of the information for a specific volume. Admins and power users can get info on
              any volume in their project. Users can only list their own volumes
        INPUT:  vol_dict - volume_id - req
                         - project_id - op -def user project id
        OUTPUT: r_dict - volume_name
                       - volume_type
                       - volume_id
                       - volume_size
                       - volume_attached
                       - volume_instance
                       - volume_instance_name
                       - volume_mount
        ACCESS: Admins can list all volumes, users can only list the volumes in their project
        """
        logger.sys_info('\n**Get specific info on a volume. Component: Cinder Def: get_volume_info**\n')
        #sanity check
        if(('volume_id' not in vol_dict) or vol_dict['volume_id'] == ''):
            logger.sys_error("Did not pass required params to get volume info.")
            raise Exception("Did not pass required params to get volume info.")

        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to list volumes.")
            raise Exception("Status level not sufficient to list volumes.")

        #make sure the project exists
        proj_id = None
        if('project_id' in vol_dict):
            try:
                select_proj = {'select':"proj_id",'from':"projects",'where':"proj_id='%s'"%(vol_dict['project_id'])}
                proj = self.db.pg_select(select_proj)
                proj_id = proj[0][0]
            except:
                logger.sql_error('Project %s given does not exist.'%(vol_dict['project_id']))
                raise Exception('Project %s given does not exist.'%(vol_dict['project_id']))
        else:
            proj_id = self.project_id

        #get the r_dict based on the user type
        get_vol_dict = None
        if(self.user_level == 2):
            if(self.project_id == proj_id):
                get_vol_dict = {'select':'*','from':'trans_system_vols','where':"vol_id='%s'" %(vol_dict['volume_id']),'and':"keystone_user_uuid='%s'" %(self.user_id)}
            else:
                logger.sys_error('User could not get vol info for vol: %s'%(vol_dict['volume_id']))
                raise Exception('User could not get vol info for vol: %s'%(vol_dict['volume_id']))
        elif(self.user_level == 1):
            if(self.project_id == proj_id):
                get_vol_dict = {'select':'*','from':'trans_system_vols','where':"vol_id='%s'" %(vol_dict['volume_id']),'and':"proj_id='%s'" %(vol_dict['project_id'])}
            else:
                logger.sys_error('User could not get vol info for vol: %s'%(vol_dict['volume_id']))
                raise Exception('User could not get vol info for vol: %s'%(vol_dict['volume_id']))
        else:
            get_vol_dict = {'select':'*','from':'trans_system_vols','where':"vol_id='%s'" %(vol_dict['volume_id']),'and':"proj_id='%s'" %(vol_dict['project_id'])}
        try:
            get_vol = self.db.pg_select(get_vol_dict)
        except:
            logger.sql_error("Could not get the volume info for %s" %(vol_dict['volume_id']))
            raise Exception("Could not get the volume info for %s" %(vol_dict['volume_id']))

        instance_name = None
        if(get_vol[0][8]):
            try:
                get_server = {'select':'inst_name','from':'trans_instances','where':"inst_id='%s'"%(get_vol[0][8])}
                inst_name = self.db.pg_select(get_server)
                instance_name = inst_name[0][0]
            except Exception as e:
                logger.sql_error("Could not get the instance name for instance id %s, %s"%(get_vol[0][8],e))

        r_dict = {'volume_name':get_vol[0][3],'volume_type':get_vol[0][10],'volume_id':get_vol[0][0],'volume_size':get_vol[0][4],'volume_attached':get_vol[0][7],'volume_instance':get_vol[0][8],'volume_instance_name':instance_name}
        return r_dict

    def create_volume_type(self,volume_type_name):
        """
        DESC: Create a volume type and add the volume key(target vlume) to it. Used to add new
              types or to customize storage layout.
        INPUT:  volume_type_name - req
        OUTPUT: r_dict - volume_type_name
                       - volume_type_id
        ACCESS: Admins can create volume types.
        """
        logger.sys_info('\n**Create a new volume type. Component: Cinder Def: get_volume_info**\n')
        if(not 'volume_type_name'):
            logger.sys_error("Requiered parameter volume_type not given for create volume type operation.")
            raise Exception("Requiered parameter volume_type not given for create volume type operation.")

        #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to create volume types.")
            raise Exception("Status level not sufficient to create volume types.")

        #Talk to the cinder API
        if(self.is_admin == 1):
            voltype = volume_type_name
            try:
                #build an api connection
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the new volume type to openstack 
                body = '{"volume_type": {"name": "%s"}}'%(voltype)
                token = self.token
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": self.project_id, "X-Auth-Token": token}
                function = 'POST'
                api_path = '/v1/%s/types' %(self.project_id)
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                logger.sys_error("Could not add the volume type %s" %(e))
                raise Exception("Could not add the volume type %s" %(e))

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s Data: %s" %(rest['response'],rest['reason'],rest['data']))
                load = json.loads(rest['data'])
                vol_type_name = str(load['volume_type']['name'])
                vol_type_id = str(load['volume_type']['id'])
                r_dict = {"volume_type_name": vol_type_name, "volume_type_id": vol_type_id}
                return r_dict
            else:
                logger.sys_error("Could not create new volume type %s, error: %s - %s" % (volume_type_name, rest['response'], rest['reason']))
                raise Exception ("Could not create new volume type %s, error: %s - %s" % (volume_type_name, rest['response'], rest['reason']))
        else:
            logger.sys_error("Could not create a new volume type, not an admin.")
            raise Exception("Could not create a new volume type, not an admin.")

    def delete_volume_type(self, volume_type_name):
        """
        DESC: Deletes a volume type.
        INPUT:  volume_type_name - req
        OUTPUT: True / False
        ACCESS: Admins can delete volume types.
        """
        logger.sys_info('\n**Delete a volume type.**\n')
        if (not 'volume_type_name'):
            logger.sys_error("Requiered parameter volume_type_name not given for delete volume type operation.")
            raise Exception("Requiered parameter volume_type_name not given for create volume type operation.")

        #sanity check
        if (self.status_level < 2):
            logger.sys_error("Status level not sufficient to delete volume types.")
            raise Exception("Status level not sufficient to delete volume types.")

        #Talk to the cinder API
        if (self.is_admin == 1):
            try:
                #build an api connection
                api_dict = {"username": self.username, "password": self.password, "project_id": self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error ("Could not connect to the API")
                raise Exception ("Could not connect to the API")

            vol_list = self.list_volume_types()
            vol_type_id = None
            for vol_type in vol_list:
                if vol_type['name'].lower() == volume_type_name.lower():
                    vol_type_id = vol_type['id']
                    break

            if vol_type_id == None:
                raise Exception ("Volume Type %s was not found for deletion" % volume_type_name)

            try:
                # delete the volume type 
                body = ''
                token = self.token
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": self.project_id, "X-Auth-Token": token}
                function = 'DELETE'
                api_path = '/v1/%s/types/%s' % (self.project_id, vol_type_id)
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                logger.sys_error("Could not delete the volume type %s, exception: %s" % (volume_type_name, e))
                raise Exception ("Could not delete the volume type %s, exception: %s" % (volume_type_name, e))

            if (rest['response'] == 202 or rest['response'] == 200):
                logger.sys_info("Delete volume type %s was successful" % volume_type_name)
                return True
            elif (rest['response'] == 400):
                data = json.loads(rest['data'])
                logger.sys_error("Could not delete the volume type %s, error: %s - %s" % (volume_type_name, rest['response'], data['badRequest']['message']))
                raise Exception ("Could not delete the volume type %s, error: %s - %s" % (volume_type_name, rest['response'], data['badRequest']['message']))
            else:
                logger.sys_error("Could not delete the volume type %s, error: %s - %s" % (volume_type_name, rest['response'], rest['reason']))
                raise Exception ("Could not delete the volume type %s, error: %s - %s" % (volume_type_name, rest['response'], rest['reason']))
        else:
            logger.sys_error ("Could not delete the volume type %s, must be an admin." % volume_type_name)
            raise Exception ("Could not delete the volume type %s, must be an admin." % volume_type_name)

    def list_volume_types(self):
        """
        DESC: List the available volume types.
        INPUT: none
        OUTPUT: array of dict  - name
                               - id
                               - extra_specs - backends, etc...
        ACCESS: Admin - can assign volume types to backends
                PU - none
                user - none
        NOTE:
        The REST output looks like this:
          {"volume_types":
            [
              {"extra_specs": {"volume_backend_name": "RHS"},     "name": "test",    "id": "3e1c9036-4ccd-40e1-9b44-6fd2cc3dff4b"},
              {"extra_specs": {"volume_backend_name": "ssd"},     "name": "ssd",     "id": "97109e9a-198f-4509-9ecc-d9859e919446"},
              {"extra_specs": {"volume_backend_name": "spindle"}, "name": "spindle", "id": "411e8c4a-7f74-4ac9-8d1a-56fdc838b973"},
              {"extra_specs": {},                                 "name": "jon",     "id": "d1c4878f-aa43-4483-8cfe-e0a7a4262b8f"}
            ]
          }
          We return an array of dicts that looks like this:
            [{"extra_specs": {"volume_backend_name": "RHS"},     "name": "test",    "id": "3e1c9036-4ccd-40e1-9b44-6fd2cc3dff4b"},
             {"extra_specs": {"volume_backend_name": "ssd"},     "name": "ssd",     "id": "97109e9a-198f-4509-9ecc-d9859e919446"},
             {"extra_specs": {"volume_backend_name": "spindle"}, "name": "spindle", "id": "411e8c4a-7f74-4ac9-8d1a-56fdc838b973"},
             {"extra_specs": {},                                 "name": "jon",     "id": "d1c4878f-aa43-4483-8cfe-e0a7a4262b8f"}
            ]
        """
        #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to create volume types.")
            raise Exception("Status level not sufficient to create volume types.")

        #Talk to the cinder API
        #if(self.is_admin == 1):
        try:
            #build an api connection
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the API")
            raise Exception("Could not connect to the API")

        try:
            #get list of volume types
            body = ''
            token = self.token
            header = {"Content-Type": "application/json", "X-Auth-Project-Id": self.project_id, "X-Auth-Token": token}
            function = 'GET'
            api_path = '/v1/%s/types' %(self.project_id)
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
            rest = api.call_rest(rest_dict)
        except Exception as e:
            logger.sys_error("Could not get volume type list, %s" %(e))
            raise Exception ("Could not get volume type list, %s" %(e))

        if(rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("list_volume_types: Response %s with Reason %s Data: %s" %(rest['response'],rest['reason'],rest['data']))
            load = json.loads(rest['data'])
            r_dict = []
            for vtype in load['volume_types']:
                name = vtype['name']
                id = vtype['id']
                extra_specs = vtype['extra_specs']
                r_dict.append({'name': name, 'id': id, 'extra_specs': extra_specs})
            return r_dict
        else:
            #util.http_codes(rest['response'],rest['reason'],rest['data'])
            #ec.error_codes(rest)
            logger.sys_error("Error getting volume type list, %s - %s" % (rest['reason'], rest['response']))
            raise Exception ("Error getting volume type list, %s - %s" % (rest['reason'], rest['response']))
        #else:
        #    logger.sys_error("Could not get volume type list.")
        #    raise ("Could not get volume type list.")

    def list_volume_backends(self):
        """
        DESC: List the available volume backend names.
        INPUT: none
        OUTPUT: r_array - backend names
        ACCESS: Admin - can assign volume types to backends
                PU - none
                user - none
        NOTE: as of now only spindle and ssd will be displayed
        """
        raise Exception ("function list_volume_backends is not supported, call list_volume_types instead")
        if(self.is_admin == 1):
            r_array = ['ssd','spindle']
            return r_array

    def assign_volume_type_to_backend(self,input_dict):
        """
        DESC: Assign a volume type to a volume backend
        INPUT:  input_dict - volume_type_id - req
                           - volume_backend_name - req
        OUTPUT: OK - success
                ERROR - fail
        ACCESS: Admin - can assign volume types to backends
                PU - none
                user - none
        """
        logger.sys_info('\n**Get specific info on a volume. Component: Cinder Def: get_volume_info**\n')
        if(('volume_type_id' not in input_dict) or input_dict['volume_type_id'] == ''):
            logger.sys_error("Did not pass required params to assign volume type to volume backend.")
            raise Exception("Did not pass required params to assign volume type to volume backend.")
        if(('volume_backend_name' not in input_dict) or input_dict['volume_backend_name'] == ''):
            logger.sys_error("Did not pass required params to assign volume type to volume backend.")
            raise Exception("Did not pass required params to assign volume type to volume backend.")

        #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to create volume types.")
            raise Exception("Status level not sufficient to create volume types.")

        #Talk to the cinder API
        if(self.is_admin == 1):
            try:
                #build an api connection
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")

            try:
                #add the new user to openstack 
                body = '{"extra_specs": {"volume_backend_name": "%s"}}'%(input_dict['volume_backend_name'])
                token = self.token
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": self.project_id, "X-Auth-Token": token}
                function = 'POST'
                api_path = '/v1/%s/types/%s/extra_specs' %(self.project_id,input_dict['volume_type_id'])
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                logger.sys_error("Could not add the volume type backend, %s" %(e))
                #back the user out of the transcirrus DB if the db works and the REST API fails
                return 'ERROR'

            if(rest['response'] == 200):
                return 'OK'
            else:
                #util.http_codes(rest['response'],rest['reason'],rest['data'])
                ec.error_codes(rest)
        else:
            logger.sys_error("Could not add volume type backing.")
            return 'ERROR'