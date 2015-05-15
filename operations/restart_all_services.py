#!/usr/bin/python

import sys
import os
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
    
    null_fds = [os.open(os.devnull, os.O_RDWR) for x in xrange(2)]
    # save the current file descriptors to a tuple
    save = os.dup(1), os.dup(2)
    # put /dev/null fds on 1 and 2
    os.dup2(null_fds[0], 1)
    os.dup2(null_fds[1], 2)
    
    success = {}

    #stop the monit service
    #sc.monit('stop')

    #restart network cards
    #try:
    #    util.restart_network_card('all')
    #    success['network'] = 'True'
    #except Exception as e:
    #    logger.sys_error('Could not restart network after setup completed: %s.'%(e))
    #    success['network'] = 'False'
    
    br = util.restart_network_card('br-ex')
    if(br == 'OK'):
        logger.sys_info('br-ex restarted.')
        os.system('sudo /transcirrus/promisc')
        logger.sys_info('Re-added the uplink port.')
        success['Uplink'] = 'True'

    #restart OpenVswitch
    #try:
    #    sc.openvswitch('restart')
    #    success['vnet'] = 'True'
    #except Exception as e:
    #    logger.sys_error('Could not restart the virtual networking layer: %s.'%(e))
    #    success['vnet'] = 'False'

    #restart Qpid/rabbit
    #try:
    #    sc.qpid('restart')
    #    success['queue'] = 'True'
    #except Exception as e:
    #    logger.sys_error('Could not restart the queue mechanism %s.'%(e))
    #    success['queue'] = 'False'

    #restart Gluster
    #sc.gluster('restart')
    '''
    try:
        sc.keystone('restart')
        logger.sys_info('Keystone restarted.')
        success['keystone'] = 'True'
    except Exception as e:
        logger.sys_error('Could not restart keystone %s.'%(e))
        success['keystone'] = 'False'

    try:
        sc.gluster_swift('restart')
        logger.sys_info('Gluster-Swift restarted.')
        success['gluster_swift'] = 'True'
    except Exception as e:
        logger.sys_error('Could not restart gluster swift %s.'%(e))
        success['gluster_swift'] = 'False'

    try:
        sc.nova('restart')
        logger.sys_info('Nova restarted.')
        success['nova'] = 'True'
    except Exception as e:
        logger.sys_error('Could not restart nova %s.'%(e))
        success['nova'] = 'False'

    try:
        sc.cinder('restart')
        logger.sys_info('Cinder restarted.')
        success['cinder'] = 'True'
    except Exception as e:
        logger.sys_error('Could not restart cinder %s.'%(e))
        success['cinder'] = 'False'

    try:
        sc.neutron('restart')
        logger.sys_info('Neutron restarted.')
        success['neutron'] = 'True'
    except Exception as e:
        logger.sys_error('Could not restart neutron %s.'%(e))
        success['neutron'] = 'False'

    try:
        sc.glance('restart')
        logger.sys_info('Glance restarted.')
        success['glance'] = 'True'
    except Exception as e:
        logger.sys_error('Could not restart glance %s.'%(e))
        success['glance'] = 'False'
    '''

    #sc.ceilometer('restart')

    #restart Qpid/rabbit
    #try:
    #    sc.apache('restart')
    #    success['apache'] = 'True'
    #except Exception as e:
    #    logger.sys_error('Could not restart the apache server %s.'%(e))
    #    success['apache'] = 'False'

    #start the monit service back up again
    #sc.monit('start')

    #always return the services successfully restarted
    
    # restore file descriptors so I can print the results
    os.dup2(save[0], 1)
    os.dup2(save[1], 2)
    # close the temporary fds
    os.close(null_fds[0])
    os.close(null_fds[1])
    
    return success