import os
import subprocess
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
    nova_array = ['openstack-nova-api','openstack-nova-cert','openstack-nova-compute','openstack-nova-conductor','openstack-nova-console','openstack-nova-consoleauth',
                  'openstack-nova-metadata-api','openstack-nova-novncproxy','openstack-nova-scheduler','openstack-nova-spicehtml5proxy','openstack-nova-xvpvncproxy']
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
    neu_array = ['quantum-server','quantum-openvswitch-agent','quantum-dhcp-agent','quantum-metadata-agent','quantum-l3-agent']
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
    glance_array = ['openstack-glance-registry','openstack-glance-api']
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
    cinder_array = ['openstack-cinder-api','openstack-cinder-scheduler','openstack-cinder-volume']
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
    key_array = ['openstack-keystone']
    out = _operator(key_array,action)
    return out

def iscsi(action):
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
    iscsi_array = ['tgtd','iscsid']
    out = _operator(iscsi_array,action)
    return out

def heat(action):
    print "not implemented"

def ceilometer(action):
    print "not implemented"

def postgresql(action):
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
    #HACK - CentOS issue with postgres files changeing permissions.
    os.system('sudo chown postgres:postgres /var/lib/pgsql/data/pg_hba.conf')
    os.system('sudo chown postgres:postgres /var/lib/pgsql/data/postgresql.conf')
    os.system('sudo chmod 766 /var/lib/pgsql/data/pg_hba.conf')
    os.system('sudo chmod 766 /var/lib/pgsql/data/postgresql.conf')
    time.sleep(1)

    psql_array = ['postgresql']
    out = _operator(psql_array,action)
    return out

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
    ovs_array = ['openvswitch']
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
    web_array = ['httpd']
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
    swift_array = ['openstack-swift-account','openstack-swift-account-auditor','openstack-swift-account-reaper','openstack-swift-account-replicator','openstack-swift-container','openstack-swift-container-auditor',
                   'openstack-swift-container-replicator','openstack-swift-container-updater','openstack-swift-object','openstack-swift-object-auditor','openstack-swift-object-replicator',
                   'openstack-swift-object-updater','openstack-swift-proxy']
    out = _operator(swift_array,action)
    return out

def gluster(action):
    """
    DESC: Control the glusterfs services
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS: Only an admin can control the gluster services.
    NOTES:
    """
    gluster_array = ['glusterd','glusterfsd']
    out = _operator(gluster_array,action)
    return out

def qpid(action):
    """
    DESC: Control the qpid service
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS: Only an admin can control the qpid services.
    NOTES:
    """
    qpid_array = ['qpidd']
    out = _operator(qpid_array,action)
    return out

def pacemaker(action):
    """
    DESC: Control the pacemaker service
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS: Only an admin can control the pacemaker services.
    NOTES:
    """
    pace_array = ['pacemaker']
    out = _operator(pace_array,action)
    return out

def zero_connect_server(action):
    """
    DESC: Control the pacemaker service
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS: Only an admin can control the pacemaker services.
    NOTES:
    """
    zero_array = ['zero_connect_server']
    out = _operator(zero_array,action)
    return out

def dhcp_server(action):
    """
    DESC: Control the dhcp server
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS: Only an admin can control the dhcp services.
    NOTES:
    """
    dhcp_array = ['dhcpd']
    out = _operator(dhcp_array,action)
    return out

def _operator(service_array,action):
    #need to check the status of the call and error corrctly - Figure this out later
    for service in service_array:
        process = []
        out = None
        time.sleep(1)
        if(action.lower() == 'start' or action.lower() == 'restart'):
            os.system('sudo chkconfig %s on'%(service))
            os.system('sudo service %s restart'%(service))
            out = subprocess.Popen('sudo service %s status'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif(action.lower() == 'stop'):
            os.system('sudo chkconfig %s off'%(service))
            os.system('sudo service %s stop'%(service))
            out = subprocess.Popen('sudo service %s status'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = out.stdout.readlines()
        print process[0]
        #if(process[0] == ""):
        #    return 'ERROR'
    return 'OK'