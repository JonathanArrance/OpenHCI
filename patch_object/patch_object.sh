#!/bin/bash -x

#put the correct packages in place
rpm -ivh libffi-devel-3.0.5-3.2.el6.x86_64.rpm
tar -zxvf ./swift-1.8.0.tar.gz -C .
cd ./swift-1.8.0
python ./setup.py build
python ./setup.py install

#rebuild the swift ring
python2.7 /home/transuser/alpo_rhel/unittests/gluster_test.py

#add the new valuse to the cinder table
psql -U postgres -d transcirrus -c "UPDATE cinder_default SET param_value='AvailabilityZoneFilter,CapacityFilter,CapabilitiesFilter' WHERE parameter='scheduler_default_filters';"
psql -U postgres -d transcirrus -c "INSERT INTO cinder_default VALUES ('storage_availability_zone', 'nova', 'cinder.conf');"
psql -U postgres -d transcirrus -c "ALTER TABLE projects ALTER COLUMN def_network_id SET DEFAULT 0;"
psql -U postgres -d transcirrus -c "ALTER TABLE trans_system_vols ADD COLUMN vol_type varchar(15)"
psql -U postgres -d transcirrus -c "ALTER TABLE trans_system_vols ADD COLUMN vol_zone varchar"

#update the cinder.conf file on the core node
sed -i 's/scheduler_default_filters=AvailabilityZoneFilter/scheduler_default_filters=AvailabilityZoneFilter,CapacityFilter,CapabilitiesFilter/g' /etc/cinder/cinder.conf
echo "storage_availability_zone=nova" >> /etc/hosts

#restart cinder
python2.7 /home/transuser/alpo_rhel/unittests/service_test.py

#add the volume types
python2.7 /home/transuser/alpo_rhel/unittests/cinder_vol_test.py
