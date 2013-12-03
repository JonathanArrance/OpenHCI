import os
#import subprocess
import time
import commands

import transcirrus.common.logger as logger
import transcirrus.common.config as config

def nova(action):
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
    out = _operator(nova_array,action)
    return out

def neutron(action):
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
    out = _operator(neu_array,action)
    return out

def glance(action):
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
    out = _operator(glance_array,action)
    return out

def cinder(action):
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
    out = _operator(cinder_array,action)
    return out

def keystone(action):
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
    out = _operator(key_array,action)
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
    out = _operator(iscsi_array,action)
    return out

def heat(action):
    print "not implemented"

def ceilometer(action):
    print "not implemented"

def postgresql(action):
    print "not implemented"

def openvswitch(action):
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
    out = _operator(ovs_array,action)
    return out

def apache(action):
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
    out = _operator(web_array,action)
    return out

def swift(action):
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
    out = _operator(swift_array,action)
    return out

def _operator(service_array,action):
    for service in service_array:
        process = []
        out = None
        #os.system('sudo /etc/init.d/%s %s'%(service,action))
        os.system('sudo service %s %s'%(service,action))
        time.sleep(1)
        if(action.lower() == 'start' or action.lower() == 'restart'):
        #    out = subprocess.Popen('sudo service %s status | grep "start/running"'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = commands.getoutput('sudo service %s status'%(service))
            print out
        #elif(action.lower() == 'stop'):
        #    out = subprocess.Popen('sudo service %s status | grep "stop/waiting"'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #    out = commands.getoutput('sudo service %s stop | grep "start/running"'%(service))
        #if(not process):
            #out = subprocess.Popen('sudo service %s status | grep "NOT"'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #    process = out.stdout.readlines()
        #    if(not process):
        #        return 'ERROR'
        #if (len(process) == 2):
        #    logger.sys_info("Service operation complete.")
        #    #print process[0]
        #elif(process[0] == ""):
        #    return 'ERROR'
        #else:
        #    return 'NA'
    return 'OK'
