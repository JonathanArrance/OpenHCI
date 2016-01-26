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
# Wait until there are no locks on the RPM lock file. This is
# required when we are being run from a RPM install script
# and we try to yum/rpm install a package. If the lock is
# held, the package we try to install will hang waiting for
# our RPM lock which won't we won't release because we are
# waiting on the package to complete it's install.
# To resolve this, we will have our RPM install script
# fork a process to run this script and then it will exit
# which will soon free the lock so we can proceed with
# this script.
#
HOSTNAME=`hostname`
MASTER_PWD='simpleprivatecloudsolutions'

while sudo lsof /var/lib/rpm/.rpm.lock
do
  echo "RPM file is locked; sleeping a second"
  sleep 1000
done

#
# Version 2.2-x section:
#

# Create the directories needed to mount NFS volumes via cinder.
# The owner of cinder-volume must be cinder so it can write to it.
/bin/mkdir -p /mnt/nfs-vol/cinder-volume
/bin/chown cinder:cinder /mnt/nfs-vol/cinder-volume

# Create the mongo db ceilometer user in case it was missing.
/bin/echo 'db.addUser({user: "ceilometer",pwd: "simpleprivatecloudsolutions",roles: [ "readWrite", "dbAdmin" ]})' >> /tmp/MongoCeilometerUser.js
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

# Fix and restart monit
monit quit
/usr/local/bin/python2.7 /usr/local/lib/python2.7/transcirrus/operations/monit/fix_monit_conf.py
monit

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
    # add email for shadow_admin
    python2.7 -c "from transcirrus.common import extras; from transcirrus.component.keystone.keystone_users import user_ops; auth = extras.shadow_auth(); uo = user_ops(auth); uo.update_user({'username': 'shadow_admin', 'email': 'bugs@transcirrus.com'})"
fi

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

# # aPersona unique email update
sudo service postgresql restart
/usr/bin/psql -U postgres -d transcirrus -c "ALTER TABLE ONLY trans_user_info DROP CONSTRAINT trans_user_info_user_email_key UNIQUE (user_email);"

# add aPersona application to cloud if it isn't already there
if [ ! -f /var/lib/tomcat6/webapps/api_portal/WEB-INF/api-portal-dispatcher-servlet.xml ]
then
    /usr/bin/yum update --skip-broken -y
    /usr/bin/yum install java-1.7.0-openjdk -y
    /usr/bin/yum install tomcat6 -y
    /sbin/service tomcat6 start
    /sbin/chkconfig tomcat6 on
    /usr/bin/yum install tomcat6-webapps -y
    /sbin/service tomcat6 restart
    /usr/bin/yum update --skip-broken -y
    /bin/rm -rf /var/lib/tomcat6/webapps/*
    /bin/cp -r /usr/local/lib/python2.7/transcirrus/upgrade_resources/aPersona/ap* /var/lib/tomcat6/webapps/
    /usr/bin/psql -U postgres -f /usr/local/lib/python2.7/transcirrus/upgrade_resources/aPersona/apersona_configured.sql
    sed -i 's/8080/8090/g' /usr/share/tomcat6/conf/server.xml
    /sbin/service tomcat6 restart
fi

# Commands to setup our rest api daemon
/bin/cp /usr/local/lib/python2.7/transcirrus/daemons/transcirrus_api /etc/init.d
/bin/chmod 755 /etc/init.d/transcirrus_api
/bin/chmod 755 /usr/local/lib/python2.7/transcirrus/daemons/transcirrus_api
/bin/chown root:root /etc/init.d/transcirrus_api
/sbin/chkconfig --levels 235 transcirrus_api on
/sbin/chkconfig --add /etc/init.d/transcirrus_api
/sbin/service transcirrus_api restart

# Commands to build and install gmp which fixes some security issues
# which also requires pycrpto to be re-installed.
if [ ! -f "/usr/local/lib/libgmp.a" ]
then
  cwd=$(pwd)
  cd /tmp
  tar -xvjpf /usr/local/lib/python2.7/transcirrus/upgrade_resources/gmp-6.1.0.tar.bz2
  cd gmp-6.1.0
  ./configure
  make
  make check
  make install

  /usr/local/bin/pip2.7 install --ignore-installed /usr/local/lib/python2.7/transcirrus/upgrade_resources/pycrypto-2.6.1.tar.gz
  cd $cwd
fi

# downgrade websockify to work with noVNC console
/usr/bin/yum downgrade -y python-websockify-0.5.1-1.el6.noarch


# Install Openswan and Openstack VPN packages
if [ ! -f "/usr/sbin/ipsec" ]
then
    yum install -y /usr/local/lib/python2.7/transcirrus/upgrade_resources/openswan-2.6.32-37.el6.x86_64.rpm
fi

if [ ! -f "/etc/init.d/neutron-vpn-agent" ]
then
    yum install -y /usr/local/lib/python2.7/transcirrus/upgrade_resources/openstack-neutron-vpn-agent-2014.1.5-1.el6.noarch.rpm
    /bin/chown neutron:neutron /etc/neutron/vpn_agent.ini
    /bin/chmod 770 /etc/neutron/vpn_agent.ini
fi

# Setup VPNaaS Neutron Config
/usr/bin/openstack-config --set /etc/neutron/neutron.conf DEFAULT service_plugins router,metering,vpnaas

/usr/bin/openstack-config --set /etc/neutron/vpn_agent.ini vpnagent vpn_device_driver neutron.services.vpn.device_drivers.ipsec.OpenSwanDriver
/usr/bin/openstack-config --set /etc/neutron/vpn_agent.ini ipsec ipsec_status_check_interval 60

######################################################
#
#------------------Version 2.5-----------------------
#
#####################################################
#chnage the master password 
echo 'MASTER_PWD="'${MASTER_PWD}'"' >> /usr/local/lib/python2.7/transcirrus/common/config.py
sudo rm /usr/local/lib/python2.7/transcirrus/common/config.pyc
#create the mongo file
echo 'db.changeUserPassword("ceilometer", "'${MASTER_PWD}'")' >> /transcirrus/update_mongo_pwd.js

#add master pwd to trans_system_settings table
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('master_pwd','"$MASTER_PWD"','"${HOSTNAME}"');"

/usr/local/bin/python2.7 /usr/local/lib/python2.7/transcirrus/operations/change_master_password.py ${MASTER_PWD}

######################################################
#
#------------------Restart Services-------------------
#
######################################################

/sbin/service ipsec restart

cd /etc/init.d/; for i in $( /bin/ls openstack-* ); do sudo service $i restart; done
cd /etc/init.d/; for i in $( /bin/ls neutron-* ); do sudo service $i restart; done

/sbin/service ceilometer_third_party_meters restart
/sbin/service transcirrus_api restart

exit 0
