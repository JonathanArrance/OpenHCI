##This file will be written out by values inserted into the system database
#defaults will be factory set
#file will update when local admin sets up system.
TRANSCIRRUS_DB="192.168.10.16"
TRAN_DB_USER="cacsystem"
TRAN_DB_PASS="cacsystem"
TRAN_DB_NAME="cac_system"
TRAN_DB_PORT="5432"

#change during setup if needed from DB vars
DEFAULT_ADMIN_TOKEN="cheapass"
DEFAULT_API_IP="192.168.10.30"

#change this, update as neccessary from setup operation
DEFAULT_CLOUD_CONTROLER="jon-devstack"

#DEFAULT openstack roles
DEFAULT_MEMBER_ROLE_ID="6d361bbd2a044fec9e1069b1e2cb7125"
DEFAULT_ADMIN_ROLE_ID="2cb555d6e9194092a3e526c3ad78e82d"


##PATHS##
COMPONENT_PATH="/home/jonathan/alpo.0/component"
COMMON_PATH="/home/jonathan/alpo.0/common"
DB_PATH="/home/jonathan/alpo.0/database"


##DEFAULT OPENSTACK DB SETTINGS##
OS_DB="192.168.10.30"
OS_DB_PORT="5432"

KEYSTONE_DB_NAME="keystone"
KEYSTONE_DB_USER="cacsystem"
KEYSTONE_DB_PASS="cacsystem"

NOVA_DB_NAME=""
NOVA_DB_USER=""
NOVA_DB_PASS=""

QUANTUM_DB_NAME=""
QUANTUM_DB_USER=""
QUANTUM_DB_PASS=""

CINDER_DB_NAME=""
CINDER_DB_USER=""
CINDER_DB_PASS=""

GLANCE_DB_NAME=""
GLANCE_DB_USER=""
GLANCE_DB_PASS=""