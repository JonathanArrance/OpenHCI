#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

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

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

    def create_volume(self,create_vol):
        """
        DESC: Create a new volume in a project
        All user levels can spin up new volumes.
        INPUTS: self object
                create_vol - dictionary containing the
                        volume_name - REQ
                        volume_size - REQ
                        project_id - REQ
                        description - Optional
        OUTPUTS: r_dict - volume_name
                        - volume_id
                        - volume_size
        ACCESS: Admins can create a volume in any project, Users can only create
                volumes in their primary projects
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

        #connect to the transcirrus DB
        try:
            #connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB ")
            raise e

        create_flag = 0
        if(self.is_admin == 0):
            if(self.project_id == create_vol['project_id']):
                create_flag = 1
            print create_flag
        elif(self.is_admin == 1):
            if(create_vol['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,create_vol['project_id'])
            create_flag = 1

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

        #check the project capacity
        

        if(create_flag == 1):
            try:
                #build an api connection
                api_dict = {"username":self.username, "password":self.password, "project_id":create_vol['project_id']}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the API")
                raise Exception("Could not connect to the API")
    
            try:
                #add the new user to openstack 
                body = '{"volume":{"status": "creating", "availability_zone": null, "source_volid": null, "display_description": null, "snapshot_id": null, "user_id": null, "size": %s, "display_name": "%s", "imageRef": null,"attach_status": "detached","volume_type": null, "project_id": null, "metadata": {}}}'%(create_vol['volume_size'],create_vol['volume_name'])
                token = self.token
                #NOTE: if token is not converted python will pass unicode and not a string
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": token}
                function = 'POST'
                api_path = '/v1/%s/volumes' %(create_vol['project_id'])
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                logger.sql_error("Could not get the project_id from the Transcirrus DB.%s" %(e))
                #back the user out of the transcirrus DB if the db works and the REST API fails
                raise

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s Data: %s" %(rest['response'],rest['reason'],rest['data']))
                load = json.loads(rest['data'])
                volname = str(load['volume']['display_name'])
                volid = str(load['volume']['id'])
                volsize = int(load['volume']['size'])
                try:
                    #insert the volume info into the DB
                    self.db.pg_transaction_begin()
                    insert_vol = {"vol_id": volid,"proj_id": create_vol['project_id'],"keystone_user_uuid": keystone_user[0][0],"vol_name": volname,"vol_size": volsize,"vol_attached_to_inst":"NONE"}
                    self.db.pg_insert("trans_system_vols",insert_vol)
                except:
                    self.db.pg_transaction_rollback()
                    self.db.pg_close_connection()
                    logger.sql_error("Could not enter in volume %s information into Transcirrus DB" %(r_dict['volume_name']))
                    raise Exception("Could not enter in volume %s information into Transcirrus DB" %(r_dict['volume_name']))
                else:
                    self.db.pg_transaction_commit()
                    self.db.pg_close_connection()
                    r_dict = {"volume_id": volid, "volume_name": volname, "volume_size": volsize}
                    return r_dict
            else:
                util.http_codes(rest['response'],rest['reason'],rest['data'])
        else:
            logger.sys_error("Could not create a new volume.")
            raise Exception("Could not create a new volume.")

    def create_vol_from_snapshot(self):
        print "not implemented"

    def delete_volume(self,delete_vol):
        """
        DESC: Delete a volume from the environmnet.
        INPUT delete_vol - volume_id
                         - project_id
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

        #connect to the transcirrus DB
        try:
            #connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB ")
            raise e

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
                api_dict = {"username":self.username, "password":self.password, "project_id":delete_vol['project_id']}
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
                raise

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
                    self.db.pg_close_connection()
                    logger.sql_error("Could not delete volume %s information into Transcirrus DB" %(vol_id[0][0]))
                    raise Exception("Could not delete volume %s information into Transcirrus DB" %(vol_id[0][0]))
                else:
                    self.db.pg_transaction_commit()
                    self.db.pg_close_connection()
                    return 'OK'
            else:
                util.http_codes(rest['response'],rest['reason'])
        else:
            logger.sys_error("The user level is invalid, can not delete the volume.")

    def list_volumes(self,project_id=None):
        """
        DESC: list the volumes for a particular project if the user is a member
              only admins can list all volumes on the system
        INPUT: project_id - op
        OUTPUT - array of volumes dict {"volume_id":'',"volume_name":'',"project_id":''}
        ACCESS: Admins can list all volumes, users can only list the volumes in their project
        """
        logger.sys_info('\n**List volums. Component: Cinder Def: list_volumes**\n')
        #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to list volumes.")
            raise Exception("Status level not sufficient to list volumes.")

        #connect to the transcirrus DB
        try:
            #connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB ")
            raise e

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
        self.db.pg_close_connection()

        vol_array = []
        for vol in volumes:
            vol_dict = {"volume_id":vol[0],"volume_name":vol[3],"project_id":vol[1]}
            vol_array.append(vol_dict)

        return vol_array

    def get_volume_info(self,vol_dict):
        """
        DESC: Get all of the information for a specific volume. Admins and power users can get info on
              any volume in their project. Users can only list their own volumes
        INPUT:  vol_dict - volume_id
                         - project_id - op -def user project id
        OUTPUT: r_dict - volume_name
                       - volume_id
                       - volume_size
                       - volume_attached
                       - volume_instance
        ACCESS: Admins can list all volumes, users can only list the volumes in their project
        """
        logger.sys_info('\n**Get specific info on a volume. Component: Cinder Def: get_volume_info**\n')
        #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to list volumes.")
            raise Exception("Status level not sufficient to list volumes.")

         #connect to the transcirrus DB
        try:
            #connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB ")
            raise e

        #make sure the project exists
        proj_id = None
        if('project_id' in vol_dict):
            try:
                select_proj = {'select':"proj_id",'from':"projects",'where':"proj_id='%s'"%(vol_dict['project_id'])}
                proj = self.db.pg_select(select_proj)
                proj_id = proj[0][0]
            except:
                logger.sql_error('Project given does not exist.')
                raise Exception('Project given does not exist.')
        else:
            proj_id = self.project_id

        #get the r_dict based on the user type
        get_vol_dict = None
        if(self.user_level == 2):
            if(self.project_id == proj_id):
                get_vol_dict = {'select':'vol_id,vol_name,vol_size,vol_attached,vol_attached_to_inst','from':'trans_system_vols','where':"vol_id='%s'" %(vol_dict['volume_id']),'and':"keystone_user_uuid='%s'" %(self.user_id)}
            else:
                logger.sys_error('User could not get vol info for vol: %s'%(vol_dict['volume_id']))
                raise Exception('User could not get vol info for vol: %s'%(vol_dict['volume_id']))
        elif(self.user_level == 1):
            if(self.project_id == proj_id):
                get_vol_dict = {'select':'vol_id,vol_name,vol_size,vol_attached,vol_attached_to_inst','from':'trans_system_vols','where':"vol_id='%s'" %(vol_dict['volume_id']),'and':"proj_id='%s'" %(vol_dict['project_id'])}
            else:
                logger.sys_error('User could not get vol info for vol: %s'%(vol_dict['volume_id']))
                raise Exception('User could not get vol info for vol: %s'%(vol_dict['volume_id']))
        else:
            get_vol_dict = {'select':'vol_id,vol_name,vol_size,vol_attached,vol_attached_to_inst','from':'trans_system_vols','where':"vol_id='%s'" %(vol_dict['volume_id']),'and':"proj_id='%s'" %(vol_dict['project_id'])}

        try:
            print get_vol_dict
            get_vol = self.db.pg_select(get_vol_dict)
        except:
            logger.sql_error("Could not get the volume info for %s" %(volume_id))
            raise Exception("Could not get the volume info for %s" %(volume_id))

        self.db.pg_close_connection()
        r_dict = {'volume_name':get_vol[0][1],'volume_id':get_vol[0][0],'volume_size':get_vol[0][2],'volume_attached':get_vol[0][3],'volume_instance':get_vol[0][4]}
        return r_dict

    def create_volume_type(self,input_dict):
        """
        DESC: Create a volume tyo and add the volume key(target vlume) to it. Used to add new
              types or to customize storage layout.
        INPUT:  input_dict - volume_id
                           - project_id - op -def user project id
        OUTPUT: r_dict - volume_name
                       - volume_id
                       - volume_size
                       - volume_attached
                       - volume_instance
        ACCESS: Admins can list all volumes, users can only list the volumes in their project
        """
        logger.sys_info('\n**Get specific info on a volume. Component: Cinder Def: get_volume_info**\n')
        pass
