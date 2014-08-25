#!/bin/bash

export START_DIR=/tmp

if [ -z $1 ]
then
    export HOST=$(hostname)
else
    export HOST=$1
fi

if [ -z $2 ]
then
    export TIMESTAMP=$(date +%Y%m%d%H%M%S)
else
    export TIMESTAMP=$2
fi

# Get the nodeid. /etc/nodid is only 1 line with just the id in it.
while read line
do
    export NODEID=$line
done </etc/nodeid

# Determine our destination directory, proc and tar file for all of the data we collect.
export PHNAME=phonehome_${HOST}_${NODEID}_${TIMESTAMP}
export DUMP_DIR=${START_DIR}/${PHNAME}
export PROC_FILE=${START_DIR}/phproc_${TIMESTAMP}
export LOG_FILE=${START_DIR}/ph_${TIMESTAMP}.log
export TAR_FILE=${START_DIR}/${PHNAME}.tar.gz

#
# Put anything here that needs to happen before we start collecting data.
#
touch ${PROC_FILE}
chown transuser:transuser ${PROC_FILE}
mkdir ${DUMP_DIR}
chown transuser:transuser ${DUMP_DIR}

#
# The collecting of data goes here.
# This is placed in a code block so the output can be captured from all commands.
#

# Collect the running system data.
# We will start with sosreport since it collects most everything we want plus a lot more. We try
# to skip some of the stuff we shouldn't need. The big one is selinux which really takes a long time.
sosreport -v -a --build --diagnose --analyze --report --batch --tmp-dir=${DUMP_DIR}              \
          -k pgsql.username=transuser -k pgsql.password=transcirrus1 -k pgsql.dbname=transcirrus \
          -k pgsql.dbport=5432 -k pgsql.dbhost=localhost                                         \
          --skip-plugins=acpid,cgroups,dovecot,foreman,gdm,hts,i18n,iscsi,iscsitarget,krb5,ldap  \
          --skip-plugins=mrggrid,mrgmessg,mysql,openhpi,printing,psacct,samba,sar,x11,xen,yum    \
          --skip-plugins=auditd,nfs,ntp,sunrpc,selinux,rpm

top -b -n 1 > ${DUMP_DIR}/top
vmstat > ${DUMP_DIR}/vmstat

# Get the nodeid.
cp /etc/nodeid ${DUMP_DIR}

# Get the caclogs.
cp -r /var/log/caclogs ${DUMP_DIR}/caclogs

# Get the swift-startup logs.
cp /var/log/swift-startup.log ${DUMP_DIR}

# Get the cinder logs.
cp -r /var/log/cinder ${DUMP_DIR}/cinder

# Get the glance logs.
cp -r /var/log/glance ${DUMP_DIR}/glance

# Get the monit logs.
cp -r /var/log/monit ${DUMP_DIR}/monit

# Get the nova logs.
cp -r /var/log/nova ${DUMP_DIR}/nova

# Get the keystone logs.
cp -r /var/log/keystone ${DUMP_DIR}/keystone

# Get the openvswitch logs.
cp -r /var/log/openvswitch ${DUMP_DIR}/openvswitch

#
# Put anything here that needs to happen after we have completed collecting data.
#
cp ${LOG_FILE} ${DUMP_DIR}
cp ${PROC_FILE} ${DUMP_DIR}
tar -czf ${TAR_FILE} -C ${START_DIR} ${DUMP_DIR}
chown transuser:transuser ${TAR_FILE}
rm -f ${PROC_FILE}
rm -fr ${DUMP_DIR}

exit 0
