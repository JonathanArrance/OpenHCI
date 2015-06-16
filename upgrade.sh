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
mkdir -p /mnt/nfs-vol/cinder-volume
chown cinder:cinder /mnt/nfs-vol/cinder-volume

# Commands to setup our ceilometer deamon.
cp /usr/local/lib/python2.7/transcirrus/daemons/ceilometer_memory_patch /etc/init.d
chmod 755 /etc/init.d/ceilometer_memory_patch
chmod 755 /usr/local/lib/python2.7/transcirrus/daemons/ceilometer_memory_patch
chown root:root /etc/init.d/ceilometer_memory_patch
chkconfig --levels 235 ceilometer_memory_patch on

# Create the symlinks so that libvirt python 2.6 files are found in python 2.7.
if [ ! -f /usr/local/lib/python2.7/site-packages/libvirt.py ]
then
    ln -s /usr/lib64/python2.6/site-packages/libvirt.py /usr/local/lib/python2.7/site-packages/libvirt.py
fi
if [ ! -f /usr/local/lib/python2.7/site-packages/libvirtmod.so ]
then
    ln -s /usr/lib64/python2.6/site-packages/libvirtmod.so /usr/local/lib/python2.7/site-packages/libvirtmod.so
fi

# Delete obsolete monit config files.
if [ -f /usr/local/lib/python2.7/transcirrus/operations/monit/openstack.conf ]
then
    rm -f /usr/local/lib/python2.7/transcirrus/operations/monit/openstack.conf 
fi
if [ -f /usr/local/lib/python2.7/transcirrus/operations/monit/quantum.conf ]
then
    rm -f /usr/local/lib/python2.7/transcirrus/operations/monit/quantum.conf
fi
if [ -f /usr/local/lib/python2.7/transcirrus/operations/monit/neutron.conf ]
then
    rm -f /usr/local/lib/python2.7/transcirrus/operations/monit/neutron.conf
fi
