#!/usr/bin/python

# get the user level from the transcirrus system DB
#passes the user level out 
import sys
import json

sys.path.append('../../common')
import logger
import config

from api_caller import caller

sys.path.append(config.DB_PATH)
from postgres import pgsql

class token_ops:
    
    #DESC: Constructor to build out the tokens object
    #INPUT: user_dict dictionary containing - built in auth.py
    #           username
    #           password
    #           project_id - could be blank
    #           
    def __init__(self,user_dict):
        #try:
            #Try to connect to the transcirrus db
        #    self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        #except StandardError as e:
        #    logger.sys_error("Could not connect to db with error: %s" %(e))
        #    raise

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
            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if((self.token == 'error') or (self.token == '')):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")
        
        if ((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

    #DESC: get the user auth token from openstack so that api commands can be run aginst the
    #      cloud environment
    #INPUT: self object
    #OUTPUT: api_token used to run REST API commands
    #NOTE: implemented in auth.py for now. this def is not used right now
    def get_token(self):

        #submit the values passed in 
        api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
        api = caller(api_dict)
        #       body - body of the rest call
        #       Function - POST,PUT,GET,HEAD,DELETE,INSERT
        #       api_path - ex /v2.0/tenants
        #       token - auth or admin token
        #       sec - TRUE/FALSE, use https = True
        logger.sys_info("Tenant id was passwed in %s." %(self.username))
        body = '{"auth":{"passwordCredentials":{"username": "%s", "password":"%s"}, "tenantId":"%s"}}' %(self.username,self.password,self.project_id)
        header = {"Content-Type": "application/json"}
        function = 'POST'
        api_path = '/v2.0/tokens'
        token = ""
        sec = 'FALSE'
        rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
        rest = api.call_rest(rest_dict)
    
        if((rest['response'] == 200) or (rest['response'] == 203)):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            apitoken = load['access']['token']['id']
            return apitoken
        else:
            _http_codes(rest['response'],rest['reason'])

    #DESC: Check that a token is valid and that it belongs to a particular tenant (For performance).
    #      Does NOT return the tenant permissions
    #INPUT: self object
    #       permissions - dictionary of permissions and tokens from a particular user auth
    #OUTPUT: 403 if invalid token, "valid" flag if token is valid
    def check_token(self):
        #NOTE: fix this shit
        #get the permissions settings from the dictionary - sanity check
        #if((self.is_admin != 1) or (self.is_admin != 0)):
        #    logger.sys_error("User not identified as a user or an admin.")
        #    raise Exception("User not identified as a user or an admin.")
        #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
        #if(self.status_level <= 1):
        #    logger.sys_error("User status not sufficient, can not list endpoints.")
        #    raise Exception("User status not sufficient, can not list endpoints.")

        #standard users can not list a tenants endpoints
        #if(permissions['user_level'] >= 0):
        #    logger.sys_error("Only admins and power users can may list endpoints.")
        #    raise Exception("Only admins and power users can may list endpoints.")
        
        #
        if(self.is_admin == 0):
            #submit the values passed in
            api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
            api = caller(api_dict)
            #       body - body of the rest call
            #       Function - POST,PUT,GET,HEAD,DELETE,INSERT
            #       api_path - ex /v2.0/tenants
            #       token - auth or admin token
            #       sec - TRUE/FALSE, use https = True
            logger.sys_info("Tenant id was passwed in %s." %(self.username))
            #NOTE: The body could be wrong
            body = '{"auth":{"passwordCredentials":{"username": "%s", "password":"%s"}, "tenantId":"%s"}}' %(self.username,self.password,self.project_id)
            header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
            function = 'HEAD'
            api_path = '/v2.0/tokens/%s?belongsTo=%s' %(self.token,self.project_id)
            token = self.token
            if(self.sec == 'TRUE'):
                logger.sys_info("Security paramters have been passed sec: %s" %(self.sec))
            rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": self.sec}
            rest = api.call_rest(rest_dict)

            if((rest['response'] == 200) or (rest['response'] == 203)):
                #read the json that is returned
                logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
                return "valid"
            else:
                _http_codes(rest['response'],rest['reason'])
        elif(self.is_admin == 1):
            #NOTE: this is a little bit of a hack, may need to fix
            return "valid"
        else:
            _http_codes("400","badRequest")
        
    def validate_token(self):

        #get the permissions settings from the dictionary - sanity check
        if((permissions['is_admin'] != 1) or (permissions['is_admin'] != 0)):
            logger.sys_error("User not identified as a user or an admin.")
            raise Exception("User not identified as a user or an admin.")
        #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
        if(permissions['status_level'] <= 1):
            logger.sys_error("User status not sufficient, can not list endpoints.")
            raise Exception("User status not sufficient, can not list endpoints.")
        #check to see if a token is passed
        if((permissions['token'] == 'error') or (permissions['token'] == '')):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")
        #standard users can not list a tenants endpoints
        #if(permissions['user_level'] >= 0):
        #    logger.sys_error("Only admins and power users can may list endpoints.")
        #    raise Exception("Only admins and power users can may list endpoints.")

        #submit the values passed in 
        api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
        api = caller(api_dict)
        #       body - body of the rest call
        #       Function - POST,PUT,GET,HEAD,DELETE,INSERT
        #       api_path - ex /v2.0/tenants
        #       token - auth or admin token
        #       sec - TRUE/FALSE, use https = True
        logger.sys_info("Tenant id was passwed in %s." %(self.username))
        body = '{"auth":{"passwordCredentials":{"username": "%s", "password":"%s"}, "tenantId":"%s"}}' %(self.username,self.password,self.project_id)
        header = {"Content-Type": "application/json"}
        function = 'POST'
        api_path = '/v2.0/tokens/%s' %(permissions['token'])
        token = ""
        sec = 'FALSE'
        if(permissions['sec'] and permission['sec'] == 'TRUE'):
            logger.sys_info("Security paramters have been passed sec: %s" %(permissions['sec']))
            sec = 'TRUE'
        rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
        rest = api.call_rest(rest_dict)

        
        
    def list_token_endpoints(self):
        
        #get the permissions settings from the dictionary - sanity check
        if((permissions['is_admin'] != 1) or (permissions['is_admin'] != 0)):
            logger.sys_error("User not identified as a user or an admin.")
            raise Exception("User not identified as a user or an admin.")
        #check the user status if user status is <= 1 error - must be enabled in both OS and Tran
        if(permissions['status_level'] <= 1):
            logger.sys_error("User status not sufficient, can not list endpoints.")
            raise Exception("User status not sufficient, can not list endpoints.")
        #check to see if a token is passed
        if((permissions['token'] == 'error') or (permissions['token'] == '')):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")
        #standard users can not list a tenants endpoints
        if(permissions['user_level'] > 1):
            logger.sys_error("Only admins and power users can may list endpoints.")
            raise Exception("Only admins and power users can may list endpoints.")

        #submit the values passed in 
        api_dict = {"username":self.username, "password":self.password, "project_id":self.project_id}
        api = caller(api_dict)
        #       body - body of the rest call
        #       Function - POST,PUT,GET,HEAD,DELETE,INSERT
        #       api_path - ex /v2.0/tenants
        #       token - auth or admin token
        #       sec - TRUE/FALSE, use https = True
        logger.sys_info("Tenant id was passed in %s." %(self.username))
        body = '{"auth":{"passwordCredentials":{"username": "%s", "password":"%s"}, "tenantId":"%s"}}' %(self.username,self.password,self.project_id)
        headers = {"X-Auth-Token":token, "Content-Type": "application/json", "Accept": "application/json"}
        function = 'GET'
        api_path = '/v2.0/tokens/%s/endpoints' %(permissions['token'])
        token = permissions['token']
        sec = 'FALSE'
        #security - http/https
        if(permissions['sec'] and permission['sec'] == 'TRUE'):
            logger.sys_info("Security paramters have been passed sec: %s" %(permissions['sec']))
            sec = 'TRUE'
        rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec}
        rest = api.call_rest(rest_dict)

        if((rest['response'] == 200) or (rest['response'] == 203)):
            #read the json that is returned
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            apitoken = load['access']['token']['id']
            return apitoken
        else:
            _http_codes(rest['response'],rest['reason'])


######Internal defs
def _http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")
