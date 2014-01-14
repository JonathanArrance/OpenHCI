#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token

from transcirrus.database.postgres import pgsql

class snapshot_ops:
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

    def create_snapshot(self,create_snap):
        """
        DESC: create a new snapshot of an exsisting volume
        INPUT create_snap - snap_name - snapshot name - REQ
                          - snap_desc - description - REQ
                          - project_id - project volume lives in - REQ
                          - vol_id - volume to snap - REQ
        OUTPUT: r_dict - snap_name
                       - snap_id
                       - vol_id
        ACCESS: users can only snap volumes in their project, admins can snapshot any volume
        """
        #check to make sure all params have been passed
        if(not create_snap):
            logger.sys_error("Did not pass in create_snap dictionary to create snapshot operation.")
            raise Exception("Did not pass in create_snap dictionary to create snapshot operation.")
        if(('snap_name' not in create_snap) or ('snap_desc' not in create_snap) or ('project_id' not in create_snap) or ('vol_id' not in create_snap)):
            logger.sys_error("Did not pass required params to create snapshot operation.")
            raise Exception("Did not pass required params to create snapshot operation.")
        #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to snapshot volumes.")
            raise Exception("Status level not sufficient to snapshot volumes.")

        #connect to the transcirrus DB
        try:
            #connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB ")
            raise e

        #get the name of the project based on the id
        try:
            select = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(create_snap['project_id'])}
            proj_name = self.db.pg_select(select)
        except:
            logger.sql_error("Could not get the project name from Transcirrus DB.")
            raise Exception("Could not get the project name from Transcirrus DB.")

        snap_status = 0
        if(self.user_level >=1):
            if(self.project_id == create_snap['project_id']):
                logger.sys_info("The user can not create a snap of a volume in this project.")
                snap_status = 1
            else:
                logger.sys_error("Users can not snapshot volumes outside of their project.")
                raise Exception("Users can not snapshot volumes outside of their project.")
        elif(self.user_level == 0):
            logger.sys_info("The user is an admin and can snapshot any volume.")
            snap_status = 1
        else:
            logger.sys_error("The user level is invalid, can not delete the volume.")
            raise Exception("The user level is invalid, can not delete the volume.")

        #check the volid in the project
        try:
            get_vol = {'select':"proj_id",'from':"trans_system_vols",'where':"vol_id='%s'"%(create_snap['vol_id'])}
            vol_proj = self.db.pg_select(get_vol)
            if(vol_proj[0][0] == create_snap['project_id']):
                logger.sys_info("The volume is in the requested project.")
                snap_status = 1
            else:
                logger.sys_info("The volume is not in the requested project.")
                snap_status = 0
        except:
            logger.sql_error("Could not get the volume name from Transcirrus DB.")
            raise Exception("Could not get the volume name from Transcirrus DB.")

        if(snap_status == 1):
            #connect to the API
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":create_snap['project_id']}
                if(create_snap['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,create_snap['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the Keystone API")
                raise Exception("Could not connect to the Keystone API")

            try:
                #add the new user to openstack 
                body = '{"snapshot": {"display_name": "%s", "force": false, "display_description": "%s", "volume_id": "%s"}}' %(create_snap['snap_name'],create_snap['snap_desc'],create_snap['vol_id'])
                token = self.token
                #NOTE: if token is not converted python will pass unicode and not a string - WTF not sure what was goin on here
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": str(token)}
                function = 'POST'
                api_path = '/v1/%s/snapshots' %(create_snap['project_id'])
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
                r_dict = ""
            except:
                logger.sys_error("Volume snapshot %s may or may not have been created." %(create_snap['snap_name']))
                #back the user out of the transcirrus DB if the db works and the REST API fails
                raise

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                #NOTE: this has to work - Celery?
                #loop until snap becomes available
                load = json.loads(rest['data'])
                try:
                    #insert the volume info into the DB
                    self.db.pg_transaction_begin()
                    insert_snap = {"snap_id": load['snapshot']['id'],"vol_id": load['snapshot']['volume_id'],"proj_id": create_snap['project_id'],"snap_name": create_snap['snap_name'],"snap_desc": create_snap['snap_desc']}
                    self.db.pg_insert("trans_system_snapshots",insert_snap)
                except:
                    self.db.pg_transaction_rollback()
                    self.db.pg_close_connection()
                    logger.sql_error("Could not enter in snapshot %s information into Transcirrus DB" %(create_snap['snap_name']))
                    raise Exception("Could not enter in snapshot %s information into Transcirrus DB" %(create_snap['snap_name']))
                else:
                    self.db.pg_transaction_commit()
                    self.db.pg_close_connection()
                    r_dict = {"snap_name": create_snap['snap_name'],"snap_id": load['snapshot']['id'], "vol_id": load['snapshot']['volume_id']}
                    return r_dict
            else:
                util.http_codes(rest['response'],rest['reason'])
        else:
            logger.sys_error("The user level is invalid, can not delete the volume.")

    def delete_snapshot(self,input_dict):
        """
        DESC: Delete a snapshot
        INPUT: input_dict - snap_id
                          - project_id
        OUTPUT: OK if successful
        ACCESS: Admins can delete any volume
                Users can only snap volumes in their project.
        """
        #check to make sure all params have been passed
        if((input_dict['snap_id'] == '') or ('snap_id' not in input_dict)):
            logger.sys_error("Did not pass snap_id to delete_snapshot operation.")
            raise Exception("Did not pass snap_id to delete_snapshot operation.")
        if((input_dict['project_id'] == '') or ('project_id' not in input_dict)):
            logger.sys_error("Did not pass project_id to delete_snapshot operation.")
            raise Exception("Did not pass project_id to delete_snapshot operation.")

        #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to snapshot volumes.")
            raise Exception("Status level not sufficient to snapshot volumes.")

        #connect to the transcirrus DB
        try:
            #connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB ")
            raise e

        #get the id of the snapshot based on the name
        try:
            select = {"select":"snap_name","from":"trans_system_snapshots","where":"snap_id='%s'" %(input_dict['snap_id'])}
            snap_name = self.db.pg_select(select)
        except:
            logger.sql_error("Could not get the snap name from Transcirrus DB.")
            raise Exception("Could not get the snap name from Transcirrus DB.")

        try:
            select_proj = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(input_dict['project_id'])}
            proj_name = self.db.pg_select(select_proj)
        except:
            logger.sql_error("Could not get the project name from Transcirrus DB.")
            raise Exception("Could not get the project name from Transcirrus DB.")

        #make sure the project id of the snap matches the user project
        #default the del_status to 0 - DO NOT delete
        snap_status = 0
        #if the user proj id matches the volume proj_id they can delete the volume
        if(self.is_admin == 0):
            if(self.project_id == input_dict['snap_id']):
                #snap_status = 1 - list snap info
                snap_status = 1
            else:
                logger.sys_error("Users can not delete snapshots outside of their project.")
                raise Exception("Users can not delete snapshots outside of their project.")
        elif(self.user_level == 0):
            logger.sys_info("The user is an admin and can delete any snapshot.")
            snap_status = 1
        else:
            logger.sys_error("The user level is invalid, and can not delete snap.")
            raise Exception("The user level is invalid, and can not delete snap.")

        #check to see if the snapshot exists
        snap_info = self.get_snapshot(snap_name)

        #if the snap exisits and you are allowed to delete it
        if(snap_info['snap_id'] and (snap_status == 1)):
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":input_dict['project_id']}
                if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the Keystone API")
                raise Exception("Could not connect to the Keystone API")

            try:
                #add the new user to openstack 
                body = ''
                token = self.token
                #NOTE: if token is not converted python will pass unicode and not a string
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": str(token)}
                function = 'DELETE'
                api_path = '/v1/%s/snapshots/%s' %(input_dict['project_id'],snap_info['snap_id'])
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
                r_dict = ""
            except Exception as e:
                print "%s" %(e)
                raise

            if(rest['response'] == 202):
                #remove snap info from the transcirrus db
                try:
                    self.db.pg_transaction_begin()
                    delete = {"table":'trans_system_snapshots',"where":"snap_id='%s'" %(snap_info['snap_id'])}
                    self.db.pg_delete(delete)
                except:
                    self.db.pg_transaction_rollback()
                    self.db.pg_close_connection()
                    logger.sql_error("Could not enter in snapshot %s information into Transcirrus DB" %(create_snap['snap_name']))
                    raise Exception("Could not enter in snapshot %s information into Transcirrus DB" %(create_snap['snap_name']))
                else:
                    self.db.pg_transaction_commit()
                    self.db.pg_close_connection()
                    return "OK"
            else:
                util.http_codes(rest['response'],rest['reason'])
        else:
            logger.sys_error("The snapshot: %s does not exist." %(snap_name))
            raise Exception("The snapshot: %s does not exist." %(snap_name))

    def list_snapshots(self):
        """
        DESC: List all of the snapshots in a project
        INPUT: None
        OUTPUT: array of r_dict - volume_name
                                - volume_id
                                - snapshot_name
                                - snapshot_id
        ACCESS: Admins can list snapshots in any project, users and power users can list snapshots in their
                project only.
        NOTE: This will only list out the snapshots that are for volume in the users project. All users
              can list the snapshots
        """
        #connect to the transcirrus DB
        try:
            #connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB ")
            raise e

        try:
            select_snap = None
            if(self.is_admin == 1):
                select_snap = {'select':"*",'from':"trans_system_snapshots"}
            else:
                select_snap = {'select':"*",'from':"trans_system_snapshots",'where':"proj_id='%s'" %(self.project_id)}
            snaps = self.db.pg_select(select_snap)
        except:
            logger.sys_error("Could not list snapshots.")
            raise Exception("Could not list snapshots.")

        r_array = []
        for snap in snaps:
            try:
                select_vol = {'select':"vol_name",'from':"trans_system_vols",'where':"vol_id='%s'"%(snap[1])}
                vol_name = self.db.pg_select(select_vol)
            except:
                logger.sys_error("Could not get the volume name.")
                raise Exception("Could not get the volume name.")
            snap_dict = {"vol_name":vol_name[0][0],"vol_id":snap[1],"snapshot_name":snap[3],"snapshot_id":snap[0]}
            r_array.append(snap_dict)

        self.db.pg_close_connection()
        return r_array

    def get_snapshot(self,snap_name):
        """
        DESC: Get the details of a specific snapshot
        INPUT: snap_name
        OUTPUT: dictionary containing
                snap_id
                snap_status
                volume_id
                create_time
        ACCESS: Admins can list snapshots in any project, users and power users can list snapshots in their
                project only
        """
        #check to make sure all params have been passed
        if(not snap_name):
            logger.sys_error("Did not pass snap_name to get_snapshot operation.")
            raise Exception("Did not pass snap_name to get_snapshot operation.")
        #sanity check
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to snapshot volumes.")
            raise Exception("Status level not sufficient to snapshot volumes.")

        #connect to the transcirrus DB
        try:
            #connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB ")
            raise e

        #get the id of the snapshot based on the name
        try:
            select = {'select':"snap_id,proj_id",'from':"trans_system_snapshots",'where':"snap_name='%s'" %(snap_name)}
            snap_id = self.db.pg_select(select)
        except:
            logger.sql_error("Could not get the snap name from Transcirrus DB.")
            raise Exception("Could not get the snap name from Transcirrus DB.")

        try:
            select_proj = {'select':"proj_name",'from':"projects",'where':"proj_id='%s'" %(snap_id[0][1])}
            proj_name = self.db.pg_select(select_proj)
        except:
            logger.sql_error("Could not get the project name from Transcirrus DB.")
            raise Exception("Could not get the project name from Transcirrus DB.")

        #make sure the project id of the snap matches the user project
        #default the del_status to 0 - DO NOT delete
        snap_status = 0
        #if the user proj id matches the volume proj_id they can delete the volume
        if(self.user_level >= 1):
            if(self.project_id == snap_id[0][1]):
                #snap_status = 1 - list snap info
                snap_status = 1
            else:
                logger.sys_error("Users can not get snapshots outside of their project.")
                raise Exception("Users can not get snapshots outside of their project.")
        elif(self.user_level == 0):
            logger.sys_info("The user is an admin and can get the snap info on any snapshot.")
            snap_status = 1
        else:
            logger.sys_error("The user level is invalid, and can not list snap info.")
            raise Exception("The user level is invalid, and can not list snap info.")

        if(snap_status == 1):
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the Keystone API")
                raise Exception("Could not connect to the Keystone API")

            try:
                #add the new user to openstack 
                body = ''
                token = self.token
                #NOTE: if token is not converted python will pass unicode and not a string
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": token}
                function = 'GET'
                api_path = '/v1/%s/snapshots/%s' %(snap_id[0][1],snap_id[0][0])
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
                r_dict = ""
            except Exception as e:
                print "%s" %(e)
                raise

            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                r_dict = {"snap_id": str(load['snapshot']['id']), "snap_status": str(load['snapshot']['status']), "volume_id": str(load['snapshot']['volume_id']), "create_time": str(load['snapshot']['created_at'])}
                return r_dict
            else:
                util.http_codes(rest['response'],rest['reason'])
        else:
            logger.sys_error('Could not get detailed information on the snapshot.')
            raise Exception('Could not get detailed information on the snapshot.')
