#!/bin/bash -x
# NEED TO ADD THE MANUAL EDIT OF proxy-server.conf and FILTER
# NEED TO ADD THE MANUAL EDIT OF nova.conf
echo "***Getting Ceilometer via yum***"
yum install -y openstack-ceilometer-api openstack-ceilometer-collector openstack-ceilometer-central python-ceilometerclient
sleep 5

echo "***Getting MongoDB via yum***"
yum install -y mongodb-server mongodb
sleep 5

echo "***Starting MongoDB***"
service mongod start chkconfig mongod on
sleep 5

echo "***Configuring Ceilometer for MongoDB***"
openstack-config --set /etc/ceilometer/ceilometer.conf database connection mongodb://ceilometer:CEILOMETER_DBPASS@localhost:27017/ceilometer
ADMIN_TOKEN=$(openssl rand -hex 10)
openstack-config --set /etc/ceilometer/ceilometer.conf publisher_rpc metering_secret $ADMIN_TOKEN

echo "***Creating user***"
keystone user-create --name=ceilometer --pass=CEILOMETER_PASS --email=ceilometer@example.com
keystone user-role-add --user=ceilometer --tenant=service --role=admin

echo "***Configuring MongoDB using mongo_config.js***" 
mongo localhost mongo_config.js

echo "***Configuring Ceilometer for Keystone***"
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_host localhost
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_user ceilometer
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_tenant_name service
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_password CEILOMETER_PASS
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_username ceilometer
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_tenant_name service
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_password CEILOMETER_PASS

echo "***Creating service***"
service_id=$(keystone service-create --name=ceilometer --type=metering --description="Ceilometer Telemetry Service" | grep 'id' | cut -d: -f2 | awk '{print$4}')

echo "***Creating endpoint***"
keystone endpoint-create --service-id=$service_id --publicurl=http://localhost:8777 --internalurl=http://localhost:8777 --adminurl=http://localhost:8777

echo "***Starting Ceilometer services***"
service openstack-ceilometer-api start
service openstack-ceilometer-central start
service openstack-ceilometer-collector start
chkconfig openstack-ceilometer-api on
chkconfig openstack-ceilometer-central on
chkconfig openstack-ceilometer-collector on

echo "***Getting Ceilometer-Compute via yum***"
yum install -y openstack-ceilometer-compute

echo "***Configuring Nova***"
openstack-config --set /etc/nova/nova.conf DEFAULT instance_usage_audit True
openstack-config --set /etc/nova/nova.conf DEFAULT instance_usage_audit_period hour
openstack-config --set /etc/nova/nova.conf DEFAULT notify_on_state_change vm_and_task_state

echo "***Configuring Ceilometer for Compute***"
openstack-config --set /etc/ceilometer/ceilometer.conf publisher_rpc metering_secret $ADMIN_TOKEN
openstack-config --set /etc/ceilometer/ceilometer.conf DEFAULT qpid_hostname localhost
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_host localhost
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_user ceilometer
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_tenant_name service
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken auth_protocol http
openstack-config --set /etc/ceilometer/ceilometer.conf keystone_authtoken admin_password CEILOMETER_PASS
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_username ceilometer
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_tenant_name service
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_password CEILOMETER_PASS
openstack-config --set /etc/ceilometer/ceilometer.conf service_credentials os_auth_url http://localhost:5000/v2.0

echo "***Starting Ceilometer-Compute service***"
service openstack-ceilometer-compute start
chkconfig openstack-ceilometer-compute on

echo "***Configuring Glance***"
openstack-config --set /etc/glance/glance-api.conf DEFAULT notifier_strategy qpid

echo "***Restarting Glance services***"
service openstack-glance-api restart
service openstack-glance-registry restart

echo "***Configuring Cinder***"
openstack-config --set /etc/cinder/cinder.conf DEFAULT control_exchange cinder
openstack-config --set /etc/cinder/cinder.conf DEFAULT notification_driver cinder.openstack.common.notifier.rpc_notifier

echo "***Restarting Cinder services***"
service openstack-cinder-api restart
service openstack-cinder-volume restart

echo "***Adding ResellerAdmin role***"
role_id=$(keystone role-create --name=ResellerAdmin | grep 'id' | cut -d: -f2 | awk '{print$4}')
keystone user-role-add --tenant service --user ceilometer --role $role_id

echo "***Resarting Swift-Proxy service***"
service openstack-swift-proxy restart
