import json
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token

class absolute_limits_ops:
    def __init__(self, user_dict):
        if (not user_dict):
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

            if (self.is_admin == 1):
                self.adm_token = user_dict['adm_token']
            else:
                self.adm_token = 'NULL'

            if ('sec' in user_dict):
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'

            # get the default cloud controller info
            self.controller = config.CLOUD_CONTROLLER
            self.api_ip = config.API_IP

        if ((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if (self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

    def get_absolute_limit_for_tenant(self, project_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if (project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Accept": "application/json",
                      "User-Agent": "python-novaclient"}
            function = 'GET'
            api_path = '/v2/' + project_id + '/limits'
            token = self.token
            sec = self.sec
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 8774}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except Exception, e:
            logger.sys_error("Could not get absolute limits for user: %s" % e)
            raise Exception("Could not get absolute limits for user: %s" % e)

        payload = None
        if rest['response'] == 200:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" % (rest['response'], rest['reason']))
            payload = json.loads(rest['data'])
        else:
            logger.sys_error("Could not get absolute limits for user: %s - %s" % (rest['response'], rest['reason']))
            raise Exception("Could not get absolute limits for user: %s - %s" % (rest['response'], rest['reason']))
        return payload