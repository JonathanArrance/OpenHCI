#!/usr/bin/python

import json

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config

from transcirrus.common.auth import get_token
from transcirrus.common.api_caller import caller

class vpn_ops:

    def __init__(self, user_dict):
        reload(config)
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
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

            # used to overide the value in the DB, mostly used during setup or re init
            if('api_ip' in user_dict):
                # NOTE may have to add an IP check
                self.api_ip = user_dict['api_ip']
            else:
                self.api_ip = config.API_IP

            # get the default cloud controller info
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
            logger.sys_error("Invalid status level passed for user: %s" % self.username)
            raise Exception("Invalid status level passed for user: %s" % self.username)

    def list_vpn_ike_policy(self, project_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'GET'
            api_path = '/v2.0/vpn/ikepolicies.json'
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list IKE Policies.")
            raise Exception("Could not list IKE Policies.")

        if rest['response'] == 200:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def create_vpn_ike_policy(self, project_id, ike_policy_name):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = '{"ikepolicy": {"encryption_algorithm": "aes-128", "pfs": "group5", "phase1_negotiation_mode": "main", "name": "%s", "auth_algorithm": "sha1", "ike_version": "v1"}}' % (ike_policy_name)
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'POST'
            api_path = '/v2.0/vpn/ikepolicies.json'
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not create IKE Policy.")
            raise Exception("Could not create IKE Policy.")

        if rest['response'] == 201:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def show_vpn_ike_policy(self, project_id, ike_policy_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'GET'
            api_path = '/v2.0/vpn/ikepolicies/%s.json' % ike_policy_id
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not show IKE Policy.")
            raise Exception("Could not show IKE Policy.")

        if rest['response'] == 200:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def delete_vpn_ike_policy(self, project_id, ike_policy_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'DELETE'
            api_path = '/v2.0/vpn/ikepolicies/%s.json' % (ike_policy_id)
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not delete IKE Policy.")
            raise Exception("Could not delete IKE Policy.")

        if rest['response'] == 204:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            # load = json.loads(rest['data'])
            # return "Response %s with Reason %s" % (rest['response'], rest['reason'])
            return rest['response']
        else:
            util.http_codes(rest['response'], rest['reason'])

    def list_vpn_ipsec_policy(self, project_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'GET'
            api_path = '/v2.0/vpn/ipsecpolicies.json'
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list IPSec Policies.")
            raise Exception("Could not list IPSec Policies.")

        if rest['response'] == 200:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def create_vpn_ipsec_policy(self, project_id, ipsec_policy_name):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = '{"ipsecpolicy": {"encapsulation_mode": "tunnel", "encryption_algorithm": "aes-128", "pfs": "group5", "name": "%s", "transform_protocol": "esp", "auth_algorithm": "sha1"}}' % (ipsec_policy_name)
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'POST'
            api_path = '/v2.0/vpn/ipsecpolicies.json'
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not create ipsec Policy.")
            raise Exception("Could not create ipsec Policy.")

        if rest['response'] == 201:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def show_vpn_ipsec_policy(self, project_id, ipsec_policy_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'GET'
            api_path = '/v2.0/vpn/ipsecpolicies/%s.json' % ipsec_policy_id
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not show ipsec Policy.")
            raise Exception("Could not show ipsec Policy.")

        if rest['response'] == 200:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def delete_vpn_ipsec_policy(self, project_id, ipsec_policy_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'DELETE'
            api_path = '/v2.0/vpn/ipsecpolicies/%s.json' % (ipsec_policy_id)
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not delete ipsec Policy.")
            raise Exception("Could not delete ipsec Policy.")

        if rest['response'] == 204:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            # load = json.loads(rest['data'])
            # return "Response %s with Reason %s" % (rest['response'], rest['reason'])
            return rest['response']
        else:
            util.http_codes(rest['response'], rest['reason'])

    def list_vpn_service(self, project_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'GET'
            api_path = '/v2.0/vpn/vpnservices.json'
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list VPN Services.")
            raise Exception("Could not list VPN Services.")

        if rest['response'] == 200:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def create_vpn_service(self, project_id, service_name, service_description, subnet_id, router_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = '{"vpnservice": {"subnet_id": "%s", "router_id": "%s", "description": "%s", "name": "%s", "admin_state_up": true}}'  % (subnet_id, router_id, service_description, service_name)
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'POST'
            api_path = '/v2.0/vpn/vpnservices.json'
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not create vpn service.")
            raise Exception("Could not create vpn service.")

        if rest['response'] == 201:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def show_vpn_service(self, project_id, service_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'GET'
            api_path = '/v2.0/vpn/vpnservices/%s.json' % service_id
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not show vpn service.")
            raise Exception("Could not show vpn service.")

        if rest['response'] == 200:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def delete_vpn_service(self, project_id, service_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'DELETE'
            api_path = '/v2.0/vpn/vpnservices/%s.json' % service_id
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not delete vpn service.")
            raise Exception("Could not delete vpn service.")

        if rest['response'] == 204:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            # load = json.loads(rest['data'])
            # return "Response %s with Reason %s" % (rest['response'], rest['reason'])
            return rest['response']
        else:
            util.http_codes(rest['response'], rest['reason'])



    def list_vpn_ipsec_site_connection(self, project_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'GET'
            api_path = '/v2.0/vpn/ipsec-site-connections.json'
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not list VPN IPSec Site Connections.")
            raise Exception("Could not list VPN IPSec Site Connections.")

        if rest['response'] == 200:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def create_vpn_ipsec_site_connection(self, project_id, peer_cidrs, ikepolicy_id, vpnservice_id, peer_address, tunnel_name, ipsecpolicy_id, peer_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = '{"ipsec_site_connection": {"psk": "secret", "peer_cidrs": ["%s"], "ikepolicy_id": "%s", "vpnservice_id": "%s", "peer_address": "%s", "initiator": "bi-directional", "name": "%s", "admin_state_up": true, "mtu": "1500", "ipsecpolicy_id": "%s", "peer_id": "%s"}}' % (peer_cidrs, ikepolicy_id, vpnservice_id, peer_address, tunnel_name, ipsecpolicy_id, peer_id)
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'POST'
            api_path = '/v2.0/vpn/ipsec-site-connections.json'
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not create vpn ipsec tunnel.")
            raise Exception("Could not create vpn ipsec tunnel.")

        if rest['response'] == 201:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def show_vpn_ipsec_site_connection(self, project_id, tunnel_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'GET'
            api_path = '/v2.0/vpn/ipsec-site-connections/%s.json' % tunnel_id
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not show vpn ipsec tunnel.")
            raise Exception("Could not show vpn ipsec tunnel.")

        if rest['response'] == 200:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            load = json.loads(rest['data'])
            return load
        else:
            util.http_codes(rest['response'], rest['reason'])

    def delete_vpn_ipsec_site_connection(self, project_id, tunnel_id):
        try:
            api_dict = {"username": self.username, "password": self.password, "project_id": project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username, self.password, self.project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the Keystone API")
            raise Exception("Could not connect to the Keystone API")

        try:
            body = ''
            header = {"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-neutronclient"}
            function = 'DELETE'
            api_path = '/v2.0/vpn/ipsec-site-connections/%s.json' % tunnel_id
            token = self.token
            sec = 'FALSE'
            rest_dict = {"body": body,
                         "header": header,
                         "function": function,
                         "api_path": api_path,
                         "token": token,
                         "sec": sec,
                         "port": 9696}
            if self.api_ip:
                rest_dict['api_ip'] = self.api_ip
            rest = api.call_rest(rest_dict)
        except:
            logger.sys_error("Could not delete vpn ipsec tunnel.")
            raise Exception("Could not delete vpn ipsec tunnel.")

        if rest['response'] == 204:
            # read the json that is returned.
            logger.sys_info("Response %s with Reason %s" %(rest['response'],rest['reason']))
            # load = json.loads(rest['data'])
            # return "Response %s with Reason %s" % (rest['response'], rest['reason'])
            return rest['response']
        else:
            util.http_codes(rest['response'], rest['reason'])