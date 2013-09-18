#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class snapshot_ops:
    
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

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

    #DESC: create a new snapshot of an exsisting volume
    #INPUT - self object
    #        create_snap dictionary
    #          snap_name - snapshot name - REQ
    #          snap_desc - description - REQ
    #          project_id - project volume lives in - REQ
    #          vol_id - volume to snap - REQ
    #OUTPUT: dictionary containing snap_name,snap_id,vol_id
    #users can only snap volumes in their project, admins can snapshot any volume
    def create_snapshot(self,create_snap):
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
            select = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(self.project_id)}
            proj_name = self.db.pg_select(select)
        except:
            logger.sql_error("Could not get the project name from Transcirrus DB.")
            raise Exception("Could not get the project name from Transcirrus DB.")

        #default the del_status to 0 - DO NOT delete
        snap_status = 0
        #if the user proj id matches the volume proj_id they can delete the volume
        if(self.user_level >=1):
            if(self.project_id == create_snap['project_id']):
                #del_status = 1 - DELETE volume
                logger.sys_info("The user is not an and can delete the volume in their project.")
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

        if(snap_status == 1):
            try:
                #build an api connection
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)
    
                #add the new user to openstack 
                body = '{"snapshot": {"display_name": "%s", "force": false, "display_description": "%s", "volume_id": "%s"}}' %(create_snap['snap_name'],create_snap['snap_desc'],create_snap['vol_id'])
                token = self.token
                #NOTE: if token is not converted python will pass unicode and not a string
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": str(token)}
                function = 'POST'
                api_path = '/v1/%s/snapshots' %(create_snap['project_id'])
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 200
                r_dict = ""
                if(rest['response'] == 200):
                    #read the json that is returned
                    logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                    #NOTE: his has to work
                    #loop until snap becomes available
                    #available = False
                    #x = 0
                    #while not available:
                    ##    out = self.get_snapshot(create_snap['snap_name'])
                    #    if(out['snap_status'] == 'available'):
                    #        available = True
                    #    else:
                    #        logger.sys_info("Waiting for snapshot: %s to become available" %(create_snap['snap_name']))
                    #        x+=1
                    #        time.sleep(1)
                    #    if(x == 30):
                    #        logger.sys_error("The snapshot: %s did not become available" %(create_snap['snap_name']))
                    #        raise Exception("The snapshot: %s did not become available" %(create_snap['snap_name']))
                    load = json.loads(rest['data'])
                    try:
                        #insert the volume info into the DB
                        insert_snap = {"snap_id": load['snapshot']['id'],"vol_id": load['snapshot']['volume_id'],"proj_id": create_snap['project_id'],"snap_name": create_snap['snap_name'],"snap_desc": create_snap['snap_desc']}
                        print insert_snap
                        self.db.pg_insert("trans_system_snapshots",insert_snap)
                        self.db.pg_close_connection()
                        r_dict = {"snap_name": create_snap['snap_name'],"snap_id": load['snapshot']['id'], "vol_id": load['snapshot']['volume_id']}
                    except:
                        logger.sql_error("Could not enter in snapshot %s information into Transcirrus DB" %(create_snap['snap_name']))
                        raise Exception("Could not enter in snapshot %s information into Transcirrus DB" %(create_snap['snap_name']))
                else:
                    _http_codes(rest['response'],rest['reason'])
            except:
                logger.sys_error("Volume snapshot %s may or may not have been created." %(create_snap['snap_name']))
                #back the user out of the transcirrus DB if the db works and the REST API fails
                raise
        else:
            logger.sys_error("The user level is invalid, can not delete the volume.")

        return r_dict

    #DESC: Delete a snapshot
    #INPUT: Snap name
    #OUTPUT: OK if successful
    def delete_snapshot(self,delete_snap):
        #check to make sure all params have been passed
        if(not delete_snap):
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
            select = {"select":"snap_id,proj_id","from":"trans_system_snapshots","where":"snap_name='%s'" %(delete_snap)}
            snap_id = self.db.pg_select(select)

            select_proj = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(self.project_id)}
            proj_name = self.db.pg_select(select)
        except:
            logger.sql_error("Could not get the snap id from Transcirrus DB.")
            raise Exception("Could not get the snap id from Transcirrus DB.")

        #make sure the project id of the snap matches the user project
        #default the del_status to 0 - DO NOT delete
        snap_status = 0
        #if the user proj id matches the volume proj_id they can delete the volume
        if(self.user_level >=1):
            if(self.project_id == snap_id[0][0]):
                #snap_status = 1 - list snap info
                snap_status = 1
            else:
                logger.sys_error("Users can not delete snapshots outside of their project.")
                raise Exception("Users can not delete snapshots outside of their project.")
        elif(self.user_level == 0):
            logger.sys_info("The user is an admin and can delete any snapshot.")
            snap_status = 1
        else:
            logger.sys_error("The user level is invalid, and can not list snap info.")
            raise Exception("The user level is invalid, and can not list snap info.")

        #check to see if the snapshot exists
        snap_info = self.get_snapshot(delete_snap)

        #if the snap exisits and you are allowed to delete it
        if(snap_info['snap_id'] and (snap_status == 1)):
            try:
                #build an api connection
                api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
                api = caller(api_dict)

                #add the new user to openstack 
                body = ''
                token = self.token
                #NOTE: if token is not converted python will pass unicode and not a string
                header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": str(token)}
                function = 'DELETE'
                api_path = '/v1/%s/snapshots/%s' %(snap_id[0][1],snap_id[0][0])
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
                rest = api.call_rest(rest_dict)
                #check the response and make sure it is a 200
                r_dict = ""
                if(rest['response'] == 202):
                    #remove snap info from the transcirrus db
                    delete = {"table":'trans_system_snapshots',"where":"snap_id='%s'" %(snap_id[0][0])}
                    self.db.pg_delete(delete)
                    self.db.pg_close_connection()
                else:
                    _http_codes(rest['response'],rest['reason'])
            except Exception as e:
                print "%s" %(e)
                raise
            return "OK"
        else:
            logger.sys_error("The snapshot: %s does not exist." %(delete_snap))
            raise Exception("The snapshot: %s does not exist." %(delete_snap))

    def list_snapshots(self):
        print "yo"
    
    #DESC: Get the details of a specific snapshot
    #INPUT: snap_name
    #OUTPUT: dictionary containing
    #        snap_id
    #        snap_status
    #        volume_id
    #        create_time
    def get_snapshot(self,snap_name):
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
            select = {"select":"snap_id,proj_id","from":"trans_system_snapshots","where":"snap_name='%s'" %(snap_name)}
            snap_id = self.db.pg_select(select)
            if(not snap_id[0][0]):
                print "juice"

            select_proj = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(self.project_id)}
            proj_name = self.db.pg_select(select)
        except:
            logger.sql_error("Could not get the snap name from Transcirrus DB.")
            raise Exception("Could not get the snap name from Transcirrus DB.")

        #make sure the project id of the snap matches the user project
        #default the del_status to 0 - DO NOT delete
        snap_status = 0
        #if the user proj id matches the volume proj_id they can delete the volume
        if(self.user_level >=1):
            if(self.project_id == snap_id[0][0]):
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

        try:
            #build an api connection
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)

            #add the new user to openstack 
            body = ''
            token = self.token
            #NOTE: if token is not converted python will pass unicode and not a string
            header = {"Content-Type": "application/json", "X-Auth-Project-Id": proj_name[0][0], "X-Auth-Token": str(token)}
            function = 'GET'
            api_path = '/v1/%s/snapshots/%s' %(snap_id[0][1],snap_id[0][0])
            sec = self.sec
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":"8776"}
            rest = api.call_rest(rest_dict)
            #check the response and make sure it is a 200
            r_dict = ""
            if(rest['response'] == 200):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                load = json.loads(rest['data'])
                r_dict = {"snap_id": str(load['snapshot']['id']), "snap_status": str(load['snapshot']['status']), "volume_id": str(load['snapshot']['volume_id']), "create_time": str(load['snapshot']['created_at'])}
            else:
                _http_codes(rest['response'],rest['reason'])
        except Exception as e:
            print "%s" %(e)
            raise

        return r_dict
######Internal defs#######
def _http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")
