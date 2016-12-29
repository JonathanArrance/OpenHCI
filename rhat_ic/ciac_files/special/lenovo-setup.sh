#!/bin/bash -x

#add postgres to the yum repos files
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.old
wget -P /etc/yum.repos.d/ http://192.168.10.10/rhat_ic/ciac_files/CentOS-Base.repo

chkconfig ntpd on
service ntpd restart

#set up postgresql
chkconfig postgresql on
service postgresql initdb

mv /var/lib/pgsql/data/pg_hba.conf /var/lib/pgsql/data/pg_hba.conf.old
mv /var/lib/pgsql/data/postgresql.conf /var/lib/pgsql/data/postgresql.conf.old
wget -P /var/lib/pgsql/data/ http://192.168.10.10/rhat_ic/ciac_files/pg_hba.conf
chown postgres:postgres /var/lib/pgsql/data/pg_hba.conf
wget -P /var/lib/pgsql/data/ http://192.168.10.10/rhat_ic/ciac_files/postgresql.conf
chown postgres:postgres /var/lib/pgsql/data/postgresql.conf
chmod 766 /var/lib/pgsql/data/pg_hba.conf
chmod 766 /var/lib/pgsql/data/postgresql.conf

#restart psql
service postgresql restart

sleep 10

#add the transuser account to postgres and set the password
#used as the admin account for all transcirrus and openstack databases/tables
psql -U postgres -c "CREATE USER transuser;"
psql -U postgres -c "ALTER USER transuser WITH PASSWORD 'transcirrus1';"

#create all of the empty dbs for the openstack users
psql -U postgres -c "CREATE DATABASE nova;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE nova TO transuser;"
psql -U postgres -c "ALTER DATABASE nova OWNER TO transuser;"

psql -U postgres -c "CREATE DATABASE cinder;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE cinder TO transuser;"
psql -U postgres -c "ALTER DATABASE cinder OWNER TO transuser;"

psql -U postgres -c "CREATE DATABASE keystone;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE keystone TO transuser;"
psql -U postgres -c "ALTER DATABASE keystone OWNER TO transuser;"

psql -U postgres -c "CREATE DATABASE neutron;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE neutron TO transuser;"
psql -U postgres -c "ALTER DATABASE neutron OWNER TO transuser;"

psql -U postgres -c "CREATE DATABASE glance;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE glance TO transuser;"
psql -U postgres -c "ALTER DATABASE glance OWNER TO transuser;"

psql -U postgres -c "CREATE DATABASE heat;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE heat TO transuser;"
psql -U postgres -c "ALTER DATABASE heat OWNER TO transuser;"

psql -U postgres -c "CREATE DATABASE transcirrus;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE transcirrus TO transuser;"
psql -U postgres -c "ALTER DATABASE transcirrus OWNER TO transuser;"


#set the hostname to ciac-xxxxx random digits
echo "Setting the hostname."
mv /etc/hostname /etc/hostname.old
#RAND=$RANDOM

NODEONE=$(($RANDOM % 99999999 + 10000000))
NODETWO=$(($RANDOM % 99999 + 10000))

ADMIN_TOKEN=$(($RANDOM % 999999999999999999 + 100000000000000000))
#ADMIN_TOKEN="transcirrus109283"

HOSTNAME=ciac-${NODETWO}

#ciac node id
NODEID=000-${NODEONE}-${NODETWO}

echo $NODEID > /etc/nodeid

#add the hostname
mv /etc/sysconfig/network /etc/sysconfig/network.old
echo 'HOSTNAME='$HOSTNAME > /etc/sysconfig/network
echo 'NETWORKING=yes' >> /etc/sysconfig/network

#change the hosts file
mv /etc/hosts /etc/hosts.old

echo '127.0.0.1   localhost' > /etc/hosts
echo "127.0.1.1   $HOSTNAME" >> /etc/hosts

echo '::1     ip6-localhost ip6-loopback' >> /etc/hosts
echo 'fe00::0 ip6-localnet' >> /etc/hosts
echo 'ff00::0 ip6-mcastprefix' >> /etc/hosts
echo 'ff02::1 ip6-allnodes' >> /etc/hosts
echo 'ff02::2 ip6-allrouters' >> /etc/hosts

sed -i 's/PATH=\$PATH:\$HOME\/bin/PATH=\$PATH:\$HOME\/bin:\/usr\/local\/bin/g' /root/.bash_profile
sed -i 's/secure_path = \/sbin:\/bin:\/usr\/sbin:\/usr\/bin/secure_path = \/sbin:\/bin:\/usr\/sbin:\/usr\/bin:\/usr\/local\/bin/g' /etc/sudoers
sed -i 's/IPTABLES_SAVE_ON_STOP="no"/IPTABLES_SAVE_ON_STOP="yes"/g' /etc/sysconfig/iptables-config
sed -i 's/IPTABLES_SAVE_ON_RESTART="no"/IPTABLES_SAVE_ON_RESTART="yes"/g' /etc/sysconfig/iptables-config

#fix so sudo can use python2.7 
#echo 'DEFAULTS    secure_path += /usr/local/bin' >> /etc/sudoers

sleep 1

hostname $HOSTNAME

#scratch dir for transcirrus
mkdir /transcirrus
chmod -R 777 /transcirrus

#create the gluster mount file
touch /transcirrus/gluster-mounts
chmod 777 /transcirrus/gluster-mounts

#create a gluster-object mount file
touch /transcirrus/gluster-object-mount
chmod 777 /transcirrus/gluster-object-mount

wget -P /transcirrus http://192.168.10.10/images/cirros-0.3.1-x86_64-disk.img
wget -P /transcirrus http://192.168.10.10/images/centos-6.5-20140117.0.x86_64.qcow2
wget -P /transcirrus http://192.168.10.10/images/precise-server-cloudimg-amd64-disk1.img
wget -P /transcirrus http://192.168.10.10/rhat_ic/ciac_files/pg_hba.proto
chmod 777 /transcirrus/pg_hba.proto

#set up rbash
ln -s /bin/bash /bin/rbash
echo '/bin/rbash' >> /etc/shells
echo '/bin/admin.sh' >> /etc/shells

#create admin shell - admin.sh
touch /bin/admin.sh
(
cat <<'EOP'
#!/bin/rbash
python2.7 /usr/local/lib/python2.7/transcirrus/interfaces/shell/coalesce.py
EOP
) >> /bin/admin.sh
chmod +x /bin/admin.sh
chown transuser:transystem /bin/admin.sh

#add the admin user
useradd -d /home/admin -g transystem -s /bin/admin.sh admin

#set admin default password
echo -e 'password\npassword\n' | passwd admin

#make it so apaceh can run sudo
sed -i 's/Defaults    requiretty/#Defaults    requiretty/g' /etc/sudoers

#echo "Setting up transuser sudo."
#set the transuser account up in sudo
(
cat <<'EOP'
transuser ALL=(ALL) NOPASSWD: ALL
admin ALL=(ALL) NOPASSWD: ALL
apache ALL=(ALL:ALL) NOPASSWD: ALL
EOP
) >> /etc/sudoers

#fix postgres user groups
usermod -a -G postgres admin
usermod -a -G postgres apache
usermod -a -G postgres transuser

#iceHouse repo
yum install -y http://192.168.10.10/rhat_ic/common/rdo-release-icehouse-4.noarch.rpm
yum install -y http://192.168.10.10/rhat_ic/common/epel-release-6-8.noarch.rpm

# install some additional packages
echo "Installing software on the system."
yum groupinstall -y "Development tools"
yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel
yum install -y wget

#gluster3.5 repo
wget -P /root http://192.168.10.10/rhat_ic/gluster/glusterfs-epel-35.repo
yum-config-manager --add-repo /root/glusterfs-epel-35.repo
yum install -y glusterfs-libs-3.5.2-1.el6.x86_64
yum install -y glusterfs-3.5.2-1.el6.x86_64
yum install -y glusterfs-devel-3.5.2-1.el6.x86_64
yum install -y glusterfs-server-3.5.2-1.el6.x86_64
yum install -y glusterfs-geo-replication-3.5.2-1.el6.x86_64

#yum
yum install -y redhat-lsb
yum install -y erlang
yum install -y mod_ssl openssl
yum install -y libguestfs-tools
yum install -y qemu-kvm
yum install -y jwhois
yum install -y dhcp
yum install -y ethtool net-tools
yum install -y python-setuptools python-devel python-simplejson
yum install -y dnsmasq-utils
yum install -y python-psycopg2
yum install -y memcached xfsprogs openstack-utils python-keystone-auth-token
yum install -y dialog
yum install -y python-pip
yum install -y gcc
yum install -y avahi-autoipd
yum install -y cluster-glue
yum install -y resource-agents
yum install -y pcs
yum install -y ncurses-devel gdbm-devel db4-devel libpcap-devel xz-devel
yum install -y httpd-devel
yum install -y xauth
yum install -y mongodb-server mongodb
yum install -y conntrack-tools

#get the RabbitMQ server
rpm --import http://192.168.10.10/rhat_ic/common/rabbitmq-signing-key-public.asc
yum install -y http://192.168.10.10/rhat_ic/common/rabbitmq-server-3.3.5-1.noarch.rpm


#may need to remove this with yum before openstack components
#yum erase python27-2.7.3-6.2.sdl6.2.x86_64

echo "Installing OpenStack Keystone components."
yum install -y openstack-keystone python-keystoneclient
echo "Installing OpenStack Glance components."
yum install -y openstack-glance python-glanceclient
echo "Installing OpenStack Nova components."
yum install -y openstack-nova-api openstack-nova-scheduler openstack-nova-cert openstack-nova-console openstack-nova-doc genisoimage openstack-nova-novncproxy openstack-nova-conductor novnc openstack-nova-compute python-novaclient
echo "Installing OpenStack Cinder components."
yum install -y openstack-cinder openstack-cinder-doc
echo "Installing OpenStack Neutron components."
yum install -y openstack-neutron openstack-neutron-ml2 python-neutronclient openstack-neutron-openvswitch
echo "installing OpenStack Ceilometer"
yum install -y openstack-ceilometer-api openstack-ceilometer-collector openstack-ceilometer-notification openstack-ceilometer-central openstack-ceilometer-alarm python-ceilometerclient openstack-ceilometer-compute python-pecan
echo "Installing OpenStack Heat"
yum install -y openstack-heat-api openstack-heat-engine openstack-heat-api-cfn
echo "Installing OpenStack Swift components"
yum install -y openstack-swift-account openstack-swift-container openstack-swift-object xfsprogs xinetd openstack-swift-proxy python-swiftclient python-keystone-auth-token

#install monit
wget -P /root http://192.168.10.10/rhat_ic/common/monit-5.8.1-1.x86_64.rpm
rpm -ivh /root/monit-5.8.1-1.x86_64.rpm

#install python2.7
#/usr/local/bin/python2.7
wget -P /root http://192.168.10.10/rhat_ic/common/Python-2.7.3.tar.bz2
cd /root
tar xf Python-2.7.3.tar.bz2
cd Python-2.7.3
./configure --prefix=/usr/local --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
make
make altinstall

sleep 1
sudo ln -s /usr/local/lib/libpython2.7.so.1.0 /usr/lib/libpython2.7.so.1.0
ldd /usr/lib/libpython2.7.so.1.0
ldconfig

#enable https in apache
wget -P /etc/pki/tls/certs http://192.168.10.10/rhat_ic/ciac_files/keys/ca.crt
wget -P /etc/pki/tls/private http://192.168.10.10/rhat_ic/ciac_files/keys/ca.key
wget -P /etc/pki/tls/private http://192.168.10.10/rhat_ic/ciac_files/keys/ca.csr
mv /etc/httpd/conf.d/ssl.conf /etc/httpd/conf.d/ssl.old
wget -P /etc/httpd/conf.d http://192.168.10.10/rhat_ic/ciac_files/keys/ssl.conf

#python2.7 RPM version Hack needed for gluster swift.
wget -P /root http://192.168.10.10/rhat_ic/common/environment-modules-3.2.9c-6.el6.x86_64.rpm
wget -P /root http://192.168.10.10/rhat_ic/common/python27-libs-2.7.3-6.2.sdl6.2.x86_64.rpm
wget -P /root http://192.168.10.10/rhat_ic/common/python27-2.7.3-6.2.sdl6.2.x86_64.rpm
rpm -ivh /root/environment-modules-3.2.9c-6.el6.x86_64.rpm
rpm -ivh /root/python27-libs-2.7.3-6.2.sdl6.2.x86_64.rpm
rpm -ivh /root/python27-2.7.3-6.2.sdl6.2.x86_64.rpm

#install python 2.7 pip
wget -P /root http://192.168.10.10/rhat_ic/common/ez_setup.py
wget -P /root http://192.168.10.10/rhat_ic/common/get-pip.py
python2.7 /root/ez_setup.py
python2.7 /root/get-pip.py

sleep 1
#install setuptools
wget -P /root http://192.168.10.10/rhat_ic/ciac_files/setuptools-0.6c11-py2.7.egg
cd /root
sh setuptools-0.6c11-py2.7.egg --prefix=/usr/local

#get psycopg2 in python2.7
wget -P /root http://192.168.10.10/rhat_ic/common/psycopg2-2.5.2.tar.gz
tar -zxvf /root/psycopg2-2.5.2.tar.gz -C /root
cd /root/psycopg2-2.5.2
python2.7 ./setup.py install

#install wget
wget -P /root http://192.168.10.10/rhat_ic/ciac_files/wget-2.2.tar.gz
tar -zxvf /root/wget-2.2.tar.gz -C /root
cd /root/wget-2.2
python2.7 ./setup.py install

#add the hack for loopback users in rabbitmq
echo '[{rabbit, [{loopback_users, []}]}].' >> /etc/rabbitmq/rabbitmq.config

#start Rabbit
chkconfig rabbitmq-server on
service rabbitmq-server start

#create a new rabbitmq user/password
#rabbitmqctl add_user transuser transcirrus1
#rabbitmqctl set_user_tags transuser administrator
rabbitmqctl change_password guest transcirrus1

mv /etc/sysconfig/dhcpd /etc/sysconfig/dhcpd.old
mv /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf.old
#get the config files
wget -P /etc/sysconfig http://192.168.10.10/rhat_ic/ciac_files/dhcpd
wget -P /etc/dhcp http://192.168.10.10/rhat_ic/ciac_files/dhcpd.conf
#dhcp on by default
chkconfig --levels 235 dhcpd on

#need to figure out or multi node stratagy this should be off by defualt.
#chkconfig --levels 235 dhcpd off

#add confparser
wget -P /root http://192.168.10.10/rhat_ic/common/confparse-1.0a1-py2.5.egg
easy_install-2.7 /root/confparse-1.0a1-py2.5.egg

#not getting this package - check
wget -P /root http://192.168.10.10/rhat_ic/common/python-ifconfig-0.1.tar.gz
tar -zxvf /root/python-ifconfig-0.1.tar.gz -C /root
cd /root/python-ifconfig-0.1
python2.7 ./setup.py install
python2.7 /root/python-ifconfig-0.1/test/test_ifconfig.py

#get the python dialog package
wget -P /root http://192.168.10.10/rhat_ic/common/pythondialog-2.11.tar
tar -xvf /root/pythondialog-2.11.tar -C /root
cd /root/pythondialog-2.11
python2.7 ./setup.py build
python2.7 ./setup.py install

#install celery to python 2.7
easy_install-2.7 Celery

#used for the ssh update util
easy_install-2.7 paramiko

#get FLASK - REST API framework
pip install Flask
pip2.7 install Flask

#install ipy
pip2.7 install ipy

#install django
pip2.7 install django==1.5
pip2.7 install django-bootstrap-toolkit
pip2.7 install django-tables2
pip2.7 install django-filter
pip2.7 install django-crispy-forms
pip2.7 install django-celery

#make sure all service belong to thier user
rm -rf /etc/neutron
rm -rf /etc/nova
rm -rf /etc/glance
rm -rf /etc/cinder
rm -rf /etc/heat
rm -rf /etc/ceilometer

#setting up etc files
#get the new configs from the install repo
wget -P /etc http://192.168.10.10/rhat_ic/ciac_files/version22/os_configs_22.tar
tar -xvf /etc/os_configs_22.tar -C /etc

#make sure all service belong to thier user
chown -R nova:nova /etc/nova
chown -R cinder:cinder /etc/cinder
chown -R glance:glance /etc/glance
chown -R neutron:neutron /etc/neutron
chown -R heat:heat /etc/heat
chown -R ceilometer:ceilometer /etc/ceilometer

chmod -R 770 /etc/nova
chmod -R 770 /etc/cinder
chmod -R 770 /etc/glance
chmod -R 770 /etc/neutron
chmod -R 770 /etc/keystone
chmod -R 770 /etc/heat
chmod -R 770 /etc/ceilometer


#add transuser to groups
usermod -a -G nova transuser
usermod -a -G cinder transuser
usermod -a -G glance transuser
usermod -a -G swift transuser
usermod -a -G neutron transuser
usermod -a -G keystone transuser
usermod -a -G heat transuser
usermod -a -G ceilometer transuser

#add admin to groups
usermod -a -G nova admin
usermod -a -G cinder admin
usermod -a -G glance admin
usermod -a -G swift admin
usermod -a -G neutron admin
usermod -a -G keystone admin
usermod -a -G heat admin
usermod -a -G ceilometer admin

#add apache webserver
usermod -a -G nova apache
usermod -a -G cinder apache
usermod -a -G glance apache
usermod -a -G swift apache
usermod -a -G neutron apache
usermod -a -G keystone apache
usermod -a -G transuser apache
usermod -a -G heat apache
usermod -a -G ceilometer apache

usermod -a -G apache glance

#update log file permissions - these did not work sice the log files do not exist.
chmod 664 /var/log/glance/registry.log
chmod 664 /var/log/nova/nova-manage.log

#this worked
chmod 664 /etc/neutron/l3_agent.ini

#fix the log files
chmod g+w /var/log/neutron
chmod g+w /var/log/nova
chmod g+w /var/log/cinder
chmod g+w /var/log/glance
chmod g+w /var/log/keystone
chmod g+w /var/log/heat
chmod g+w /var/log/ceilometer

chown neutron:neutron /var/log/neutron
chown nova:nova /var/log/nova
chown cinder:cinder /var/log/cinder
chown glance:glance /var/log/glance
chown keystone:keystone /var/log/keystone
chown heat:heat /var/log/heat
chown ceilometer:ceilometer /var/log/ceilometer

sleep 1
mkdir -p /usr/local/lib/python2.7/transcirrus
#download the transcirrus code
wget -P /usr/local/lib/python2.7/transcirrus http://192.168.10.10/builds/rhat_ic/version_221_release
sleep 1
tar -xvf /usr/local/lib/python2.7/transcirrus/version_221_release -C /usr/local/lib/python2.7/transcirrus

#check to see if the log file exists
if [ -e /var/log/caclogs/system.log ]
then
echo "CAClog exists"
else
mkdir -p /var/log/caclogs
touch /var/log/caclogs/system.log
chmod -R 777 /var/log/caclogs
chown -R transuser:transystem /var/log/caclogs
fi

# We have to do this so multiple users/processes can write to the log file.
chmod -R g+s /var/log/caclogs
chmod -R 777 /var/log/caclogs

#add the chmod log hack
(crontab -l 2>/dev/null; echo "0 * * * * /bin/chmod 777 /var/log/caclogs/system.log") | crontab -

#add the django site to its proper place in the file system
echo 'Adding Coalesce to the opt directory.'
cp -Rf /usr/local/lib/python2.7/transcirrus/interfaces/Coalesce /opt
chown -R apache:apache /opt/Coalesce

#restart the apache2 service
#Starting httpd: httpd: Syntax error on line 221 of /etc/httpd/conf/httpd.conf: Syntax error on line 12 of /etc/httpd/conf.d/ssl.conf: Cannot load /etc/httpd/modules/mod_ssl.so into server: /etc/httpd/modules/mod_ssl.so: cannot open shared object file: No such file or directory
chkconfig httpd on
service httpd restart

rm /usr/local/lib/python2.7/transcirrus/version_221_release

#set up the postgres DB
psql -U postgres -d transcirrus -a -f /usr/local/lib/python2.7/transcirrus/SQL_files/transcirrus_default_db.sql

#set up the MongoDB - Ceilometer
mv /etc/mongodb.conf /etc/mongodb.orig
wget -P /etc http://192.168.10.10/rhat_ic/ciac_files/mongodb.conf
chmod 644 /etc/mongodb.conf

service mongod start
chkconfig mongod on
sleep 5
echo 'db.addUser({user: "ceilometer",pwd: "transcirrus1",roles: [ "readWrite", "dbAdmin" ]})' >> /transcirrus/mongo.js
#mongo --host 172.24.24.10 ceilometer /root/mongo.js

#add the metering secret to ceilometer
CEILOMETER_TOKEN=$(openssl rand -hex 10)
#sed -i 's/metering_secret=/metering_secret='${CEILOMETER_TOKEN}'/g' /etc/ceilometer/ceilometer.conf
psql -U postgres -d transcirrus -c "INSERT INTO ceilometer_default VALUES ('metering_secret','"${CEILOMETER_TOKEN}"','ceilometer.conf');"

#get link local ip
avahi-autoipd --force-bind -D bond3
sleep 10
IP=`ip addr | grep inet | grep bond3 | awk -F" " '{print $2}' | sed -e 's/\/.*$//'`
sed -i 's/IPADDR=/IPADDR='${IP}'/g' /etc/sysconfig/network-scripts/ifcfg-bond3
sed -i 's/NETMASK=/NETMASK="255.255.0.0"/g' /etc/sysconfig/network-scripts/ifcfg-bond3
psql -U postgres -d transcirrus -c "INSERT INTO net_adapter_settings VALUES (1, 'bond3', '"${IP}"', '255.255.0.0', NULL, NULL, NULL, '"${NODEID}"', '"${HOSTNAME}"', NULL, NULL, 'none', NULL, '1500', NULL, 'clust', 'localdomain');"

echo "Adding the default net adapter settings."
#set up the defualt network entries for the ciac node
psql -U postgres -d transcirrus -c "INSERT INTO net_adapter_settings VALUES (2, 'bond0', '192.168.0.2', '255.255.255.0', '8.8.8.8', '8.8.4.4', '204.85.3.3', '"${NODEID}"', '"${HOSTNAME}"', NULL, NULL, 'none', '192.168.0.1', '1500', NULL, 'mgmt', 'localdomain');"
psql -U postgres -d transcirrus -c "INSERT INTO net_adapter_settings VALUES (3, 'br-ex', '192.168.0.3', '255.255.255.0', '8.8.8.8', '8.8.4.4', '204.85.3.3', '"${NODEID}"', '"${HOSTNAME}"', NULL, NULL, 'none', '192.168.0.1', '9000', NULL, 'uplink', 'localdomain');"


#set up the Keystone service
#move the old file and write the new file in place
#set the auth token to some radom number
sleep 2
mv /etc/keystone/keystone.conf /etc/keystone/keystone.conf.old
echo [DEFAULT] > /etc/keystone/keystone.conf
echo admin_token = ${ADMIN_TOKEN} >> /etc/keystone/keystone.conf
(
cat <<'EOP'
bind_host = 0.0.0.0
public_port = 5000
admin_port = 35357
compute_port = 8774
debug = False
verbose = False
[sql]
connection = postgresql://transuser:transcirrus1@localhost/keystone
[identity]
driver = keystone.identity.backends.sql.Identity
[trust]
driver = keystone.trust.backends.sql.Trust
[catalog]
driver = keystone.catalog.backends.sql.Catalog
[token]
driver = keystone.token.backends.sql.Token
[policy]
driver = keystone.policy.backends.sql.Policy
[ec2]
driver = keystone.contrib.ec2.backends.sql.Ec2
[signing]
token_format = PKI
[auth]
methods = password,token
password = keystone.auth.plugins.password.Password
token = keystone.auth.plugins.token.Token

[filter:debug]
paste.filter_factory = keystone.common.wsgi:Debug.factory

[filter:token_auth]
paste.filter_factory = keystone.middleware:TokenAuthMiddleware.factory

[filter:admin_token_auth]
paste.filter_factory = keystone.middleware:AdminTokenAuthMiddleware.factory

#[filter:xml_body]
#paste.filter_factory = keystone.middleware:XmlBodyMiddleware.factory

[filter:json_body]
paste.filter_factory = keystone.middleware:JsonBodyMiddleware.factory

[filter:user_crud_extension]
paste.filter_factory = keystone.contrib.user_crud:CrudExtension.factory

[filter:crud_extension]
paste.filter_factory = keystone.contrib.admin_crud:CrudExtension.factory

[filter:ec2_extension]
paste.filter_factory = keystone.contrib.ec2:Ec2Extension.factory

[filter:s3_extension]
paste.filter_factory = keystone.contrib.s3:S3Extension.factory
[filter:url_normalize]
paste.filter_factory = keystone.middleware:NormalizingFilter.factory

[filter:sizelimit]
paste.filter_factory = keystone.middleware:RequestBodySizeLimiter.factory

[filter:stats_monitoring]
paste.filter_factory = keystone.contrib.stats:StatsMiddleware.factory

[filter:stats_reporting]
paste.filter_factory = keystone.contrib.stats:StatsExtension.factory

[filter:access_log]
paste.filter_factory = keystone.contrib.access:AccessLogMiddleware.factory

[app:public_service]
paste.app_factory = keystone.service:public_app_factory

[app:service_v3]
paste.app_factory = keystone.service:v3_app_factory

[app:admin_service]
paste.app_factory = keystone.service:admin_app_factory

[pipeline:public_api]
pipeline = access_log sizelimit stats_monitoring url_normalize token_auth admin_token_auth xml_body json_body debug ec2_extension user_crud_extension public_service

[pipeline:admin_api]
pipeline = access_log sizelimit stats_monitoring url_normalize token_auth admin_token_auth xml_body json_body debug stats_reporting ec2_extension s3_extension crud_extension admin_service

[app:public_version_service]
paste.app_factory = keystone.service:public_version_app_factory

[app:admin_version_service]
paste.app_factory = keystone.service:admin_version_app_factory

[pipeline:public_version_api]
pipeline = access_log sizelimit stats_monitoring url_normalize xml_body public_version_service

[pipeline:admin_version_api]
pipeline = access_log sizelimit stats_monitoring url_normalize xml_body admin_version_service

[pipeline:api_v3]
pipeline = access_log sizelimit stats_monitoring url_normalize token_auth admin_token_auth xml_body json_body debug stats_reporting ec2_extension s3_extension service_v3

[composite:main]
use = egg:Paste#urlmap
/v2.0 = public_api
/v3 = api_v3
/ = public_version_api

[composite:admin]
use = egg:Paste#urlmap
/v2.0 = admin_api
/v3 = api_v3
/ = admin_version_api
EOP
) >> /etc/keystone/keystone.conf

#make sure keystone owns the files
chown -R keystone:keystone /etc/keystone
#chmod -R 664 /etc/keystone

#create the keys
keystone-manage pki_setup --keystone-user keystone --keystone-group keystone
chown -R keystone:keystone /etc/keystone/ssl
chmod -R o-rwx /etc/keystone/ssl

chown -R keystone:keystone /var/log/keystone

#enable keystone
chkconfig openstack-keystone on
#restart keystone
service openstack-keystone restart
sleep 5
#sync keystone dbchmod 
keystone-manage db_sync
sleep 5


#create default factory creds file
echo "export OS_SERVICE_TOKEN="${ADMIN_TOKEN}"" > /home/transuser/factory_creds 
(
cat <<'EOP'
export OS_USERNAME=admin
export OS_PASSWORD=password
export OS_TENANT_NAME=trans_default
export OS_AUTH_URL=http://localhost:5000/v2.0
export OS_REGION_NAME=TransCirrusCloud
export OS_SERVICE_ENDPOINT=http://localhost:35357/v2.0
EOP
) >> /home/transuser/factory_creds

chmod 0666 /home/transuser/factory_creds
chown transuser:transystem /home/transuser/factory_creds
#source /home/transuser/factory_creds
export OS_SERVICE_TOKEN=${ADMIN_TOKEN}
export OS_USERNAME=admin
export OS_PASSWORD=password
export OS_TENANT_NAME=trans_default
export OS_AUTH_URL=http://localhost:5000/v2.0
export OS_REGION_NAME=TransCirrusCloud
export OS_SERVICE_ENDPOINT=http://localhost:35357/v2.0

# Shortcut function to get a newly generated ID
function get_field() {
    while read data; do
        if [ "$1" -lt 0 ]; then
            field="(\$(NF$1))"
        else
            field="\$$(($1 + 1))"
        fi
        echo "$data" | awk -F'[ \t]*\\|[ \t]*' "{print $field}"
    done
}

#set up keystone
#set up the initial keystone entries just to get things working
CONTROLLER_PUBLIC_ADDRESS=${CONTROLLER_PUBLIC_ADDRESS:-$HOSTNAME}
CONTROLLER_ADMIN_ADDRESS=${CONTROLLER_ADMIN_ADDRESS:-$HOSTNAME}
CONTROLLER_INTERNAL_ADDRESS=${CONTROLLER_INTERNAL_ADDRESS:-$HOSTNAME}

TOOLS_DIR=$(cd $(dirname "$0") && pwd)
KEYSTONE_CONF=${KEYSTONE_CONF:-/etc/keystone/keystone.conf}
if [[ -r "$KEYSTONE_CONF" ]]; then
    EC2RC="$(dirname "$KEYSTONE_CONF")/ec2rc"
elif [[ -r "$TOOLS_DIR/../etc/keystone.conf" ]]; then
    # assume git checkout
    KEYSTONE_CONF="$TOOLS_DIR/../etc/keystone.conf"
    EC2RC="$TOOLS_DIR/../etc/ec2rc"
