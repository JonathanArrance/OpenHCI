import sys
import exceptions
import httplib


sys.path.append('../common')
import logger
import config

sys.path.append('../database')
from postgres import pgsql

class caller:
    #INPUT: options dictionary containing
    #       username
    #       password
    #       project_id
    def __init__(self, options):

        if (not options):
            logger.sys_error("Options not passed to caller.__init__")
            raise Exception("Options not passed to caller.__init__")

        try:
            #connect to the transcirrus db
            self.db = pgsql(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        except Exception as e:
            logger.sql_error("Could not connect to the Transcirrus DB ")
            raise e

        #if it makes it this far with no exception set the username and password
        self.username = options['username']
        self.password = options['password']
        self.project_id = options['project_id']

        if (self.username == ""):
            logger.sys_error("Username entered in class.__init__ is blank")
            raise Exception("Username entered in class.__init__ is blank")

        if (self.password == ""):
            logger.sys_error("Password entered in class.__init__ is blank")
            raise Exception("Password entered in class.__init__ is blank")

        if (self.project_id == ""):
            #query the user table in the transcirrus db and get the
            #user primary prject id
            get_project = {"select": 'user_project_id', "from": 'trans_user_info', "where": "user='%s'" %(username)}
            project = self.db.pg_select(get_project)
            #if none is found raise an exception
            if (project[0][0] == ""):
                logger.sys_error("Could not get user primary project id, class.__init__")
                raise Exception("Could not get user primary project id, class.__init__")
            else:
                logger.sys_info("Found the primary project ID: %s for user: %s" %(project[0][0],username))
                self.project_id = project[0][0]

        #get the host system where the prject lives
        host_dict = {"select":"host_system_name", "from":"projects", "where":"proj_id='%s'" %(self.project_id)}
        self.host = self.db.pg_select(host_dict)

        #get the ip used to access the api form the transcirrus db and the admin token for verification in call_rest
        api_dict = {"select":"param_value", "from":"trans_system_settings", "where":"parameter='api_ip'", "and":"host_system='%s'" %(self.host[0][0])}
        self.api_ip = self.db.pg_select(api_dict)

        #get the admin token in case it needs to be verified aginst a passed in "token"
        adm_dict = {"select":"param_value", "from":"trans_system_settings", "where":"parameter='admin_token'", "and":"host_system='%s'" %(self.host[0][0])}
        self.adm_token = self.db.pg_select(adm_dict)

    #DESC: call the rest api via python Httplib
    #INPUT: Dictionary containing the following
    #       body - body of the rest call
    #       header - http header used
    #       function - POST,PUT,GET,HEAD,DELETE,INSERT
    #       api_path - ex /v2.0/tenants
    #       token - auth or admin token
    #       sec - TRUE/FALSE, use https = True
    #OUTPUT - Result of the call to be passed back
    def call_rest(self,api_dict):
        #standard keystone login port
        port = '5000'
        #if an admin token is passed make sure that port 35357 is used
        if (api_dict['token'] == self.adm_token[0][0]):
            #set the admin port defaults to 50000
            logger.sys_info("Setting api_caller.call_rest to  use admin port 35357.")
            port = '35357'
        url = "%s:%s" %(self.api_ip[0][0],port)
        sec = api_dict['sec']
        if (sec == 'TRUE'):
            logger.sys_info("%s is connecting to REST API with a secured connection." %(self.username))
            self.connection = httplib.HTTPSConnection(url, key_file='../cert/priv.pem', cert_file='../cert/srv_test.crt')
        elif(sec == 'FALSE' or sec == ""):
            logger.sys_info("%s is connecting to REST API with an unsecured Connection." %(self.username))
            self.connection = httplib.HTTPConnection(url)
        else:
            logger.sys_error("There was an error connecting to the REST API. Check input params.")
            raise Exception("There was an error connecting to the REST API. Check input params.")

        self.connection.request(api_dict['function'], api_dict['api_path'], api_dict['body'], api_dict['header'])
        response = self.connection.getresponse()
        #get the response and the reason
        return_resp = response.status
        return_reason = response.reason
        #get the raw resonse data
        data = response.read()
        self.connection.close()

        http_dict = {"response": response.status, "reason": response.reason, "data": data}
        return http_dict