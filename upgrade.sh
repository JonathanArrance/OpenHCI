#!/bin/bash

# This is the primary upgrade script for the product. This file will
# be executed by our rpm installer after the files have been upgraded.
# 
# Most of the commands here will also need to go into the installer
# that runs when the product is first installed/setup.
#
# NOTE: Make sure to check that this script will not error out if
#       a command is run a second time. This WILL happen if the
#       installer or this upgrade script has already been run from
#       a previous install or upgrade.

#
# Version 2.2-x section:
#

# Create the directories needed to mount NFS volumes via cinder.
# The owner of cinder-volume must be cinder so it can write to it.
/bin/mkdir -p /mnt/nfs-vol/cinder-volume
/bin/chown cinder:cinder /mnt/nfs-vol/cinder-volume

# Create the mongo db ceilometer user in case it was missing.
/bin/echo 'db.addUser({user: "ceilometer",pwd: "transcirrus1",roles: [ "readWrite", "dbAdmin" ]})' >> /tmp/MongoCeilometerUser.js
/usr/bin/mongo --host 172.24.24.10 ceilometer /tmp/MongoCeilometerUser.js

# Fix any configs that may not have been setup for ceilometer meters
/usr/bin/openstack-config --set /etc/ceilometer/ceilometer.conf DEFAULT pipeline_cfg_file pipeline.yaml
/usr/bin/openstack-config --set /etc/ceilometer/ceilometer.conf DEFAULT host $HOSTNAME
/usr/bin/openstack-config --set /etc/nova/nova.conf DEFAULT notification_driver nova.openstack.common.notifier.rpc_notifier
/usr/bin/openstack-config --set /etc/nova/nova.conf DEFAULT notification_driver ceilometer.compute.nova_notifier
/usr/bin/openstack-config --set /etc/nova/nova.conf DEFAULT compute_available_monitors nova.compute.monitors.all_monitors
/usr/bin/openstack-config --set /etc/nova/nova.conf DEFAULT compute_monitors ComputeDriverCPUMonitor

# Create the symlinks so that libvirt python 2.6 files are found in python 2.7.
if [ ! -f /usr/local/lib/python2.7/site-packages/libvirt.py ]
then
    /bin/ln -s /usr/lib64/python2.6/site-packages/libvirt.py /usr/local/lib/python2.7/site-packages/libvirt.py
fi
if [ ! -f /usr/local/lib/python2.7/site-packages/libvirtmod.so ]
then
    /bin/ln -s /usr/lib64/python2.6/site-packages/libvirtmod.so /usr/local/lib/python2.7/site-packages/libvirtmod.so
fi

# Delete obsolete monit config files.
if [ -f /usr/local/lib/python2.7/transcirrus/operations/monit/openstack.conf ]
then
    /bin/rm -f /usr/local/lib/python2.7/transcirrus/operations/monit/openstack.conf
fi
if [ -f /usr/local/lib/python2.7/transcirrus/operations/monit/quantum.conf ]
then
    /bin/rm -f /usr/local/lib/python2.7/transcirrus/operations/monit/quantum.conf
fi
if [ -f /usr/local/lib/python2.7/transcirrus/operations/monit/neutron.conf ]
then
    /bin/rm -f /usr/local/lib/python2.7/transcirrus/operations/monit/neutron.conf
fi

# Install python IPy lib "Offline"
if [ ! -f /usr/local/lib/python2.7/site-packages/IPy.py ]
then
    /usr/local/bin/pip2.7 install /usr/local/lib/python2.7/transcirrus/upgrade_resources/IPy-0.83.tar
fi

# Commands to setup our ceilometer deamon.
/bin/cp /usr/local/lib/python2.7/transcirrus/daemons/ceilometer_memory_patch /etc/init.d
/bin/chmod 755 /etc/init.d/ceilometer_memory_patch
/bin/chmod 755 /usr/local/lib/python2.7/transcirrus/daemons/ceilometer_memory_patch
/bin/chown root:root /etc/init.d/ceilometer_memory_patch
/sbin/chkconfig --levels 235 ceilometer_memory_patch on
/sbin/chkconfig --add /etc/init.d/ceilometer_memory_patch
/sbin/service ceilometer_memory_patch restart

######################################################
#
#---------------------2.3 Patches---------------------
#
######################################################

#Add time to live feilds to new records recorded in mongo db
/usr/bin/openstack-config --set /etc/ceilometer/ceilometer.conf database time_to_live 604800
