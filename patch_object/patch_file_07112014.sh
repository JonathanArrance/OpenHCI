#!/bin/bash -x

#add new DB entries
psql -U postgres -d transcirrus -a -f ./add_gluster_table.sql
psql -U postgres -d transcirrus -c "ALTER TABLE trans_nodes ADD COLUMN node_gluster_disks varchar"


#fix file system and config stuff
#create the gluster mount file
touch /transcirrus/gluster-mounts
chmod 777 /transcirrus/gluster-mounts

#create a gluster-object mount file
touch /transcirrus/gluster-object-mount
chmod 777 /transcirrus/gluster-object-mount

echo 'source /transcirrus/gluster-mounts' >> /etc/rc.local
echo 'source /transcirrus/gluster-object-mount' >> /etc/rc.local