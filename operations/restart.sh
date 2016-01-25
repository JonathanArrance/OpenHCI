#!/bin/bash

#
# Stop all services
#
sudo monit quit

CWD=$(pwd)
cd /etc/init.d/

sudo service ceilometer_third_party_meters stop
sudo service transcirrus_api               stop
sudo service zero_connect                  stop

for i in $( ls openstack-swift* );      do sudo service $i stop; done
for i in $( ls openstack-heat* );       do sudo service $i stop; done
for i in $( ls openstack-glance* );     do sudo service $i stop; done
for i in $( ls openstack-ceilometer* ); do sudo service $i stop; done
for i in $( ls openstack-cinder* );     do sudo service $i stop; done
for i in $( ls openstack-nova* );       do sudo service $i stop; done
for i in $( ls neutron* );              do sudo service $i stop; done

sudo service openvswitch        stop
sudo service openstack-keystone stop
sudo service httpd              stop
sudo service mongod             stop
sudo service postgresql         stop
sudo service rabbitmq-server    stop

#
# Start all services if reverse order
#
sudo service rabbitmq-server    start
sudo service postgresql         start
sudo service mongod             start
sudo service httpd              start
sudo service openstack-keystone start
sudo service openvswitch        start

for i in $( ls neutron* );              do sudo service $i start; done
for i in $( ls openstack-nova* );       do sudo service $i start; done
for i in $( ls openstack-cinder* );     do sudo service $i start; done
for i in $( ls openstack-ceilometer* ); do sudo service $i start; done
for i in $( ls openstack-glance* );     do sudo service $i start; done
for i in $( ls openstack-heat* );       do sudo service $i start; done
for i in $( ls openstack-swift* );      do sudo service $i start; done

sudo service zero_connect                  start
sudo service transcirrus_api               start
sudo service ceilometer_third_party_meters start

sudo monit

#
# Output some results
#
source /home/transuser/factory_creds
sudo openstack-status
sudo monit summary

cd $CWD
exit 0
