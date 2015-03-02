import software_config
import stack_actions
import stack_events
import stack_resources
import stacks
import templates

def __init__(self,user_dict):
    if(not user_dict):
        logger.sys_warning("No auth settings passed.")
        raise Exception("No auth settings passed")
    else:
        self.username = user_dict['username']
        self.user_id = user_dict['user_id']
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
        
        if('sec' in user_dict):
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
