#!/usr/bin/python

import sys
import json

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.auth import get_token
from transcirrus.common.api_caller import caller

from transcirrus.database.postgres import pgsql

class meter_ops:

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

            #used to overide the value in the DB, mostly used during setup or reinit
            if('api_ip' in user_dict):
                #NOTE may have to add an IP check
                self.api_ip = user_dict['api_ip']
            else:
                self.api_ip = config.API_IP

            #get the default cloud controller info
            self.controller = config.CLOUD_CONTROLLER

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")

        if((self.token == 'error') or (self.token == '')):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

    def list_meters(self, project_id):
        
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username,self.password,self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
            function = 'GET'
            api_path = '/v2/meters'
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function": function, "api_path": api_path, "token": token, "sec": sec, "port": 8777}
            if(self.api_ip):
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list meters.")
            raise Exception("Could not list meters.")

        if(rest['response'] == 200):
            #read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            print load
        else:
            util.http_codes(rest['response'],rest['reason'])

    def show_statistics(self, project_id, start_time, end_time, meter_type):
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username,self.password,self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
            function = 'GET'
            api_path = '/v2/meters/' + meter_type + '/statistics?q.field=timestamp&q.field=timestamp&q.op=gt&q.op=le&q.type=&q.type=&q.value=' + start_time + '&q.value=' + end_time
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function": function, "api_path": api_path, "token": token, "sec": sec, "port": 8777}
            if(self.api_ip):
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list meters.")
            raise Exception("Could not list meters.")

        if(rest['response'] == 200):
            #read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            print load
        else:
            util.http_codes(rest['response'],rest['reason'])

    def show_statistics_for_meter_and_resource(self, project_id, start_time, end_time, meter_type, resource_identifier):
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username,self.password,self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
            function = 'GET'
            #api_path = '/v2/meters/vcpus/statistics?q.field=resource&q.field=timestamp&q.field=timestamp&q.op=eq&q.op=gt&q.op=le&q.type=&q.type=&q.type=&q.value=9d60427f-2602-4582-9bd6-18b9757f976f&q.value=2015-05-05T13%3A00%3A00&q.value=2015-05-07T23%3A00'
            api_path = '/v2/meters/' + meter_type + '/statistics?q.field=timestamp&q.field=timestamp&q.op=gt&q.op=le&q.type=&q.type=&q.value=' + start_time + '&q.value=' + end_time
            # api_path = '/v2/meters/' + meter_type + '/statistics?q.field=resource&q.field=timestamp&q.field=timestamp&q.op=eq&q.op=gt&q.op=le&q.type=&q.type=&q.type=&q.value=' + resource_identifier + '&q.value=' + start_time + '&q.value=' + end_time
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body, "header": header, "function": function, "api_path": api_path, "token": token, "sec": sec, "port": 8777}
            if(self.api_ip):
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list meters.")
            raise Exception("Could not list meters.")

        if(rest['response'] == 200):
            #read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
        else:
            util.http_codes(rest['response'],rest['reason'])