else
    KEYSTONE_CONF="/etc/keystone/keystone.conf"
    EC2RC="ec2rc"
fi

# Extract some info from Keystone's configuration file
if [[ -r "$KEYSTONE_CONF" ]]; then
    CONFIG_SERVICE_TOKEN=$(sed 's/[[:space:]]//g' $KEYSTONE_CONF | grep ^admin_token= | cut -d'=' -f2)
    CONFIG_ADMIN_PORT=$(sed 's/[[:space:]]//g' $KEYSTONE_CONF | grep ^admin_port= | cut -d'=' -f2)
fi

export ADMIN_TOKEN=${SERVICE_TOKEN:-$CONFIG_SERVICE_TOKEN}
if [[ -z "$ADMIN_TOKEN" ]]; then
    echo "No service token found."
    echo "Set SERVICE_TOKEN manually from keystone.conf admin_token."
    exit 1
fi

export SERVICE_ENDPOINT=${SERVICE_ENDPOINT:-http://$CONTROLLER_PUBLIC_ADDRESS:${CONFIG_ADMIN_PORT:-35357}/v2.0}

#
# Default tenant
#
TRANS_TENANT=$(keystone tenant-create --name=trans_default --description "Default Tenant" | grep " id " | get_field 2)

ADMIN_USER=$(keystone user-create --name=admin --pass=password | grep " id " | get_field 2)

ADMIN_ROLE=$(keystone role-create --name=admin | grep " id " | get_field 2)
MEMBER_ROLE=$(keystone role-create --name=Member | grep " id " | get_field 2)
DEF_MEM_ROLE=$(keystone role-list | grep " _member_ " | get_field 1)

keystone user-role-add --user-id $ADMIN_USER \
                       --role-id $ADMIN_ROLE \
                       --tenant-id $TRANS_TENANT

#
# Service tenant
#
SERVICE_TENANT=$(keystone tenant-create --name=service \
                                               --description "Service Tenant" | grep " id " | get_field 2)

GLANCE_USER=$(keystone user-create --name=glance \
                                          --pass=transcirrus1 \
                                          --tenant-id $SERVICE_TENANT | grep " id " | get_field 2)

keystone user-role-add --user-id $GLANCE_USER \
                       --role-id $ADMIN_ROLE \
                       --tenant-id $SERVICE_TENANT


CINDER_USER=$(keystone user-create --name=cinder \
                                          --pass=transcirrus1 \
                                          --tenant-id $SERVICE_TENANT | grep " id " | get_field 2)

keystone user-role-add --user-id $CINDER_USER \
                       --role-id $ADMIN_ROLE \
                       --tenant-id $SERVICE_TENANT

NEUTRON_USER=$(keystone user-create --name=neutron \
                                          --pass=transcirrus1 \
                                          --tenant-id $SERVICE_TENANT | grep " id " | get_field 2)

keystone user-role-add --user-id $NEUTRON_USER \
                       --role-id $ADMIN_ROLE \
                       --tenant-id $SERVICE_TENANT


NOVA_USER=$(keystone user-create --name=nova \
                                        --pass=transcirrus1 \
                                        --tenant-id $SERVICE_TENANT | grep " id " | get_field 2)

keystone user-role-add --user-id $NOVA_USER \
                       --role-id $ADMIN_ROLE \
                       --tenant-id $SERVICE_TENANT

EC2_USER=$(keystone user-create --name=ec2 \
                                       --pass=transcirrus1 \
                                       --tenant-id $SERVICE_TENANT | grep " id " | get_field 2)

keystone user-role-add --user-id $EC2_USER \
                       --role-id $ADMIN_ROLE \
                       --tenant-id $SERVICE_TENANT

S3_USER=$(keystone user-create --name=s3 \
                                       --pass=transcirrus1 \
                                       --tenant-id $SERVICE_TENANT | grep " id " | get_field 2)

keystone user-role-add --user-id $S3_USER \
                       --role-id $ADMIN_ROLE \
                       --tenant-id $SERVICE_TENANT

SWIFT_USER=$(keystone user-create --name=swift \
                                         --pass=transcirrus1 \
                                         --tenant-id $SERVICE_TENANT | grep " id " | get_field 2)

keystone user-role-add --user-id $SWIFT_USER \
                       --role-id $ADMIN_ROLE \
                       --tenant-id $SERVICE_TENANT

CEILOMETER_USER=$(keystone user-create --name=ceilometer \
                                         --pass=transcirrus1 \
                                         --tenant-id $SERVICE_TENANT | grep " id " | get_field 2)

keystone user-role-add --user-id $CEILOMETER_USER \
                       --role-id $ADMIN_ROLE \
                       --tenant-id $SERVICE_TENANT

HEAT_USER=$(keystone user-create --name=heat \
                                         --pass=transcirrus1 \
                                         --tenant-id $SERVICE_TENANT | grep " id " | get_field 2)

keystone user-role-add --user-id $HEAT_USER \
                       --role-id $ADMIN_ROLE \
                       --tenant-id $SERVICE_TENANT

keystone-manage pki_setup
chown -R keystone:keystone /etc/keystone

#
# Keystone service
#
KEYSTONE_SERVICE=$(keystone service-create --name=keystone \
                        --type=identity \
                        --description="Keystone Identity Service" | grep " id " | get_field 2)
if [[ -z "$DISABLE_ENDPOINTS" ]]; then
    keystone endpoint-create --region TransCirrusCloud --service-id $KEYSTONE_SERVICE \
        --publicurl "http://$CONTROLLER_PUBLIC_ADDRESS:5000/v2.0" \
        --adminurl "http://$CONTROLLER_ADMIN_ADDRESS:35357/v2.0" \
        --internalurl "http://$CONTROLLER_INTERNAL_ADDRESS:5000/v2.0"
fi

#insert the Service tenant and Default admin project into trans_system_settings
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('trans_default_id','"${TRANS_TENANT}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('service_id','"${SERVICE_TENANT}"','"${HOSTNAME}"');"

#add admin and trans_default project to transcirrus db
psql -U postgres -d transcirrus -c "INSERT INTO trans_user_info VALUES (0, 'admin', 'admin', 0, 'TRUE', '"${ADMIN_USER}"', 'trans_default','"${TRANS_TENANT}"', 'admin', NULL);"
psql -U postgres -d transcirrus -c "INSERT INTO projects VALUES ('"${TRANS_TENANT}"', 'trans_default',NULL,NULL,NULL,NULL,'"${HOSTNAME}"','172.24.24.10',NULL,NULL);"

#add the default availability zone
psql -U postgres -d transcirrus -c "INSERT INTO trans_user_info VALUES (0, 'nova', 'The default availability zone.');"

#update the keystone endpoint
psql -U postgres -d transcirrus -c "UPDATE trans_service_settings SET service_id='"${KEYSTONE_SERVICE}"',service_admin_ip='"${CONTROLLER_PUBLIC_ADDRESS}"',service_int_ip='"${CONTROLLER_PUBLIC_ADDRESS}"',service_public_ip='"${CONTROLLER_PUBLIC_ADDRESS}"',service_endpoint_id='"${KEYSTONE_ENDPOINT}"' WHERE service_port=5000;"
psql -U postgres -d transcirrus -c "UPDATE trans_service_settings SET service_id='"${KEYSTONE_SERVICE}"',service_admin_ip='"${CONTROLLER_PUBLIC_ADDRESS}"',service_int_ip='"${CONTROLLER_PUBLIC_ADDRESS}"',service_public_ip='"${CONTROLLER_PUBLIC_ADDRESS}"',service_endpoint_id='"${KEYSTONE_ENDPOINT}"' WHERE service_port=35357;"

#Add in the default system values THESE WILL NEVER BE TOUCHED AGAIN. Used to keep
#system from turning into mush at initial setup.
echo "Adding the default system settings."
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('member_role_id','"${MEMBER_ROLE}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('def_member_role_id','"${DEF_MEM_ROLE}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('admin_token','"${ADMIN_TOKEN}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('mgmt_ip','"${CONTROLLER_PUBLIC_ADDRESS}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('hosted_flavor','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('api_ip','"${CONTROLLER_PUBLIC_ADDRESS}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('admin_role_id','"${ADMIN_ROLE}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('node_type','cc','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('admin_api_ip','"${CONTROLLER_PUBLIC_ADDRESS}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('int_api_ip','"${CONTROLLER_PUBLIC_ADDRESS}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('admin_pass_set','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('first_time_boot','1','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('cloud_name','TransCirrusCloud','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('single_node','1','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('transcirrus_db','172.24.24.10','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('tran_db_user','transuser','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('tran_db_pass','transcirrus1','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('tran_db_name','transcirrus','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('tran_db_port','5432','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('cloud_controller_id','"${NODEID}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('os_db','172.24.24.10','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('vm_ip_min','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('vm_ip_max','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('os_db_user','transuser','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('os_db_pass','transcirrus1','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('os_db_port','5432','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('node_id','"${NODEID}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('hosted_os','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('cloud_controller','"${HOSTNAME}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('uplink_ip','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('node_name','"${HOSTNAME}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('default_pub_net_id','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('default_pub_subnet_id','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('software_version','alpo.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('uplink_subnet','255.255.255.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('uplink_gateway','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('uplink_dns','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('uplink_domain_name','localdomain','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('mgmt_subnet','255.255.255.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('mgmt_dns','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('mgmt_domain_name','localdomain','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('cluster_ip','"${IP}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('physical_node','1','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('spindle_node','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('hybrid_node','0','"${HOSTNAME}"');"
#psql -U postgres -d transcirrus -c "INSERT INTO trans_system_settings VALUES ('host_system','"${HOSTNAME}"','"${HOSTNAME}"');"

#add the system defaults setting. These settings are the exact same but will never be touched again.Used to reset to factory default
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('member_role_id','"${MEMBER_ROLE}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('def_member_role_id','"${DEF_MEM_ROLE}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('admin_token','"${ADMIN_TOKEN}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('mgmt_ip','"${CONTROLLER_PUBLIC_ADDRESS}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('hosted_flavor','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('api_ip','"${CONTROLLER_PUBLIC_ADDRESS}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('admin_role_id','"${ADMIN_ROLE}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('node_type','cc','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('admin_api_ip','"${CONTROLLER_PUBLIC_ADDRESS}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('int_api_ip','"${CONTROLLER_PUBLIC_ADDRESS}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('admin_pass_set','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('first_time_boot','1','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('cloud_name','TransCirrusCloud','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('single_node','1','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('transcirrus_db','172.24.24.10','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('tran_db_user','transuser','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('tran_db_pass','transcirrus1','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('tran_db_name','transcirrus','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('tran_db_port','5432','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('cloud_controller_id','"${NODEID}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('os_db','172.24.24.10','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('vm_ip_min','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('vm_ip_max','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('os_db_user','transuser','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('os_db_pass','transcirrus1','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('os_db_port','5432','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('node_id','"${NODEID}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('hosted_os','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('cloud_controller','"${HOSTNAME}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('uplink_ip','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('node_name','"${HOSTNAME}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('default_pub_net_id','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('default_pub_subnet_id','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('uplink_subnet','255.255.255.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('uplink_gateway','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('uplink_dns','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('uplink_domain_name','localdomain','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('mgmt_subnet','255.255.255.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('mgmt_dns','0.0.0.0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('mgmt_domain_name','localdomain','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('cluster_ip','"${IP}"','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('physical_node','1','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('spindle_node','0','"${HOSTNAME}"');"
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('hybrid_node','0','"${HOSTNAME}"');"
#psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('host_system','"${HOSTNAME}"','"${HOSTNAME}"');"

#insert the default private subnets
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('0',NULL,'c','4','10.0.0.0/24','10.0.0.1','10.0.0.2','10.0.0.254',NULL,NULL,NULL,'false',0,'int-sub-0','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1',NULL,'c','4','10.0.1.0/24','10.0.1.1','10.0.1.2','10.0.1.254',NULL,NULL,NULL,'false',0,'int-sub-1','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('2',NULL,'c','4','10.0.2.0/24','10.0.2.1','10.0.2.2','10.0.2.254',NULL,NULL,NULL,'false',0,'int-sub-2','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('3',NULL,'c','4','10.0.3.0/24','10.0.3.1','10.0.3.2','10.0.3.254',NULL,NULL,NULL,'false',0,'int-sub-3','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('4',NULL,'c','4','10.0.4.0/24','10.0.4.1','10.0.4.2','10.0.4.254',NULL,NULL,NULL,'false',0,'int-sub-4','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('5',NULL,'c','4','10.0.5.0/24','10.0.5.1','10.0.5.2','10.0.5.254',NULL,NULL,NULL,'false',0,'int-sub-5','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('6',NULL,'c','4','10.0.6.0/24','10.0.6.1','10.0.6.2','10.0.6.254',NULL,NULL,NULL,'false',0,'int-sub-6','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('7',NULL,'c','4','10.0.7.0/24','10.0.7.1','10.0.7.2','10.0.7.254',NULL,NULL,NULL,'false',0,'int-sub-7','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('8',NULL,'c','4','10.0.8.0/24','10.0.8.1','10.0.8.2','10.0.8.254',NULL,NULL,NULL,'false',0,'int-sub-8','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('9',NULL,'c','4','10.0.9.0/24','10.0.9.1','10.0.9.2','10.0.9.254',NULL,NULL,NULL,'false',0,'int-sub-9','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('10',NULL,'c','4','10.0.10.0/24','10.0.10.1','10.0.10.2','10.0.10.254',NULL,NULL,NULL,'false',0,'int-sub-10','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('11',NULL,'c','4','10.0.11.0/24','10.0.11.1','10.0.11.2','10.0.11.254',NULL,NULL,NULL,'false',0,'int-sub-11','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('12',NULL,'c','4','10.0.12.0/24','10.0.12.1','10.0.12.2','10.0.12.254',NULL,NULL,NULL,'false',0,'int-sub-12','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('13',NULL,'c','4','10.0.13.0/24','10.0.13.1','10.0.13.2','10.0.13.254',NULL,NULL,NULL,'false',0,'int-sub-13','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('14',NULL,'c','4','10.0.14.0/24','10.0.14.1','10.0.14.2','10.0.14.254',NULL,NULL,NULL,'false',0,'int-sub-14','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('15',NULL,'c','4','10.0.15.0/24','10.0.15.1','10.0.15.2','10.0.15.254',NULL,NULL,NULL,'false',0,'int-sub-15','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('16',NULL,'c','4','10.0.16.0/24','10.0.16.1','10.0.16.2','10.0.16.254',NULL,NULL,NULL,'false',0,'int-sub-16','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('17',NULL,'c','4','10.0.17.0/24','10.0.17.1','10.0.17.2','10.0.17.254',NULL,NULL,NULL,'false',0,'int-sub-17','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('18',NULL,'c','4','10.0.18.0/24','10.0.18.1','10.0.18.2','10.0.18.254',NULL,NULL,NULL,'false',0,'int-sub-18','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('19',NULL,'c','4','10.0.19.0/24','10.0.19.1','10.0.19.2','10.0.19.254',NULL,NULL,NULL,'false',0,'int-sub-19','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('20',NULL,'c','4','10.0.20.0/24','10.0.20.1','10.0.20.2','10.0.20.254',NULL,NULL,NULL,'false',0,'int-sub-20','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('21',NULL,'c','4','10.0.21.0/24','10.0.21.1','10.0.21.2','10.0.21.254',NULL,NULL,NULL,'false',0,'int-sub-21','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('22',NULL,'c','4','10.0.22.0/24','10.0.22.1','10.0.22.2','10.0.22.254',NULL,NULL,NULL,'false',0,'int-sub-22','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('23',NULL,'c','4','10.0.23.0/24','10.0.23.1','10.0.23.2','10.0.23.254',NULL,NULL,NULL,'false',0,'int-sub-23','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('24',NULL,'c','4','10.0.24.0/24','10.0.24.1','10.0.24.2','10.0.24.254',NULL,NULL,NULL,'false',0,'int-sub-24','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('25',NULL,'c','4','10.0.25.0/24','10.0.25.1','10.0.25.2','10.0.25.254',NULL,NULL,NULL,'false',0,'int-sub-25','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('26',NULL,'c','4','10.0.26.0/24','10.0.26.1','10.0.26.2','10.0.26.254',NULL,NULL,NULL,'false',0,'int-sub-26','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('27',NULL,'c','4','10.0.27.0/24','10.0.27.1','10.0.27.2','10.0.27.254',NULL,NULL,NULL,'false',0,'int-sub-27','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('28',NULL,'c','4','10.0.28.0/24','10.0.28.1','10.0.28.2','10.0.28.254',NULL,NULL,NULL,'false',0,'int-sub-28','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('29',NULL,'c','4','10.0.29.0/24','10.0.29.1','10.0.29.2','10.0.29.254',NULL,NULL,NULL,'false',0,'int-sub-29','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('30',NULL,'c','4','10.0.30.0/24','10.0.30.1','10.0.30.2','10.0.30.254',NULL,NULL,NULL,'false',0,'int-sub-30','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('31',NULL,'c','4','10.0.31.0/24','10.0.31.1','10.0.31.2','10.0.31.254',NULL,NULL,NULL,'false',0,'int-sub-31','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('32',NULL,'c','4','10.0.32.0/24','10.0.32.1','10.0.32.2','10.0.32.254',NULL,NULL,NULL,'false',0,'int-sub-32','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('33',NULL,'c','4','10.0.33.0/24','10.0.33.1','10.0.33.2','10.0.33.254',NULL,NULL,NULL,'false',0,'int-sub-33','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('34',NULL,'c','4','10.0.34.0/24','10.0.34.1','10.0.34.2','10.0.34.254',NULL,NULL,NULL,'false',0,'int-sub-34','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('35',NULL,'c','4','10.0.35.0/24','10.0.35.1','10.0.35.2','10.0.35.254',NULL,NULL,NULL,'false',0,'int-sub-35','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('36',NULL,'c','4','10.0.36.0/24','10.0.36.1','10.0.36.2','10.0.36.254',NULL,NULL,NULL,'false',0,'int-sub-36','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('37',NULL,'c','4','10.0.37.0/24','10.0.37.1','10.0.37.2','10.0.37.254',NULL,NULL,NULL,'false',0,'int-sub-37','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('38',NULL,'c','4','10.0.38.0/24','10.0.38.1','10.0.38.2','10.0.38.254',NULL,NULL,NULL,'false',0,'int-sub-38','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('39',NULL,'c','4','10.0.39.0/24','10.0.39.1','10.0.39.2','10.0.39.254',NULL,NULL,NULL,'false',0,'int-sub-39','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('40',NULL,'c','4','10.0.40.0/24','10.0.40.1','10.0.40.2','10.0.40.254',NULL,NULL,NULL,'false',0,'int-sub-40','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('41',NULL,'c','4','10.0.41.0/24','10.0.41.1','10.0.41.2','10.0.41.254',NULL,NULL,NULL,'false',0,'int-sub-41','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('42',NULL,'c','4','10.0.42.0/24','10.0.42.1','10.0.42.2','10.0.42.254',NULL,NULL,NULL,'false',0,'int-sub-42','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('43',NULL,'c','4','10.0.43.0/24','10.0.43.1','10.0.43.2','10.0.43.254',NULL,NULL,NULL,'false',0,'int-sub-43','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('44',NULL,'c','4','10.0.44.0/24','10.0.44.1','10.0.44.2','10.0.44.254',NULL,NULL,NULL,'false',0,'int-sub-44','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('45',NULL,'c','4','10.0.45.0/24','10.0.45.1','10.0.45.2','10.0.45.254',NULL,NULL,NULL,'false',0,'int-sub-45','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('46',NULL,'c','4','10.0.46.0/24','10.0.46.1','10.0.46.2','10.0.46.254',NULL,NULL,NULL,'false',0,'int-sub-46','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('47',NULL,'c','4','10.0.47.0/24','10.0.47.1','10.0.47.2','10.0.47.254',NULL,NULL,NULL,'false',0,'int-sub-47','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('48',NULL,'c','4','10.0.48.0/24','10.0.48.1','10.0.48.2','10.0.48.254',NULL,NULL,NULL,'false',0,'int-sub-48','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('49',NULL,'c','4','10.0.49.0/24','10.0.49.1','10.0.49.2','10.0.49.254',NULL,NULL,NULL,'false',0,'int-sub-49','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('50',NULL,'c','4','10.0.50.0/24','10.0.50.1','10.0.50.2','10.0.50.254',NULL,NULL,NULL,'false',0,'int-sub-50','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('51',NULL,'c','4','10.0.51.0/24','10.0.51.1','10.0.51.2','10.0.51.254',NULL,NULL,NULL,'false',0,'int-sub-51','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('52',NULL,'c','4','10.0.52.0/24','10.0.52.1','10.0.52.2','10.0.52.254',NULL,NULL,NULL,'false',0,'int-sub-52','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('53',NULL,'c','4','10.0.53.0/24','10.0.53.1','10.0.53.2','10.0.53.254',NULL,NULL,NULL,'false',0,'int-sub-53','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('54',NULL,'c','4','10.0.54.0/24','10.0.54.1','10.0.54.2','10.0.54.254',NULL,NULL,NULL,'false',0,'int-sub-54','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('55',NULL,'c','4','10.0.55.0/24','10.0.55.1','10.0.55.2','10.0.55.254',NULL,NULL,NULL,'false',0,'int-sub-55','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('56',NULL,'c','4','10.0.56.0/24','10.0.56.1','10.0.56.2','10.0.56.254',NULL,NULL,NULL,'false',0,'int-sub-56','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('57',NULL,'c','4','10.0.57.0/24','10.0.57.1','10.0.57.2','10.0.57.254',NULL,NULL,NULL,'false',0,'int-sub-57','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('58',NULL,'c','4','10.0.58.0/24','10.0.58.1','10.0.58.2','10.0.58.254',NULL,NULL,NULL,'false',0,'int-sub-58','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('59',NULL,'c','4','10.0.59.0/24','10.0.59.1','10.0.59.2','10.0.59.254',NULL,NULL,NULL,'false',0,'int-sub-59','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('60',NULL,'c','4','10.0.60.0/24','10.0.60.1','10.0.60.2','10.0.60.254',NULL,NULL,NULL,'false',0,'int-sub-60','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('61',NULL,'c','4','10.0.61.0/24','10.0.61.1','10.0.61.2','10.0.61.254',NULL,NULL,NULL,'false',0,'int-sub-61','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('62',NULL,'c','4','10.0.62.0/24','10.0.62.1','10.0.62.2','10.0.62.254',NULL,NULL,NULL,'false',0,'int-sub-62','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('63',NULL,'c','4','10.0.63.0/24','10.0.63.1','10.0.63.2','10.0.63.254',NULL,NULL,NULL,'false',0,'int-sub-63','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('64',NULL,'c','4','10.0.64.0/24','10.0.64.1','10.0.64.2','10.0.64.254',NULL,NULL,NULL,'false',0,'int-sub-64','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('65',NULL,'c','4','10.0.65.0/24','10.0.65.1','10.0.65.2','10.0.65.254',NULL,NULL,NULL,'false',0,'int-sub-65','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('66',NULL,'c','4','10.0.66.0/24','10.0.66.1','10.0.66.2','10.0.66.254',NULL,NULL,NULL,'false',0,'int-sub-66','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('67',NULL,'c','4','10.0.67.0/24','10.0.67.1','10.0.67.2','10.0.67.254',NULL,NULL,NULL,'false',0,'int-sub-67','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('68',NULL,'c','4','10.0.68.0/24','10.0.68.1','10.0.68.2','10.0.68.254',NULL,NULL,NULL,'false',0,'int-sub-68','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('69',NULL,'c','4','10.0.69.0/24','10.0.69.1','10.0.69.2','10.0.69.254',NULL,NULL,NULL,'false',0,'int-sub-69','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('70',NULL,'c','4','10.0.70.0/24','10.0.70.1','10.0.70.2','10.0.70.254',NULL,NULL,NULL,'false',0,'int-sub-70','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('71',NULL,'c','4','10.0.71.0/24','10.0.71.1','10.0.71.2','10.0.71.254',NULL,NULL,NULL,'false',0,'int-sub-71','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('72',NULL,'c','4','10.0.72.0/24','10.0.72.1','10.0.72.2','10.0.72.254',NULL,NULL,NULL,'false',0,'int-sub-72','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('73',NULL,'c','4','10.0.73.0/24','10.0.73.1','10.0.73.2','10.0.73.254',NULL,NULL,NULL,'false',0,'int-sub-73','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('74',NULL,'c','4','10.0.74.0/24','10.0.74.1','10.0.74.2','10.0.74.254',NULL,NULL,NULL,'false',0,'int-sub-74','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('75',NULL,'c','4','10.0.75.0/24','10.0.75.1','10.0.75.2','10.0.75.254',NULL,NULL,NULL,'false',0,'int-sub-75','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('76',NULL,'c','4','10.0.76.0/24','10.0.76.1','10.0.76.2','10.0.76.254',NULL,NULL,NULL,'false',0,'int-sub-76','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('77',NULL,'c','4','10.0.77.0/24','10.0.77.1','10.0.77.2','10.0.77.254',NULL,NULL,NULL,'false',0,'int-sub-77','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('78',NULL,'c','4','10.0.78.0/24','10.0.78.1','10.0.78.2','10.0.78.254',NULL,NULL,NULL,'false',0,'int-sub-78','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('79',NULL,'c','4','10.0.79.0/24','10.0.79.1','10.0.79.2','10.0.79.254',NULL,NULL,NULL,'false',0,'int-sub-79','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('80',NULL,'c','4','10.0.80.0/24','10.0.80.1','10.0.80.2','10.0.80.254',NULL,NULL,NULL,'false',0,'int-sub-80','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('81',NULL,'c','4','10.0.81.0/24','10.0.81.1','10.0.81.2','10.0.81.254',NULL,NULL,NULL,'false',0,'int-sub-81','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('82',NULL,'c','4','10.0.82.0/24','10.0.82.1','10.0.82.2','10.0.82.254',NULL,NULL,NULL,'false',0,'int-sub-82','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('83',NULL,'c','4','10.0.83.0/24','10.0.83.1','10.0.83.2','10.0.83.254',NULL,NULL,NULL,'false',0,'int-sub-83','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('84',NULL,'c','4','10.0.84.0/24','10.0.84.1','10.0.84.2','10.0.84.254',NULL,NULL,NULL,'false',0,'int-sub-84','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('85',NULL,'c','4','10.0.85.0/24','10.0.85.1','10.0.85.2','10.0.85.254',NULL,NULL,NULL,'false',0,'int-sub-85','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('86',NULL,'c','4','10.0.86.0/24','10.0.86.1','10.0.86.2','10.0.86.254',NULL,NULL,NULL,'false',0,'int-sub-86','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('87',NULL,'c','4','10.0.87.0/24','10.0.87.1','10.0.87.2','10.0.87.254',NULL,NULL,NULL,'false',0,'int-sub-87','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('88',NULL,'c','4','10.0.88.0/24','10.0.88.1','10.0.88.2','10.0.88.254',NULL,NULL,NULL,'false',0,'int-sub-88','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('89',NULL,'c','4','10.0.89.0/24','10.0.89.1','10.0.89.2','10.0.89.254',NULL,NULL,NULL,'false',0,'int-sub-89','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('90',NULL,'c','4','10.0.90.0/24','10.0.90.1','10.0.90.2','10.0.90.254',NULL,NULL,NULL,'false',0,'int-sub-90','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('91',NULL,'c','4','10.0.91.0/24','10.0.91.1','10.0.91.2','10.0.91.254',NULL,NULL,NULL,'false',0,'int-sub-91','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('92',NULL,'c','4','10.0.92.0/24','10.0.92.1','10.0.92.2','10.0.92.254',NULL,NULL,NULL,'false',0,'int-sub-92','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('93',NULL,'c','4','10.0.93.0/24','10.0.93.1','10.0.93.2','10.0.93.254',NULL,NULL,NULL,'false',0,'int-sub-93','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('94',NULL,'c','4','10.0.94.0/24','10.0.94.1','10.0.94.2','10.0.94.254',NULL,NULL,NULL,'false',0,'int-sub-94','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('95',NULL,'c','4','10.0.95.0/24','10.0.95.1','10.0.95.2','10.0.95.254',NULL,NULL,NULL,'false',0,'int-sub-95','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('96',NULL,'c','4','10.0.96.0/24','10.0.96.1','10.0.96.2','10.0.96.254',NULL,NULL,NULL,'false',0,'int-sub-96','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('97',NULL,'c','4','10.0.97.0/24','10.0.97.1','10.0.97.2','10.0.97.254',NULL,NULL,NULL,'false',0,'int-sub-97','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('98',NULL,'c','4','10.0.98.0/24','10.0.98.1','10.0.98.2','10.0.98.254',NULL,NULL,NULL,'false',0,'int-sub-98','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('99',NULL,'c','4','10.0.99.0/24','10.0.99.1','10.0.99.2','10.0.99.254',NULL,NULL,NULL,'false',0,'int-sub-99','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('100',NULL,'c','4','10.0.100.0/24','10.0.100.1','10.0.100.2','10.0.100.254',NULL,NULL,NULL,'false',0,'int-sub-100','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('101',NULL,'c','4','10.0.101.0/24','10.0.101.1','10.0.101.2','10.0.101.254',NULL,NULL,NULL,'false',0,'int-sub-101','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('102',NULL,'c','4','10.0.102.0/24','10.0.102.1','10.0.102.2','10.0.102.254',NULL,NULL,NULL,'false',0,'int-sub-102','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('103',NULL,'c','4','10.0.103.0/24','10.0.103.1','10.0.103.2','10.0.103.254',NULL,NULL,NULL,'false',0,'int-sub-103','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('104',NULL,'c','4','10.0.104.0/24','10.0.104.1','10.0.104.2','10.0.104.254',NULL,NULL,NULL,'false',0,'int-sub-104','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('105',NULL,'c','4','10.0.105.0/24','10.0.105.1','10.0.105.2','10.0.105.254',NULL,NULL,NULL,'false',0,'int-sub-105','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('106',NULL,'c','4','10.0.106.0/24','10.0.106.1','10.0.106.2','10.0.106.254',NULL,NULL,NULL,'false',0,'int-sub-106','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('107',NULL,'c','4','10.0.107.0/24','10.0.107.1','10.0.107.2','10.0.107.254',NULL,NULL,NULL,'false',0,'int-sub-107','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('108',NULL,'c','4','10.0.108.0/24','10.0.108.1','10.0.108.2','10.0.108.254',NULL,NULL,NULL,'false',0,'int-sub-108','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('109',NULL,'c','4','10.0.109.0/24','10.0.109.1','10.0.109.2','10.0.109.254',NULL,NULL,NULL,'false',0,'int-sub-109','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('110',NULL,'c','4','10.0.110.0/24','10.0.110.1','10.0.110.2','10.0.110.254',NULL,NULL,NULL,'false',0,'int-sub-110','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('111',NULL,'c','4','10.0.111.0/24','10.0.111.1','10.0.111.2','10.0.111.254',NULL,NULL,NULL,'false',0,'int-sub-111','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('112',NULL,'c','4','10.0.112.0/24','10.0.112.1','10.0.112.2','10.0.112.254',NULL,NULL,NULL,'false',0,'int-sub-112','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('113',NULL,'c','4','10.0.113.0/24','10.0.113.1','10.0.113.2','10.0.113.254',NULL,NULL,NULL,'false',0,'int-sub-113','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('114',NULL,'c','4','10.0.114.0/24','10.0.114.1','10.0.114.2','10.0.114.254',NULL,NULL,NULL,'false',0,'int-sub-114','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('115',NULL,'c','4','10.0.115.0/24','10.0.115.1','10.0.115.2','10.0.115.254',NULL,NULL,NULL,'false',0,'int-sub-115','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('116',NULL,'c','4','10.0.116.0/24','10.0.116.1','10.0.116.2','10.0.116.254',NULL,NULL,NULL,'false',0,'int-sub-116','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('117',NULL,'c','4','10.0.117.0/24','10.0.117.1','10.0.117.2','10.0.117.254',NULL,NULL,NULL,'false',0,'int-sub-117','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('118',NULL,'c','4','10.0.118.0/24','10.0.118.1','10.0.118.2','10.0.118.254',NULL,NULL,NULL,'false',0,'int-sub-118','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('119',NULL,'c','4','10.0.119.0/24','10.0.119.1','10.0.119.2','10.0.119.254',NULL,NULL,NULL,'false',0,'int-sub-119','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('120',NULL,'c','4','10.0.120.0/24','10.0.120.1','10.0.120.2','10.0.120.254',NULL,NULL,NULL,'false',0,'int-sub-120','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('121',NULL,'c','4','10.0.121.0/24','10.0.121.1','10.0.121.2','10.0.121.254',NULL,NULL,NULL,'false',0,'int-sub-121','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('122',NULL,'c','4','10.0.122.0/24','10.0.122.1','10.0.122.2','10.0.122.254',NULL,NULL,NULL,'false',0,'int-sub-122','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('123',NULL,'c','4','10.0.123.0/24','10.0.123.1','10.0.123.2','10.0.123.254',NULL,NULL,NULL,'false',0,'int-sub-123','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('124',NULL,'c','4','10.0.124.0/24','10.0.124.1','10.0.124.2','10.0.124.254',NULL,NULL,NULL,'false',0,'int-sub-124','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('125',NULL,'c','4','10.0.125.0/24','10.0.125.1','10.0.125.2','10.0.125.254',NULL,NULL,NULL,'false',0,'int-sub-125','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('126',NULL,'c','4','10.0.126.0/24','10.0.126.1','10.0.126.2','10.0.126.254',NULL,NULL,NULL,'false',0,'int-sub-126','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('127',NULL,'c','4','10.0.127.0/24','10.0.127.1','10.0.127.2','10.0.127.254',NULL,NULL,NULL,'false',0,'int-sub-127','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('128',NULL,'c','4','10.0.128.0/24','10.0.128.1','10.0.128.2','10.0.128.254',NULL,NULL,NULL,'false',0,'int-sub-128','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('129',NULL,'c','4','10.0.129.0/24','10.0.129.1','10.0.129.2','10.0.129.254',NULL,NULL,NULL,'false',0,'int-sub-129','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('130',NULL,'c','4','10.0.130.0/24','10.0.130.1','10.0.130.2','10.0.130.254',NULL,NULL,NULL,'false',0,'int-sub-130','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('131',NULL,'c','4','10.0.131.0/24','10.0.131.1','10.0.131.2','10.0.131.254',NULL,NULL,NULL,'false',0,'int-sub-131','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('132',NULL,'c','4','10.0.132.0/24','10.0.132.1','10.0.132.2','10.0.132.254',NULL,NULL,NULL,'false',0,'int-sub-132','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('133',NULL,'c','4','10.0.133.0/24','10.0.133.1','10.0.133.2','10.0.133.254',NULL,NULL,NULL,'false',0,'int-sub-133','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('134',NULL,'c','4','10.0.134.0/24','10.0.134.1','10.0.134.2','10.0.134.254',NULL,NULL,NULL,'false',0,'int-sub-134','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('135',NULL,'c','4','10.0.135.0/24','10.0.135.1','10.0.135.2','10.0.135.254',NULL,NULL,NULL,'false',0,'int-sub-135','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('136',NULL,'c','4','10.0.136.0/24','10.0.136.1','10.0.136.2','10.0.136.254',NULL,NULL,NULL,'false',0,'int-sub-136','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('137',NULL,'c','4','10.0.137.0/24','10.0.137.1','10.0.137.2','10.0.137.254',NULL,NULL,NULL,'false',0,'int-sub-137','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('138',NULL,'c','4','10.0.138.0/24','10.0.138.1','10.0.138.2','10.0.138.254',NULL,NULL,NULL,'false',0,'int-sub-138','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('139',NULL,'c','4','10.0.139.0/24','10.0.139.1','10.0.139.2','10.0.139.254',NULL,NULL,NULL,'false',0,'int-sub-139','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('140',NULL,'c','4','10.0.140.0/24','10.0.140.1','10.0.140.2','10.0.140.254',NULL,NULL,NULL,'false',0,'int-sub-140','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('141',NULL,'c','4','10.0.141.0/24','10.0.141.1','10.0.141.2','10.0.141.254',NULL,NULL,NULL,'false',0,'int-sub-141','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('142',NULL,'c','4','10.0.142.0/24','10.0.142.1','10.0.142.2','10.0.142.254',NULL,NULL,NULL,'false',0,'int-sub-142','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('143',NULL,'c','4','10.0.143.0/24','10.0.143.1','10.0.143.2','10.0.143.254',NULL,NULL,NULL,'false',0,'int-sub-143','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('144',NULL,'c','4','10.0.144.0/24','10.0.144.1','10.0.144.2','10.0.144.254',NULL,NULL,NULL,'false',0,'int-sub-144','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('145',NULL,'c','4','10.0.145.0/24','10.0.145.1','10.0.145.2','10.0.145.254',NULL,NULL,NULL,'false',0,'int-sub-145','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('146',NULL,'c','4','10.0.146.0/24','10.0.146.1','10.0.146.2','10.0.146.254',NULL,NULL,NULL,'false',0,'int-sub-146','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('147',NULL,'c','4','10.0.147.0/24','10.0.147.1','10.0.147.2','10.0.147.254',NULL,NULL,NULL,'false',0,'int-sub-147','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('148',NULL,'c','4','10.0.148.0/24','10.0.148.1','10.0.148.2','10.0.148.254',NULL,NULL,NULL,'false',0,'int-sub-148','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('149',NULL,'c','4','10.0.149.0/24','10.0.149.1','10.0.149.2','10.0.149.254',NULL,NULL,NULL,'false',0,'int-sub-149','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('150',NULL,'c','4','10.0.150.0/24','10.0.150.1','10.0.150.2','10.0.150.254',NULL,NULL,NULL,'false',0,'int-sub-150','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('151',NULL,'c','4','10.0.151.0/24','10.0.151.1','10.0.151.2','10.0.151.254',NULL,NULL,NULL,'false',0,'int-sub-151','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('152',NULL,'c','4','10.0.152.0/24','10.0.152.1','10.0.152.2','10.0.152.254',NULL,NULL,NULL,'false',0,'int-sub-152','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('153',NULL,'c','4','10.0.153.0/24','10.0.153.1','10.0.153.2','10.0.153.254',NULL,NULL,NULL,'false',0,'int-sub-153','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('154',NULL,'c','4','10.0.154.0/24','10.0.154.1','10.0.154.2','10.0.154.254',NULL,NULL,NULL,'false',0,'int-sub-154','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('155',NULL,'c','4','10.0.155.0/24','10.0.155.1','10.0.155.2','10.0.155.254',NULL,NULL,NULL,'false',0,'int-sub-155','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('156',NULL,'c','4','10.0.156.0/24','10.0.156.1','10.0.156.2','10.0.156.254',NULL,NULL,NULL,'false',0,'int-sub-156','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('157',NULL,'c','4','10.0.157.0/24','10.0.157.1','10.0.157.2','10.0.157.254',NULL,NULL,NULL,'false',0,'int-sub-157','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('158',NULL,'c','4','10.0.158.0/24','10.0.158.1','10.0.158.2','10.0.158.254',NULL,NULL,NULL,'false',0,'int-sub-158','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('159',NULL,'c','4','10.0.159.0/24','10.0.159.1','10.0.159.2','10.0.159.254',NULL,NULL,NULL,'false',0,'int-sub-159','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('160',NULL,'c','4','10.0.160.0/24','10.0.160.1','10.0.160.2','10.0.160.254',NULL,NULL,NULL,'false',0,'int-sub-160','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('161',NULL,'c','4','10.0.161.0/24','10.0.161.1','10.0.161.2','10.0.161.254',NULL,NULL,NULL,'false',0,'int-sub-161','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('162',NULL,'c','4','10.0.162.0/24','10.0.162.1','10.0.162.2','10.0.162.254',NULL,NULL,NULL,'false',0,'int-sub-162','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('163',NULL,'c','4','10.0.163.0/24','10.0.163.1','10.0.163.2','10.0.163.254',NULL,NULL,NULL,'false',0,'int-sub-163','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('164',NULL,'c','4','10.0.164.0/24','10.0.164.1','10.0.164.2','10.0.164.254',NULL,NULL,NULL,'false',0,'int-sub-164','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('165',NULL,'c','4','10.0.165.0/24','10.0.165.1','10.0.165.2','10.0.165.254',NULL,NULL,NULL,'false',0,'int-sub-165','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('166',NULL,'c','4','10.0.166.0/24','10.0.166.1','10.0.166.2','10.0.166.254',NULL,NULL,NULL,'false',0,'int-sub-166','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('167',NULL,'c','4','10.0.167.0/24','10.0.167.1','10.0.167.2','10.0.167.254',NULL,NULL,NULL,'false',0,'int-sub-167','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('168',NULL,'c','4','10.0.168.0/24','10.0.168.1','10.0.168.2','10.0.168.254',NULL,NULL,NULL,'false',0,'int-sub-168','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('169',NULL,'c','4','10.0.169.0/24','10.0.169.1','10.0.169.2','10.0.169.254',NULL,NULL,NULL,'false',0,'int-sub-169','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('170',NULL,'c','4','10.0.170.0/24','10.0.170.1','10.0.170.2','10.0.170.254',NULL,NULL,NULL,'false',0,'int-sub-170','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('171',NULL,'c','4','10.0.171.0/24','10.0.171.1','10.0.171.2','10.0.171.254',NULL,NULL,NULL,'false',0,'int-sub-171','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('172',NULL,'c','4','10.0.172.0/24','10.0.172.1','10.0.172.2','10.0.172.254',NULL,NULL,NULL,'false',0,'int-sub-172','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('173',NULL,'c','4','10.0.173.0/24','10.0.173.1','10.0.173.2','10.0.173.254',NULL,NULL,NULL,'false',0,'int-sub-173','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('174',NULL,'c','4','10.0.174.0/24','10.0.174.1','10.0.174.2','10.0.174.254',NULL,NULL,NULL,'false',0,'int-sub-174','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('175',NULL,'c','4','10.0.175.0/24','10.0.175.1','10.0.175.2','10.0.175.254',NULL,NULL,NULL,'false',0,'int-sub-175','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('176',NULL,'c','4','10.0.176.0/24','10.0.176.1','10.0.176.2','10.0.176.254',NULL,NULL,NULL,'false',0,'int-sub-176','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('177',NULL,'c','4','10.0.177.0/24','10.0.177.1','10.0.177.2','10.0.177.254',NULL,NULL,NULL,'false',0,'int-sub-177','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('178',NULL,'c','4','10.0.178.0/24','10.0.178.1','10.0.178.2','10.0.178.254',NULL,NULL,NULL,'false',0,'int-sub-178','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('179',NULL,'c','4','10.0.179.0/24','10.0.179.1','10.0.179.2','10.0.179.254',NULL,NULL,NULL,'false',0,'int-sub-179','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('180',NULL,'c','4','10.0.180.0/24','10.0.180.1','10.0.180.2','10.0.180.254',NULL,NULL,NULL,'false',0,'int-sub-180','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('181',NULL,'c','4','10.0.181.0/24','10.0.181.1','10.0.181.2','10.0.181.254',NULL,NULL,NULL,'false',0,'int-sub-181','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('182',NULL,'c','4','10.0.182.0/24','10.0.182.1','10.0.182.2','10.0.182.254',NULL,NULL,NULL,'false',0,'int-sub-182','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('183',NULL,'c','4','10.0.183.0/24','10.0.183.1','10.0.183.2','10.0.183.254',NULL,NULL,NULL,'false',0,'int-sub-183','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('184',NULL,'c','4','10.0.184.0/24','10.0.184.1','10.0.184.2','10.0.184.254',NULL,NULL,NULL,'false',0,'int-sub-184','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('185',NULL,'c','4','10.0.185.0/24','10.0.185.1','10.0.185.2','10.0.185.254',NULL,NULL,NULL,'false',0,'int-sub-185','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('186',NULL,'c','4','10.0.186.0/24','10.0.186.1','10.0.186.2','10.0.186.254',NULL,NULL,NULL,'false',0,'int-sub-186','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('187',NULL,'c','4','10.0.187.0/24','10.0.187.1','10.0.187.2','10.0.187.254',NULL,NULL,NULL,'false',0,'int-sub-187','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('188',NULL,'c','4','10.0.188.0/24','10.0.188.1','10.0.188.2','10.0.188.254',NULL,NULL,NULL,'false',0,'int-sub-188','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('189',NULL,'c','4','10.0.189.0/24','10.0.189.1','10.0.189.2','10.0.189.254',NULL,NULL,NULL,'false',0,'int-sub-189','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('190',NULL,'c','4','10.0.190.0/24','10.0.190.1','10.0.190.2','10.0.190.254',NULL,NULL,NULL,'false',0,'int-sub-190','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('191',NULL,'c','4','10.0.191.0/24','10.0.191.1','10.0.191.2','10.0.191.254',NULL,NULL,NULL,'false',0,'int-sub-191','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('192',NULL,'c','4','10.0.192.0/24','10.0.192.1','10.0.192.2','10.0.192.254',NULL,NULL,NULL,'false',0,'int-sub-192','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('193',NULL,'c','4','10.0.193.0/24','10.0.193.1','10.0.193.2','10.0.193.254',NULL,NULL,NULL,'false',0,'int-sub-193','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('194',NULL,'c','4','10.0.194.0/24','10.0.194.1','10.0.194.2','10.0.194.254',NULL,NULL,NULL,'false',0,'int-sub-194','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('195',NULL,'c','4','10.0.195.0/24','10.0.195.1','10.0.195.2','10.0.195.254',NULL,NULL,NULL,'false',0,'int-sub-195','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('196',NULL,'c','4','10.0.196.0/24','10.0.196.1','10.0.196.2','10.0.196.254',NULL,NULL,NULL,'false',0,'int-sub-196','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('197',NULL,'c','4','10.0.197.0/24','10.0.197.1','10.0.197.2','10.0.197.254',NULL,NULL,NULL,'false',0,'int-sub-197','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('198',NULL,'c','4','10.0.198.0/24','10.0.198.1','10.0.198.2','10.0.198.254',NULL,NULL,NULL,'false',0,'int-sub-198','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('199',NULL,'c','4','10.0.199.0/24','10.0.199.1','10.0.199.2','10.0.199.254',NULL,NULL,NULL,'false',0,'int-sub-199','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('200',NULL,'c','4','10.0.200.0/24','10.0.200.1','10.0.200.2','10.0.200.254',NULL,NULL,NULL,'false',0,'int-sub-200','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('201',NULL,'c','4','10.0.201.0/24','10.0.201.1','10.0.201.2','10.0.201.254',NULL,NULL,NULL,'false',0,'int-sub-201','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('202',NULL,'c','4','10.0.202.0/24','10.0.202.1','10.0.202.2','10.0.202.254',NULL,NULL,NULL,'false',0,'int-sub-202','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('203',NULL,'c','4','10.0.203.0/24','10.0.203.1','10.0.203.2','10.0.203.254',NULL,NULL,NULL,'false',0,'int-sub-203','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('204',NULL,'c','4','10.0.204.0/24','10.0.204.1','10.0.204.2','10.0.204.254',NULL,NULL,NULL,'false',0,'int-sub-204','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('205',NULL,'c','4','10.0.205.0/24','10.0.205.1','10.0.205.2','10.0.205.254',NULL,NULL,NULL,'false',0,'int-sub-205','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('206',NULL,'c','4','10.0.206.0/24','10.0.206.1','10.0.206.2','10.0.206.254',NULL,NULL,NULL,'false',0,'int-sub-206','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('207',NULL,'c','4','10.0.207.0/24','10.0.207.1','10.0.207.2','10.0.207.254',NULL,NULL,NULL,'false',0,'int-sub-207','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('208',NULL,'c','4','10.0.208.0/24','10.0.208.1','10.0.208.2','10.0.208.254',NULL,NULL,NULL,'false',0,'int-sub-208','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('209',NULL,'c','4','10.0.209.0/24','10.0.209.1','10.0.209.2','10.0.209.254',NULL,NULL,NULL,'false',0,'int-sub-209','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('210',NULL,'c','4','10.0.210.0/24','10.0.210.1','10.0.210.2','10.0.210.254',NULL,NULL,NULL,'false',0,'int-sub-210','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('211',NULL,'c','4','10.0.211.0/24','10.0.211.1','10.0.211.2','10.0.211.254',NULL,NULL,NULL,'false',0,'int-sub-211','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('212',NULL,'c','4','10.0.212.0/24','10.0.212.1','10.0.212.2','10.0.212.254',NULL,NULL,NULL,'false',0,'int-sub-212','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('213',NULL,'c','4','10.0.213.0/24','10.0.213.1','10.0.213.2','10.0.213.254',NULL,NULL,NULL,'false',0,'int-sub-213','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('214',NULL,'c','4','10.0.214.0/24','10.0.214.1','10.0.214.2','10.0.214.254',NULL,NULL,NULL,'false',0,'int-sub-214','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('215',NULL,'c','4','10.0.215.0/24','10.0.215.1','10.0.215.2','10.0.215.254',NULL,NULL,NULL,'false',0,'int-sub-215','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('216',NULL,'c','4','10.0.216.0/24','10.0.216.1','10.0.216.2','10.0.216.254',NULL,NULL,NULL,'false',0,'int-sub-216','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('217',NULL,'c','4','10.0.217.0/24','10.0.217.1','10.0.217.2','10.0.217.254',NULL,NULL,NULL,'false',0,'int-sub-217','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('218',NULL,'c','4','10.0.218.0/24','10.0.218.1','10.0.218.2','10.0.218.254',NULL,NULL,NULL,'false',0,'int-sub-218','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('219',NULL,'c','4','10.0.219.0/24','10.0.219.1','10.0.219.2','10.0.219.254',NULL,NULL,NULL,'false',0,'int-sub-219','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('220',NULL,'c','4','10.0.220.0/24','10.0.220.1','10.0.220.2','10.0.220.254',NULL,NULL,NULL,'false',0,'int-sub-220','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('221',NULL,'c','4','10.0.221.0/24','10.0.221.1','10.0.221.2','10.0.221.254',NULL,NULL,NULL,'false',0,'int-sub-221','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('222',NULL,'c','4','10.0.222.0/24','10.0.222.1','10.0.222.2','10.0.222.254',NULL,NULL,NULL,'false',0,'int-sub-222','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('223',NULL,'c','4','10.0.223.0/24','10.0.223.1','10.0.223.2','10.0.223.254',NULL,NULL,NULL,'false',0,'int-sub-223','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('224',NULL,'c','4','10.0.224.0/24','10.0.224.1','10.0.224.2','10.0.224.254',NULL,NULL,NULL,'false',0,'int-sub-224','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('225',NULL,'c','4','10.0.225.0/24','10.0.225.1','10.0.225.2','10.0.225.254',NULL,NULL,NULL,'false',0,'int-sub-225','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('226',NULL,'c','4','10.0.226.0/24','10.0.226.1','10.0.226.2','10.0.226.254',NULL,NULL,NULL,'false',0,'int-sub-226','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('227',NULL,'c','4','10.0.227.0/24','10.0.227.1','10.0.227.2','10.0.227.254',NULL,NULL,NULL,'false',0,'int-sub-227','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('228',NULL,'c','4','10.0.228.0/24','10.0.228.1','10.0.228.2','10.0.228.254',NULL,NULL,NULL,'false',0,'int-sub-228','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('229',NULL,'c','4','10.0.229.0/24','10.0.229.1','10.0.229.2','10.0.229.254',NULL,NULL,NULL,'false',0,'int-sub-229','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('230',NULL,'c','4','10.0.230.0/24','10.0.230.1','10.0.230.2','10.0.230.254',NULL,NULL,NULL,'false',0,'int-sub-230','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('231',NULL,'c','4','10.0.231.0/24','10.0.231.1','10.0.231.2','10.0.231.254',NULL,NULL,NULL,'false',0,'int-sub-231','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('232',NULL,'c','4','10.0.232.0/24','10.0.232.1','10.0.232.2','10.0.232.254',NULL,NULL,NULL,'false',0,'int-sub-232','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('233',NULL,'c','4','10.0.233.0/24','10.0.233.1','10.0.233.2','10.0.233.254',NULL,NULL,NULL,'false',0,'int-sub-233','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('234',NULL,'c','4','10.0.234.0/24','10.0.234.1','10.0.234.2','10.0.234.254',NULL,NULL,NULL,'false',0,'int-sub-234','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('235',NULL,'c','4','10.0.235.0/24','10.0.235.1','10.0.235.2','10.0.235.254',NULL,NULL,NULL,'false',0,'int-sub-235','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('236',NULL,'c','4','10.0.236.0/24','10.0.236.1','10.0.236.2','10.0.236.254',NULL,NULL,NULL,'false',0,'int-sub-236','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('237',NULL,'c','4','10.0.237.0/24','10.0.237.1','10.0.237.2','10.0.237.254',NULL,NULL,NULL,'false',0,'int-sub-237','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('238',NULL,'c','4','10.0.238.0/24','10.0.238.1','10.0.238.2','10.0.238.254',NULL,NULL,NULL,'false',0,'int-sub-238','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('239',NULL,'c','4','10.0.239.0/24','10.0.239.1','10.0.239.2','10.0.239.254',NULL,NULL,NULL,'false',0,'int-sub-239','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('240',NULL,'c','4','10.0.240.0/24','10.0.240.1','10.0.240.2','10.0.240.254',NULL,NULL,NULL,'false',0,'int-sub-240','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('241',NULL,'c','4','10.0.241.0/24','10.0.241.1','10.0.241.2','10.0.241.254',NULL,NULL,NULL,'false',0,'int-sub-241','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('242',NULL,'c','4','10.0.242.0/24','10.0.242.1','10.0.242.2','10.0.242.254',NULL,NULL,NULL,'false',0,'int-sub-242','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('243',NULL,'c','4','10.0.243.0/24','10.0.243.1','10.0.243.2','10.0.243.254',NULL,NULL,NULL,'false',0,'int-sub-243','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('244',NULL,'c','4','10.0.244.0/24','10.0.244.1','10.0.244.2','10.0.244.254',NULL,NULL,NULL,'false',0,'int-sub-244','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('245',NULL,'c','4','10.0.245.0/24','10.0.245.1','10.0.245.2','10.0.245.254',NULL,NULL,NULL,'false',0,'int-sub-245','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('246',NULL,'c','4','10.0.246.0/24','10.0.246.1','10.0.246.2','10.0.246.254',NULL,NULL,NULL,'false',0,'int-sub-246','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('247',NULL,'c','4','10.0.247.0/24','10.0.247.1','10.0.247.2','10.0.247.254',NULL,NULL,NULL,'false',0,'int-sub-247','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('248',NULL,'c','4','10.0.248.0/24','10.0.248.1','10.0.248.2','10.0.248.254',NULL,NULL,NULL,'false',0,'int-sub-248','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('249',NULL,'c','4','10.0.249.0/24','10.0.249.1','10.0.249.2','10.0.249.254',NULL,NULL,NULL,'false',0,'int-sub-249','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('250',NULL,'c','4','10.0.250.0/24','10.0.250.1','10.0.250.2','10.0.250.254',NULL,NULL,NULL,'false',0,'int-sub-250','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('251',NULL,'c','4','10.0.251.0/24','10.0.251.1','10.0.251.2','10.0.251.254',NULL,NULL,NULL,'false',0,'int-sub-251','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('252',NULL,'c','4','10.0.252.0/24','10.0.252.1','10.0.252.2','10.0.252.254',NULL,NULL,NULL,'false',0,'int-sub-252','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('253',NULL,'c','4','10.0.253.0/24','10.0.253.1','10.0.253.2','10.0.253.254',NULL,NULL,NULL,'false',0,'int-sub-253','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('254',NULL,'c','4','10.0.254.0/24','10.0.254.1','10.0.254.2','10.0.254.254',NULL,NULL,NULL,'false',0,'int-sub-254','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('255',NULL,'c','4','10.1.0.0/24','10.1.0.1','10.1.0.2','10.1.0.254',NULL,NULL,NULL,'false',0,'int-sub-255','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('256',NULL,'c','4','10.1.1.0/24','10.1.1.1','10.1.1.2','10.1.1.254',NULL,NULL,NULL,'false',0,'int-sub-256','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('257',NULL,'c','4','10.1.2.0/24','10.1.2.1','10.1.2.2','10.1.2.254',NULL,NULL,NULL,'false',0,'int-sub-257','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('258',NULL,'c','4','10.1.3.0/24','10.1.3.1','10.1.3.2','10.1.3.254',NULL,NULL,NULL,'false',0,'int-sub-258','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('259',NULL,'c','4','10.1.4.0/24','10.1.4.1','10.1.4.2','10.1.4.254',NULL,NULL,NULL,'false',0,'int-sub-259','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('260',NULL,'c','4','10.1.5.0/24','10.1.5.1','10.1.5.2','10.1.5.254',NULL,NULL,NULL,'false',0,'int-sub-260','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('261',NULL,'c','4','10.1.6.0/24','10.1.6.1','10.1.6.2','10.1.6.254',NULL,NULL,NULL,'false',0,'int-sub-261','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('262',NULL,'c','4','10.1.7.0/24','10.1.7.1','10.1.7.2','10.1.7.254',NULL,NULL,NULL,'false',0,'int-sub-262','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('263',NULL,'c','4','10.1.8.0/24','10.1.8.1','10.1.8.2','10.1.8.254',NULL,NULL,NULL,'false',0,'int-sub-263','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('264',NULL,'c','4','10.1.9.0/24','10.1.9.1','10.1.9.2','10.1.9.254',NULL,NULL,NULL,'false',0,'int-sub-264','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('265',NULL,'c','4','10.1.10.0/24','10.1.10.1','10.1.10.2','10.1.10.254',NULL,NULL,NULL,'false',0,'int-sub-265','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('266',NULL,'c','4','10.1.11.0/24','10.1.11.1','10.1.11.2','10.1.11.254',NULL,NULL,NULL,'false',0,'int-sub-266','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('267',NULL,'c','4','10.1.12.0/24','10.1.12.1','10.1.12.2','10.1.12.254',NULL,NULL,NULL,'false',0,'int-sub-267','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('268',NULL,'c','4','10.1.13.0/24','10.1.13.1','10.1.13.2','10.1.13.254',NULL,NULL,NULL,'false',0,'int-sub-268','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('269',NULL,'c','4','10.1.14.0/24','10.1.14.1','10.1.14.2','10.1.14.254',NULL,NULL,NULL,'false',0,'int-sub-269','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('270',NULL,'c','4','10.1.15.0/24','10.1.15.1','10.1.15.2','10.1.15.254',NULL,NULL,NULL,'false',0,'int-sub-270','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('271',NULL,'c','4','10.1.16.0/24','10.1.16.1','10.1.16.2','10.1.16.254',NULL,NULL,NULL,'false',0,'int-sub-271','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('272',NULL,'c','4','10.1.17.0/24','10.1.17.1','10.1.17.2','10.1.17.254',NULL,NULL,NULL,'false',0,'int-sub-272','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('273',NULL,'c','4','10.1.18.0/24','10.1.18.1','10.1.18.2','10.1.18.254',NULL,NULL,NULL,'false',0,'int-sub-273','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('274',NULL,'c','4','10.1.19.0/24','10.1.19.1','10.1.19.2','10.1.19.254',NULL,NULL,NULL,'false',0,'int-sub-274','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('275',NULL,'c','4','10.1.20.0/24','10.1.20.1','10.1.20.2','10.1.20.254',NULL,NULL,NULL,'false',0,'int-sub-275','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('276',NULL,'c','4','10.1.21.0/24','10.1.21.1','10.1.21.2','10.1.21.254',NULL,NULL,NULL,'false',0,'int-sub-276','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('277',NULL,'c','4','10.1.22.0/24','10.1.22.1','10.1.22.2','10.1.22.254',NULL,NULL,NULL,'false',0,'int-sub-277','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('278',NULL,'c','4','10.1.23.0/24','10.1.23.1','10.1.23.2','10.1.23.254',NULL,NULL,NULL,'false',0,'int-sub-278','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('279',NULL,'c','4','10.1.24.0/24','10.1.24.1','10.1.24.2','10.1.24.254',NULL,NULL,NULL,'false',0,'int-sub-279','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('280',NULL,'c','4','10.1.25.0/24','10.1.25.1','10.1.25.2','10.1.25.254',NULL,NULL,NULL,'false',0,'int-sub-280','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('281',NULL,'c','4','10.1.26.0/24','10.1.26.1','10.1.26.2','10.1.26.254',NULL,NULL,NULL,'false',0,'int-sub-281','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('282',NULL,'c','4','10.1.27.0/24','10.1.27.1','10.1.27.2','10.1.27.254',NULL,NULL,NULL,'false',0,'int-sub-282','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('283',NULL,'c','4','10.1.28.0/24','10.1.28.1','10.1.28.2','10.1.28.254',NULL,NULL,NULL,'false',0,'int-sub-283','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('284',NULL,'c','4','10.1.29.0/24','10.1.29.1','10.1.29.2','10.1.29.254',NULL,NULL,NULL,'false',0,'int-sub-284','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('285',NULL,'c','4','10.1.30.0/24','10.1.30.1','10.1.30.2','10.1.30.254',NULL,NULL,NULL,'false',0,'int-sub-285','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('286',NULL,'c','4','10.1.31.0/24','10.1.31.1','10.1.31.2','10.1.31.254',NULL,NULL,NULL,'false',0,'int-sub-286','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('287',NULL,'c','4','10.1.32.0/24','10.1.32.1','10.1.32.2','10.1.32.254',NULL,NULL,NULL,'false',0,'int-sub-287','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('288',NULL,'c','4','10.1.33.0/24','10.1.33.1','10.1.33.2','10.1.33.254',NULL,NULL,NULL,'false',0,'int-sub-288','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('289',NULL,'c','4','10.1.34.0/24','10.1.34.1','10.1.34.2','10.1.34.254',NULL,NULL,NULL,'false',0,'int-sub-289','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('290',NULL,'c','4','10.1.35.0/24','10.1.35.1','10.1.35.2','10.1.35.254',NULL,NULL,NULL,'false',0,'int-sub-290','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('291',NULL,'c','4','10.1.36.0/24','10.1.36.1','10.1.36.2','10.1.36.254',NULL,NULL,NULL,'false',0,'int-sub-291','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('292',NULL,'c','4','10.1.37.0/24','10.1.37.1','10.1.37.2','10.1.37.254',NULL,NULL,NULL,'false',0,'int-sub-292','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('293',NULL,'c','4','10.1.38.0/24','10.1.38.1','10.1.38.2','10.1.38.254',NULL,NULL,NULL,'false',0,'int-sub-293','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('294',NULL,'c','4','10.1.39.0/24','10.1.39.1','10.1.39.2','10.1.39.254',NULL,NULL,NULL,'false',0,'int-sub-294','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('295',NULL,'c','4','10.1.40.0/24','10.1.40.1','10.1.40.2','10.1.40.254',NULL,NULL,NULL,'false',0,'int-sub-295','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('296',NULL,'c','4','10.1.41.0/24','10.1.41.1','10.1.41.2','10.1.41.254',NULL,NULL,NULL,'false',0,'int-sub-296','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('297',NULL,'c','4','10.1.42.0/24','10.1.42.1','10.1.42.2','10.1.42.254',NULL,NULL,NULL,'false',0,'int-sub-297','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('298',NULL,'c','4','10.1.43.0/24','10.1.43.1','10.1.43.2','10.1.43.254',NULL,NULL,NULL,'false',0,'int-sub-298','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('299',NULL,'c','4','10.1.44.0/24','10.1.44.1','10.1.44.2','10.1.44.254',NULL,NULL,NULL,'false',0,'int-sub-299','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('300',NULL,'c','4','10.1.45.0/24','10.1.45.1','10.1.45.2','10.1.45.254',NULL,NULL,NULL,'false',0,'int-sub-300','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('301',NULL,'c','4','10.1.46.0/24','10.1.46.1','10.1.46.2','10.1.46.254',NULL,NULL,NULL,'false',0,'int-sub-301','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('302',NULL,'c','4','10.1.47.0/24','10.1.47.1','10.1.47.2','10.1.47.254',NULL,NULL,NULL,'false',0,'int-sub-302','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('303',NULL,'c','4','10.1.48.0/24','10.1.48.1','10.1.48.2','10.1.48.254',NULL,NULL,NULL,'false',0,'int-sub-303','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('304',NULL,'c','4','10.1.49.0/24','10.1.49.1','10.1.49.2','10.1.49.254',NULL,NULL,NULL,'false',0,'int-sub-304','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('305',NULL,'c','4','10.1.50.0/24','10.1.50.1','10.1.50.2','10.1.50.254',NULL,NULL,NULL,'false',0,'int-sub-305','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('306',NULL,'c','4','10.1.51.0/24','10.1.51.1','10.1.51.2','10.1.51.254',NULL,NULL,NULL,'false',0,'int-sub-306','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('307',NULL,'c','4','10.1.52.0/24','10.1.52.1','10.1.52.2','10.1.52.254',NULL,NULL,NULL,'false',0,'int-sub-307','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('308',NULL,'c','4','10.1.53.0/24','10.1.53.1','10.1.53.2','10.1.53.254',NULL,NULL,NULL,'false',0,'int-sub-308','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('309',NULL,'c','4','10.1.54.0/24','10.1.54.1','10.1.54.2','10.1.54.254',NULL,NULL,NULL,'false',0,'int-sub-309','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('310',NULL,'c','4','10.1.55.0/24','10.1.55.1','10.1.55.2','10.1.55.254',NULL,NULL,NULL,'false',0,'int-sub-310','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('311',NULL,'c','4','10.1.56.0/24','10.1.56.1','10.1.56.2','10.1.56.254',NULL,NULL,NULL,'false',0,'int-sub-311','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('312',NULL,'c','4','10.1.57.0/24','10.1.57.1','10.1.57.2','10.1.57.254',NULL,NULL,NULL,'false',0,'int-sub-312','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('313',NULL,'c','4','10.1.58.0/24','10.1.58.1','10.1.58.2','10.1.58.254',NULL,NULL,NULL,'false',0,'int-sub-313','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('314',NULL,'c','4','10.1.59.0/24','10.1.59.1','10.1.59.2','10.1.59.254',NULL,NULL,NULL,'false',0,'int-sub-314','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('315',NULL,'c','4','10.1.60.0/24','10.1.60.1','10.1.60.2','10.1.60.254',NULL,NULL,NULL,'false',0,'int-sub-315','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('316',NULL,'c','4','10.1.61.0/24','10.1.61.1','10.1.61.2','10.1.61.254',NULL,NULL,NULL,'false',0,'int-sub-316','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('317',NULL,'c','4','10.1.62.0/24','10.1.62.1','10.1.62.2','10.1.62.254',NULL,NULL,NULL,'false',0,'int-sub-317','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('318',NULL,'c','4','10.1.63.0/24','10.1.63.1','10.1.63.2','10.1.63.254',NULL,NULL,NULL,'false',0,'int-sub-318','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('319',NULL,'c','4','10.1.64.0/24','10.1.64.1','10.1.64.2','10.1.64.254',NULL,NULL,NULL,'false',0,'int-sub-319','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('320',NULL,'c','4','10.1.65.0/24','10.1.65.1','10.1.65.2','10.1.65.254',NULL,NULL,NULL,'false',0,'int-sub-320','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('321',NULL,'c','4','10.1.66.0/24','10.1.66.1','10.1.66.2','10.1.66.254',NULL,NULL,NULL,'false',0,'int-sub-321','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('322',NULL,'c','4','10.1.67.0/24','10.1.67.1','10.1.67.2','10.1.67.254',NULL,NULL,NULL,'false',0,'int-sub-322','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('323',NULL,'c','4','10.1.68.0/24','10.1.68.1','10.1.68.2','10.1.68.254',NULL,NULL,NULL,'false',0,'int-sub-323','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('324',NULL,'c','4','10.1.69.0/24','10.1.69.1','10.1.69.2','10.1.69.254',NULL,NULL,NULL,'false',0,'int-sub-324','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('325',NULL,'c','4','10.1.70.0/24','10.1.70.1','10.1.70.2','10.1.70.254',NULL,NULL,NULL,'false',0,'int-sub-325','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('326',NULL,'c','4','10.1.71.0/24','10.1.71.1','10.1.71.2','10.1.71.254',NULL,NULL,NULL,'false',0,'int-sub-326','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('327',NULL,'c','4','10.1.72.0/24','10.1.72.1','10.1.72.2','10.1.72.254',NULL,NULL,NULL,'false',0,'int-sub-327','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('328',NULL,'c','4','10.1.73.0/24','10.1.73.1','10.1.73.2','10.1.73.254',NULL,NULL,NULL,'false',0,'int-sub-328','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('329',NULL,'c','4','10.1.74.0/24','10.1.74.1','10.1.74.2','10.1.74.254',NULL,NULL,NULL,'false',0,'int-sub-329','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('330',NULL,'c','4','10.1.75.0/24','10.1.75.1','10.1.75.2','10.1.75.254',NULL,NULL,NULL,'false',0,'int-sub-330','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('331',NULL,'c','4','10.1.76.0/24','10.1.76.1','10.1.76.2','10.1.76.254',NULL,NULL,NULL,'false',0,'int-sub-331','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('332',NULL,'c','4','10.1.77.0/24','10.1.77.1','10.1.77.2','10.1.77.254',NULL,NULL,NULL,'false',0,'int-sub-332','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('333',NULL,'c','4','10.1.78.0/24','10.1.78.1','10.1.78.2','10.1.78.254',NULL,NULL,NULL,'false',0,'int-sub-333','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('334',NULL,'c','4','10.1.79.0/24','10.1.79.1','10.1.79.2','10.1.79.254',NULL,NULL,NULL,'false',0,'int-sub-334','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('335',NULL,'c','4','10.1.80.0/24','10.1.80.1','10.1.80.2','10.1.80.254',NULL,NULL,NULL,'false',0,'int-sub-335','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('336',NULL,'c','4','10.1.81.0/24','10.1.81.1','10.1.81.2','10.1.81.254',NULL,NULL,NULL,'false',0,'int-sub-336','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('337',NULL,'c','4','10.1.82.0/24','10.1.82.1','10.1.82.2','10.1.82.254',NULL,NULL,NULL,'false',0,'int-sub-337','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('338',NULL,'c','4','10.1.83.0/24','10.1.83.1','10.1.83.2','10.1.83.254',NULL,NULL,NULL,'false',0,'int-sub-338','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('339',NULL,'c','4','10.1.84.0/24','10.1.84.1','10.1.84.2','10.1.84.254',NULL,NULL,NULL,'false',0,'int-sub-339','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('340',NULL,'c','4','10.1.85.0/24','10.1.85.1','10.1.85.2','10.1.85.254',NULL,NULL,NULL,'false',0,'int-sub-340','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('341',NULL,'c','4','10.1.86.0/24','10.1.86.1','10.1.86.2','10.1.86.254',NULL,NULL,NULL,'false',0,'int-sub-341','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('342',NULL,'c','4','10.1.87.0/24','10.1.87.1','10.1.87.2','10.1.87.254',NULL,NULL,NULL,'false',0,'int-sub-342','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('343',NULL,'c','4','10.1.88.0/24','10.1.88.1','10.1.88.2','10.1.88.254',NULL,NULL,NULL,'false',0,'int-sub-343','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('344',NULL,'c','4','10.1.89.0/24','10.1.89.1','10.1.89.2','10.1.89.254',NULL,NULL,NULL,'false',0,'int-sub-344','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('345',NULL,'c','4','10.1.90.0/24','10.1.90.1','10.1.90.2','10.1.90.254',NULL,NULL,NULL,'false',0,'int-sub-345','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('346',NULL,'c','4','10.1.91.0/24','10.1.91.1','10.1.91.2','10.1.91.254',NULL,NULL,NULL,'false',0,'int-sub-346','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('347',NULL,'c','4','10.1.92.0/24','10.1.92.1','10.1.92.2','10.1.92.254',NULL,NULL,NULL,'false',0,'int-sub-347','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('348',NULL,'c','4','10.1.93.0/24','10.1.93.1','10.1.93.2','10.1.93.254',NULL,NULL,NULL,'false',0,'int-sub-348','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('349',NULL,'c','4','10.1.94.0/24','10.1.94.1','10.1.94.2','10.1.94.254',NULL,NULL,NULL,'false',0,'int-sub-349','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('350',NULL,'c','4','10.1.95.0/24','10.1.95.1','10.1.95.2','10.1.95.254',NULL,NULL,NULL,'false',0,'int-sub-350','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('351',NULL,'c','4','10.1.96.0/24','10.1.96.1','10.1.96.2','10.1.96.254',NULL,NULL,NULL,'false',0,'int-sub-351','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('352',NULL,'c','4','10.1.97.0/24','10.1.97.1','10.1.97.2','10.1.97.254',NULL,NULL,NULL,'false',0,'int-sub-352','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('353',NULL,'c','4','10.1.98.0/24','10.1.98.1','10.1.98.2','10.1.98.254',NULL,NULL,NULL,'false',0,'int-sub-353','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('354',NULL,'c','4','10.1.99.0/24','10.1.99.1','10.1.99.2','10.1.99.254',NULL,NULL,NULL,'false',0,'int-sub-354','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('355',NULL,'c','4','10.1.100.0/24','10.1.100.1','10.1.100.2','10.1.100.254',NULL,NULL,NULL,'false',0,'int-sub-355','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('356',NULL,'c','4','10.1.101.0/24','10.1.101.1','10.1.101.2','10.1.101.254',NULL,NULL,NULL,'false',0,'int-sub-356','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('357',NULL,'c','4','10.1.102.0/24','10.1.102.1','10.1.102.2','10.1.102.254',NULL,NULL,NULL,'false',0,'int-sub-357','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('358',NULL,'c','4','10.1.103.0/24','10.1.103.1','10.1.103.2','10.1.103.254',NULL,NULL,NULL,'false',0,'int-sub-358','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('359',NULL,'c','4','10.1.104.0/24','10.1.104.1','10.1.104.2','10.1.104.254',NULL,NULL,NULL,'false',0,'int-sub-359','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('360',NULL,'c','4','10.1.105.0/24','10.1.105.1','10.1.105.2','10.1.105.254',NULL,NULL,NULL,'false',0,'int-sub-360','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('361',NULL,'c','4','10.1.106.0/24','10.1.106.1','10.1.106.2','10.1.106.254',NULL,NULL,NULL,'false',0,'int-sub-361','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('362',NULL,'c','4','10.1.107.0/24','10.1.107.1','10.1.107.2','10.1.107.254',NULL,NULL,NULL,'false',0,'int-sub-362','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('363',NULL,'c','4','10.1.108.0/24','10.1.108.1','10.1.108.2','10.1.108.254',NULL,NULL,NULL,'false',0,'int-sub-363','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('364',NULL,'c','4','10.1.109.0/24','10.1.109.1','10.1.109.2','10.1.109.254',NULL,NULL,NULL,'false',0,'int-sub-364','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('365',NULL,'c','4','10.1.110.0/24','10.1.110.1','10.1.110.2','10.1.110.254',NULL,NULL,NULL,'false',0,'int-sub-365','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('366',NULL,'c','4','10.1.111.0/24','10.1.111.1','10.1.111.2','10.1.111.254',NULL,NULL,NULL,'false',0,'int-sub-366','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('367',NULL,'c','4','10.1.112.0/24','10.1.112.1','10.1.112.2','10.1.112.254',NULL,NULL,NULL,'false',0,'int-sub-367','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('368',NULL,'c','4','10.1.113.0/24','10.1.113.1','10.1.113.2','10.1.113.254',NULL,NULL,NULL,'false',0,'int-sub-368','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('369',NULL,'c','4','10.1.114.0/24','10.1.114.1','10.1.114.2','10.1.114.254',NULL,NULL,NULL,'false',0,'int-sub-369','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('370',NULL,'c','4','10.1.115.0/24','10.1.115.1','10.1.115.2','10.1.115.254',NULL,NULL,NULL,'false',0,'int-sub-370','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('371',NULL,'c','4','10.1.116.0/24','10.1.116.1','10.1.116.2','10.1.116.254',NULL,NULL,NULL,'false',0,'int-sub-371','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('372',NULL,'c','4','10.1.117.0/24','10.1.117.1','10.1.117.2','10.1.117.254',NULL,NULL,NULL,'false',0,'int-sub-372','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('373',NULL,'c','4','10.1.118.0/24','10.1.118.1','10.1.118.2','10.1.118.254',NULL,NULL,NULL,'false',0,'int-sub-373','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('374',NULL,'c','4','10.1.119.0/24','10.1.119.1','10.1.119.2','10.1.119.254',NULL,NULL,NULL,'false',0,'int-sub-374','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('375',NULL,'c','4','10.1.120.0/24','10.1.120.1','10.1.120.2','10.1.120.254',NULL,NULL,NULL,'false',0,'int-sub-375','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('376',NULL,'c','4','10.1.121.0/24','10.1.121.1','10.1.121.2','10.1.121.254',NULL,NULL,NULL,'false',0,'int-sub-376','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('377',NULL,'c','4','10.1.122.0/24','10.1.122.1','10.1.122.2','10.1.122.254',NULL,NULL,NULL,'false',0,'int-sub-377','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('378',NULL,'c','4','10.1.123.0/24','10.1.123.1','10.1.123.2','10.1.123.254',NULL,NULL,NULL,'false',0,'int-sub-378','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('379',NULL,'c','4','10.1.124.0/24','10.1.124.1','10.1.124.2','10.1.124.254',NULL,NULL,NULL,'false',0,'int-sub-379','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('380',NULL,'c','4','10.1.125.0/24','10.1.125.1','10.1.125.2','10.1.125.254',NULL,NULL,NULL,'false',0,'int-sub-380','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('381',NULL,'c','4','10.1.126.0/24','10.1.126.1','10.1.126.2','10.1.126.254',NULL,NULL,NULL,'false',0,'int-sub-381','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('382',NULL,'c','4','10.1.127.0/24','10.1.127.1','10.1.127.2','10.1.127.254',NULL,NULL,NULL,'false',0,'int-sub-382','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('383',NULL,'c','4','10.1.128.0/24','10.1.128.1','10.1.128.2','10.1.128.254',NULL,NULL,NULL,'false',0,'int-sub-383','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('384',NULL,'c','4','10.1.129.0/24','10.1.129.1','10.1.129.2','10.1.129.254',NULL,NULL,NULL,'false',0,'int-sub-384','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('385',NULL,'c','4','10.1.130.0/24','10.1.130.1','10.1.130.2','10.1.130.254',NULL,NULL,NULL,'false',0,'int-sub-385','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('386',NULL,'c','4','10.1.131.0/24','10.1.131.1','10.1.131.2','10.1.131.254',NULL,NULL,NULL,'false',0,'int-sub-386','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('387',NULL,'c','4','10.1.132.0/24','10.1.132.1','10.1.132.2','10.1.132.254',NULL,NULL,NULL,'false',0,'int-sub-387','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('388',NULL,'c','4','10.1.133.0/24','10.1.133.1','10.1.133.2','10.1.133.254',NULL,NULL,NULL,'false',0,'int-sub-388','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('389',NULL,'c','4','10.1.134.0/24','10.1.134.1','10.1.134.2','10.1.134.254',NULL,NULL,NULL,'false',0,'int-sub-389','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('390',NULL,'c','4','10.1.135.0/24','10.1.135.1','10.1.135.2','10.1.135.254',NULL,NULL,NULL,'false',0,'int-sub-390','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('391',NULL,'c','4','10.1.136.0/24','10.1.136.1','10.1.136.2','10.1.136.254',NULL,NULL,NULL,'false',0,'int-sub-391','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('392',NULL,'c','4','10.1.137.0/24','10.1.137.1','10.1.137.2','10.1.137.254',NULL,NULL,NULL,'false',0,'int-sub-392','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('393',NULL,'c','4','10.1.138.0/24','10.1.138.1','10.1.138.2','10.1.138.254',NULL,NULL,NULL,'false',0,'int-sub-393','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('394',NULL,'c','4','10.1.139.0/24','10.1.139.1','10.1.139.2','10.1.139.254',NULL,NULL,NULL,'false',0,'int-sub-394','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('395',NULL,'c','4','10.1.140.0/24','10.1.140.1','10.1.140.2','10.1.140.254',NULL,NULL,NULL,'false',0,'int-sub-395','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('396',NULL,'c','4','10.1.141.0/24','10.1.141.1','10.1.141.2','10.1.141.254',NULL,NULL,NULL,'false',0,'int-sub-396','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('397',NULL,'c','4','10.1.142.0/24','10.1.142.1','10.1.142.2','10.1.142.254',NULL,NULL,NULL,'false',0,'int-sub-397','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('398',NULL,'c','4','10.1.143.0/24','10.1.143.1','10.1.143.2','10.1.143.254',NULL,NULL,NULL,'false',0,'int-sub-398','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('399',NULL,'c','4','10.1.144.0/24','10.1.144.1','10.1.144.2','10.1.144.254',NULL,NULL,NULL,'false',0,'int-sub-399','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('400',NULL,'c','4','10.1.145.0/24','10.1.145.1','10.1.145.2','10.1.145.254',NULL,NULL,NULL,'false',0,'int-sub-400','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('401',NULL,'c','4','10.1.146.0/24','10.1.146.1','10.1.146.2','10.1.146.254',NULL,NULL,NULL,'false',0,'int-sub-401','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('402',NULL,'c','4','10.1.147.0/24','10.1.147.1','10.1.147.2','10.1.147.254',NULL,NULL,NULL,'false',0,'int-sub-402','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('403',NULL,'c','4','10.1.148.0/24','10.1.148.1','10.1.148.2','10.1.148.254',NULL,NULL,NULL,'false',0,'int-sub-403','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('404',NULL,'c','4','10.1.149.0/24','10.1.149.1','10.1.149.2','10.1.149.254',NULL,NULL,NULL,'false',0,'int-sub-404','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('405',NULL,'c','4','10.1.150.0/24','10.1.150.1','10.1.150.2','10.1.150.254',NULL,NULL,NULL,'false',0,'int-sub-405','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('406',NULL,'c','4','10.1.151.0/24','10.1.151.1','10.1.151.2','10.1.151.254',NULL,NULL,NULL,'false',0,'int-sub-406','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('407',NULL,'c','4','10.1.152.0/24','10.1.152.1','10.1.152.2','10.1.152.254',NULL,NULL,NULL,'false',0,'int-sub-407','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('408',NULL,'c','4','10.1.153.0/24','10.1.153.1','10.1.153.2','10.1.153.254',NULL,NULL,NULL,'false',0,'int-sub-408','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('409',NULL,'c','4','10.1.154.0/24','10.1.154.1','10.1.154.2','10.1.154.254',NULL,NULL,NULL,'false',0,'int-sub-409','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('410',NULL,'c','4','10.1.155.0/24','10.1.155.1','10.1.155.2','10.1.155.254',NULL,NULL,NULL,'false',0,'int-sub-410','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('411',NULL,'c','4','10.1.156.0/24','10.1.156.1','10.1.156.2','10.1.156.254',NULL,NULL,NULL,'false',0,'int-sub-411','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('412',NULL,'c','4','10.1.157.0/24','10.1.157.1','10.1.157.2','10.1.157.254',NULL,NULL,NULL,'false',0,'int-sub-412','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('413',NULL,'c','4','10.1.158.0/24','10.1.158.1','10.1.158.2','10.1.158.254',NULL,NULL,NULL,'false',0,'int-sub-413','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('414',NULL,'c','4','10.1.159.0/24','10.1.159.1','10.1.159.2','10.1.159.254',NULL,NULL,NULL,'false',0,'int-sub-414','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('415',NULL,'c','4','10.1.160.0/24','10.1.160.1','10.1.160.2','10.1.160.254',NULL,NULL,NULL,'false',0,'int-sub-415','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('416',NULL,'c','4','10.1.161.0/24','10.1.161.1','10.1.161.2','10.1.161.254',NULL,NULL,NULL,'false',0,'int-sub-416','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('417',NULL,'c','4','10.1.162.0/24','10.1.162.1','10.1.162.2','10.1.162.254',NULL,NULL,NULL,'false',0,'int-sub-417','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('418',NULL,'c','4','10.1.163.0/24','10.1.163.1','10.1.163.2','10.1.163.254',NULL,NULL,NULL,'false',0,'int-sub-418','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('419',NULL,'c','4','10.1.164.0/24','10.1.164.1','10.1.164.2','10.1.164.254',NULL,NULL,NULL,'false',0,'int-sub-419','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('420',NULL,'c','4','10.1.165.0/24','10.1.165.1','10.1.165.2','10.1.165.254',NULL,NULL,NULL,'false',0,'int-sub-420','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('421',NULL,'c','4','10.1.166.0/24','10.1.166.1','10.1.166.2','10.1.166.254',NULL,NULL,NULL,'false',0,'int-sub-421','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('422',NULL,'c','4','10.1.167.0/24','10.1.167.1','10.1.167.2','10.1.167.254',NULL,NULL,NULL,'false',0,'int-sub-422','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('423',NULL,'c','4','10.1.168.0/24','10.1.168.1','10.1.168.2','10.1.168.254',NULL,NULL,NULL,'false',0,'int-sub-423','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('424',NULL,'c','4','10.1.169.0/24','10.1.169.1','10.1.169.2','10.1.169.254',NULL,NULL,NULL,'false',0,'int-sub-424','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('425',NULL,'c','4','10.1.170.0/24','10.1.170.1','10.1.170.2','10.1.170.254',NULL,NULL,NULL,'false',0,'int-sub-425','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('426',NULL,'c','4','10.1.171.0/24','10.1.171.1','10.1.171.2','10.1.171.254',NULL,NULL,NULL,'false',0,'int-sub-426','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('427',NULL,'c','4','10.1.172.0/24','10.1.172.1','10.1.172.2','10.1.172.254',NULL,NULL,NULL,'false',0,'int-sub-427','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('428',NULL,'c','4','10.1.173.0/24','10.1.173.1','10.1.173.2','10.1.173.254',NULL,NULL,NULL,'false',0,'int-sub-428','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('429',NULL,'c','4','10.1.174.0/24','10.1.174.1','10.1.174.2','10.1.174.254',NULL,NULL,NULL,'false',0,'int-sub-429','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('430',NULL,'c','4','10.1.175.0/24','10.1.175.1','10.1.175.2','10.1.175.254',NULL,NULL,NULL,'false',0,'int-sub-430','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('431',NULL,'c','4','10.1.176.0/24','10.1.176.1','10.1.176.2','10.1.176.254',NULL,NULL,NULL,'false',0,'int-sub-431','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('432',NULL,'c','4','10.1.177.0/24','10.1.177.1','10.1.177.2','10.1.177.254',NULL,NULL,NULL,'false',0,'int-sub-432','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('433',NULL,'c','4','10.1.178.0/24','10.1.178.1','10.1.178.2','10.1.178.254',NULL,NULL,NULL,'false',0,'int-sub-433','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('434',NULL,'c','4','10.1.179.0/24','10.1.179.1','10.1.179.2','10.1.179.254',NULL,NULL,NULL,'false',0,'int-sub-434','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('435',NULL,'c','4','10.1.180.0/24','10.1.180.1','10.1.180.2','10.1.180.254',NULL,NULL,NULL,'false',0,'int-sub-435','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('436',NULL,'c','4','10.1.181.0/24','10.1.181.1','10.1.181.2','10.1.181.254',NULL,NULL,NULL,'false',0,'int-sub-436','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('437',NULL,'c','4','10.1.182.0/24','10.1.182.1','10.1.182.2','10.1.182.254',NULL,NULL,NULL,'false',0,'int-sub-437','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('438',NULL,'c','4','10.1.183.0/24','10.1.183.1','10.1.183.2','10.1.183.254',NULL,NULL,NULL,'false',0,'int-sub-438','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('439',NULL,'c','4','10.1.184.0/24','10.1.184.1','10.1.184.2','10.1.184.254',NULL,NULL,NULL,'false',0,'int-sub-439','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('440',NULL,'c','4','10.1.185.0/24','10.1.185.1','10.1.185.2','10.1.185.254',NULL,NULL,NULL,'false',0,'int-sub-440','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('441',NULL,'c','4','10.1.186.0/24','10.1.186.1','10.1.186.2','10.1.186.254',NULL,NULL,NULL,'false',0,'int-sub-441','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('442',NULL,'c','4','10.1.187.0/24','10.1.187.1','10.1.187.2','10.1.187.254',NULL,NULL,NULL,'false',0,'int-sub-442','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('443',NULL,'c','4','10.1.188.0/24','10.1.188.1','10.1.188.2','10.1.188.254',NULL,NULL,NULL,'false',0,'int-sub-443','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('444',NULL,'c','4','10.1.189.0/24','10.1.189.1','10.1.189.2','10.1.189.254',NULL,NULL,NULL,'false',0,'int-sub-444','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('445',NULL,'c','4','10.1.190.0/24','10.1.190.1','10.1.190.2','10.1.190.254',NULL,NULL,NULL,'false',0,'int-sub-445','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('446',NULL,'c','4','10.1.191.0/24','10.1.191.1','10.1.191.2','10.1.191.254',NULL,NULL,NULL,'false',0,'int-sub-446','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('447',NULL,'c','4','10.1.192.0/24','10.1.192.1','10.1.192.2','10.1.192.254',NULL,NULL,NULL,'false',0,'int-sub-447','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('448',NULL,'c','4','10.1.193.0/24','10.1.193.1','10.1.193.2','10.1.193.254',NULL,NULL,NULL,'false',0,'int-sub-448','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('449',NULL,'c','4','10.1.194.0/24','10.1.194.1','10.1.194.2','10.1.194.254',NULL,NULL,NULL,'false',0,'int-sub-449','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('450',NULL,'c','4','10.1.195.0/24','10.1.195.1','10.1.195.2','10.1.195.254',NULL,NULL,NULL,'false',0,'int-sub-450','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('451',NULL,'c','4','10.1.196.0/24','10.1.196.1','10.1.196.2','10.1.196.254',NULL,NULL,NULL,'false',0,'int-sub-451','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('452',NULL,'c','4','10.1.197.0/24','10.1.197.1','10.1.197.2','10.1.197.254',NULL,NULL,NULL,'false',0,'int-sub-452','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('453',NULL,'c','4','10.1.198.0/24','10.1.198.1','10.1.198.2','10.1.198.254',NULL,NULL,NULL,'false',0,'int-sub-453','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('454',NULL,'c','4','10.1.199.0/24','10.1.199.1','10.1.199.2','10.1.199.254',NULL,NULL,NULL,'false',0,'int-sub-454','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('455',NULL,'c','4','10.1.200.0/24','10.1.200.1','10.1.200.2','10.1.200.254',NULL,NULL,NULL,'false',0,'int-sub-455','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('456',NULL,'c','4','10.1.201.0/24','10.1.201.1','10.1.201.2','10.1.201.254',NULL,NULL,NULL,'false',0,'int-sub-456','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('457',NULL,'c','4','10.1.202.0/24','10.1.202.1','10.1.202.2','10.1.202.254',NULL,NULL,NULL,'false',0,'int-sub-457','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('458',NULL,'c','4','10.1.203.0/24','10.1.203.1','10.1.203.2','10.1.203.254',NULL,NULL,NULL,'false',0,'int-sub-458','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('459',NULL,'c','4','10.1.204.0/24','10.1.204.1','10.1.204.2','10.1.204.254',NULL,NULL,NULL,'false',0,'int-sub-459','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('460',NULL,'c','4','10.1.205.0/24','10.1.205.1','10.1.205.2','10.1.205.254',NULL,NULL,NULL,'false',0,'int-sub-460','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('461',NULL,'c','4','10.1.206.0/24','10.1.206.1','10.1.206.2','10.1.206.254',NULL,NULL,NULL,'false',0,'int-sub-461','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('462',NULL,'c','4','10.1.207.0/24','10.1.207.1','10.1.207.2','10.1.207.254',NULL,NULL,NULL,'false',0,'int-sub-462','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('463',NULL,'c','4','10.1.208.0/24','10.1.208.1','10.1.208.2','10.1.208.254',NULL,NULL,NULL,'false',0,'int-sub-463','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('464',NULL,'c','4','10.1.209.0/24','10.1.209.1','10.1.209.2','10.1.209.254',NULL,NULL,NULL,'false',0,'int-sub-464','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('465',NULL,'c','4','10.1.210.0/24','10.1.210.1','10.1.210.2','10.1.210.254',NULL,NULL,NULL,'false',0,'int-sub-465','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('466',NULL,'c','4','10.1.211.0/24','10.1.211.1','10.1.211.2','10.1.211.254',NULL,NULL,NULL,'false',0,'int-sub-466','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('467',NULL,'c','4','10.1.212.0/24','10.1.212.1','10.1.212.2','10.1.212.254',NULL,NULL,NULL,'false',0,'int-sub-467','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('468',NULL,'c','4','10.1.213.0/24','10.1.213.1','10.1.213.2','10.1.213.254',NULL,NULL,NULL,'false',0,'int-sub-468','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('469',NULL,'c','4','10.1.214.0/24','10.1.214.1','10.1.214.2','10.1.214.254',NULL,NULL,NULL,'false',0,'int-sub-469','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('470',NULL,'c','4','10.1.215.0/24','10.1.215.1','10.1.215.2','10.1.215.254',NULL,NULL,NULL,'false',0,'int-sub-470','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('471',NULL,'c','4','10.1.216.0/24','10.1.216.1','10.1.216.2','10.1.216.254',NULL,NULL,NULL,'false',0,'int-sub-471','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('472',NULL,'c','4','10.1.217.0/24','10.1.217.1','10.1.217.2','10.1.217.254',NULL,NULL,NULL,'false',0,'int-sub-472','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('473',NULL,'c','4','10.1.218.0/24','10.1.218.1','10.1.218.2','10.1.218.254',NULL,NULL,NULL,'false',0,'int-sub-473','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('474',NULL,'c','4','10.1.219.0/24','10.1.219.1','10.1.219.2','10.1.219.254',NULL,NULL,NULL,'false',0,'int-sub-474','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('475',NULL,'c','4','10.1.220.0/24','10.1.220.1','10.1.220.2','10.1.220.254',NULL,NULL,NULL,'false',0,'int-sub-475','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('476',NULL,'c','4','10.1.221.0/24','10.1.221.1','10.1.221.2','10.1.221.254',NULL,NULL,NULL,'false',0,'int-sub-476','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('477',NULL,'c','4','10.1.222.0/24','10.1.222.1','10.1.222.2','10.1.222.254',NULL,NULL,NULL,'false',0,'int-sub-477','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('478',NULL,'c','4','10.1.223.0/24','10.1.223.1','10.1.223.2','10.1.223.254',NULL,NULL,NULL,'false',0,'int-sub-478','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('479',NULL,'c','4','10.1.224.0/24','10.1.224.1','10.1.224.2','10.1.224.254',NULL,NULL,NULL,'false',0,'int-sub-479','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('480',NULL,'c','4','10.1.225.0/24','10.1.225.1','10.1.225.2','10.1.225.254',NULL,NULL,NULL,'false',0,'int-sub-480','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('481',NULL,'c','4','10.1.226.0/24','10.1.226.1','10.1.226.2','10.1.226.254',NULL,NULL,NULL,'false',0,'int-sub-481','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('482',NULL,'c','4','10.1.227.0/24','10.1.227.1','10.1.227.2','10.1.227.254',NULL,NULL,NULL,'false',0,'int-sub-482','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('483',NULL,'c','4','10.1.228.0/24','10.1.228.1','10.1.228.2','10.1.228.254',NULL,NULL,NULL,'false',0,'int-sub-483','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('484',NULL,'c','4','10.1.229.0/24','10.1.229.1','10.1.229.2','10.1.229.254',NULL,NULL,NULL,'false',0,'int-sub-484','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('485',NULL,'c','4','10.1.230.0/24','10.1.230.1','10.1.230.2','10.1.230.254',NULL,NULL,NULL,'false',0,'int-sub-485','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('486',NULL,'c','4','10.1.231.0/24','10.1.231.1','10.1.231.2','10.1.231.254',NULL,NULL,NULL,'false',0,'int-sub-486','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('487',NULL,'c','4','10.1.232.0/24','10.1.232.1','10.1.232.2','10.1.232.254',NULL,NULL,NULL,'false',0,'int-sub-487','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('488',NULL,'c','4','10.1.233.0/24','10.1.233.1','10.1.233.2','10.1.233.254',NULL,NULL,NULL,'false',0,'int-sub-488','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('489',NULL,'c','4','10.1.234.0/24','10.1.234.1','10.1.234.2','10.1.234.254',NULL,NULL,NULL,'false',0,'int-sub-489','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('490',NULL,'c','4','10.1.235.0/24','10.1.235.1','10.1.235.2','10.1.235.254',NULL,NULL,NULL,'false',0,'int-sub-490','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('491',NULL,'c','4','10.1.236.0/24','10.1.236.1','10.1.236.2','10.1.236.254',NULL,NULL,NULL,'false',0,'int-sub-491','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('492',NULL,'c','4','10.1.237.0/24','10.1.237.1','10.1.237.2','10.1.237.254',NULL,NULL,NULL,'false',0,'int-sub-492','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('493',NULL,'c','4','10.1.238.0/24','10.1.238.1','10.1.238.2','10.1.238.254',NULL,NULL,NULL,'false',0,'int-sub-493','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('494',NULL,'c','4','10.1.239.0/24','10.1.239.1','10.1.239.2','10.1.239.254',NULL,NULL,NULL,'false',0,'int-sub-494','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('495',NULL,'c','4','10.1.240.0/24','10.1.240.1','10.1.240.2','10.1.240.254',NULL,NULL,NULL,'false',0,'int-sub-495','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('496',NULL,'c','4','10.1.241.0/24','10.1.241.1','10.1.241.2','10.1.241.254',NULL,NULL,NULL,'false',0,'int-sub-496','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('497',NULL,'c','4','10.1.242.0/24','10.1.242.1','10.1.242.2','10.1.242.254',NULL,NULL,NULL,'false',0,'int-sub-497','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('498',NULL,'c','4','10.1.243.0/24','10.1.243.1','10.1.243.2','10.1.243.254',NULL,NULL,NULL,'false',0,'int-sub-498','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('499',NULL,'c','4','10.1.244.0/24','10.1.244.1','10.1.244.2','10.1.244.254',NULL,NULL,NULL,'false',0,'int-sub-499','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('500',NULL,'c','4','10.1.245.0/24','10.1.245.1','10.1.245.2','10.1.245.254',NULL,NULL,NULL,'false',0,'int-sub-500','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('501',NULL,'c','4','10.1.246.0/24','10.1.246.1','10.1.246.2','10.1.246.254',NULL,NULL,NULL,'false',0,'int-sub-501','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('502',NULL,'c','4','10.1.247.0/24','10.1.247.1','10.1.247.2','10.1.247.254',NULL,NULL,NULL,'false',0,'int-sub-502','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('503',NULL,'c','4','10.1.248.0/24','10.1.248.1','10.1.248.2','10.1.248.254',NULL,NULL,NULL,'false',0,'int-sub-503','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('504',NULL,'c','4','10.1.249.0/24','10.1.249.1','10.1.249.2','10.1.249.254',NULL,NULL,NULL,'false',0,'int-sub-504','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('505',NULL,'c','4','10.1.250.0/24','10.1.250.1','10.1.250.2','10.1.250.254',NULL,NULL,NULL,'false',0,'int-sub-505','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('506',NULL,'c','4','10.1.251.0/24','10.1.251.1','10.1.251.2','10.1.251.254',NULL,NULL,NULL,'false',0,'int-sub-506','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('507',NULL,'c','4','10.1.252.0/24','10.1.252.1','10.1.252.2','10.1.252.254',NULL,NULL,NULL,'false',0,'int-sub-507','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('508',NULL,'c','4','10.1.253.0/24','10.1.253.1','10.1.253.2','10.1.253.254',NULL,NULL,NULL,'false',0,'int-sub-508','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('509',NULL,'c','4','10.1.254.0/24','10.1.254.1','10.1.254.2','10.1.254.254',NULL,NULL,NULL,'false',0,'int-sub-509','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('510',NULL,'c','4','10.2.0.0/24','10.2.0.1','10.2.0.2','10.2.0.254',NULL,NULL,NULL,'false',0,'int-sub-510','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('511',NULL,'c','4','10.2.1.0/24','10.2.1.1','10.2.1.2','10.2.1.254',NULL,NULL,NULL,'false',0,'int-sub-511','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('512',NULL,'c','4','10.2.2.0/24','10.2.2.1','10.2.2.2','10.2.2.254',NULL,NULL,NULL,'false',0,'int-sub-512','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('513',NULL,'c','4','10.2.3.0/24','10.2.3.1','10.2.3.2','10.2.3.254',NULL,NULL,NULL,'false',0,'int-sub-513','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('514',NULL,'c','4','10.2.4.0/24','10.2.4.1','10.2.4.2','10.2.4.254',NULL,NULL,NULL,'false',0,'int-sub-514','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('515',NULL,'c','4','10.2.5.0/24','10.2.5.1','10.2.5.2','10.2.5.254',NULL,NULL,NULL,'false',0,'int-sub-515','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('516',NULL,'c','4','10.2.6.0/24','10.2.6.1','10.2.6.2','10.2.6.254',NULL,NULL,NULL,'false',0,'int-sub-516','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('517',NULL,'c','4','10.2.7.0/24','10.2.7.1','10.2.7.2','10.2.7.254',NULL,NULL,NULL,'false',0,'int-sub-517','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('518',NULL,'c','4','10.2.8.0/24','10.2.8.1','10.2.8.2','10.2.8.254',NULL,NULL,NULL,'false',0,'int-sub-518','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('519',NULL,'c','4','10.2.9.0/24','10.2.9.1','10.2.9.2','10.2.9.254',NULL,NULL,NULL,'false',0,'int-sub-519','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('520',NULL,'c','4','10.2.10.0/24','10.2.10.1','10.2.10.2','10.2.10.254',NULL,NULL,NULL,'false',0,'int-sub-520','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('521',NULL,'c','4','10.2.11.0/24','10.2.11.1','10.2.11.2','10.2.11.254',NULL,NULL,NULL,'false',0,'int-sub-521','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('522',NULL,'c','4','10.2.12.0/24','10.2.12.1','10.2.12.2','10.2.12.254',NULL,NULL,NULL,'false',0,'int-sub-522','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('523',NULL,'c','4','10.2.13.0/24','10.2.13.1','10.2.13.2','10.2.13.254',NULL,NULL,NULL,'false',0,'int-sub-523','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('524',NULL,'c','4','10.2.14.0/24','10.2.14.1','10.2.14.2','10.2.14.254',NULL,NULL,NULL,'false',0,'int-sub-524','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('525',NULL,'c','4','10.2.15.0/24','10.2.15.1','10.2.15.2','10.2.15.254',NULL,NULL,NULL,'false',0,'int-sub-525','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('526',NULL,'c','4','10.2.16.0/24','10.2.16.1','10.2.16.2','10.2.16.254',NULL,NULL,NULL,'false',0,'int-sub-526','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('527',NULL,'c','4','10.2.17.0/24','10.2.17.1','10.2.17.2','10.2.17.254',NULL,NULL,NULL,'false',0,'int-sub-527','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('528',NULL,'c','4','10.2.18.0/24','10.2.18.1','10.2.18.2','10.2.18.254',NULL,NULL,NULL,'false',0,'int-sub-528','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('529',NULL,'c','4','10.2.19.0/24','10.2.19.1','10.2.19.2','10.2.19.254',NULL,NULL,NULL,'false',0,'int-sub-529','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('530',NULL,'c','4','10.2.20.0/24','10.2.20.1','10.2.20.2','10.2.20.254',NULL,NULL,NULL,'false',0,'int-sub-530','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('531',NULL,'c','4','10.2.21.0/24','10.2.21.1','10.2.21.2','10.2.21.254',NULL,NULL,NULL,'false',0,'int-sub-531','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('532',NULL,'c','4','10.2.22.0/24','10.2.22.1','10.2.22.2','10.2.22.254',NULL,NULL,NULL,'false',0,'int-sub-532','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('533',NULL,'c','4','10.2.23.0/24','10.2.23.1','10.2.23.2','10.2.23.254',NULL,NULL,NULL,'false',0,'int-sub-533','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('534',NULL,'c','4','10.2.24.0/24','10.2.24.1','10.2.24.2','10.2.24.254',NULL,NULL,NULL,'false',0,'int-sub-534','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('535',NULL,'c','4','10.2.25.0/24','10.2.25.1','10.2.25.2','10.2.25.254',NULL,NULL,NULL,'false',0,'int-sub-535','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('536',NULL,'c','4','10.2.26.0/24','10.2.26.1','10.2.26.2','10.2.26.254',NULL,NULL,NULL,'false',0,'int-sub-536','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('537',NULL,'c','4','10.2.27.0/24','10.2.27.1','10.2.27.2','10.2.27.254',NULL,NULL,NULL,'false',0,'int-sub-537','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('538',NULL,'c','4','10.2.28.0/24','10.2.28.1','10.2.28.2','10.2.28.254',NULL,NULL,NULL,'false',0,'int-sub-538','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('539',NULL,'c','4','10.2.29.0/24','10.2.29.1','10.2.29.2','10.2.29.254',NULL,NULL,NULL,'false',0,'int-sub-539','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('540',NULL,'c','4','10.2.30.0/24','10.2.30.1','10.2.30.2','10.2.30.254',NULL,NULL,NULL,'false',0,'int-sub-540','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('541',NULL,'c','4','10.2.31.0/24','10.2.31.1','10.2.31.2','10.2.31.254',NULL,NULL,NULL,'false',0,'int-sub-541','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('542',NULL,'c','4','10.2.32.0/24','10.2.32.1','10.2.32.2','10.2.32.254',NULL,NULL,NULL,'false',0,'int-sub-542','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('543',NULL,'c','4','10.2.33.0/24','10.2.33.1','10.2.33.2','10.2.33.254',NULL,NULL,NULL,'false',0,'int-sub-543','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('544',NULL,'c','4','10.2.34.0/24','10.2.34.1','10.2.34.2','10.2.34.254',NULL,NULL,NULL,'false',0,'int-sub-544','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('545',NULL,'c','4','10.2.35.0/24','10.2.35.1','10.2.35.2','10.2.35.254',NULL,NULL,NULL,'false',0,'int-sub-545','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('546',NULL,'c','4','10.2.36.0/24','10.2.36.1','10.2.36.2','10.2.36.254',NULL,NULL,NULL,'false',0,'int-sub-546','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('547',NULL,'c','4','10.2.37.0/24','10.2.37.1','10.2.37.2','10.2.37.254',NULL,NULL,NULL,'false',0,'int-sub-547','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('548',NULL,'c','4','10.2.38.0/24','10.2.38.1','10.2.38.2','10.2.38.254',NULL,NULL,NULL,'false',0,'int-sub-548','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('549',NULL,'c','4','10.2.39.0/24','10.2.39.1','10.2.39.2','10.2.39.254',NULL,NULL,NULL,'false',0,'int-sub-549','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('550',NULL,'c','4','10.2.40.0/24','10.2.40.1','10.2.40.2','10.2.40.254',NULL,NULL,NULL,'false',0,'int-sub-550','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('551',NULL,'c','4','10.2.41.0/24','10.2.41.1','10.2.41.2','10.2.41.254',NULL,NULL,NULL,'false',0,'int-sub-551','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('552',NULL,'c','4','10.2.42.0/24','10.2.42.1','10.2.42.2','10.2.42.254',NULL,NULL,NULL,'false',0,'int-sub-552','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('553',NULL,'c','4','10.2.43.0/24','10.2.43.1','10.2.43.2','10.2.43.254',NULL,NULL,NULL,'false',0,'int-sub-553','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('554',NULL,'c','4','10.2.44.0/24','10.2.44.1','10.2.44.2','10.2.44.254',NULL,NULL,NULL,'false',0,'int-sub-554','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('555',NULL,'c','4','10.2.45.0/24','10.2.45.1','10.2.45.2','10.2.45.254',NULL,NULL,NULL,'false',0,'int-sub-555','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('556',NULL,'c','4','10.2.46.0/24','10.2.46.1','10.2.46.2','10.2.46.254',NULL,NULL,NULL,'false',0,'int-sub-556','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('557',NULL,'c','4','10.2.47.0/24','10.2.47.1','10.2.47.2','10.2.47.254',NULL,NULL,NULL,'false',0,'int-sub-557','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('558',NULL,'c','4','10.2.48.0/24','10.2.48.1','10.2.48.2','10.2.48.254',NULL,NULL,NULL,'false',0,'int-sub-558','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('559',NULL,'c','4','10.2.49.0/24','10.2.49.1','10.2.49.2','10.2.49.254',NULL,NULL,NULL,'false',0,'int-sub-559','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('560',NULL,'c','4','10.2.50.0/24','10.2.50.1','10.2.50.2','10.2.50.254',NULL,NULL,NULL,'false',0,'int-sub-560','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('561',NULL,'c','4','10.2.51.0/24','10.2.51.1','10.2.51.2','10.2.51.254',NULL,NULL,NULL,'false',0,'int-sub-561','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('562',NULL,'c','4','10.2.52.0/24','10.2.52.1','10.2.52.2','10.2.52.254',NULL,NULL,NULL,'false',0,'int-sub-562','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('563',NULL,'c','4','10.2.53.0/24','10.2.53.1','10.2.53.2','10.2.53.254',NULL,NULL,NULL,'false',0,'int-sub-563','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('564',NULL,'c','4','10.2.54.0/24','10.2.54.1','10.2.54.2','10.2.54.254',NULL,NULL,NULL,'false',0,'int-sub-564','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('565',NULL,'c','4','10.2.55.0/24','10.2.55.1','10.2.55.2','10.2.55.254',NULL,NULL,NULL,'false',0,'int-sub-565','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('566',NULL,'c','4','10.2.56.0/24','10.2.56.1','10.2.56.2','10.2.56.254',NULL,NULL,NULL,'false',0,'int-sub-566','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('567',NULL,'c','4','10.2.57.0/24','10.2.57.1','10.2.57.2','10.2.57.254',NULL,NULL,NULL,'false',0,'int-sub-567','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('568',NULL,'c','4','10.2.58.0/24','10.2.58.1','10.2.58.2','10.2.58.254',NULL,NULL,NULL,'false',0,'int-sub-568','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('569',NULL,'c','4','10.2.59.0/24','10.2.59.1','10.2.59.2','10.2.59.254',NULL,NULL,NULL,'false',0,'int-sub-569','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('570',NULL,'c','4','10.2.60.0/24','10.2.60.1','10.2.60.2','10.2.60.254',NULL,NULL,NULL,'false',0,'int-sub-570','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('571',NULL,'c','4','10.2.61.0/24','10.2.61.1','10.2.61.2','10.2.61.254',NULL,NULL,NULL,'false',0,'int-sub-571','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('572',NULL,'c','4','10.2.62.0/24','10.2.62.1','10.2.62.2','10.2.62.254',NULL,NULL,NULL,'false',0,'int-sub-572','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('573',NULL,'c','4','10.2.63.0/24','10.2.63.1','10.2.63.2','10.2.63.254',NULL,NULL,NULL,'false',0,'int-sub-573','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('574',NULL,'c','4','10.2.64.0/24','10.2.64.1','10.2.64.2','10.2.64.254',NULL,NULL,NULL,'false',0,'int-sub-574','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('575',NULL,'c','4','10.2.65.0/24','10.2.65.1','10.2.65.2','10.2.65.254',NULL,NULL,NULL,'false',0,'int-sub-575','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('576',NULL,'c','4','10.2.66.0/24','10.2.66.1','10.2.66.2','10.2.66.254',NULL,NULL,NULL,'false',0,'int-sub-576','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('577',NULL,'c','4','10.2.67.0/24','10.2.67.1','10.2.67.2','10.2.67.254',NULL,NULL,NULL,'false',0,'int-sub-577','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('578',NULL,'c','4','10.2.68.0/24','10.2.68.1','10.2.68.2','10.2.68.254',NULL,NULL,NULL,'false',0,'int-sub-578','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('579',NULL,'c','4','10.2.69.0/24','10.2.69.1','10.2.69.2','10.2.69.254',NULL,NULL,NULL,'false',0,'int-sub-579','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('580',NULL,'c','4','10.2.70.0/24','10.2.70.1','10.2.70.2','10.2.70.254',NULL,NULL,NULL,'false',0,'int-sub-580','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('581',NULL,'c','4','10.2.71.0/24','10.2.71.1','10.2.71.2','10.2.71.254',NULL,NULL,NULL,'false',0,'int-sub-581','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('582',NULL,'c','4','10.2.72.0/24','10.2.72.1','10.2.72.2','10.2.72.254',NULL,NULL,NULL,'false',0,'int-sub-582','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('583',NULL,'c','4','10.2.73.0/24','10.2.73.1','10.2.73.2','10.2.73.254',NULL,NULL,NULL,'false',0,'int-sub-583','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('584',NULL,'c','4','10.2.74.0/24','10.2.74.1','10.2.74.2','10.2.74.254',NULL,NULL,NULL,'false',0,'int-sub-584','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('585',NULL,'c','4','10.2.75.0/24','10.2.75.1','10.2.75.2','10.2.75.254',NULL,NULL,NULL,'false',0,'int-sub-585','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('586',NULL,'c','4','10.2.76.0/24','10.2.76.1','10.2.76.2','10.2.76.254',NULL,NULL,NULL,'false',0,'int-sub-586','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('587',NULL,'c','4','10.2.77.0/24','10.2.77.1','10.2.77.2','10.2.77.254',NULL,NULL,NULL,'false',0,'int-sub-587','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('588',NULL,'c','4','10.2.78.0/24','10.2.78.1','10.2.78.2','10.2.78.254',NULL,NULL,NULL,'false',0,'int-sub-588','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('589',NULL,'c','4','10.2.79.0/24','10.2.79.1','10.2.79.2','10.2.79.254',NULL,NULL,NULL,'false',0,'int-sub-589','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('590',NULL,'c','4','10.2.80.0/24','10.2.80.1','10.2.80.2','10.2.80.254',NULL,NULL,NULL,'false',0,'int-sub-590','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('591',NULL,'c','4','10.2.81.0/24','10.2.81.1','10.2.81.2','10.2.81.254',NULL,NULL,NULL,'false',0,'int-sub-591','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('592',NULL,'c','4','10.2.82.0/24','10.2.82.1','10.2.82.2','10.2.82.254',NULL,NULL,NULL,'false',0,'int-sub-592','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('593',NULL,'c','4','10.2.83.0/24','10.2.83.1','10.2.83.2','10.2.83.254',NULL,NULL,NULL,'false',0,'int-sub-593','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('594',NULL,'c','4','10.2.84.0/24','10.2.84.1','10.2.84.2','10.2.84.254',NULL,NULL,NULL,'false',0,'int-sub-594','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('595',NULL,'c','4','10.2.85.0/24','10.2.85.1','10.2.85.2','10.2.85.254',NULL,NULL,NULL,'false',0,'int-sub-595','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('596',NULL,'c','4','10.2.86.0/24','10.2.86.1','10.2.86.2','10.2.86.254',NULL,NULL,NULL,'false',0,'int-sub-596','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('597',NULL,'c','4','10.2.87.0/24','10.2.87.1','10.2.87.2','10.2.87.254',NULL,NULL,NULL,'false',0,'int-sub-597','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('598',NULL,'c','4','10.2.88.0/24','10.2.88.1','10.2.88.2','10.2.88.254',NULL,NULL,NULL,'false',0,'int-sub-598','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('599',NULL,'c','4','10.2.89.0/24','10.2.89.1','10.2.89.2','10.2.89.254',NULL,NULL,NULL,'false',0,'int-sub-599','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('600',NULL,'c','4','10.2.90.0/24','10.2.90.1','10.2.90.2','10.2.90.254',NULL,NULL,NULL,'false',0,'int-sub-600','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('601',NULL,'c','4','10.2.91.0/24','10.2.91.1','10.2.91.2','10.2.91.254',NULL,NULL,NULL,'false',0,'int-sub-601','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('602',NULL,'c','4','10.2.92.0/24','10.2.92.1','10.2.92.2','10.2.92.254',NULL,NULL,NULL,'false',0,'int-sub-602','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('603',NULL,'c','4','10.2.93.0/24','10.2.93.1','10.2.93.2','10.2.93.254',NULL,NULL,NULL,'false',0,'int-sub-603','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('604',NULL,'c','4','10.2.94.0/24','10.2.94.1','10.2.94.2','10.2.94.254',NULL,NULL,NULL,'false',0,'int-sub-604','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('605',NULL,'c','4','10.2.95.0/24','10.2.95.1','10.2.95.2','10.2.95.254',NULL,NULL,NULL,'false',0,'int-sub-605','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('606',NULL,'c','4','10.2.96.0/24','10.2.96.1','10.2.96.2','10.2.96.254',NULL,NULL,NULL,'false',0,'int-sub-606','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('607',NULL,'c','4','10.2.97.0/24','10.2.97.1','10.2.97.2','10.2.97.254',NULL,NULL,NULL,'false',0,'int-sub-607','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('608',NULL,'c','4','10.2.98.0/24','10.2.98.1','10.2.98.2','10.2.98.254',NULL,NULL,NULL,'false',0,'int-sub-608','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('609',NULL,'c','4','10.2.99.0/24','10.2.99.1','10.2.99.2','10.2.99.254',NULL,NULL,NULL,'false',0,'int-sub-609','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('610',NULL,'c','4','10.2.100.0/24','10.2.100.1','10.2.100.2','10.2.100.254',NULL,NULL,NULL,'false',0,'int-sub-610','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('611',NULL,'c','4','10.2.101.0/24','10.2.101.1','10.2.101.2','10.2.101.254',NULL,NULL,NULL,'false',0,'int-sub-611','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('612',NULL,'c','4','10.2.102.0/24','10.2.102.1','10.2.102.2','10.2.102.254',NULL,NULL,NULL,'false',0,'int-sub-612','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('613',NULL,'c','4','10.2.103.0/24','10.2.103.1','10.2.103.2','10.2.103.254',NULL,NULL,NULL,'false',0,'int-sub-613','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('614',NULL,'c','4','10.2.104.0/24','10.2.104.1','10.2.104.2','10.2.104.254',NULL,NULL,NULL,'false',0,'int-sub-614','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('615',NULL,'c','4','10.2.105.0/24','10.2.105.1','10.2.105.2','10.2.105.254',NULL,NULL,NULL,'false',0,'int-sub-615','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('616',NULL,'c','4','10.2.106.0/24','10.2.106.1','10.2.106.2','10.2.106.254',NULL,NULL,NULL,'false',0,'int-sub-616','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('617',NULL,'c','4','10.2.107.0/24','10.2.107.1','10.2.107.2','10.2.107.254',NULL,NULL,NULL,'false',0,'int-sub-617','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('618',NULL,'c','4','10.2.108.0/24','10.2.108.1','10.2.108.2','10.2.108.254',NULL,NULL,NULL,'false',0,'int-sub-618','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('619',NULL,'c','4','10.2.109.0/24','10.2.109.1','10.2.109.2','10.2.109.254',NULL,NULL,NULL,'false',0,'int-sub-619','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('620',NULL,'c','4','10.2.110.0/24','10.2.110.1','10.2.110.2','10.2.110.254',NULL,NULL,NULL,'false',0,'int-sub-620','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('621',NULL,'c','4','10.2.111.0/24','10.2.111.1','10.2.111.2','10.2.111.254',NULL,NULL,NULL,'false',0,'int-sub-621','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('622',NULL,'c','4','10.2.112.0/24','10.2.112.1','10.2.112.2','10.2.112.254',NULL,NULL,NULL,'false',0,'int-sub-622','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('623',NULL,'c','4','10.2.113.0/24','10.2.113.1','10.2.113.2','10.2.113.254',NULL,NULL,NULL,'false',0,'int-sub-623','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('624',NULL,'c','4','10.2.114.0/24','10.2.114.1','10.2.114.2','10.2.114.254',NULL,NULL,NULL,'false',0,'int-sub-624','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('625',NULL,'c','4','10.2.115.0/24','10.2.115.1','10.2.115.2','10.2.115.254',NULL,NULL,NULL,'false',0,'int-sub-625','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('626',NULL,'c','4','10.2.116.0/24','10.2.116.1','10.2.116.2','10.2.116.254',NULL,NULL,NULL,'false',0,'int-sub-626','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('627',NULL,'c','4','10.2.117.0/24','10.2.117.1','10.2.117.2','10.2.117.254',NULL,NULL,NULL,'false',0,'int-sub-627','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('628',NULL,'c','4','10.2.118.0/24','10.2.118.1','10.2.118.2','10.2.118.254',NULL,NULL,NULL,'false',0,'int-sub-628','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('629',NULL,'c','4','10.2.119.0/24','10.2.119.1','10.2.119.2','10.2.119.254',NULL,NULL,NULL,'false',0,'int-sub-629','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('630',NULL,'c','4','10.2.120.0/24','10.2.120.1','10.2.120.2','10.2.120.254',NULL,NULL,NULL,'false',0,'int-sub-630','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('631',NULL,'c','4','10.2.121.0/24','10.2.121.1','10.2.121.2','10.2.121.254',NULL,NULL,NULL,'false',0,'int-sub-631','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('632',NULL,'c','4','10.2.122.0/24','10.2.122.1','10.2.122.2','10.2.122.254',NULL,NULL,NULL,'false',0,'int-sub-632','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('633',NULL,'c','4','10.2.123.0/24','10.2.123.1','10.2.123.2','10.2.123.254',NULL,NULL,NULL,'false',0,'int-sub-633','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('634',NULL,'c','4','10.2.124.0/24','10.2.124.1','10.2.124.2','10.2.124.254',NULL,NULL,NULL,'false',0,'int-sub-634','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('635',NULL,'c','4','10.2.125.0/24','10.2.125.1','10.2.125.2','10.2.125.254',NULL,NULL,NULL,'false',0,'int-sub-635','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('636',NULL,'c','4','10.2.126.0/24','10.2.126.1','10.2.126.2','10.2.126.254',NULL,NULL,NULL,'false',0,'int-sub-636','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('637',NULL,'c','4','10.2.127.0/24','10.2.127.1','10.2.127.2','10.2.127.254',NULL,NULL,NULL,'false',0,'int-sub-637','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('638',NULL,'c','4','10.2.128.0/24','10.2.128.1','10.2.128.2','10.2.128.254',NULL,NULL,NULL,'false',0,'int-sub-638','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('639',NULL,'c','4','10.2.129.0/24','10.2.129.1','10.2.129.2','10.2.129.254',NULL,NULL,NULL,'false',0,'int-sub-639','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('640',NULL,'c','4','10.2.130.0/24','10.2.130.1','10.2.130.2','10.2.130.254',NULL,NULL,NULL,'false',0,'int-sub-640','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('641',NULL,'c','4','10.2.131.0/24','10.2.131.1','10.2.131.2','10.2.131.254',NULL,NULL,NULL,'false',0,'int-sub-641','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('642',NULL,'c','4','10.2.132.0/24','10.2.132.1','10.2.132.2','10.2.132.254',NULL,NULL,NULL,'false',0,'int-sub-642','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('643',NULL,'c','4','10.2.133.0/24','10.2.133.1','10.2.133.2','10.2.133.254',NULL,NULL,NULL,'false',0,'int-sub-643','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('644',NULL,'c','4','10.2.134.0/24','10.2.134.1','10.2.134.2','10.2.134.254',NULL,NULL,NULL,'false',0,'int-sub-644','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('645',NULL,'c','4','10.2.135.0/24','10.2.135.1','10.2.135.2','10.2.135.254',NULL,NULL,NULL,'false',0,'int-sub-645','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('646',NULL,'c','4','10.2.136.0/24','10.2.136.1','10.2.136.2','10.2.136.254',NULL,NULL,NULL,'false',0,'int-sub-646','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('647',NULL,'c','4','10.2.137.0/24','10.2.137.1','10.2.137.2','10.2.137.254',NULL,NULL,NULL,'false',0,'int-sub-647','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('648',NULL,'c','4','10.2.138.0/24','10.2.138.1','10.2.138.2','10.2.138.254',NULL,NULL,NULL,'false',0,'int-sub-648','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('649',NULL,'c','4','10.2.139.0/24','10.2.139.1','10.2.139.2','10.2.139.254',NULL,NULL,NULL,'false',0,'int-sub-649','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('650',NULL,'c','4','10.2.140.0/24','10.2.140.1','10.2.140.2','10.2.140.254',NULL,NULL,NULL,'false',0,'int-sub-650','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('651',NULL,'c','4','10.2.141.0/24','10.2.141.1','10.2.141.2','10.2.141.254',NULL,NULL,NULL,'false',0,'int-sub-651','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('652',NULL,'c','4','10.2.142.0/24','10.2.142.1','10.2.142.2','10.2.142.254',NULL,NULL,NULL,'false',0,'int-sub-652','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('653',NULL,'c','4','10.2.143.0/24','10.2.143.1','10.2.143.2','10.2.143.254',NULL,NULL,NULL,'false',0,'int-sub-653','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('654',NULL,'c','4','10.2.144.0/24','10.2.144.1','10.2.144.2','10.2.144.254',NULL,NULL,NULL,'false',0,'int-sub-654','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('655',NULL,'c','4','10.2.145.0/24','10.2.145.1','10.2.145.2','10.2.145.254',NULL,NULL,NULL,'false',0,'int-sub-655','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('656',NULL,'c','4','10.2.146.0/24','10.2.146.1','10.2.146.2','10.2.146.254',NULL,NULL,NULL,'false',0,'int-sub-656','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('657',NULL,'c','4','10.2.147.0/24','10.2.147.1','10.2.147.2','10.2.147.254',NULL,NULL,NULL,'false',0,'int-sub-657','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('658',NULL,'c','4','10.2.148.0/24','10.2.148.1','10.2.148.2','10.2.148.254',NULL,NULL,NULL,'false',0,'int-sub-658','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('659',NULL,'c','4','10.2.149.0/24','10.2.149.1','10.2.149.2','10.2.149.254',NULL,NULL,NULL,'false',0,'int-sub-659','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('660',NULL,'c','4','10.2.150.0/24','10.2.150.1','10.2.150.2','10.2.150.254',NULL,NULL,NULL,'false',0,'int-sub-660','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('661',NULL,'c','4','10.2.151.0/24','10.2.151.1','10.2.151.2','10.2.151.254',NULL,NULL,NULL,'false',0,'int-sub-661','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('662',NULL,'c','4','10.2.152.0/24','10.2.152.1','10.2.152.2','10.2.152.254',NULL,NULL,NULL,'false',0,'int-sub-662','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('663',NULL,'c','4','10.2.153.0/24','10.2.153.1','10.2.153.2','10.2.153.254',NULL,NULL,NULL,'false',0,'int-sub-663','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('664',NULL,'c','4','10.2.154.0/24','10.2.154.1','10.2.154.2','10.2.154.254',NULL,NULL,NULL,'false',0,'int-sub-664','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('665',NULL,'c','4','10.2.155.0/24','10.2.155.1','10.2.155.2','10.2.155.254',NULL,NULL,NULL,'false',0,'int-sub-665','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('666',NULL,'c','4','10.2.156.0/24','10.2.156.1','10.2.156.2','10.2.156.254',NULL,NULL,NULL,'false',0,'int-sub-666','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('667',NULL,'c','4','10.2.157.0/24','10.2.157.1','10.2.157.2','10.2.157.254',NULL,NULL,NULL,'false',0,'int-sub-667','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('668',NULL,'c','4','10.2.158.0/24','10.2.158.1','10.2.158.2','10.2.158.254',NULL,NULL,NULL,'false',0,'int-sub-668','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('669',NULL,'c','4','10.2.159.0/24','10.2.159.1','10.2.159.2','10.2.159.254',NULL,NULL,NULL,'false',0,'int-sub-669','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('670',NULL,'c','4','10.2.160.0/24','10.2.160.1','10.2.160.2','10.2.160.254',NULL,NULL,NULL,'false',0,'int-sub-670','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('671',NULL,'c','4','10.2.161.0/24','10.2.161.1','10.2.161.2','10.2.161.254',NULL,NULL,NULL,'false',0,'int-sub-671','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('672',NULL,'c','4','10.2.162.0/24','10.2.162.1','10.2.162.2','10.2.162.254',NULL,NULL,NULL,'false',0,'int-sub-672','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('673',NULL,'c','4','10.2.163.0/24','10.2.163.1','10.2.163.2','10.2.163.254',NULL,NULL,NULL,'false',0,'int-sub-673','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('674',NULL,'c','4','10.2.164.0/24','10.2.164.1','10.2.164.2','10.2.164.254',NULL,NULL,NULL,'false',0,'int-sub-674','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('675',NULL,'c','4','10.2.165.0/24','10.2.165.1','10.2.165.2','10.2.165.254',NULL,NULL,NULL,'false',0,'int-sub-675','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('676',NULL,'c','4','10.2.166.0/24','10.2.166.1','10.2.166.2','10.2.166.254',NULL,NULL,NULL,'false',0,'int-sub-676','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('677',NULL,'c','4','10.2.167.0/24','10.2.167.1','10.2.167.2','10.2.167.254',NULL,NULL,NULL,'false',0,'int-sub-677','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('678',NULL,'c','4','10.2.168.0/24','10.2.168.1','10.2.168.2','10.2.168.254',NULL,NULL,NULL,'false',0,'int-sub-678','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('679',NULL,'c','4','10.2.169.0/24','10.2.169.1','10.2.169.2','10.2.169.254',NULL,NULL,NULL,'false',0,'int-sub-679','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('680',NULL,'c','4','10.2.170.0/24','10.2.170.1','10.2.170.2','10.2.170.254',NULL,NULL,NULL,'false',0,'int-sub-680','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('681',NULL,'c','4','10.2.171.0/24','10.2.171.1','10.2.171.2','10.2.171.254',NULL,NULL,NULL,'false',0,'int-sub-681','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('682',NULL,'c','4','10.2.172.0/24','10.2.172.1','10.2.172.2','10.2.172.254',NULL,NULL,NULL,'false',0,'int-sub-682','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('683',NULL,'c','4','10.2.173.0/24','10.2.173.1','10.2.173.2','10.2.173.254',NULL,NULL,NULL,'false',0,'int-sub-683','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('684',NULL,'c','4','10.2.174.0/24','10.2.174.1','10.2.174.2','10.2.174.254',NULL,NULL,NULL,'false',0,'int-sub-684','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('685',NULL,'c','4','10.2.175.0/24','10.2.175.1','10.2.175.2','10.2.175.254',NULL,NULL,NULL,'false',0,'int-sub-685','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('686',NULL,'c','4','10.2.176.0/24','10.2.176.1','10.2.176.2','10.2.176.254',NULL,NULL,NULL,'false',0,'int-sub-686','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('687',NULL,'c','4','10.2.177.0/24','10.2.177.1','10.2.177.2','10.2.177.254',NULL,NULL,NULL,'false',0,'int-sub-687','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('688',NULL,'c','4','10.2.178.0/24','10.2.178.1','10.2.178.2','10.2.178.254',NULL,NULL,NULL,'false',0,'int-sub-688','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('689',NULL,'c','4','10.2.179.0/24','10.2.179.1','10.2.179.2','10.2.179.254',NULL,NULL,NULL,'false',0,'int-sub-689','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('690',NULL,'c','4','10.2.180.0/24','10.2.180.1','10.2.180.2','10.2.180.254',NULL,NULL,NULL,'false',0,'int-sub-690','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('691',NULL,'c','4','10.2.181.0/24','10.2.181.1','10.2.181.2','10.2.181.254',NULL,NULL,NULL,'false',0,'int-sub-691','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('692',NULL,'c','4','10.2.182.0/24','10.2.182.1','10.2.182.2','10.2.182.254',NULL,NULL,NULL,'false',0,'int-sub-692','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('693',NULL,'c','4','10.2.183.0/24','10.2.183.1','10.2.183.2','10.2.183.254',NULL,NULL,NULL,'false',0,'int-sub-693','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('694',NULL,'c','4','10.2.184.0/24','10.2.184.1','10.2.184.2','10.2.184.254',NULL,NULL,NULL,'false',0,'int-sub-694','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('695',NULL,'c','4','10.2.185.0/24','10.2.185.1','10.2.185.2','10.2.185.254',NULL,NULL,NULL,'false',0,'int-sub-695','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('696',NULL,'c','4','10.2.186.0/24','10.2.186.1','10.2.186.2','10.2.186.254',NULL,NULL,NULL,'false',0,'int-sub-696','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('697',NULL,'c','4','10.2.187.0/24','10.2.187.1','10.2.187.2','10.2.187.254',NULL,NULL,NULL,'false',0,'int-sub-697','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('698',NULL,'c','4','10.2.188.0/24','10.2.188.1','10.2.188.2','10.2.188.254',NULL,NULL,NULL,'false',0,'int-sub-698','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('699',NULL,'c','4','10.2.189.0/24','10.2.189.1','10.2.189.2','10.2.189.254',NULL,NULL,NULL,'false',0,'int-sub-699','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('700',NULL,'c','4','10.2.190.0/24','10.2.190.1','10.2.190.2','10.2.190.254',NULL,NULL,NULL,'false',0,'int-sub-700','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('701',NULL,'c','4','10.2.191.0/24','10.2.191.1','10.2.191.2','10.2.191.254',NULL,NULL,NULL,'false',0,'int-sub-701','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('702',NULL,'c','4','10.2.192.0/24','10.2.192.1','10.2.192.2','10.2.192.254',NULL,NULL,NULL,'false',0,'int-sub-702','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('703',NULL,'c','4','10.2.193.0/24','10.2.193.1','10.2.193.2','10.2.193.254',NULL,NULL,NULL,'false',0,'int-sub-703','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('704',NULL,'c','4','10.2.194.0/24','10.2.194.1','10.2.194.2','10.2.194.254',NULL,NULL,NULL,'false',0,'int-sub-704','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('705',NULL,'c','4','10.2.195.0/24','10.2.195.1','10.2.195.2','10.2.195.254',NULL,NULL,NULL,'false',0,'int-sub-705','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('706',NULL,'c','4','10.2.196.0/24','10.2.196.1','10.2.196.2','10.2.196.254',NULL,NULL,NULL,'false',0,'int-sub-706','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('707',NULL,'c','4','10.2.197.0/24','10.2.197.1','10.2.197.2','10.2.197.254',NULL,NULL,NULL,'false',0,'int-sub-707','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('708',NULL,'c','4','10.2.198.0/24','10.2.198.1','10.2.198.2','10.2.198.254',NULL,NULL,NULL,'false',0,'int-sub-708','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('709',NULL,'c','4','10.2.199.0/24','10.2.199.1','10.2.199.2','10.2.199.254',NULL,NULL,NULL,'false',0,'int-sub-709','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('710',NULL,'c','4','10.2.200.0/24','10.2.200.1','10.2.200.2','10.2.200.254',NULL,NULL,NULL,'false',0,'int-sub-710','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('711',NULL,'c','4','10.2.201.0/24','10.2.201.1','10.2.201.2','10.2.201.254',NULL,NULL,NULL,'false',0,'int-sub-711','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('712',NULL,'c','4','10.2.202.0/24','10.2.202.1','10.2.202.2','10.2.202.254',NULL,NULL,NULL,'false',0,'int-sub-712','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('713',NULL,'c','4','10.2.203.0/24','10.2.203.1','10.2.203.2','10.2.203.254',NULL,NULL,NULL,'false',0,'int-sub-713','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('714',NULL,'c','4','10.2.204.0/24','10.2.204.1','10.2.204.2','10.2.204.254',NULL,NULL,NULL,'false',0,'int-sub-714','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('715',NULL,'c','4','10.2.205.0/24','10.2.205.1','10.2.205.2','10.2.205.254',NULL,NULL,NULL,'false',0,'int-sub-715','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('716',NULL,'c','4','10.2.206.0/24','10.2.206.1','10.2.206.2','10.2.206.254',NULL,NULL,NULL,'false',0,'int-sub-716','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('717',NULL,'c','4','10.2.207.0/24','10.2.207.1','10.2.207.2','10.2.207.254',NULL,NULL,NULL,'false',0,'int-sub-717','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('718',NULL,'c','4','10.2.208.0/24','10.2.208.1','10.2.208.2','10.2.208.254',NULL,NULL,NULL,'false',0,'int-sub-718','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('719',NULL,'c','4','10.2.209.0/24','10.2.209.1','10.2.209.2','10.2.209.254',NULL,NULL,NULL,'false',0,'int-sub-719','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('720',NULL,'c','4','10.2.210.0/24','10.2.210.1','10.2.210.2','10.2.210.254',NULL,NULL,NULL,'false',0,'int-sub-720','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('721',NULL,'c','4','10.2.211.0/24','10.2.211.1','10.2.211.2','10.2.211.254',NULL,NULL,NULL,'false',0,'int-sub-721','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('722',NULL,'c','4','10.2.212.0/24','10.2.212.1','10.2.212.2','10.2.212.254',NULL,NULL,NULL,'false',0,'int-sub-722','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('723',NULL,'c','4','10.2.213.0/24','10.2.213.1','10.2.213.2','10.2.213.254',NULL,NULL,NULL,'false',0,'int-sub-723','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('724',NULL,'c','4','10.2.214.0/24','10.2.214.1','10.2.214.2','10.2.214.254',NULL,NULL,NULL,'false',0,'int-sub-724','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('725',NULL,'c','4','10.2.215.0/24','10.2.215.1','10.2.215.2','10.2.215.254',NULL,NULL,NULL,'false',0,'int-sub-725','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('726',NULL,'c','4','10.2.216.0/24','10.2.216.1','10.2.216.2','10.2.216.254',NULL,NULL,NULL,'false',0,'int-sub-726','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('727',NULL,'c','4','10.2.217.0/24','10.2.217.1','10.2.217.2','10.2.217.254',NULL,NULL,NULL,'false',0,'int-sub-727','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('728',NULL,'c','4','10.2.218.0/24','10.2.218.1','10.2.218.2','10.2.218.254',NULL,NULL,NULL,'false',0,'int-sub-728','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('729',NULL,'c','4','10.2.219.0/24','10.2.219.1','10.2.219.2','10.2.219.254',NULL,NULL,NULL,'false',0,'int-sub-729','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('730',NULL,'c','4','10.2.220.0/24','10.2.220.1','10.2.220.2','10.2.220.254',NULL,NULL,NULL,'false',0,'int-sub-730','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('731',NULL,'c','4','10.2.221.0/24','10.2.221.1','10.2.221.2','10.2.221.254',NULL,NULL,NULL,'false',0,'int-sub-731','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('732',NULL,'c','4','10.2.222.0/24','10.2.222.1','10.2.222.2','10.2.222.254',NULL,NULL,NULL,'false',0,'int-sub-732','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('733',NULL,'c','4','10.2.223.0/24','10.2.223.1','10.2.223.2','10.2.223.254',NULL,NULL,NULL,'false',0,'int-sub-733','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('734',NULL,'c','4','10.2.224.0/24','10.2.224.1','10.2.224.2','10.2.224.254',NULL,NULL,NULL,'false',0,'int-sub-734','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('735',NULL,'c','4','10.2.225.0/24','10.2.225.1','10.2.225.2','10.2.225.254',NULL,NULL,NULL,'false',0,'int-sub-735','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('736',NULL,'c','4','10.2.226.0/24','10.2.226.1','10.2.226.2','10.2.226.254',NULL,NULL,NULL,'false',0,'int-sub-736','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('737',NULL,'c','4','10.2.227.0/24','10.2.227.1','10.2.227.2','10.2.227.254',NULL,NULL,NULL,'false',0,'int-sub-737','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('738',NULL,'c','4','10.2.228.0/24','10.2.228.1','10.2.228.2','10.2.228.254',NULL,NULL,NULL,'false',0,'int-sub-738','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('739',NULL,'c','4','10.2.229.0/24','10.2.229.1','10.2.229.2','10.2.229.254',NULL,NULL,NULL,'false',0,'int-sub-739','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('740',NULL,'c','4','10.2.230.0/24','10.2.230.1','10.2.230.2','10.2.230.254',NULL,NULL,NULL,'false',0,'int-sub-740','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('741',NULL,'c','4','10.2.231.0/24','10.2.231.1','10.2.231.2','10.2.231.254',NULL,NULL,NULL,'false',0,'int-sub-741','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('742',NULL,'c','4','10.2.232.0/24','10.2.232.1','10.2.232.2','10.2.232.254',NULL,NULL,NULL,'false',0,'int-sub-742','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('743',NULL,'c','4','10.2.233.0/24','10.2.233.1','10.2.233.2','10.2.233.254',NULL,NULL,NULL,'false',0,'int-sub-743','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('744',NULL,'c','4','10.2.234.0/24','10.2.234.1','10.2.234.2','10.2.234.254',NULL,NULL,NULL,'false',0,'int-sub-744','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('745',NULL,'c','4','10.2.235.0/24','10.2.235.1','10.2.235.2','10.2.235.254',NULL,NULL,NULL,'false',0,'int-sub-745','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('746',NULL,'c','4','10.2.236.0/24','10.2.236.1','10.2.236.2','10.2.236.254',NULL,NULL,NULL,'false',0,'int-sub-746','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('747',NULL,'c','4','10.2.237.0/24','10.2.237.1','10.2.237.2','10.2.237.254',NULL,NULL,NULL,'false',0,'int-sub-747','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('748',NULL,'c','4','10.2.238.0/24','10.2.238.1','10.2.238.2','10.2.238.254',NULL,NULL,NULL,'false',0,'int-sub-748','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('749',NULL,'c','4','10.2.239.0/24','10.2.239.1','10.2.239.2','10.2.239.254',NULL,NULL,NULL,'false',0,'int-sub-749','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('750',NULL,'c','4','10.2.240.0/24','10.2.240.1','10.2.240.2','10.2.240.254',NULL,NULL,NULL,'false',0,'int-sub-750','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('751',NULL,'c','4','10.2.241.0/24','10.2.241.1','10.2.241.2','10.2.241.254',NULL,NULL,NULL,'false',0,'int-sub-751','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('752',NULL,'c','4','10.2.242.0/24','10.2.242.1','10.2.242.2','10.2.242.254',NULL,NULL,NULL,'false',0,'int-sub-752','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('753',NULL,'c','4','10.2.243.0/24','10.2.243.1','10.2.243.2','10.2.243.254',NULL,NULL,NULL,'false',0,'int-sub-753','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('754',NULL,'c','4','10.2.244.0/24','10.2.244.1','10.2.244.2','10.2.244.254',NULL,NULL,NULL,'false',0,'int-sub-754','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('755',NULL,'c','4','10.2.245.0/24','10.2.245.1','10.2.245.2','10.2.245.254',NULL,NULL,NULL,'false',0,'int-sub-755','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('756',NULL,'c','4','10.2.246.0/24','10.2.246.1','10.2.246.2','10.2.246.254',NULL,NULL,NULL,'false',0,'int-sub-756','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('757',NULL,'c','4','10.2.247.0/24','10.2.247.1','10.2.247.2','10.2.247.254',NULL,NULL,NULL,'false',0,'int-sub-757','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('758',NULL,'c','4','10.2.248.0/24','10.2.248.1','10.2.248.2','10.2.248.254',NULL,NULL,NULL,'false',0,'int-sub-758','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('759',NULL,'c','4','10.2.249.0/24','10.2.249.1','10.2.249.2','10.2.249.254',NULL,NULL,NULL,'false',0,'int-sub-759','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('760',NULL,'c','4','10.2.250.0/24','10.2.250.1','10.2.250.2','10.2.250.254',NULL,NULL,NULL,'false',0,'int-sub-760','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('761',NULL,'c','4','10.2.251.0/24','10.2.251.1','10.2.251.2','10.2.251.254',NULL,NULL,NULL,'false',0,'int-sub-761','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('762',NULL,'c','4','10.2.252.0/24','10.2.252.1','10.2.252.2','10.2.252.254',NULL,NULL,NULL,'false',0,'int-sub-762','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('763',NULL,'c','4','10.2.253.0/24','10.2.253.1','10.2.253.2','10.2.253.254',NULL,NULL,NULL,'false',0,'int-sub-763','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('764',NULL,'c','4','10.2.254.0/24','10.2.254.1','10.2.254.2','10.2.254.254',NULL,NULL,NULL,'false',0,'int-sub-764','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('765',NULL,'c','4','10.3.0.0/24','10.3.0.1','10.3.0.2','10.3.0.254',NULL,NULL,NULL,'false',0,'int-sub-765','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('766',NULL,'c','4','10.3.1.0/24','10.3.1.1','10.3.1.2','10.3.1.254',NULL,NULL,NULL,'false',0,'int-sub-766','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('767',NULL,'c','4','10.3.2.0/24','10.3.2.1','10.3.2.2','10.3.2.254',NULL,NULL,NULL,'false',0,'int-sub-767','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('768',NULL,'c','4','10.3.3.0/24','10.3.3.1','10.3.3.2','10.3.3.254',NULL,NULL,NULL,'false',0,'int-sub-768','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('769',NULL,'c','4','10.3.4.0/24','10.3.4.1','10.3.4.2','10.3.4.254',NULL,NULL,NULL,'false',0,'int-sub-769','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('770',NULL,'c','4','10.3.5.0/24','10.3.5.1','10.3.5.2','10.3.5.254',NULL,NULL,NULL,'false',0,'int-sub-770','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('771',NULL,'c','4','10.3.6.0/24','10.3.6.1','10.3.6.2','10.3.6.254',NULL,NULL,NULL,'false',0,'int-sub-771','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('772',NULL,'c','4','10.3.7.0/24','10.3.7.1','10.3.7.2','10.3.7.254',NULL,NULL,NULL,'false',0,'int-sub-772','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('773',NULL,'c','4','10.3.8.0/24','10.3.8.1','10.3.8.2','10.3.8.254',NULL,NULL,NULL,'false',0,'int-sub-773','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('774',NULL,'c','4','10.3.9.0/24','10.3.9.1','10.3.9.2','10.3.9.254',NULL,NULL,NULL,'false',0,'int-sub-774','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('775',NULL,'c','4','10.3.10.0/24','10.3.10.1','10.3.10.2','10.3.10.254',NULL,NULL,NULL,'false',0,'int-sub-775','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('776',NULL,'c','4','10.3.11.0/24','10.3.11.1','10.3.11.2','10.3.11.254',NULL,NULL,NULL,'false',0,'int-sub-776','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('777',NULL,'c','4','10.3.12.0/24','10.3.12.1','10.3.12.2','10.3.12.254',NULL,NULL,NULL,'false',0,'int-sub-777','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('778',NULL,'c','4','10.3.13.0/24','10.3.13.1','10.3.13.2','10.3.13.254',NULL,NULL,NULL,'false',0,'int-sub-778','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('779',NULL,'c','4','10.3.14.0/24','10.3.14.1','10.3.14.2','10.3.14.254',NULL,NULL,NULL,'false',0,'int-sub-779','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('780',NULL,'c','4','10.3.15.0/24','10.3.15.1','10.3.15.2','10.3.15.254',NULL,NULL,NULL,'false',0,'int-sub-780','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('781',NULL,'c','4','10.3.16.0/24','10.3.16.1','10.3.16.2','10.3.16.254',NULL,NULL,NULL,'false',0,'int-sub-781','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('782',NULL,'c','4','10.3.17.0/24','10.3.17.1','10.3.17.2','10.3.17.254',NULL,NULL,NULL,'false',0,'int-sub-782','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('783',NULL,'c','4','10.3.18.0/24','10.3.18.1','10.3.18.2','10.3.18.254',NULL,NULL,NULL,'false',0,'int-sub-783','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('784',NULL,'c','4','10.3.19.0/24','10.3.19.1','10.3.19.2','10.3.19.254',NULL,NULL,NULL,'false',0,'int-sub-784','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('785',NULL,'c','4','10.3.20.0/24','10.3.20.1','10.3.20.2','10.3.20.254',NULL,NULL,NULL,'false',0,'int-sub-785','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('786',NULL,'c','4','10.3.21.0/24','10.3.21.1','10.3.21.2','10.3.21.254',NULL,NULL,NULL,'false',0,'int-sub-786','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('787',NULL,'c','4','10.3.22.0/24','10.3.22.1','10.3.22.2','10.3.22.254',NULL,NULL,NULL,'false',0,'int-sub-787','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('788',NULL,'c','4','10.3.23.0/24','10.3.23.1','10.3.23.2','10.3.23.254',NULL,NULL,NULL,'false',0,'int-sub-788','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('789',NULL,'c','4','10.3.24.0/24','10.3.24.1','10.3.24.2','10.3.24.254',NULL,NULL,NULL,'false',0,'int-sub-789','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('790',NULL,'c','4','10.3.25.0/24','10.3.25.1','10.3.25.2','10.3.25.254',NULL,NULL,NULL,'false',0,'int-sub-790','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('791',NULL,'c','4','10.3.26.0/24','10.3.26.1','10.3.26.2','10.3.26.254',NULL,NULL,NULL,'false',0,'int-sub-791','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('792',NULL,'c','4','10.3.27.0/24','10.3.27.1','10.3.27.2','10.3.27.254',NULL,NULL,NULL,'false',0,'int-sub-792','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('793',NULL,'c','4','10.3.28.0/24','10.3.28.1','10.3.28.2','10.3.28.254',NULL,NULL,NULL,'false',0,'int-sub-793','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('794',NULL,'c','4','10.3.29.0/24','10.3.29.1','10.3.29.2','10.3.29.254',NULL,NULL,NULL,'false',0,'int-sub-794','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('795',NULL,'c','4','10.3.30.0/24','10.3.30.1','10.3.30.2','10.3.30.254',NULL,NULL,NULL,'false',0,'int-sub-795','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('796',NULL,'c','4','10.3.31.0/24','10.3.31.1','10.3.31.2','10.3.31.254',NULL,NULL,NULL,'false',0,'int-sub-796','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('797',NULL,'c','4','10.3.32.0/24','10.3.32.1','10.3.32.2','10.3.32.254',NULL,NULL,NULL,'false',0,'int-sub-797','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('798',NULL,'c','4','10.3.33.0/24','10.3.33.1','10.3.33.2','10.3.33.254',NULL,NULL,NULL,'false',0,'int-sub-798','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('799',NULL,'c','4','10.3.34.0/24','10.3.34.1','10.3.34.2','10.3.34.254',NULL,NULL,NULL,'false',0,'int-sub-799','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('800',NULL,'c','4','10.3.35.0/24','10.3.35.1','10.3.35.2','10.3.35.254',NULL,NULL,NULL,'false',0,'int-sub-800','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('801',NULL,'c','4','10.3.36.0/24','10.3.36.1','10.3.36.2','10.3.36.254',NULL,NULL,NULL,'false',0,'int-sub-801','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('802',NULL,'c','4','10.3.37.0/24','10.3.37.1','10.3.37.2','10.3.37.254',NULL,NULL,NULL,'false',0,'int-sub-802','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('803',NULL,'c','4','10.3.38.0/24','10.3.38.1','10.3.38.2','10.3.38.254',NULL,NULL,NULL,'false',0,'int-sub-803','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('804',NULL,'c','4','10.3.39.0/24','10.3.39.1','10.3.39.2','10.3.39.254',NULL,NULL,NULL,'false',0,'int-sub-804','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('805',NULL,'c','4','10.3.40.0/24','10.3.40.1','10.3.40.2','10.3.40.254',NULL,NULL,NULL,'false',0,'int-sub-805','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('806',NULL,'c','4','10.3.41.0/24','10.3.41.1','10.3.41.2','10.3.41.254',NULL,NULL,NULL,'false',0,'int-sub-806','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('807',NULL,'c','4','10.3.42.0/24','10.3.42.1','10.3.42.2','10.3.42.254',NULL,NULL,NULL,'false',0,'int-sub-807','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('808',NULL,'c','4','10.3.43.0/24','10.3.43.1','10.3.43.2','10.3.43.254',NULL,NULL,NULL,'false',0,'int-sub-808','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('809',NULL,'c','4','10.3.44.0/24','10.3.44.1','10.3.44.2','10.3.44.254',NULL,NULL,NULL,'false',0,'int-sub-809','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('810',NULL,'c','4','10.3.45.0/24','10.3.45.1','10.3.45.2','10.3.45.254',NULL,NULL,NULL,'false',0,'int-sub-810','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('811',NULL,'c','4','10.3.46.0/24','10.3.46.1','10.3.46.2','10.3.46.254',NULL,NULL,NULL,'false',0,'int-sub-811','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('812',NULL,'c','4','10.3.47.0/24','10.3.47.1','10.3.47.2','10.3.47.254',NULL,NULL,NULL,'false',0,'int-sub-812','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('813',NULL,'c','4','10.3.48.0/24','10.3.48.1','10.3.48.2','10.3.48.254',NULL,NULL,NULL,'false',0,'int-sub-813','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('814',NULL,'c','4','10.3.49.0/24','10.3.49.1','10.3.49.2','10.3.49.254',NULL,NULL,NULL,'false',0,'int-sub-814','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('815',NULL,'c','4','10.3.50.0/24','10.3.50.1','10.3.50.2','10.3.50.254',NULL,NULL,NULL,'false',0,'int-sub-815','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('816',NULL,'c','4','10.3.51.0/24','10.3.51.1','10.3.51.2','10.3.51.254',NULL,NULL,NULL,'false',0,'int-sub-816','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('817',NULL,'c','4','10.3.52.0/24','10.3.52.1','10.3.52.2','10.3.52.254',NULL,NULL,NULL,'false',0,'int-sub-817','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('818',NULL,'c','4','10.3.53.0/24','10.3.53.1','10.3.53.2','10.3.53.254',NULL,NULL,NULL,'false',0,'int-sub-818','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('819',NULL,'c','4','10.3.54.0/24','10.3.54.1','10.3.54.2','10.3.54.254',NULL,NULL,NULL,'false',0,'int-sub-819','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('820',NULL,'c','4','10.3.55.0/24','10.3.55.1','10.3.55.2','10.3.55.254',NULL,NULL,NULL,'false',0,'int-sub-820','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('821',NULL,'c','4','10.3.56.0/24','10.3.56.1','10.3.56.2','10.3.56.254',NULL,NULL,NULL,'false',0,'int-sub-821','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('822',NULL,'c','4','10.3.57.0/24','10.3.57.1','10.3.57.2','10.3.57.254',NULL,NULL,NULL,'false',0,'int-sub-822','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('823',NULL,'c','4','10.3.58.0/24','10.3.58.1','10.3.58.2','10.3.58.254',NULL,NULL,NULL,'false',0,'int-sub-823','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('824',NULL,'c','4','10.3.59.0/24','10.3.59.1','10.3.59.2','10.3.59.254',NULL,NULL,NULL,'false',0,'int-sub-824','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('825',NULL,'c','4','10.3.60.0/24','10.3.60.1','10.3.60.2','10.3.60.254',NULL,NULL,NULL,'false',0,'int-sub-825','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('826',NULL,'c','4','10.3.61.0/24','10.3.61.1','10.3.61.2','10.3.61.254',NULL,NULL,NULL,'false',0,'int-sub-826','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('827',NULL,'c','4','10.3.62.0/24','10.3.62.1','10.3.62.2','10.3.62.254',NULL,NULL,NULL,'false',0,'int-sub-827','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('828',NULL,'c','4','10.3.63.0/24','10.3.63.1','10.3.63.2','10.3.63.254',NULL,NULL,NULL,'false',0,'int-sub-828','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('829',NULL,'c','4','10.3.64.0/24','10.3.64.1','10.3.64.2','10.3.64.254',NULL,NULL,NULL,'false',0,'int-sub-829','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('830',NULL,'c','4','10.3.65.0/24','10.3.65.1','10.3.65.2','10.3.65.254',NULL,NULL,NULL,'false',0,'int-sub-830','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('831',NULL,'c','4','10.3.66.0/24','10.3.66.1','10.3.66.2','10.3.66.254',NULL,NULL,NULL,'false',0,'int-sub-831','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('832',NULL,'c','4','10.3.67.0/24','10.3.67.1','10.3.67.2','10.3.67.254',NULL,NULL,NULL,'false',0,'int-sub-832','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('833',NULL,'c','4','10.3.68.0/24','10.3.68.1','10.3.68.2','10.3.68.254',NULL,NULL,NULL,'false',0,'int-sub-833','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('834',NULL,'c','4','10.3.69.0/24','10.3.69.1','10.3.69.2','10.3.69.254',NULL,NULL,NULL,'false',0,'int-sub-834','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('835',NULL,'c','4','10.3.70.0/24','10.3.70.1','10.3.70.2','10.3.70.254',NULL,NULL,NULL,'false',0,'int-sub-835','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('836',NULL,'c','4','10.3.71.0/24','10.3.71.1','10.3.71.2','10.3.71.254',NULL,NULL,NULL,'false',0,'int-sub-836','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('837',NULL,'c','4','10.3.72.0/24','10.3.72.1','10.3.72.2','10.3.72.254',NULL,NULL,NULL,'false',0,'int-sub-837','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('838',NULL,'c','4','10.3.73.0/24','10.3.73.1','10.3.73.2','10.3.73.254',NULL,NULL,NULL,'false',0,'int-sub-838','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('839',NULL,'c','4','10.3.74.0/24','10.3.74.1','10.3.74.2','10.3.74.254',NULL,NULL,NULL,'false',0,'int-sub-839','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('840',NULL,'c','4','10.3.75.0/24','10.3.75.1','10.3.75.2','10.3.75.254',NULL,NULL,NULL,'false',0,'int-sub-840','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('841',NULL,'c','4','10.3.76.0/24','10.3.76.1','10.3.76.2','10.3.76.254',NULL,NULL,NULL,'false',0,'int-sub-841','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('842',NULL,'c','4','10.3.77.0/24','10.3.77.1','10.3.77.2','10.3.77.254',NULL,NULL,NULL,'false',0,'int-sub-842','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('843',NULL,'c','4','10.3.78.0/24','10.3.78.1','10.3.78.2','10.3.78.254',NULL,NULL,NULL,'false',0,'int-sub-843','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('844',NULL,'c','4','10.3.79.0/24','10.3.79.1','10.3.79.2','10.3.79.254',NULL,NULL,NULL,'false',0,'int-sub-844','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('845',NULL,'c','4','10.3.80.0/24','10.3.80.1','10.3.80.2','10.3.80.254',NULL,NULL,NULL,'false',0,'int-sub-845','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('846',NULL,'c','4','10.3.81.0/24','10.3.81.1','10.3.81.2','10.3.81.254',NULL,NULL,NULL,'false',0,'int-sub-846','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('847',NULL,'c','4','10.3.82.0/24','10.3.82.1','10.3.82.2','10.3.82.254',NULL,NULL,NULL,'false',0,'int-sub-847','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('848',NULL,'c','4','10.3.83.0/24','10.3.83.1','10.3.83.2','10.3.83.254',NULL,NULL,NULL,'false',0,'int-sub-848','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('849',NULL,'c','4','10.3.84.0/24','10.3.84.1','10.3.84.2','10.3.84.254',NULL,NULL,NULL,'false',0,'int-sub-849','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('850',NULL,'c','4','10.3.85.0/24','10.3.85.1','10.3.85.2','10.3.85.254',NULL,NULL,NULL,'false',0,'int-sub-850','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('851',NULL,'c','4','10.3.86.0/24','10.3.86.1','10.3.86.2','10.3.86.254',NULL,NULL,NULL,'false',0,'int-sub-851','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('852',NULL,'c','4','10.3.87.0/24','10.3.87.1','10.3.87.2','10.3.87.254',NULL,NULL,NULL,'false',0,'int-sub-852','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('853',NULL,'c','4','10.3.88.0/24','10.3.88.1','10.3.88.2','10.3.88.254',NULL,NULL,NULL,'false',0,'int-sub-853','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('854',NULL,'c','4','10.3.89.0/24','10.3.89.1','10.3.89.2','10.3.89.254',NULL,NULL,NULL,'false',0,'int-sub-854','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('855',NULL,'c','4','10.3.90.0/24','10.3.90.1','10.3.90.2','10.3.90.254',NULL,NULL,NULL,'false',0,'int-sub-855','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('856',NULL,'c','4','10.3.91.0/24','10.3.91.1','10.3.91.2','10.3.91.254',NULL,NULL,NULL,'false',0,'int-sub-856','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('857',NULL,'c','4','10.3.92.0/24','10.3.92.1','10.3.92.2','10.3.92.254',NULL,NULL,NULL,'false',0,'int-sub-857','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('858',NULL,'c','4','10.3.93.0/24','10.3.93.1','10.3.93.2','10.3.93.254',NULL,NULL,NULL,'false',0,'int-sub-858','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('859',NULL,'c','4','10.3.94.0/24','10.3.94.1','10.3.94.2','10.3.94.254',NULL,NULL,NULL,'false',0,'int-sub-859','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('860',NULL,'c','4','10.3.95.0/24','10.3.95.1','10.3.95.2','10.3.95.254',NULL,NULL,NULL,'false',0,'int-sub-860','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('861',NULL,'c','4','10.3.96.0/24','10.3.96.1','10.3.96.2','10.3.96.254',NULL,NULL,NULL,'false',0,'int-sub-861','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('862',NULL,'c','4','10.3.97.0/24','10.3.97.1','10.3.97.2','10.3.97.254',NULL,NULL,NULL,'false',0,'int-sub-862','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('863',NULL,'c','4','10.3.98.0/24','10.3.98.1','10.3.98.2','10.3.98.254',NULL,NULL,NULL,'false',0,'int-sub-863','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('864',NULL,'c','4','10.3.99.0/24','10.3.99.1','10.3.99.2','10.3.99.254',NULL,NULL,NULL,'false',0,'int-sub-864','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('865',NULL,'c','4','10.3.100.0/24','10.3.100.1','10.3.100.2','10.3.100.254',NULL,NULL,NULL,'false',0,'int-sub-865','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('866',NULL,'c','4','10.3.101.0/24','10.3.101.1','10.3.101.2','10.3.101.254',NULL,NULL,NULL,'false',0,'int-sub-866','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('867',NULL,'c','4','10.3.102.0/24','10.3.102.1','10.3.102.2','10.3.102.254',NULL,NULL,NULL,'false',0,'int-sub-867','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('868',NULL,'c','4','10.3.103.0/24','10.3.103.1','10.3.103.2','10.3.103.254',NULL,NULL,NULL,'false',0,'int-sub-868','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('869',NULL,'c','4','10.3.104.0/24','10.3.104.1','10.3.104.2','10.3.104.254',NULL,NULL,NULL,'false',0,'int-sub-869','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('870',NULL,'c','4','10.3.105.0/24','10.3.105.1','10.3.105.2','10.3.105.254',NULL,NULL,NULL,'false',0,'int-sub-870','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('871',NULL,'c','4','10.3.106.0/24','10.3.106.1','10.3.106.2','10.3.106.254',NULL,NULL,NULL,'false',0,'int-sub-871','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('872',NULL,'c','4','10.3.107.0/24','10.3.107.1','10.3.107.2','10.3.107.254',NULL,NULL,NULL,'false',0,'int-sub-872','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('873',NULL,'c','4','10.3.108.0/24','10.3.108.1','10.3.108.2','10.3.108.254',NULL,NULL,NULL,'false',0,'int-sub-873','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('874',NULL,'c','4','10.3.109.0/24','10.3.109.1','10.3.109.2','10.3.109.254',NULL,NULL,NULL,'false',0,'int-sub-874','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('875',NULL,'c','4','10.3.110.0/24','10.3.110.1','10.3.110.2','10.3.110.254',NULL,NULL,NULL,'false',0,'int-sub-875','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('876',NULL,'c','4','10.3.111.0/24','10.3.111.1','10.3.111.2','10.3.111.254',NULL,NULL,NULL,'false',0,'int-sub-876','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('877',NULL,'c','4','10.3.112.0/24','10.3.112.1','10.3.112.2','10.3.112.254',NULL,NULL,NULL,'false',0,'int-sub-877','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('878',NULL,'c','4','10.3.113.0/24','10.3.113.1','10.3.113.2','10.3.113.254',NULL,NULL,NULL,'false',0,'int-sub-878','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('879',NULL,'c','4','10.3.114.0/24','10.3.114.1','10.3.114.2','10.3.114.254',NULL,NULL,NULL,'false',0,'int-sub-879','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('880',NULL,'c','4','10.3.115.0/24','10.3.115.1','10.3.115.2','10.3.115.254',NULL,NULL,NULL,'false',0,'int-sub-880','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('881',NULL,'c','4','10.3.116.0/24','10.3.116.1','10.3.116.2','10.3.116.254',NULL,NULL,NULL,'false',0,'int-sub-881','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('882',NULL,'c','4','10.3.117.0/24','10.3.117.1','10.3.117.2','10.3.117.254',NULL,NULL,NULL,'false',0,'int-sub-882','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('883',NULL,'c','4','10.3.118.0/24','10.3.118.1','10.3.118.2','10.3.118.254',NULL,NULL,NULL,'false',0,'int-sub-883','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('884',NULL,'c','4','10.3.119.0/24','10.3.119.1','10.3.119.2','10.3.119.254',NULL,NULL,NULL,'false',0,'int-sub-884','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('885',NULL,'c','4','10.3.120.0/24','10.3.120.1','10.3.120.2','10.3.120.254',NULL,NULL,NULL,'false',0,'int-sub-885','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('886',NULL,'c','4','10.3.121.0/24','10.3.121.1','10.3.121.2','10.3.121.254',NULL,NULL,NULL,'false',0,'int-sub-886','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('887',NULL,'c','4','10.3.122.0/24','10.3.122.1','10.3.122.2','10.3.122.254',NULL,NULL,NULL,'false',0,'int-sub-887','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('888',NULL,'c','4','10.3.123.0/24','10.3.123.1','10.3.123.2','10.3.123.254',NULL,NULL,NULL,'false',0,'int-sub-888','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('889',NULL,'c','4','10.3.124.0/24','10.3.124.1','10.3.124.2','10.3.124.254',NULL,NULL,NULL,'false',0,'int-sub-889','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('890',NULL,'c','4','10.3.125.0/24','10.3.125.1','10.3.125.2','10.3.125.254',NULL,NULL,NULL,'false',0,'int-sub-890','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('891',NULL,'c','4','10.3.126.0/24','10.3.126.1','10.3.126.2','10.3.126.254',NULL,NULL,NULL,'false',0,'int-sub-891','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('892',NULL,'c','4','10.3.127.0/24','10.3.127.1','10.3.127.2','10.3.127.254',NULL,NULL,NULL,'false',0,'int-sub-892','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('893',NULL,'c','4','10.3.128.0/24','10.3.128.1','10.3.128.2','10.3.128.254',NULL,NULL,NULL,'false',0,'int-sub-893','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('894',NULL,'c','4','10.3.129.0/24','10.3.129.1','10.3.129.2','10.3.129.254',NULL,NULL,NULL,'false',0,'int-sub-894','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('895',NULL,'c','4','10.3.130.0/24','10.3.130.1','10.3.130.2','10.3.130.254',NULL,NULL,NULL,'false',0,'int-sub-895','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('896',NULL,'c','4','10.3.131.0/24','10.3.131.1','10.3.131.2','10.3.131.254',NULL,NULL,NULL,'false',0,'int-sub-896','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('897',NULL,'c','4','10.3.132.0/24','10.3.132.1','10.3.132.2','10.3.132.254',NULL,NULL,NULL,'false',0,'int-sub-897','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('898',NULL,'c','4','10.3.133.0/24','10.3.133.1','10.3.133.2','10.3.133.254',NULL,NULL,NULL,'false',0,'int-sub-898','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('899',NULL,'c','4','10.3.134.0/24','10.3.134.1','10.3.134.2','10.3.134.254',NULL,NULL,NULL,'false',0,'int-sub-899','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('900',NULL,'c','4','10.3.135.0/24','10.3.135.1','10.3.135.2','10.3.135.254',NULL,NULL,NULL,'false',0,'int-sub-900','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('901',NULL,'c','4','10.3.136.0/24','10.3.136.1','10.3.136.2','10.3.136.254',NULL,NULL,NULL,'false',0,'int-sub-901','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('902',NULL,'c','4','10.3.137.0/24','10.3.137.1','10.3.137.2','10.3.137.254',NULL,NULL,NULL,'false',0,'int-sub-902','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('903',NULL,'c','4','10.3.138.0/24','10.3.138.1','10.3.138.2','10.3.138.254',NULL,NULL,NULL,'false',0,'int-sub-903','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('904',NULL,'c','4','10.3.139.0/24','10.3.139.1','10.3.139.2','10.3.139.254',NULL,NULL,NULL,'false',0,'int-sub-904','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('905',NULL,'c','4','10.3.140.0/24','10.3.140.1','10.3.140.2','10.3.140.254',NULL,NULL,NULL,'false',0,'int-sub-905','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('906',NULL,'c','4','10.3.141.0/24','10.3.141.1','10.3.141.2','10.3.141.254',NULL,NULL,NULL,'false',0,'int-sub-906','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('907',NULL,'c','4','10.3.142.0/24','10.3.142.1','10.3.142.2','10.3.142.254',NULL,NULL,NULL,'false',0,'int-sub-907','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('908',NULL,'c','4','10.3.143.0/24','10.3.143.1','10.3.143.2','10.3.143.254',NULL,NULL,NULL,'false',0,'int-sub-908','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('909',NULL,'c','4','10.3.144.0/24','10.3.144.1','10.3.144.2','10.3.144.254',NULL,NULL,NULL,'false',0,'int-sub-909','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('910',NULL,'c','4','10.3.145.0/24','10.3.145.1','10.3.145.2','10.3.145.254',NULL,NULL,NULL,'false',0,'int-sub-910','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('911',NULL,'c','4','10.3.146.0/24','10.3.146.1','10.3.146.2','10.3.146.254',NULL,NULL,NULL,'false',0,'int-sub-911','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('912',NULL,'c','4','10.3.147.0/24','10.3.147.1','10.3.147.2','10.3.147.254',NULL,NULL,NULL,'false',0,'int-sub-912','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('913',NULL,'c','4','10.3.148.0/24','10.3.148.1','10.3.148.2','10.3.148.254',NULL,NULL,NULL,'false',0,'int-sub-913','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('914',NULL,'c','4','10.3.149.0/24','10.3.149.1','10.3.149.2','10.3.149.254',NULL,NULL,NULL,'false',0,'int-sub-914','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('915',NULL,'c','4','10.3.150.0/24','10.3.150.1','10.3.150.2','10.3.150.254',NULL,NULL,NULL,'false',0,'int-sub-915','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('916',NULL,'c','4','10.3.151.0/24','10.3.151.1','10.3.151.2','10.3.151.254',NULL,NULL,NULL,'false',0,'int-sub-916','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('917',NULL,'c','4','10.3.152.0/24','10.3.152.1','10.3.152.2','10.3.152.254',NULL,NULL,NULL,'false',0,'int-sub-917','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('918',NULL,'c','4','10.3.153.0/24','10.3.153.1','10.3.153.2','10.3.153.254',NULL,NULL,NULL,'false',0,'int-sub-918','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('919',NULL,'c','4','10.3.154.0/24','10.3.154.1','10.3.154.2','10.3.154.254',NULL,NULL,NULL,'false',0,'int-sub-919','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('920',NULL,'c','4','10.3.155.0/24','10.3.155.1','10.3.155.2','10.3.155.254',NULL,NULL,NULL,'false',0,'int-sub-920','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('921',NULL,'c','4','10.3.156.0/24','10.3.156.1','10.3.156.2','10.3.156.254',NULL,NULL,NULL,'false',0,'int-sub-921','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('922',NULL,'c','4','10.3.157.0/24','10.3.157.1','10.3.157.2','10.3.157.254',NULL,NULL,NULL,'false',0,'int-sub-922','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('923',NULL,'c','4','10.3.158.0/24','10.3.158.1','10.3.158.2','10.3.158.254',NULL,NULL,NULL,'false',0,'int-sub-923','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('924',NULL,'c','4','10.3.159.0/24','10.3.159.1','10.3.159.2','10.3.159.254',NULL,NULL,NULL,'false',0,'int-sub-924','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('925',NULL,'c','4','10.3.160.0/24','10.3.160.1','10.3.160.2','10.3.160.254',NULL,NULL,NULL,'false',0,'int-sub-925','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('926',NULL,'c','4','10.3.161.0/24','10.3.161.1','10.3.161.2','10.3.161.254',NULL,NULL,NULL,'false',0,'int-sub-926','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('927',NULL,'c','4','10.3.162.0/24','10.3.162.1','10.3.162.2','10.3.162.254',NULL,NULL,NULL,'false',0,'int-sub-927','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('928',NULL,'c','4','10.3.163.0/24','10.3.163.1','10.3.163.2','10.3.163.254',NULL,NULL,NULL,'false',0,'int-sub-928','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('929',NULL,'c','4','10.3.164.0/24','10.3.164.1','10.3.164.2','10.3.164.254',NULL,NULL,NULL,'false',0,'int-sub-929','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('930',NULL,'c','4','10.3.165.0/24','10.3.165.1','10.3.165.2','10.3.165.254',NULL,NULL,NULL,'false',0,'int-sub-930','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('931',NULL,'c','4','10.3.166.0/24','10.3.166.1','10.3.166.2','10.3.166.254',NULL,NULL,NULL,'false',0,'int-sub-931','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('932',NULL,'c','4','10.3.167.0/24','10.3.167.1','10.3.167.2','10.3.167.254',NULL,NULL,NULL,'false',0,'int-sub-932','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('933',NULL,'c','4','10.3.168.0/24','10.3.168.1','10.3.168.2','10.3.168.254',NULL,NULL,NULL,'false',0,'int-sub-933','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('934',NULL,'c','4','10.3.169.0/24','10.3.169.1','10.3.169.2','10.3.169.254',NULL,NULL,NULL,'false',0,'int-sub-934','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('935',NULL,'c','4','10.3.170.0/24','10.3.170.1','10.3.170.2','10.3.170.254',NULL,NULL,NULL,'false',0,'int-sub-935','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('936',NULL,'c','4','10.3.171.0/24','10.3.171.1','10.3.171.2','10.3.171.254',NULL,NULL,NULL,'false',0,'int-sub-936','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('937',NULL,'c','4','10.3.172.0/24','10.3.172.1','10.3.172.2','10.3.172.254',NULL,NULL,NULL,'false',0,'int-sub-937','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('938',NULL,'c','4','10.3.173.0/24','10.3.173.1','10.3.173.2','10.3.173.254',NULL,NULL,NULL,'false',0,'int-sub-938','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('939',NULL,'c','4','10.3.174.0/24','10.3.174.1','10.3.174.2','10.3.174.254',NULL,NULL,NULL,'false',0,'int-sub-939','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('940',NULL,'c','4','10.3.175.0/24','10.3.175.1','10.3.175.2','10.3.175.254',NULL,NULL,NULL,'false',0,'int-sub-940','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('941',NULL,'c','4','10.3.176.0/24','10.3.176.1','10.3.176.2','10.3.176.254',NULL,NULL,NULL,'false',0,'int-sub-941','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('942',NULL,'c','4','10.3.177.0/24','10.3.177.1','10.3.177.2','10.3.177.254',NULL,NULL,NULL,'false',0,'int-sub-942','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('943',NULL,'c','4','10.3.178.0/24','10.3.178.1','10.3.178.2','10.3.178.254',NULL,NULL,NULL,'false',0,'int-sub-943','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('944',NULL,'c','4','10.3.179.0/24','10.3.179.1','10.3.179.2','10.3.179.254',NULL,NULL,NULL,'false',0,'int-sub-944','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('945',NULL,'c','4','10.3.180.0/24','10.3.180.1','10.3.180.2','10.3.180.254',NULL,NULL,NULL,'false',0,'int-sub-945','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('946',NULL,'c','4','10.3.181.0/24','10.3.181.1','10.3.181.2','10.3.181.254',NULL,NULL,NULL,'false',0,'int-sub-946','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('947',NULL,'c','4','10.3.182.0/24','10.3.182.1','10.3.182.2','10.3.182.254',NULL,NULL,NULL,'false',0,'int-sub-947','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('948',NULL,'c','4','10.3.183.0/24','10.3.183.1','10.3.183.2','10.3.183.254',NULL,NULL,NULL,'false',0,'int-sub-948','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('949',NULL,'c','4','10.3.184.0/24','10.3.184.1','10.3.184.2','10.3.184.254',NULL,NULL,NULL,'false',0,'int-sub-949','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('950',NULL,'c','4','10.3.185.0/24','10.3.185.1','10.3.185.2','10.3.185.254',NULL,NULL,NULL,'false',0,'int-sub-950','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('951',NULL,'c','4','10.3.186.0/24','10.3.186.1','10.3.186.2','10.3.186.254',NULL,NULL,NULL,'false',0,'int-sub-951','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('952',NULL,'c','4','10.3.187.0/24','10.3.187.1','10.3.187.2','10.3.187.254',NULL,NULL,NULL,'false',0,'int-sub-952','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('953',NULL,'c','4','10.3.188.0/24','10.3.188.1','10.3.188.2','10.3.188.254',NULL,NULL,NULL,'false',0,'int-sub-953','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('954',NULL,'c','4','10.3.189.0/24','10.3.189.1','10.3.189.2','10.3.189.254',NULL,NULL,NULL,'false',0,'int-sub-954','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('955',NULL,'c','4','10.3.190.0/24','10.3.190.1','10.3.190.2','10.3.190.254',NULL,NULL,NULL,'false',0,'int-sub-955','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('956',NULL,'c','4','10.3.191.0/24','10.3.191.1','10.3.191.2','10.3.191.254',NULL,NULL,NULL,'false',0,'int-sub-956','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('957',NULL,'c','4','10.3.192.0/24','10.3.192.1','10.3.192.2','10.3.192.254',NULL,NULL,NULL,'false',0,'int-sub-957','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('958',NULL,'c','4','10.3.193.0/24','10.3.193.1','10.3.193.2','10.3.193.254',NULL,NULL,NULL,'false',0,'int-sub-958','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('959',NULL,'c','4','10.3.194.0/24','10.3.194.1','10.3.194.2','10.3.194.254',NULL,NULL,NULL,'false',0,'int-sub-959','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('960',NULL,'c','4','10.3.195.0/24','10.3.195.1','10.3.195.2','10.3.195.254',NULL,NULL,NULL,'false',0,'int-sub-960','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('961',NULL,'c','4','10.3.196.0/24','10.3.196.1','10.3.196.2','10.3.196.254',NULL,NULL,NULL,'false',0,'int-sub-961','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('962',NULL,'c','4','10.3.197.0/24','10.3.197.1','10.3.197.2','10.3.197.254',NULL,NULL,NULL,'false',0,'int-sub-962','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('963',NULL,'c','4','10.3.198.0/24','10.3.198.1','10.3.198.2','10.3.198.254',NULL,NULL,NULL,'false',0,'int-sub-963','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('964',NULL,'c','4','10.3.199.0/24','10.3.199.1','10.3.199.2','10.3.199.254',NULL,NULL,NULL,'false',0,'int-sub-964','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('965',NULL,'c','4','10.3.200.0/24','10.3.200.1','10.3.200.2','10.3.200.254',NULL,NULL,NULL,'false',0,'int-sub-965','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('966',NULL,'c','4','10.3.201.0/24','10.3.201.1','10.3.201.2','10.3.201.254',NULL,NULL,NULL,'false',0,'int-sub-966','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('967',NULL,'c','4','10.3.202.0/24','10.3.202.1','10.3.202.2','10.3.202.254',NULL,NULL,NULL,'false',0,'int-sub-967','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('968',NULL,'c','4','10.3.203.0/24','10.3.203.1','10.3.203.2','10.3.203.254',NULL,NULL,NULL,'false',0,'int-sub-968','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('969',NULL,'c','4','10.3.204.0/24','10.3.204.1','10.3.204.2','10.3.204.254',NULL,NULL,NULL,'false',0,'int-sub-969','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('970',NULL,'c','4','10.3.205.0/24','10.3.205.1','10.3.205.2','10.3.205.254',NULL,NULL,NULL,'false',0,'int-sub-970','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('971',NULL,'c','4','10.3.206.0/24','10.3.206.1','10.3.206.2','10.3.206.254',NULL,NULL,NULL,'false',0,'int-sub-971','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('972',NULL,'c','4','10.3.207.0/24','10.3.207.1','10.3.207.2','10.3.207.254',NULL,NULL,NULL,'false',0,'int-sub-972','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('973',NULL,'c','4','10.3.208.0/24','10.3.208.1','10.3.208.2','10.3.208.254',NULL,NULL,NULL,'false',0,'int-sub-973','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('974',NULL,'c','4','10.3.209.0/24','10.3.209.1','10.3.209.2','10.3.209.254',NULL,NULL,NULL,'false',0,'int-sub-974','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('975',NULL,'c','4','10.3.210.0/24','10.3.210.1','10.3.210.2','10.3.210.254',NULL,NULL,NULL,'false',0,'int-sub-975','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('976',NULL,'c','4','10.3.211.0/24','10.3.211.1','10.3.211.2','10.3.211.254',NULL,NULL,NULL,'false',0,'int-sub-976','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('977',NULL,'c','4','10.3.212.0/24','10.3.212.1','10.3.212.2','10.3.212.254',NULL,NULL,NULL,'false',0,'int-sub-977','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('978',NULL,'c','4','10.3.213.0/24','10.3.213.1','10.3.213.2','10.3.213.254',NULL,NULL,NULL,'false',0,'int-sub-978','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('979',NULL,'c','4','10.3.214.0/24','10.3.214.1','10.3.214.2','10.3.214.254',NULL,NULL,NULL,'false',0,'int-sub-979','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('980',NULL,'c','4','10.3.215.0/24','10.3.215.1','10.3.215.2','10.3.215.254',NULL,NULL,NULL,'false',0,'int-sub-980','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('981',NULL,'c','4','10.3.216.0/24','10.3.216.1','10.3.216.2','10.3.216.254',NULL,NULL,NULL,'false',0,'int-sub-981','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('982',NULL,'c','4','10.3.217.0/24','10.3.217.1','10.3.217.2','10.3.217.254',NULL,NULL,NULL,'false',0,'int-sub-982','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('983',NULL,'c','4','10.3.218.0/24','10.3.218.1','10.3.218.2','10.3.218.254',NULL,NULL,NULL,'false',0,'int-sub-983','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('984',NULL,'c','4','10.3.219.0/24','10.3.219.1','10.3.219.2','10.3.219.254',NULL,NULL,NULL,'false',0,'int-sub-984','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('985',NULL,'c','4','10.3.220.0/24','10.3.220.1','10.3.220.2','10.3.220.254',NULL,NULL,NULL,'false',0,'int-sub-985','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('986',NULL,'c','4','10.3.221.0/24','10.3.221.1','10.3.221.2','10.3.221.254',NULL,NULL,NULL,'false',0,'int-sub-986','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('987',NULL,'c','4','10.3.222.0/24','10.3.222.1','10.3.222.2','10.3.222.254',NULL,NULL,NULL,'false',0,'int-sub-987','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('988',NULL,'c','4','10.3.223.0/24','10.3.223.1','10.3.223.2','10.3.223.254',NULL,NULL,NULL,'false',0,'int-sub-988','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('989',NULL,'c','4','10.3.224.0/24','10.3.224.1','10.3.224.2','10.3.224.254',NULL,NULL,NULL,'false',0,'int-sub-989','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('990',NULL,'c','4','10.3.225.0/24','10.3.225.1','10.3.225.2','10.3.225.254',NULL,NULL,NULL,'false',0,'int-sub-990','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('991',NULL,'c','4','10.3.226.0/24','10.3.226.1','10.3.226.2','10.3.226.254',NULL,NULL,NULL,'false',0,'int-sub-991','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('992',NULL,'c','4','10.3.227.0/24','10.3.227.1','10.3.227.2','10.3.227.254',NULL,NULL,NULL,'false',0,'int-sub-992','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('993',NULL,'c','4','10.3.228.0/24','10.3.228.1','10.3.228.2','10.3.228.254',NULL,NULL,NULL,'false',0,'int-sub-993','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('994',NULL,'c','4','10.3.229.0/24','10.3.229.1','10.3.229.2','10.3.229.254',NULL,NULL,NULL,'false',0,'int-sub-994','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('995',NULL,'c','4','10.3.230.0/24','10.3.230.1','10.3.230.2','10.3.230.254',NULL,NULL,NULL,'false',0,'int-sub-995','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('996',NULL,'c','4','10.3.231.0/24','10.3.231.1','10.3.231.2','10.3.231.254',NULL,NULL,NULL,'false',0,'int-sub-996','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('997',NULL,'c','4','10.3.232.0/24','10.3.232.1','10.3.232.2','10.3.232.254',NULL,NULL,NULL,'false',0,'int-sub-997','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('998',NULL,'c','4','10.3.233.0/24','10.3.233.1','10.3.233.2','10.3.233.254',NULL,NULL,NULL,'false',0,'int-sub-998','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('999',NULL,'c','4','10.3.234.0/24','10.3.234.1','10.3.234.2','10.3.234.254',NULL,NULL,NULL,'false',0,'int-sub-999','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1000',NULL,'c','4','10.3.235.0/24','10.3.235.1','10.3.235.2','10.3.235.254',NULL,NULL,NULL,'false',0,'int-sub-1000','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1001',NULL,'c','4','10.3.236.0/24','10.3.236.1','10.3.236.2','10.3.236.254',NULL,NULL,NULL,'false',0,'int-sub-1001','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1002',NULL,'c','4','10.3.237.0/24','10.3.237.1','10.3.237.2','10.3.237.254',NULL,NULL,NULL,'false',0,'int-sub-1002','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1003',NULL,'c','4','10.3.238.0/24','10.3.238.1','10.3.238.2','10.3.238.254',NULL,NULL,NULL,'false',0,'int-sub-1003','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1004',NULL,'c','4','10.3.239.0/24','10.3.239.1','10.3.239.2','10.3.239.254',NULL,NULL,NULL,'false',0,'int-sub-1004','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1005',NULL,'c','4','10.3.240.0/24','10.3.240.1','10.3.240.2','10.3.240.254',NULL,NULL,NULL,'false',0,'int-sub-1005','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1006',NULL,'c','4','10.3.241.0/24','10.3.241.1','10.3.241.2','10.3.241.254',NULL,NULL,NULL,'false',0,'int-sub-1006','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1007',NULL,'c','4','10.3.242.0/24','10.3.242.1','10.3.242.2','10.3.242.254',NULL,NULL,NULL,'false',0,'int-sub-1007','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1008',NULL,'c','4','10.3.243.0/24','10.3.243.1','10.3.243.2','10.3.243.254',NULL,NULL,NULL,'false',0,'int-sub-1008','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1009',NULL,'c','4','10.3.244.0/24','10.3.244.1','10.3.244.2','10.3.244.254',NULL,NULL,NULL,'false',0,'int-sub-1009','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1010',NULL,'c','4','10.3.245.0/24','10.3.245.1','10.3.245.2','10.3.245.254',NULL,NULL,NULL,'false',0,'int-sub-1010','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1011',NULL,'c','4','10.3.246.0/24','10.3.246.1','10.3.246.2','10.3.246.254',NULL,NULL,NULL,'false',0,'int-sub-1011','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1012',NULL,'c','4','10.3.247.0/24','10.3.247.1','10.3.247.2','10.3.247.254',NULL,NULL,NULL,'false',0,'int-sub-1012','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1013',NULL,'c','4','10.3.248.0/24','10.3.248.1','10.3.248.2','10.3.248.254',NULL,NULL,NULL,'false',0,'int-sub-1013','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1014',NULL,'c','4','10.3.249.0/24','10.3.249.1','10.3.249.2','10.3.249.254',NULL,NULL,NULL,'false',0,'int-sub-1014','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1015',NULL,'c','4','10.3.250.0/24','10.3.250.1','10.3.250.2','10.3.250.254',NULL,NULL,NULL,'false',0,'int-sub-1015','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1016',NULL,'c','4','10.3.251.0/24','10.3.251.1','10.3.251.2','10.3.251.254',NULL,NULL,NULL,'false',0,'int-sub-1016','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1017',NULL,'c','4','10.3.252.0/24','10.3.252.1','10.3.252.2','10.3.252.254',NULL,NULL,NULL,'false',0,'int-sub-1017','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1018',NULL,'c','4','10.3.253.0/24','10.3.253.1','10.3.253.2','10.3.253.254',NULL,NULL,NULL,'false',0,'int-sub-1018','255.255.255.0');"
psql -U postgres -d transcirrus -c "INSERT INTO trans_subnets VALUES('1019',NULL,'c','4','10.3.254.0/24','10.3.254.1','10.3.254.2','10.3.254.254',NULL,NULL,NULL,'false',0,'int-sub-1019','255.255.255.0');"


echo "NODE_ID='"${NODEID}"'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "NODE_NAME='"${HOSTNAME}"'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "NODE_TYPE='cc'" >> /usr/local/lib/python2.7/transcirrus/common/config.py

echo "TRANSCIRRUS_DB='172.24.24.10'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "TRAN_DB_USER='transuser'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "TRAN_DB_PASS='transcirrus1'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "TRAN_DB_NAME='transcirrus'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "TRAN_DB_PORT='5432'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "UPLINK_IP='0.0.0.0'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "CLUSTER_IP='"${IP}"'" >> /usr/local/lib/python2.7/transcirrus/common/config.py

#change during setup if needed from DB vars
echo "ADMIN_TOKEN='"${ADMIN_TOKEN}"'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "API_IP='"${CONTROLLER_INTERNAL_ADDRESS}"'" >> /usr/local/lib/python2.7/transcirrus/common/config.py

#change this, update as neccessary from setup operation
echo "CLOUD_CONTROLLER='"${HOSTNAME}"'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "CLOUD_CONTROLLER_ID='"${NODEID}"'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "CLOUD_NAME='TransCirrusCloud'" >> /usr/local/lib/python2.7/transcirrus/common/config.py

#DEFAULT openstack roles
echo "MEMBER_ROLE_ID='"${MEMBER_ROLE}"'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "ADMIN_ROLE_ID='"${ADMIN_ROLE}"'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "DEF_MEMBER_ROLE_ID='"${DEF_MEM_ROLE}"'" >> /usr/local/lib/python2.7/transcirrus/common/config.py

#this needs to be added when initial setup is done
#echo 'DEFAULT_PUB_NET_ID="a1c45bf0-af33-4fa0-b53a-5bd4f9d3276e"'>> /usr/local/lib/python2.7/dist-packages/transcirrus/common/config.py

##DEFAULT OPENSTACK DB SETTINGS##
echo "OS_DB='172.24.24.10'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "OS_DB_PORT='5432'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "OS_DB_USER='transuser'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "OS_DB_PASS='transcirrus1'" >> /usr/local/lib/python2.7/transcirrus/common/config.py
echo "MGMT_IP='192.168.0.3'" >> /usr/local/lib/python2.7/transcirrus/common/config.py


#Format the raid 6 as xfs - ssd
parted -s -a optimal /dev/sdb mklabel gpt -- mkpart primary xfs 1 -1
mkfs -t xfs /dev/sdb1

#Format the raid 6 as xfs - spindle
parted -s -a optimal /dev/sdc mklabel gpt -- mkpart primary xfs 1 -1
mkfs -t xfs /dev/sdc1

#set up glusterFS
mkdir -p /data/gluster
mkdir -p /data/gluster-spindle

echo '/dev/sdb1 /data/gluster xfs defaults 1 2' >> /etc/fstab
echo '/dev/sdc1 /data/gluster-spindle xfs defaults 1 2' >> /etc/fstab
mount -a && mount

#gluster log
mkdir -p /var/log/glusterfs/

#gluster mount dir
mkdir -p /mnt/gluster-vols/cinder-volume
chown -R cinder:cinder /mnt/gluster-vols/cinder-volume

#open ports in the firewall 
for x in {'111','24007','24008','24009','24010','24011','24012','24013','24014','24015','24016','24017','24018','24019','24020','24021','24022','24023','24025','24026','24027','24028','24029','34865','34866','34867'}
do
    iptables -A INPUT -p tcp --dport ${x} -j ACCEPT
    iptables -A INPUT -p udp --dport ${x} -j ACCEPT
done

iptables-save >> /transcirrus/iptables.rules

#install pylons
#easy_install pylons

#add libffi-devel
wget -P /root http://192.168.10.10/rhat_ic/ciac_files/libffi-devel-3.0.5-3.2.el6.x86_64.rpm
rpm -ivh /root/libffi-devel-3.0.5-3.2.el6.x86_64.rpm

#build swift 1.13.1
#wget -P /root http://192.168.10.10/rhat_ic/ciac_files/swift-1.13.1.tar.gz
#tar -zxvf /root/swift-1.13.1.tar.gz -C /root
#cd /root/swift-1.13.1
#python ./setup.py build
#python ./setup.py install

#wget -P /root http://192.168.10.10/rhat_ic/gluster/gluster-swift-1.13.1-2.tar
#tar -xvf /root/gluster-swift-1.13.1-2.tar -C /root
wget -P /root http://192.168.10.10/rhat_ic/gluster/swiftonfile-1.13.1-2.tar
tar -xvf /root/swiftonfile-1.13.1-2.tar -C /root
cd /root/swiftonfile-1.13.1-2
python ./setup.py install
cd /root/swiftonfile-1.13.1-2/etc/
mv /etc/swift/account-server.conf /etc/swift/account-server.conf.old
mv /etc/swift/container-server.conf /etc/swift/container-server.conf.old
mv /etc/swift/object-server.conf /etc/swift/object-server.conf.old
mv /etc/swift/proxy-server.conf /etc/swift/proxy-server.conf.old
mv /etc/swift/swift.conf /etc/swift/swift.conf.old
#move gluster swift files into place
mv /root/swiftonfile-1.13.1-2/etc/account-server.conf-gluster /etc/swift/account-server.conf
mv /root/swiftonfile-1.13.1-2/etc/container-server.conf-gluster /etc/swift/container-server.conf
mv /root/swiftonfile-1.13.1-2/etc/object-server.conf-gluster /etc/swift/object-server.conf
mv /root/swiftonfile-1.13.1-2/etc/proxy-server.conf-gluster /etc/swift/proxy-server.conf
mv /root/swiftonfile-1.13.1-2/etc/swift.conf-gluster /etc/swift/swift.conf


#create the gluster brick
sleep 1
#get some services ready for gluster/swift
chkconfig memcached on
service memcached start

#get the new /etc/glusterfs/glusterd.vol
mv /etc/glusterfs/glusterd.vol /etc/glusterfs/glusterd.old
wget -P /etc/glusterfs/ http://192.168.10.10/rhat_ic/gluster/glusterd.vol

chkconfig glusterfsd on
service glusterfsd start

chkconfig glusterd on
service glusterd start

#create the cinder volume
gluster volume create cinder-volume-ssd 172.24.24.10:/data/gluster/cinder-volume-ssd
gluster volume start cinder-volume-ssd
gluster vol set cinder-volume-ssd storage.owner-uid 165
gluster vol set cinder-volume-ssd storage.owner-gid 165
gluster vol set cinder-volume-ssd network.remote-dio enable
gluster vol set cinder-volume-ssd cluster.eager-lock enable
gluster vol set cinder-volume-ssd performance.stat-prefetch off
gluster vol set cinder-volume-ssd performance.read-ahead off
gluster vol set cinder-volume-ssd performance.quick-read off
gluster vol set cinder-volume-ssd performance.io-cache off
gluster vol set cinder-volume-ssd server.allow-insecure on

chmod 775 /data/gluster
chown -R cinder:cinder /data/gluster

gluster volume create cinder-volume-spindle 172.24.24.10:/data/gluster-spindle/cinder-volume-spindle
gluster volume start cinder-volume-spindle
gluster vol set cinder-volume-spindle storage.owner-uid 165
gluster vol set cinder-volume-spindle storage.owner-gid 165
gluster vol set cinder-volume-spindle network.remote-dio enable
gluster vol set cinder-volume-spindle cluster.eager-lock enable
gluster vol set cinder-volume-spindle performance.stat-prefetch off
gluster vol set cinder-volume-spindle performance.read-ahead off
gluster vol set cinder-volume-spindle performance.quick-read off
gluster vol set cinder-volume-spindle performance.io-cache off
gluster vol set cinder-volume-spindle server.allow-insecure on

chmod 775 /data/gluster-spindle
chown -R cinder:cinder /data/gluster-spindle


gluster volume create instances 172.24.24.10:/data/gluster/instances
gluster volume start instances
mount -t glusterfs 172.24.24.10:/instances /var/lib/nova/instances
gluster vol set instances storage.owner-uid 162
gluster vol set instances storage.owner-gid 162
gluster vol set instances network.remote-dio enable
gluster vol set instances cluster.eager-lock enable
gluster vol set instances performance.stat-prefetch off
gluster vol set instances performance.read-ahead off
gluster vol set instances performance.quick-read off
gluster vol set instances performance.io-cache off

echo '172.24.24.10:/instances /var/lib/nova/instances glusterfs defaults,_netdev 0 0' >> /etc/fstab
chown -R nova:nova /var/lib/nova/instances
echo 'chown -R nova:nova /var/lib/nova/instances' >> /etc/rc.local

gluster volume create glance 172.24.24.10:/data/gluster-spindle/glance
gluster volume start glance
mount -t glusterfs 172.24.24.10:/glance /var/lib/glance
gluster vol set glance storage.owner-uid 161
gluster vol set glance storage.owner-gid 99
gluster vol set glance network.remote-dio enable
gluster vol set glance cluster.eager-lock enable
gluster vol set glance performance.stat-prefetch off
gluster vol set glance performance.read-ahead off
gluster vol set glance performance.quick-read off
gluster vol set glance performance.io-cache off

echo '172.24.24.10:/glance /var/lib/glance glusterfs defaults,_netdev 0 0' >> /etc/fstab
chown -R glance:nobody /var/lib/glance
echo 'chown glance:nobody /var/lib/glance' >> /etc/rc.local

#turn on swift
chkconfig openstack-swift-proxy on
chkconfig openstack-swift-account on
chkconfig openstack-swift-container on
chkconfig openstack-swift-object on

#set up disks for swift object storage
gluster-swift-gen-builders storage

service openstack-swift-object start
service openstack-swift-container start
service openstack-swift-account start
service openstack-swift-proxy start

#build the swift endpoint
SWIFT_SERVICE=$(keystone service-create --name=swift \
                        --type=object-store \
                        --description="OpenStack Object Storage" | grep " id " | get_field 2)
if [[ -z "$DISABLE_ENDPOINTS" ]]; then
    keystone endpoint-create --region TransCirrusCloud --service-id $SWIFT_SERVICE \
        --publicurl 'http://'"$CONTROLLER_PUBLIC_ADDRESS"':8080/v1/AUTH_$(tenant_id)s' \
        --adminurl 'http://'"$CONTROLLER_ADMIN_ADDRESS"':8080/v1' \
        --internalurl 'http://'"$CONTROLLER_INTERNAL_ADDRESS"':8080/v1/AUTH_$(tenant_id)s'
fi

psql -U postgres -d transcirrus -c "UPDATE trans_service_settings SET service_id='"${SWIFT_SERVICE}"',service_admin_ip='"${CONTROLLER_PUBLIC_ADDRESS}"',service_int_ip='"${CONTROLLER_PUBLIC_ADDRESS}"',service_public_ip='"${CONTROLLER_PUBLIC_ADDRESS}"',service_endpoint_id='"${SWIFT_ENDPOINT}"' WHERE service_port=8080;"

mv /etc/sysctl.conf /etc/sysctl.conf.old
wget -P /etc http://192.168.10.10/rhat_ic/ciac_files/sysctl.conf
chown root:root /etc/sysctl.conf
chmod 644 /etc/sysctl.conf
sysctl -e -p /etc/sysctl.conf

wget -P /etc http://192.168.10.10/rhat_ic/ciac_files/dhclient.conf
chmod root:root /etc/dhclient.conf
chmod 644 /etc/dhclient.conf

#zero connect startup
wget -P /etc/init.d http://192.168.10.10/rhat_ic/ciac_files/zero_connect
chmod 755 /etc/init.d/zero_connect
chown root:root /etc/init.d/zero_connect
#turn on zero connect
chkconfig --levels 235 zero_connect on

#ceilometer deamon
cp /usr/local/lib/python2.7/transcirrus/daemons/ceilometer_memory_patch /etc/init.d
chmod 755 /etc/init.d/ceilometer_memory_patch
chmod 755 /usr/local/lib/python2.7/transcirrus/daemons/ceilometer_memory_patch
chown root:root /etc/init.d/ceilometer_memory_patch
#turn on zero connect
chkconfig --levels 235 ceilometer_memory_patch on

#move the openstack interface file out of conf.d
mv /etc/httpd/conf.d/openstack-dashboard.conf ..

#install mod_wsgi
rm -rf /usr/lib64/httpd/modules/mod_wsgi.so
wget -P /root http://192.168.10.10/rhat_ic/ciac_files/mod_wsgi-3.3.tar.gz
tar -zxvf /root/mod_wsgi-3.3.tar.gz -C /root
cd /root/mod_wsgi-3.3
./configure --with-python=/usr/local/bin/python2.7
make
make install

usermod -s /bin/bash nova
#Add the ssh key for nova
wget -P /root http://192.168.10.10/rhat_ic/common/ssh.tar
tar -xvf /root/ssh.tar -C /var/lib/nova

# Load mod wsgi
touch /etc/httpd/conf.d/wsgi.conf
echo "LoadModule wsgi_module modules/mod_wsgi.so" >> /etc/httpd/conf.d/wsgi.conf

#get the web/django server config
wget -P /etc/httpd/conf.d http://192.168.10.10/rhat_ic/ciac_files/transcirrus.conf
chmod 644 /etc/httpd/conf.d/transcirrus.conf
chown root:root /etc/httpd/conf.d/transcirrus.conf

#replace wsgi.so pointer
sed -i 's/modules\/mod_wsgi.so/\/usr\/lib64\/httpd\/modules\/mod_wsgi.so/' /etc/httpd/conf.d/wsgi.conf

#change doc root to /opt/Coalesce
sed -i 's/DocumentRoot \"\/var\/www\/html\"/DocumentRoot \"\/opt\/Coalesce\"/' /etc/httpd/conf/httpd.conf

#turn on openvswitch
chkconfig openvswitch on
service openvswitch start

#set up br-ex
sed -i 's/TYPE=\"Bridge\"/TYPE=\"OVSBridge\"/' /etc/sysconfig/network-scripts/ifcfg-br-ex
#echo 'DEVICETYPE="ovs"' >> /etc/sysconfig/network-scripts/ifcfg-br-ex
sleep 2

sed -i 's/BRIDGE=\"br-ex\"/#BRIDGE=\"br-ex\"/' /etc/sysconfig/network-scripts/ifcfg-eth2
sed -i 's/HWADDR=/#HWADDR=/' /etc/sysconfig/network-scripts/ifcfg-eth2
#sed -i 's/HWADDR=/#HWADDR=/' /etc/sysconfig/network-scripts/ifcfg-eth7

#create a link to the updater in transuser home
ln -s /usr/local/lib/python2.7/transcirrus/operations/upgrade.py /home/transuser/upgrade.py
#roll up the support
ln -s /usr/local/lib/python2.7/transcirrus/operations/support_create.py /home/transuser/support_create.py

#purge old tokens every hour
(crontab -l -u keystone 2>&1 | grep -q token_flush) || echo '@hourly /usr/bin/keystone-manage token_flush >/var/log/keystone/keystone-tokenflush.log 2>&1' >> /var/spool/cron/keystone

#Fix monit
python2.7 /usr/local/lib/python2.7/transcirrus/operations/monit/fix_monit_conf.py cc

#put ovs-command in rc.local
ip link set eth2 promisc on
#ip link set eth7 promisc on
ovs-vsctl add-br br-ex

#change glance
chmod 775 /var/lib/glance/images

#create promisc script
echo '#!/bin/bash' >> /transcirrus/promisc
echo 'ip link set eth2 promisc on' >> /transcirrus/promisc
#echo 'ip link set eth7 promisc on' >> /transcirrus/promisc
echo 'ovs-vsctl add-port br-ex eth2' >> /transcirrus/promisc
chmod 775 /transcirrus/promisc


echo 'mount -a' >> /etc/rc.local
echo 'source /transcirrus/promisc' >> /etc/rc.local
echo 'iptables-restore < /transcirrus/iptables.rules' >> /etc/rc.local
echo 'chmod 775 /var/lib/glance/images' >> /etc/rc.local
echo 'source /transcirrus/gluster-mounts' >> /etc/rc.local
echo 'source /transcirrus/gluster-object-mount' >> /etc/rc.local

#get rid of the raw SQL code
rm -rf /usr/local/lib/python2.7/transcirrus/SQL_files
rm -rf /usr/local/lib/python2.7/transcirrus/Coalesce

#compile the transcirrus code
#python2.7 /usr/local/lib/python2.7/transcirrus/compiler.py

#experiment - ceilometer
ln -s /usr/lib64/python2.6/site-packages/libvirt.py /usr/local/lib/python2.7/site-packages/libvirt.py
ln -s /usr/lib64/python2.6/site-packages/libvirtmod.so /usr/local/lib/python2.7/site-packages/libvirtmod.so

#cinder
mkdir Ðp /mnt/nfs-vols/cinder-volume
chown cinder:cinder /mnt/nfs-vols/cinder-volume

#update the system
yum update -y --skip-broken

#turn off unneccessary services
chkconfig postfix off
chkconfig cups off
chkconfig ip6tables off
chkconfig iscsi off
chkconfig iscsid off
chkconfig lvm2-monitor off

#Manufacturing Data
#psql -h 192.168.10.16 -U postgres -d transcirrusinternal -c "INSERT INTO manufacturing VALUES('"${NODEID}"','cc',NULL,NULL,'"${HOSTNAME}"','true','icehouse',current_date,NULL);"

#clean up roots home
rm -rf /root/*