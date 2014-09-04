#!/usr/bin/python

import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.common.service_control as sc

def restart_services():
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

    #stop the monit service

    #restart network cards
    util.restart_network_card('all')

    #restart OpenVswitch
    sc.openvswitch('restart')

    #restart Qpid/rabbit
    sc.qpid('restart')

    #restart Gluster
    sc.gluster('restart')

    #restart all openstack services
    sc.keystone('restart')
    sc.gluster_swift('restart')
    sc.nova('restart')
    sc.cinder('restart')
    sc.neutron('restart')
    sc.glance('restart')
    #sc.ceilometer('restart')

    #restart apache2
    sc.apache('restart')

    #start the monit service
    
    return 'OK'