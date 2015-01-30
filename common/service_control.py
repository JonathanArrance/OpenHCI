import os
import subprocess
import time
import commands

import transcirrus.common.logger as logger
import transcirrus.common.config as config

#Note need ability to add a verbose out put so we can watch service restart since the silent flag has been added.

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
    nova_array = []
    if(config.NODE_TYPE == 'cc'):
        nova_array = ['openstack-nova-api','openstack-nova-cert','openstack-nova-compute','openstack-nova-conductor','openstack-nova-console','openstack-nova-consoleauth',
                      'openstack-nova-metadata-api','openstack-nova-novncproxy','openstack-nova-scheduler','openstack-nova-spicehtml5proxy','openstack-nova-xvpvncproxy']
    elif(config.NODE_TYPE == 'cn'):
        nova_array = ['openstack-nova-compute']
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
    neu_array = []
    if(config.NODE_TYPE == 'cc'):
        neu_array = ['neutron-server','neutron-openvswitch-agent','neutron-dhcp-agent','neutron-metadata-agent','neutron-l3-agent','neutron-ovs-cleanup']
    if(config.NODE_TYPE == 'cn'):
        neu_array = ['neutron-openvswitch-agent','neutron-ovs-cleanup']
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
    glance_array = ['openstack-glance-registry','openstack-glance-api','openstack-glance-scrubber']
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
    cinder_array = ['openstack-cinder-api','openstack-cinder-scheduler','openstack-cinder-volume','openstack-cinder-backup']
    out = _operator(cinder_array,action)
    return out

def cinder_sn(action):
    """
    DESC: Control the Cinder service
    INPUT: start
           #restart
           #stop
    OUTPUT: OK
            #ERROR
            #NA
    ACCESS: Only an admin can control the openstack services.
    NOTES: These only work on the ciac node for now
    """
    cinder_array1 = ['openstack-cinder-api', 'openstack-cinder-scheduler','openstack-cinder-backup']
    out1 = _operator(cinder_array1,'stop')
    cinder_array = ['openstack-cinder-volume']
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
    """
    DESC: Control the heat service
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS: Only an admin can control the openstack services.
    NOTES: These only work on the ciac node for now
    """
    heat_array = ['openstack-heat-api','openstack-heat-api-cfn','openstack-heat-engine']
    out = _operator(heat_array,action)
    return out

def ceilometer(action):
    """
    DESC: Control the ceilometer service
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS: Only an admin can control the openstack services.
    NOTES: These only work on the ciac node for now
    """
    ceil_array = ['openstack-ceilometer-alarm-evaluator','openstack-ceilometer-alarm-notifier','openstack-ceilometer-api','openstack-ceilometer-central','openstack-ceilometer-collector',
                  'openstack-ceilometer-compute','openstack-ceilometer-notification']
    out = _operator(ceil_array,action)
    return out

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
    #HACK need to fix zero connect to take neutron service into consideration on compute nodes.
    if(config.NODE_TYPE == 'cn'):
        neutron(action)
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
                   'openstack-swift-container-replicator','openstack-swift-container-updater','openstack-swift-object','openstack-swift-object-auditor','openstack-swift-object-replicator','openstack-swift-object-expirer',
                   'openstack-swift-object-updater','openstack-swift-proxy']
    out = _operator(swift_array,action)
    return out

def gluster_swift(action):
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

    swift_array = ['openstack-swift-object','openstack-swift-container','openstack-swift-account','openstack-swift-proxy']
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

def rabbit(action):
    """
    DESC: Control the rabbitmq service
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS: Only an admin can control the rabbit services.
    NOTES:
    """
    rabbit_array = ['rabbitmq-server']
    out = _operator(rabbit_array,action)
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

def zero_connect_node(action):
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
    out = None
    if(config.NODE_TYPE == 'cn'):
        zero_array = ['cn_zero_connect']
        out = _operator(zero_array,action)
    if(config.NODE_TYPE == 'sn'):
        zero_array = ['sn_zero_connect']
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

def corosync(action):
    """
    DESC: Control the corosync service
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS: Only an admin can control the dhcp services.
    NOTES:
    """
    coro_array = ['corosync']
    out  = _operator(coro_array,action)
    return out

def pacemaker(action):
    """
    DESC: Control the pacemaker
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS: Only an admin can control the dhcp services.
    NOTES:
    """
    pacemaker_array = ['pacemaker']
    out  = _operator(pacemaker_array,action)
    return out

def avahi(action):
    """
    DESC: Control the avahi service for link local ips on cluster bond
    INPUT: start
           restart
           stop
    OUTPUT: OK
            ERROR
            NA
    ACCESS:
    NOTES: This does not ues the private _operator def since the "sevice" statts and stops differently.
    """
    avahi = 0
    if(action.lower() == 'start'):
        avahi = os.system('sudo avahi-autoipd --force-bind -D bond3')
    elif(action.lower() == 'stop'):
        avahi = os.system('sudo avahi-autoipd --kill bond3')
    elif(action.lower() == 'status'):
        out = subprocess.Popen('sudo ps -o pid,cmd -C avahi-autoipd', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = out.stdout.readlines()
        return process

    if(avahi == 0):
        return 'OK'
    else:
        return 'ERROR'

def monit(action):
    """
    DESC: Control the monit service for local monitoring of processes, cpu, memory disk, etc.
    INPUT: start
           restart
           stop
           status
    OUTPUT: OK
            ERROR
            pid (for status command)
    ACCESS:
    NOTES: This does not use the private _operator def since the "service" starts and stops differently.
    """
    monit = 0
    if(action.lower() == 'start'):
        monit = os.system('sudo monit')
    elif(action.lower() == 'stop'):
        monit = os.system('sudo monit quit')
    elif(action.lower() == 'restart'):
        monit = os.system('sudo monit reload')
    elif(action.lower() == 'status'):
        out = subprocess.Popen('sudo ps -o pid -C monit', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = out.stdout.readlines()
        return process

    if(monit == 0):
        return 'OK'
    else:
        return 'ERROR'

def _operator(service_array,action,silent=True):
    #need to check the status of the call and error corrctly - Figure this out later
    for service in service_array:
        process = []
        out = None
        time.sleep(1)
        if(action.lower() == 'start' or action.lower() == 'restart'):
            if(silent is True):
                os.system('sudo chkconfig %s on >> /dev/null'%(service))
                os.system('sudo service %s restart >> /dev/null'%(service))
                out = subprocess.Popen('sudo service %s status >> /dev/null'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                os.system('sudo chkconfig %s on'%(service))
                os.system('sudo service %s restart'%(service))
                out = subprocess.Popen('sudo service %s status'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1)
        elif(action.lower() == 'stop'):
            if(silent is True):
                os.system('sudo chkconfig %s off >> /dev/null'%(service))
                os.system('sudo service %s stop >> /dev/null'%(service))
                out = subprocess.Popen('sudo service %s status >> /dev/null'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                os.system('sudo chkconfig %s off'%(service))
                os.system('sudo service %s stop'%(service))
                out = subprocess.Popen('sudo service %s status'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif(action.lower() == 'status'):
            out = subprocess.Popen('sudo service %s status'%(service), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = out.stdout.readlines()
        #print process[0]
        #if(process[0] == ""):
        #    return 'ERROR'
    return 'OK'