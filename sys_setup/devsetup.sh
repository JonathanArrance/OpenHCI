#!/bin/bash

#Post install script for cloud in a can system.

echo "Disableing the Ubuntu Firewall."
ufw disable

USERNAME=whoami

echo "Setting up transuser sudo."
#set the transuser account up in sudo
(
cat <<'EOP'
$USERNAME ALL=(ALL) NOPASSWD: ALL
EOP
) >> /etc/sudoers
#restart sudo
/etc/init.d/sudo restart

#add the transuser account to postgres and set the password
#used as the admin account for all transcirrus and openstack databases/tables
psql -U postgres -c "CREATE USER transuser;"
psql -U postgres -c "ALTER USER transuser WITH PASSWORD 'cheapass1!';"
