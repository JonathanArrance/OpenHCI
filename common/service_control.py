import os
import subprocess
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config

class service_controller:
    def __init__(self,user_dict):
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
                
            #get the default cloud controller info
            self.controller = config.CLOUD_CONTROLLER

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.is_admin != 1):
            logger.sys_error("The admin flag is not set, service operations can not be done.")
            raise Exception("The admin flag is not set, service operations can not be done.")

        if(self.adm_token == ''):
            logger.sys_error("No admin tokens passed.")
            raise Exception("No admin tokens passed.")

        if((self.token == 'error') or (self.token == '')):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))
        
    def nova(self,action):
        """
        DESC: Control the nova service
        INPUT: start
               restart
               stop
        OUTPUT: OK
                ERROR
                NA
        ACCESS: Only an admin can control the openstack services.
        NOTES: Only works on the ciac node for now
        """
        nova_array = ['nova-api','nova-cert','nova-compute','nova-conductor','nova-consoleauth','nova-novncproxy','nova-scheduler']
        out = self._operator(nova_array,action)
        return out

    def neutron(self,action):
        """
        DESC: Control the neutron/quantum service
        INPUT: start
               restart
               stop
        OUTPUT: OK
                ERROR
                NA
        ACCESS: Only an admin can control the openstack services.
        NOTES: These only work on the ciac node for now
        """
        neu_array = ['quantum-dhcp-agent','quantum-l3-agent','quantum-metadata-agent','quantum-plugin-openvswitch-agent','quantum-server']
        out = self._operator(neu_array,action)
        return out

    def glance(self,action):
        """
        DESC: Control the Glance service
        INPUT: start
               restart
               stop
        OUTPUT: OK
                ERROR
                NA
        ACCESS: Only an admin can control the openstack services.
        NOTES: These only work on the ciac node for now
        """
        glance_array = ['glance-registry','glance-api']
        out = self._operator(glance_array,action)
        return out

    def cinder(self,action):
        """
        DESC: Control the Cinder service
        INPUT: start
               restart
               stop
        OUTPUT: OK
                ERROR
                NA
        ACCESS: Only an admin can control the openstack services.
        NOTES: These only work on the ciac node for now
        """
        cinder_array = ['cinder-api','cinder-scheduler','cinder-volume']
        out = self._operator(cinder_array,action)
        return out

    def keystone(self,action):
        """
        DESC: Control the keystone service
        INPUT: start
               restart
               stop
        OUTPUT: OK
                ERROR
                NA
        ACCESS: Only an admin can control the openstack services.
        NOTES: These only work on the ciac node for now
        """
        key_array = ['keystone']
        out = self._operator(key_array,action)
        return out

    def iscsi(self,action):
        """
        DESC: Control the iscsi services
        INPUT: start
               restart
               stop
        OUTPUT: OK
                ERROR
                NA
        ACCESS: Only an admin can control the openstack services.
        NOTES: These only work on the ciac node for now
        """
        iscsi_array = ['tgt','open-iscsi']
        out = self._operator(iscsi_array,action)
        return out

    def heat(self,action):
        print "not implemented"

    def ceilometer(self,action):
        print "not implemented"

    def postgresql(self,action):
        print "not implemented"

    def openvswitch(self,action):
        """
        DESC: Control the open vswitch services
        INPUT: start
               restart
               stop
        OUTPUT: OK
                ERROR
                NA
        ACCESS: Only an admin can control the openstack services.
        NOTES: This does not work - These only work on the ciac node for now
        """
        ovs_array = ['openvswitch-switch']
        out = self._operator(ovs_array,action)
        return out

    def apache(self,action):
        """
        DESC: Control the apache services
        INPUT: start
               restart
               stop
        OUTPUT: OK
                ERROR
                NA
        ACCESS: Only an admin can control the openstack services.
        NOTES: These only work on the ciac node for now
        """
        web_array = ['apache2']
        out = self._operator(web_array,action)
        return out

    def swift(self,action):
        """
        DESC: Control the swift services
        INPUT: start
               restart
               stop
        OUTPUT: OK
                ERROR
                NA
        ACCESS: Only an admin can control the openstack services.
        NOTES: These only work on the ciac node for now
        """
        swift_array = ['swift-account','swift-account-auditor','swift-account-reaper','swift-account-replicator','swift-container','swift-container-auditor','swift-container-replicator',
                       'swift-container-updater','swift-object','swift-object-auditor','swift-object-replicator','swift-object-updater','swift-proxy']
        out = self._operator(swift_array,action)
        return out

    def _operator(self,service_array,action):
        for service in service_array:
            process = []
            os.system('sudo /etc/init.d/%s %s'%(service,action))
            time.sleep(1)
            if(action == 'start' or action == 'restart'):
                self.out = subprocess.Popen('sudo service %s status | grep "running"'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            elif(action == 'stop'):
                self.out = subprocess.Popen('sudo service %s status | grep "stop/waiting"'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process = self.out.stdout.readlines()
            #look for process status the is not stop/waiting
            print "DEBUG %s"%(process)
            if(not process):
                self.out = subprocess.Popen('sudo service %s status | grep "NOT"'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                process = self.out.stdout.readlines()
            if (process[0]):
                logger.sys_info("Service operation complete.")
                print process[0]
            elif(process[0] == ""):
                return 'ERROR'
            else:
                return 'NA'
        return 'OK'
