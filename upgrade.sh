#!/bin/bash -x

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

# Commands to setup our ceilometer daemon.
# This service is no longer needed
#/bin/cp /usr/local/lib/python2.7/transcirrus/daemons/ceilometer_memory_patch /etc/init.d
#/bin/chmod 755 /etc/init.d/ceilometer_memory_patch
#/bin/chmod 755 /usr/local/lib/python2.7/transcirrus/daemons/ceilometer_memory_patch
#/bin/chown root:root /etc/init.d/ceilometer_memory_patch
#/sbin/chkconfig --levels 235 ceilometer_memory_patch on
#/sbin/chkconfig --add /etc/init.d/ceilometer_memory_patch
#/sbin/service ceilometer_memory_patch restart

######################################################
#
#---------------------2.3 Patches---------------------
#
######################################################

#Add time to live feilds to new records recorded in mongo db
/usr/bin/openstack-config --set /etc/ceilometer/ceilometer.conf database time_to_live 604800

## Ceilometer Restart Calls
#declare -a CEILO_SVCS=('compute central collector api alarm-evaluator alarm-notifier')
#
#for svc in $CEILO_SVCS
#do
#    /sbin/service openstack-ceilometer-$svc restart
#done

#diable selinux
sudo setenforce 0
sudo sed -i 's/=enforcing/=disabled/;s/=permissive/=disabled/' /etc/selinux/config

# Install python lxml lib "Offline"
if [ ! -f /usr/local/lib/python2.7/site-packages/lxml/__init__.py ]
then
    /usr/local/bin/pip2.7 install /usr/local/lib/python2.7/transcirrus/upgrade_resources/lxml-3.4.4.tar.gz
fi

# Remove old ceilometer memory patch daemon.
/sbin/service ceilometer_memory_patch stop
/sbin/chkconfig --level 235 ceilometer_memory_patch off
/sbin/chkconfig --del /etc/init.d/ceilometer_memory_patch
/bin/rm -f /etc/init.d/ceilometer_memory_patch

# Commands to setup our ceilometer third party meters daemon.
/bin/cp /usr/local/lib/python2.7/transcirrus/daemons/ceilometer_third_party_meters /etc/init.d
/bin/chmod 755 /etc/init.d/ceilometer_third_party_meters
/bin/chmod 755 /usr/local/lib/python2.7/transcirrus/daemons/ceilometer_third_party_meters
/bin/chown root:root /etc/init.d/ceilometer_third_party_meters
/sbin/chkconfig --levels 235 ceilometer_third_party_meters on
/sbin/chkconfig --add /etc/init.d/ceilometer_third_party_meters
/sbin/service ceilometer_third_party_meters restart

# update transcirrus db
sudo service postgresql restart
/usr/bin/psql -U postgres -d transcirrus -c "ALTER TABLE trans_user_info ADD COLUMN encrypted_password character varying;"
/usr/bin/psql -U postgres -d transcirrus -c "ALTER TABLE projects ADD COLUMN is_default character varying;"

SHADOW="$(sudo grep -c 'shadow_admin:' /etc/passwd)"
if [ ! $SHADOW -eq 1 ]
then
    /bin/echo "create the linux user shadow_admin"
    #create shadown_admin
    useradd -d /home/shadow_admin -g transystem -s /bin/admin.sh shadow_admin
    #set shadow_admin default password
    /bin/echo -e 'manbehindthecurtain\nmanbehindthecurtain\n' | passwd shadow_admin
    # set the shadow_admin account up in sudo
    echo 'shadow_admin ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
fi

shadowadmingroups=('postgres' 'keystone' 'glance' 'nova' 'cinder' 'neutron'  'ceilometer' 'heat' 'swift')
for i in "${shadowadmingroups[@]}"
do
    id -Gn 'shadow_admin' | grep '\b'$i'\b'
    IDRESULT=$?
    if [ ! $IDRESULT -eq 0 ]
    then
        usermod -a -G $i shadow_admin
    fi
done

# add shadow_admin
if [ ! /home/transuer/factory_creds ]
then
    /bin/echo "ERROR: No factory_creds file"
else
    /sbin/service openstack-keystone restart
    source /home/transuser/factory_creds
    keystone user-create --name="shadow_admin" --pass="manbehindthecurtain"
    SHADOW_ADMIN_USER=$(keystone user-get shadow_admin | grep " id " | awk '{print $4}')
    TRANS="$(sudo cat /usr/local/lib/python2.7/transcirrus/common/config.py | grep "TRANS_DEFAULT_ID")"
    PROJID="$(echo ${TRANS} |awk -F\" '$0=$2')"
    ADMIN_ROLE_ID=$(keystone role-list | grep "admin" | awk '{print $2}')
    keystone user-role-add --user-id=${SHADOW_ADMIN_USER} --role-id=${ADMIN_ROLE_ID} --tenant-id=${PROJID}

    # add admin, shadow_admin and trans_default project to transcirrus db
    /usr/bin/psql -U postgres -d transcirrus -c "INSERT INTO trans_user_info VALUES (1, 'shadow_admin', 'admin', 0, 'TRUE', '"${SHADOW_ADMIN_USER}"', 'trans_default','"${PROJID}"', 'admin', NULL);"
    /usr/local/bin/python2.7 /usr/local/lib/python2.7/transcirrus/upgrade_resources/add_shadow_admin.py
fi

cd /etc/init.d/; for i in $( /bin/ls openstack-* ); do sudo service $i restart; done
cd /etc/init.d/; for i in $( /bin/ls neutron-* ); do sudo service $i restart; done

/sbin/service ceilometer_third_party_meters restart

######################################################
#
#---------------------2.4 Patches---------------------
#
######################################################

# Install python ldap lib "Offline"
if [ ! -f /usr/local/lib/python2.7/site-packages/ldap/__init__.py ]
then
    /usr/local/bin/pip2.7 install /usr/local/lib/python2.7/transcirrus/upgrade_resources/python-ldap-2.4.20.tar.gz
fi

# Write ldap_config.py if it doesn't already exist
if [ ! -f /usr/local/lib/python2.7/transcirrus/operations/third_party_auth/ldap/ldap_config.py ]
then
    /bin/echo "Writing ldap_config.py..."
    /bin/touch /usr/local/lib/python2.7/transcirrus/operations/third_party_auth/ldap/ldap_config.py
    /bin/echo 'CONFIGURED=False' >> /usr/local/lib/python2.7/transcirrus/operations/third_party_auth/ldap/ldap_config.py
    /bin/chmod 777 /usr/local/lib/python2.7/transcirrus/operations/third_party_auth/ldap/ldap_config.py
fi

# Install flasgger package
if [ ! -f /usr/local/lib/python2.7/site-packages/flasgger/__init__.py ]
then
    /usr/local/bin/pip2.7 install flasgger
fi

# aPersona unique email update
sudo service postgresql restart
/usr/bin/psql -U postgres -d transcirrus -c "ALTER TABLE ONLY trans_user_info ADD CONSTRAINT trans_user_info_user_email_key UNIQUE (user_email);"

# Commands to setup our rest api daemon
/bin/cp /usr/local/lib/python2.7/transcirrus/daemons/transcirrus_api /etc/init.d
/bin/chmod 755 /etc/init.d/transcirrus_api
/bin/chmod 755 /usr/local/lib/python2.7/transcirrus/daemons/transcirrus_api
/bin/chown root:root /etc/init.d/transcirrus_api
/sbin/chkconfig --levels 235 transcirrus_api on
/sbin/chkconfig --add /etc/init.d/transcirrus_api
/sbin/service transcirrus_api restart
