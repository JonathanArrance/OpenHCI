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

# Install python IPy lib "Offline"
if [ ! -f /usr/local/lib/python2.7/site-packages/IPy.py ]
then
    pip2.7 install /usr/local/lib/python2.7/transcirrus/upgrade_resources/IPy-0.83.tar
fi

# diable selinux
sudo setenforce 0
sudo sed -i 's/=enforcing/=disabled/;s/=permissive/=disabled/' /etc/selinux/config

# add shadow_admin
if [ ! /home/transuser/factory_creds ]
then
echo "no factory_creds file"
else
source /home/transuser/factory_creds
SHADOW="$(sudo grep -c 'shadow_admin:' /etc/passwd)"
if [ -z "$SHADOW" ]
then
echo "shadow_admin already exists"
else
echo "adding shadow_admin"
TRANS="$(sudo cat /usr/local/lib/python2.7/transcirrus/common/config.py | grep "TRANS_DEFAULT_ID")"
ID="$(echo $TRANS |awk -F\" '$0=$2')"
# add the shadow_admin user
useradd -d /home/shadow_admin -g transystem -s /bin/admin.sh shadow_admin
#set shadow_admin default password
echo -e 'manbehindthecurtain\nmanbehindthecurtain\n' | passwd shadow_admin
# set the shadow_admin account up in sudo
(
cat << 'EOP'
shadow_admin ALL=(ALL) NOPASSWD: ALL
EOP
) >> /etc/sudoers
# add shadow_admin to groups
usermod -a -G postgres shadow_admin
usermod -a -G nova shadow_admin
usermod -a -G cinder shadow_admin
usermod -a -G glance shadow_admin
usermod -a -G swift shadow_admin
usermod -a -G neutron shadow_admin
usermod -a -G keystone shadow_admin
usermod -a -G heat shadow_admin
usermod -a -G ceilometer shadow_admin
SHADOW_ADMIN_USER=$(keystone user-create --name=shadow_admin --pass=manbehindthecurtain | grep " id " | awk '{print $4}')
# add admin, shadow_admin and trans_default project to transcirrus db
psql -U postgres -d transcirrus -c "INSERT INTO trans_user_info VALUES (1, 'shadow_admin', 'admin', 0, 'TRUE', '"${SHADOW_ADMIN_USER}"', 'trans_default','"${ID}"', 'admin', NULL);"
fi
fi