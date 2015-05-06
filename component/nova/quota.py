#!/usr/local/bin/python2.7
#######standard impots#######
import sys
import json
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

from transcirrus.common.api_caller import caller
from transcirrus.common.auth import get_token
import transcirrus.component.nova.error as nova_ec
import transcirrus.component.cinder.error as cinder_ec

from transcirrus.database.postgres import pgsql

#######Special imports#######

class quota_ops:
    #UPDATED/UNIT TESTED
    #DESC:
    #INPUT:
    #OUTPUT:
    def __init__(self,user_dict):
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        # user_dict = {"username":self.username,"password":self.user_pass,"project_id":exist[0][7],"status_level":status_level,"user_level":user_level,"is_admin": is_admin,"token":token}
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


    def get_project_quotas(self,project_id=None):
        logger.sys_info('\n**Getting nova and cinder project quotas. Component: Nova Def: show_project_quotas**\n')
        """
        DESC: Get the quotas that are set on a project
        INPUT: project_id - op
        OUTPUT: r_dict - id
                       - project_name
                       - cores
                       - fixed_ips
                       - floating_ips
                       - injected_file_content_bytes
                       - injected_file_path_bytes
                       - injected_files
                       - instances
                       - key_pairs
                       - metadata_items
                       - ram(in megabytes)
                       - security_group_rules
                       - security_groups
                       - storage(in gigabytes)
                       - snapshots
                       - volumes
        ACCESS: Admins can list quotas for any project
                Power users can list the quotas for the project they belong to
                Users can list the quotas for the project they belong to
        NOTE: We are combining the Cinder and Nova quota API calls. If the project id is
              not given then the users project id will be used.
        """
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to list quotas.")
            raise Exception("Status level not sufficient to list quotas.")

        if('project_id' == "" or project_id is None):
            logger.sys_error("Project id not passed using, default user project %s"%(self.project_id))
            project_id = self.project_id

        #get the name of the project based on the id
        try:
            select = {"select":"proj_name","from":"projects","where":"proj_id='%s'" %(project_id)}
            proj_name = self.db.pg_select(select)
        except:
            logger.sql_error("Could not get the project name from Transcirrus DB.")
            raise Exception("Could not get the project name from Transcirrus DB.")

        #connect to the rest api caller
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the REST api caller.")
            raise Exception("Could not connect to the REST api caller.")

        ports = ['8774','8776']
        self.r_dict = {}
        self.r_dict['project_name'] = proj_name[0][0]

        apiver = 'v1'
        for port in ports:
            if(port == '8774'):
                apiver = 'v2'

            try:
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/%s/%s/os-quota-sets/%s' %(apiver,project_id,project_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":port}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                raise e
    
            load = json.loads(rest['data'])
            if(rest['response'] == 200):
                for k, v in load['quota_set'].iteritems():
                    self.r_dict[k] = v
            else:
                if(port == '8776'):
                    cinder_ec.error_codes(rest)
                elif(port == '8774'):
                    nova_ec.error_codes(rest)

        return self.r_dict

    def get_user_quotas(self, input_dict = {}):
        """
        NOT USED in GRIZZLY
        DESC: Get the quotas that are set on a specific user in a project
        INPUT: input_dict - project_id - op
                          - user_id - op
        OUTPUT: None
        ACCESS: Admins can list quotas for any project
                Power users can list the quotas for the project they belong to
                Users can list the quotas for the project they belong to
        NOTE: We are combining the Cinder and Nova quota API calls. If the project id or user id is
              not given then the users project id  and user id will be used.
        """
        logger.sys_info('\n**Getting nova and cinder user level quotas. Component: Nova Def: show_user_quotas**\n')
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to list quotas.")
            raise Exception("Status level not sufficient to list quotas.")

        if(not input_dict):
            logger.sys_info("Input not passed, using the default user_id and project_id")
            input_dict['project_id'] = self.project_id
            input_dict['user_id'] = self.user_id
        if(('project_id' not in input_dict) or (input_dict['project_id'] == "")):
            logger.sys_info("Project id not passed using default.")
            input_dict['project_id'] = self.project_id
        if(('user_id' not in input_dict) or (input_dict['user_id'] == "")):
            logger.sys_info("User id not passed, using default.")
            input_dict['user_id'] = self.user_id

        #connect to the rest api caller
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":input_dict['project_id']}
            if(input_dict['project_id'] != self.project_id):
                self.token = get_token(self.username,self.password,input_dict['project_id'])
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the REST api caller.")
            raise Exception("Could not connect to the REST api caller.")

        ports = ['8776','8774']
        self.r_dict = {}
        apiver = 'v1'
        for port in ports:
            if(port == '8774'):
                apiver = 'v2'

            try:
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/%s/%s/os-quota-sets/%s/%s' %(apiver,self.project_id,input_dict['project_id'],input_dict['user_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":port}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                raise e
    
            load = json.loads(rest['data'])
            if(rest['response'] == 200):
                for k, v in load['quota_set'].iteritems():
                    self.r_dict[k] = v
            else:
                if(port == '8776'):
                    cinder_ec.error_codes(rest)
                elif(port == '8774'):
                    nova_ec.error_codes(rest)

        return self.r_dict

    def update_project_quotas(self,input_dict):
        """
        DESC: Get the quotas that are set on a specific user in a project
        INPUT: input_dict - project_id - op
                          - user_id - op
                          - cores - op
                          - fixed_ips - op
                          - floating_ips - op
                          - injected_file_content_bytes - op
                          - injected_file_path_bytes - op
                          - injected_files - op
                          - instances - op
                          - key_pairs - op
                          - metadata_items - op
                          - ram(in megabytes) - op
                          - security_group_rules - op
                          - security_groups - op
                          - storage(in gigabytes) - op
                          - snapshots - op
                          - volumes - op
        OUTPUT: r_dict - id
                       - cores
                       - fixed_ips
                       - floating_ips
                       - injected_file_content_bytes
                       - injected_file_path_bytes
                       - injected_files
                       - instances
                       - key_pairs
                       - metadata_items
                       - ram(in megabytes)
                       - security_group_rules
                       - security_groups
                       - storage(in gigabytes)
                       - snapshots
                       - volumes
        ACCESS: Admins can list quotas for any project
                Power users can list the quotas for the project they belong to
                Users can list the quotas for the project they belong to
        NOTE: We are combining the Cinder and Nova quota API calls. If the project id or user id is
              not given then the users project id  and user id will be used.
        """
        logger.sys_info('\n**Updateing nova and cinder quotas. Component: Nova Def: update_project_quotas**\n')
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to list quotas.")
            raise Exception("Status level not sufficient to list quotas.")

        if(not input_dict):
            logger.sys_info("Input not passed, using the default user_id and project_id")
            input_dict['project_id'] = self.project_id
            input_dict['user_id'] = self.user_id
        if(('project_id' not in input_dict) or (input_dict['project_id'] == "")):
            logger.sys_info("Project id not passed using default.")
            input_dict['project_id'] = self.project_id
        if(('user_id' not in input_dict) or (input_dict['user_id'] == "")):
            logger.sys_info("User id not passed, using default.")
            input_dict['user_id'] = self.user_id

        if(self.is_admin == 1):
            current = self.get_project_quotas(input_dict['project_id'])

            #cinder updates
            if(('storage' in input_dict) and (input_dict['storage'] is not None)):
                self.gigabytes = int(input_dict['storage'])
            else:
                self.gigabytes = int(current['gigabytes'])

            if(('snapshots' in input_dict) and (input_dict['snapshots'] is not None)):
                self.snapshots = int(input_dict['snapshots'])
            else:
                self.snapshots = int(current['snapshots'])

            if(('volumes' in input_dict) and (input_dict['volumes'] is not None)):
                self.volumes = int(input_dict['volumes'])
            else:
                self.volumes = int(current['volumes'])

            #Nova updates
            if(('cores' in input_dict) and (input_dict['cores'] is not None)):
                self.cores = int(input_dict['cores'])
            else:
                self.cores = int(current['cores'])

            if(('fixed_ips' in input_dict) and (input_dict['fixed_ips'] is not None)):
                self.fixed_ips = int(input_dict['fixed_ips'])
            else:
                self.fixed_ips = int(current['fixed_ips'])

            if(('floating_ips' in input_dict) and (input_dict['floating_ips'] is not None)):
                self.floating_ips = int(input_dict['floating_ips'])
            else:
                self.floating_ips = int(current['floating_ips'])

            if(('injected_file_content_bytes' in input_dict) and (input_dict['injected_file_content_bytes'] is not None)):
                self.injected_file_content_bytes = int(input_dict['injected_file_content_bytes'])
            else:
                self.injected_file_content_bytes = int(current['injected_file_content_bytes'])

            if(('injected_file_path_bytes' in input_dict) and (input_dict['injected_file_path_bytes'] is not None)):
                self.injected_file_path_bytes = int(input_dict['injected_file_path_bytes'])
            else:
                self.injected_file_path_bytes = int(current['injected_file_path_bytes'])

            if(('injected_files' in input_dict) and (input_dict['injected_files'] is not None)):
                self.injected_files = int(input_dict['injected_files'])
            else:
                self.injected_files = int(current['injected_files'])

            if(('instances' in input_dict) and (input_dict['instances'] is not None)):
                self.instances = int(input_dict['instances'])
            else:
                self.instances = int(current['instances'])

            if(('key_pairs' in input_dict) and (input_dict['key_pairs'] is not None)):
                self.key_pairs = int(input_dict['key_pairs'])
            else:
                self.key_pairs = int(current['key_pairs'])

            if(('metadata_items' in input_dict) and (input_dict['metadata_items'] is not None)):
                self.metadata_items = int(input_dict['metadata_items'])
            else:
                self.metadata_items = int(current['metadata_items'])

            if(('ram' in input_dict) and (input_dict['ram'] is not None)):
                self.ram = int(input_dict['ram'])
            else:
                self.ram = int(current['ram'])

            if(('security_group_rules' in input_dict) and (input_dict['security_group_rules'] is not None)):
                self.security_group_rules = int(input_dict['security_group_rules'])
            else:
                self.security_group_rules = int(current['security_group_rules'])

            if(('security_groups' in input_dict) and (input_dict['security_groups'] is not None)):
                self.security_groups = int(input_dict['security_groups'])
            else:
                self.security_groups = int(current['security_groups'])

            ports = ['8776','8774']
            #connect to the rest api caller
            try:
                api_dict = {"username":self.username, "password":self.password, "project_id":input_dict['project_id']}
                if(input_dict['project_id'] != self.project_id):
                    self.token = get_token(self.username,self.password,input_dict['project_id'])
                api = caller(api_dict)
            except:
                logger.sys_error("Could not connect to the REST api caller.")
                raise Exception("Could not connect to the REST api caller.")

            self.r_dict = {}
            apiver = 'v1'
            for port in ports:
                if(port == '8774'):
                    apiver = 'v2'

                #try:
                self.body = {}
                if(port == '8776'):
                    self.body = '{"quota_set": {"gigabytes": %d, "tenant_id": "%s", "snapshots": %d, "volumes": %d}}'%(self.gigabytes,input_dict['project_id'],self.snapshots,self.volumes)
                elif(port == '8774'):
                    self.body = '{"quota_set": {"metadata_items": %d, "injected_files": %d, "ram": %d, "key_pairs": %d, "instances": %d, "security_group_rules": %d, "fixed_ips": %d, "security_groups": %d, "injected_file_content_bytes": %d, "tenant_id": "%s", "floating_ips": %d, "cores": %d, "injected_file_path_bytes": %d}}'%(self.metadata_items,self.injected_files,self.ram,self.key_pairs,self.instances,
                     self.security_group_rules,self.fixed_ips,self.security_groups,self.injected_file_content_bytes,input_dict['project_id'],self.floating_ips,self.cores,self.injected_file_path_bytes)
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'PUT'
                api_path = '/%s/%s/os-quota-sets/%s' %(apiver,input_dict['project_id'],input_dict['project_id'])
                token = self.token
                sec = self.sec
                rest_dict = {"body": self.body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":port}
                rest = api.call_rest(rest_dict)
                #except Exception as e:
                #    raise e
        
                load = json.loads(rest['data'])
                if(rest['response'] == 200):
                    for k, v in load['quota_set'].iteritems():
                        self.r_dict[k] = v
                else:
                    if(port == '8776'):
                        cinder_ec.error_codes(rest)
                    elif(port == '8774'):
                        nova_ec.error_codes(rest)
    
            return self.r_dict
        else:
            logger.sys_error("Only an admin can update the system quotas.")
            raise Exception("Only an admin can update the system quotas.")

    def update_user_quotas(self):
        """
        DESC: Get the quotas that are set on a specific user in a project
        INPUT: project_id - op
               user_id - op
        OUTPUT: r_dict - id
                       - cores
                       - fixed_ips
                       - floating_ips
                       - injected_file_content_bytes
                       - injected_file_path_bytes
                       - injected_files
                       - instances
                       - key_pairs
                       - metadata_items
                       - ram(in megabytes)
                       - security_group_rules
                       - storage(in gigabytes)
                       - snapshots
                       - volumes
        ACCESS: Admins can list quotas for any project
                Power users can list the quotas for the project they belong to
                Users can list the quotas for the project they belong to
        NOTE: We are combining the Cinder and Nova quota API calls. If the project id or user id is
              not given then the users project id  and user id will be used.
        """
    def delete_project_quota(self):
        #admin
        pass
    def delete_user_quota(self):
        #admin
        pass
    def get_default_project_quotas(self):
        #all
        pass
    def get_default_user_quotas(self):
        #all
        pass

    def get_max_limits(self,project_id=None):
        """
        DESC: Get the quotas that are set on a project
        INPUT: project_id - op
        OUTPUT: r_dict - maxServerMeta
                       - maxPersonality
                       - maxImageMeta
                       - maxPersonalitySize
                       - totalVolumesUsed
                       - maxSecurityGroupRules
                       - maxTotalKeypairs
                       - totalRAMUsed
                       - maxTotalVolumes
                       - maxSecurityGroups
                       - totalFloatingIpsUsed
                       - totalInstancesUsed
                       - totalSecurityGroupsUsed
                       - maxTotalVolumeGigabytes
                       - maxTotalFloatingIps
                       - maxTotalInstances
                       - totalCoresUsed
                       - totalStorageUsed
                       - maxTotalRAMSize
                       - maxTotalCores
        ACCESS: Admins can list quotas for any project
                Power users can list the quotas for the project they belong to
                Users can list the quotas for the project they belong to
        NOTE: We are combining the Cinder and Nova quota API calls. If the project id is
              not given then the users project id will be used.
        """
        if(self.status_level < 2):
            logger.sys_error("Status level not sufficient to list quotas.")
            raise Exception("Status level not sufficient to list quotas.")

        if('project_id' == "" or project_id == None):
            logger.sys_error("Project id not passed using, default user project %s"%(self.project_id))
            project_id = self.project_id

        #connect to the rest api caller
        try:
            api_dict = {"username":self.username, "password":self.password, "project_id":project_id}
            if(project_id != self.project_id):
                self.token = get_token(self.username,self.password,project_id)
            api = caller(api_dict)
        except:
            logger.sys_error("Could not connect to the REST api caller.")
            raise Exception("Could not connect to the REST api caller.")

        #get the total volumes in a project
        count = 0
        try:
            get_vol_count = {'table':'trans_system_vols','where':"proj_id='%s'"%(project_id)}
            count = self.db.count_elements(get_vol_count)
        except Exception as e:
            logger.sql_error('Could not find any volumes in project %s.'%(project_id))

        #get the total space used by volumes in project
        total_used = 0
        try:
            get_vol_space = {'select':"vol_size",'from':"trans_system_vols",'where':"proj_id='%s'"%(project_id)}
            space = self.db.pg_select(get_vol_space)
            for size in space:
                total_used = size[0] + total_used
        except Exception as e:
            logger.sql_error('Could not find any volumes in project %s.'%(project_id))

        ports = ['8774','8776']
        self.r_dict = {}
        apiver = 'v1'
        for port in ports:
            if(port == '8774'):
                apiver = 'v2'

            try:
                body = ''
                header = {"X-Auth-Token":self.token, "Content-Type": "application/json"}
                function = 'GET'
                api_path = '/%s/%s/limits' %(apiver,project_id)
                token = self.token
                sec = self.sec
                rest_dict = {"body": body, "header": header, "function":function, "api_path":api_path, "token": token, "sec": sec, "port":port}
                rest = api.call_rest(rest_dict)
            except Exception as e:
                raise e
    
            load = json.loads(rest['data'])
            if(rest['response'] == 200):
                for k, v in load['limits']['absolute'].iteritems():
                    self.r_dict[k] = v
            else:
                if(port == '8776'):
                    cinder_ec.error_codes(rest)
                elif(port == '8774'):
                    nova_ec.error_codes(rest)

        self.r_dict['totalStorageUsed'] = int(total_used)
        self.r_dict['totalVolumesUsed'] = int(count)
        return self.r_dict

#privat helper
class _mydict(dict):
        def __str__(self):
            return json.dumps(self)