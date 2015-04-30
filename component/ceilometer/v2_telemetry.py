#!/usr/bin/python

import sys
import json

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class telemetry_ops:

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
            self.user_id = user_dict['user_id']

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

        if(self.is_admin == 1 and self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")
            raise Exception("No admin tokens passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        self.keystone_users = user_ops(user_dict)
        self.gluster = gluster_ops(user_dict)


    def __del__(self):
        self.db.pg_close_connection()
    
    
    def alarm_combination_create():
      pass
        #Create a new alarm based on state of other alarms.
    
    
    def alarm_combination_update():
      pass
        #Update an existing alarm based on state of other alarms.
        
    
    def alarm_create():
      pass
        #Create a new alarm (Deprecated). Use alarm-threshold-create instead.
    
    
    def alarm_delete():
      pass
        #Delete an alarm.
    
    
    def alarm_history():
      pass
        #Display the change history of an alarm.
        
    
    def alarm_list(self, project_id):
        #List the user's alarms.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(self.project_id != project_id):
                    self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")
    
        try:
            body = ''
            header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
            function = 'GET'
            api_path = '/v2/alarms'
            token = self.adm_token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function": function, "api_path": api_path, "token": token, "sec": sec, "port": 8777}
            if(self.api_ip):
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list alarms.")
            raise Exception("Could not list alarms.")
    
        if(rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            print load
        else:
            util.http_codes(rest['response'],rest['reason'])
            
        
    def alarm_show():
        pass
        #Show an alarm.
        
        
    def alarm_state_get():
        pass
        #Get the state of an alarm.
    
    
    def alarm_state_set():
        pass
        #Set the state of an alarm.
        
    
    def alarm_threshold_create():
        pass
        #Create a new alarm based on computed statistics.
    
    
    def alarm_threshold_update():
        pass
        #Update an existing alarm based on computed statistics.
        
    
    def alarm_update():
        pass
        #Update an existing alarm (Deprecated).
        
    
    def event_list():
        pass
        #List events.
        #Events not implemented in packstack
        
    
    def event_show():
        pass
        #Show a particular event.
        #Events not implemented in packstack
    
    
    def event_type_list():
        pass
        #List event types.
        #Events not implemented in packstack
        
    def list_meters(self, project_id):
        pass
        #List the meters.
        
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(self.project_id != project_id):
                    self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")
    
        try:
            body = ''
            header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
            function = 'GET'
            api_path = '/v2/meters'
            token = self.adm_token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function": function, "api_path": api_path, "token": token, "sec": sec, "port": 8777}
            if(self.api_ip):
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list meters.")
            raise Exception("Could not list meters.")
    
        if(rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            print load
        else:
            util.http_codes(rest['response'],rest['reason'])
        
    def query_alarm_history():
        pass
        #Query Alarm History.
    
        
    def query_alarms():
        pass
        #Query Alarms.
    
    
    def query_samples():
        pass
        #Query samples.
        
        
    def resource_list(self, project_id):
        #List the resources.
        
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(self.project_id != project_id):
                    self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")
    
        try:
            body = ''
            header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
            function = 'GET'
            api_path = '/v2/resources'
            token = self.adm_token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function": function, "api_path": api_path, "token": token, "sec": sec, "port": 8777}
            if(self.api_ip):
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list resources.")
            raise Exception("Could not list resources.")
    
        if(rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            print load
        else:
            util.http_codes(rest['response'],rest['reason'])
        
        
    def resource_show():
        pass
        #Show the resource.
        
        
    def sample_create():
        pass
        #Create a sample.
        
        
    def sample_list(self, meter_id):
        #List the samples for a meter.
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(self.project_id != project_id):
                    self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")
    
        try:
            body = ''
            header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
            function = 'GET'
            api_path = '/v2/meter/%s' %(meter_id)
            token = self.adm_token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function": function, "api_path": api_path, "token": token, "sec": sec, "port": 8777}
            if(self.api_ip):
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list samples.")
            raise Exception("Could not list samples.")
    
        if(rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            print load
        else:
            util.http_codes(rest['response'],rest['reason'])
        
        
    def statistics(self, meter_id):
        #List the statistics for a meter.
        
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            if(self.project_id != project_id):
                    self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")
    
        try:
            body = ''
            header = {"X-Auth-Token":self.adm_token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
            function = 'GET'
            api_path = '/v2/meter/%s/statistics' %(meter_id)
            token = self.adm_token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function": function, "api_path": api_path, "token": token, "sec": sec, "port": 8777}
            if(self.api_ip):
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could get statistics.")
            raise Exception("Could get statistics.")
    
        if(rest['response'] == 200):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            print load
        else:
            util.http_codes(rest['response'],rest['reason'])
        
        
    def trait_description_list():
        pass
        #List trait info for an event type.
        #Events not implemented in packstack
        
        
    def trait_list():
        pass
        #List trait all traits with name <trait_name> for Event Type
        #Events not implemented in packstack
