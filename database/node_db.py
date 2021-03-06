from transcirrus.database.postgres import pgsql
import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util

#pushed to alpo.1
#import transcirrus.common.status_codes as status

def check_node_exists(node_id):
    """
    DESC: Do a check if the node exists in the transcirrus system DB.
    INPUT: node_id
    OUTPUT: node_status OK/NA/ERROR
    ACCESS: Wide open. This is not an openstack level call.
    NOTES: status of OK means the node exists in the DB. Status of NA means node does not exist in the DB. ERROR is a catch all.
    """
    logger.sys_info('\n**Check if a node exists. Component: Database Def: check_node_exists**\n')
    #connect to the database
    #db = db_connect(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
    db = util.db_connect()
    try:
        find_node_dict = {'select':"node_name",'from':"trans_nodes",'where':"node_id='%s'" %(node_id)}
        node_name = db.pg_select(find_node_dict)
        db.pg_close_connection()
        if(node_name[0][0]):
            return 'OK'
        else:
            return 'ERROR'
    except:
        logger.sql_error("Could not find the node id in the Transcirrus DB.")
        return 'NA'

def get_node(node_id):
    """
    DESC: Get all of the specific information on a particular node.
    INPUT: node_id
    OUTPUT: r_dict - node_name
                    - node_type
                    - node_data_ip
                    - node_mgmt_ip
                    - node_controller
                    - node_cloud_name
                    - availability_zone
                    - node_fault_flag
                    - node_ready_flag
                    - node_gluster_peer
                    - node_disk_type
                    - status
    ACCESS: Wide open
    NOTES: Return the r_dict with a status of OK, else status code of NA or ERROR is returned outside of the ductionary.
    """
    logger.sys_info('\n**Get node info. Component: Database Def: get_node**\n')
    #connect to the database
    #db = db_connect(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
    db = util.db_connect()
    try:
        find_node_dict = {'select':"*",'from':"trans_nodes",'where':"node_id='%s'" %(node_id)}
        node = db.pg_select(find_node_dict)
        db.pg_close_connection()
        if(node[0][0] == node_id):
            r_dict = {'node_name':node[0][1],'node_type':node[0][2],'node_data_ip':node[0][4],'node_mgmt_ip':node[0][3],'node_controller':node[0][5],
                      'node_cloud_name':node[0][6],'availability_zone':node[0][7],'node_fault_flag':node[0][8],'node_ready_flag':node[0][9],'node_gluster_peer':node[0][10],'node_disk_type':node[0][11],'status':"OK"}
        else:
            return'ERROR'
    except:
        logger.sql_error("Could not find the node with ID %s in the Transcirrus DB." %(node_id))
        return 'NA'

    return r_dict

def update_nova_node():
    insert_nova_conf = {"parameter":"sql_connection","param_value":"postgresql://transuser:%s@172.24.24.10/nova",'file_name':"nova.conf",'node':"%s" %(config.MASTER_PWD,input_dict['node_id'])}
    insert_nova_ip = {"parameter":"my_ip","param_value":"%s" %(input_dict['node_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
    insert_novncproxy = {"parameter":"novncproxy_base_url","param_value":"http://%s:6080/vnc_auto.html"%(util.get_uplink_ip()),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
    insert_vncproxy = {"parameter":"vncserver_proxyclient_address","param_value":"%s" %(input_dict['node_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
    insert_vnclisten = {"parameter":"vncserver_listen","param_value":"0.0.0.0",'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
    nova_array = [insert_nova_conf,insert_nova_ip,insert_vncproxy,insert_vnclisten,insert_novncproxy]
    for nova in nova_array:
        db.pg_transaction_begin()
        db.pg_insert('nova_node',nova)
        db.pg_transaction_commit()

def insert_node(input_dict):
    #Need to add in the OVS/neutron stuff
    """
    DESC: Insert a new node into the Transcirrus DB.
    INPUT: input_dict - node_id - req - transcirrus assigned node_id
                      - node_name - req
                      - node_type - req
                      - node_mgmt_ip - req
                      - node_data_ip - req
                      - node_controller - req
                      - avail_zone - op
                      - node_cloud_name - op
                      - node_virt_type - op
                      - node_gluster_peer - op
                      - node_gluster_disks - op
    OUTPUT: OK if successful
            ERROR if not successful
            raise error
    ACCESS: wide open
    NOTES: If node count in db is 20 or greater for a particular cloud_controller new nodes will not be added to the nodes db.
           The node types are cc - cloud in a can, sn - storage node, cn - compute node.
           This function does not add a node to the openstack cloud
    """
    logger.sys_info('\n**Insert a new node into the system. Component: Database Def: insert_node**\n')
    #make sure none of the values are empty
    for key, val in input_dict.items():
        #skip over these
        if((key == 'avail_zone') or (key == 'node_virt_type') or \
                (key == 'node_cloud_name') or (key == 'node_gluster_peer') or \
                (key == 'node_mgmt_ip') or (key == 'node_controller') or (key == 'node_gluster_disks')):
            continue
        if(val == ""):
            logger.sys_error("The value %s::%s was left blank" %(key, val))
            raise Exception("The value %s::%s was left blank" %(key, val))
        if(key not in input_dict):
            logger.sys_error("Node info not specified")
            raise Exception ("Node info not specified")

    #get the db connection
    db = util.db_connect()
    #static assign nova availability zone for now
    if('avail_zone' not in input_dict):
        input_dict['avail_zone'] = 'nova'
    else:
        #check if zone given is valid.
        try:
            select_zone = {'select':'index','from':'trans_zones','where':"zone_name='%s'"%(input_dict['avail_zone'])}
            get_zone = db.pg_select(select_zone)
        except:
            logger.sql_error('The specifed zone is not defined.')
            raise Exception('The specifed zone is not defined.')

    if('node_virt_type' not in input_dict):
        input_dict['node_virt_type'] = 'qemu'
    if(input_dict['node_virt_type'] == ''):
        input_dict['node_virt_type'] = 'qemu'

    #hack to account for physical core node
    cpu_mode = None
    if(util.is_node_phy() == '1'):
        input_dict['node_virt_type'] = 'kvm'
        cpu_mode = {"parameter":"cpu_mode","param_value":"host-passthrough",'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
    elif(util.is_node_phy() == '0'):
        input_dict['node_virt_type'] = 'qemu'
        cpu_mode = {"parameter":"cpu_mode","param_value":"host-model",'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}

    if('node_gluster_peer' not in input_dict):
        input_dict['node_gluster_peer'] = '0'
    if(input_dict['node_gluster_peer'] == ''):
        input_dict['node_gluster_peer'] = '0'

    if('node_cloud_name' not in input_dict):
        input_dict['node_cloud_name'] = 'TransCirrusCloud'
    if(input_dict['node_cloud_name'] == ''):
        input_dict['node_cloud_name'] = 'TransCirrusCloud'

    if('node_gluster_disks' not in input_dict):
        input_dict['node_gluster_disks'] = 'None'
    if(input_dict['node_gluster_disks'] == ''):
        input_dict['node_gluster_disks'] = 'None'

    if(input_dict['node_type'] == 'cc'):
        input_dict['cc_data_ip'] = 'localhost'
    else:
        input_dict['cc_data_ip'] = '172.24.24.10'

    #get the cloud controllers mgmt_ip
    #this actually returns the uplink ip - this needs to be chnaged to return_uplink_ip
    cc_uplink_ip = util.get_cloud_controller_uplink_ip()

    #get the controller mgmt ip, used to set up NOvnc for intrnal use, Spice and XVPNV will be used externally
    cc_mgmt_ip = util.get_cloud_controller_mgmt_ip()

    #get the node uplink and mgmt domains
    domains = util.list_domain_names()

    #get worker count - equal to the number of procs
    #NOTE proc_info['total_cores'] = workers
    proc_info = util.getCPUInfo()

    #get the service tenant ID
    service_tenant = util.get_service_tenant_id()

    #count up the number of nodes attached to controller
    elem_dict = {'table':"trans_nodes",'where':"node_controller='%s'" %(input_dict['node_controller'])}
    count = db.count_elements(elem_dict)
    if(int(count) >= 20):
        logger.sys_error("The maximum limit of 20 nodes has been reached for controller %s" %(input_dict['node_controller']))
        raise Exception("The maximum limit of 20 nodes has been reached for controller %s" %(input_dict['node_controller']))
    else:
        logger.sys_info("Controller %s has %s nodes attached." %(input_dict['node_controller'],count))

    #insert node info into specific service dbs based on node_type
    try:
        insert_ceil_db = {'parameter':"connection",'param_value':"mongodb://ceilometer:%s@%s:27017/ceilometer"%(config.MASTER_PWD,input_dict['cc_data_ip']),'file_name':"ceilometer.conf",'node':"%s" %(input_dict['node_id'])}
        insert_ceil_rabbit = {'parameter':"rabbit_host",'param_value':"%s"%(input_dict['cc_data_ip']),'file_name':"ceilometer.conf",'node':"%s" %(input_dict['node_id'])}
        insert_ceil_auth_host_api = {'parameter':"auth_host",'param_value':"%s"%(input_dict['cc_data_ip']),'file_name':"ceilometer.conf",'node':"%s" %(input_dict['node_id'])}
        insert_ceil_auth_uri = {'parameter':"auth_uri",'param_value':"http://%s:5000"%(input_dict['cc_data_ip']),'file_name':"ceilometer.conf",'node':"%s" %(input_dict['node_id'])}
        insert_ceil_memcached = {'parameter':"memcached_servers",'param_value':"%s:11211"%(input_dict['cc_data_ip']),'file_name':"ceilometer.conf",'node':"%s" %(input_dict['node_id'])}
        insert_ceil_osauth_uri = {'parameter':"os_auth_url",'param_value':"http://%s:5000/v2.0"%(input_dict['cc_data_ip']),'file_name':"ceilometer.conf",'node':"%s" %(input_dict['node_id'])}
        insert_ceil_cworkers = {'parameter':'collector_workers','param_value':"%s"%(proc_info['total_cores']),'file_name':"ceilometer.conf",'node':"%s" %(input_dict['node_id'])}
        insert_ceil_nworkers = {'parameter':'notification_workers','param_value':"%s"%(proc_info['total_cores']),'file_name':"ceilometer.conf",'node':"%s" %(input_dict['node_id'])}
        insert_ceil_virt = {'parameter':"libvirt_type",'param_value':"%s"%(input_dict['node_virt_type']),'file_name':"ceilometer.conf",'node':"%s" %(input_dict['node_id'])}
        insert_ceil_host = {"parameter":"host","param_value":"%s" %(input_dict['node_name']),'file_name':"ceilometer.conf",'node':"%s" %(input_dict['node_id'])}
        ceil_array = [insert_ceil_db,insert_ceil_rabbit,insert_ceil_auth_host_api,insert_ceil_auth_uri,insert_ceil_memcached,insert_ceil_osauth_uri,insert_ceil_cworkers,insert_ceil_nworkers,insert_ceil_virt,insert_ceil_host]
        for ceil in ceil_array:
            db.pg_transaction_begin()
            db.pg_insert('ceilometer_node',ceil)
            db.pg_transaction_commit()
    except:
        db.pg_transaction_rollback()
        logger.sql_error("Could not insert node specific ceilometer config into TransCirrus db.")
        return 'ERROR'

    if(input_dict['node_type'] == 'cc'):
        try:
            #glance workers
            #insert_glance_workers = {'parameter':'workers','param_value':"%s"%(proc_info['total_cores']),'host_name':"%s"%(input_dict['node_id']),'file_name':'glance-api.conf','index':'48'}
            insert_glance_db = {'parameter':"connection",'param_value':"postgresql://transuser:%s@%s/glance"%(config.MASTER_PWD,input_dict['cc_data_ip']),'file_name':"glance-registry.conf",'host_name':"%s" %(input_dict['node_id'])}
            insert_glance_db2 = {'parameter':"connection",'param_value':"postgresql://transuser:%s@%s/glance"%(config.MASTER_PWD,input_dict['cc_data_ip']),'file_name':"glance-api.conf",'host_name':"%s" %(input_dict['node_id'])}
            glance_array = [insert_glance_db,insert_glance_db2]
            for glance in glance_array:
                db.pg_transaction_begin()
                db.pg_insert('glance_defaults',glance)
                db.pg_transaction_commit()
        except:
            db.pg_transaction_rollback()
            logger.sql_error("Could not insert node specific glance config into TransCirrus db.")
            return 'ERROR'

        try:
            insert_nova_ec2 = {'parameter':'ec2_host',"param_value":"%s"%(cc_uplink_ip),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_ec2dmz = {'parameter':'ec2_dmz_host',"param_value":"172.24.24.10",'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            ec2_array = [insert_nova_ec2,insert_nova_ec2dmz]
            for ec in ec2_array:
                db.pg_transaction_begin()
                db.pg_insert('nova_node',ec)
                db.pg_transaction_commit()
        except:
            db.pg_transaction_rollback()
            logger.sql_error("Could not insert node specific Nova EC2 config into TransCirrus db.")
            return 'ERROR'

    if((input_dict['node_type'] == 'sn') or (input_dict['node_type'] == 'cc')):
        #do the cinder config for now.
        #HACK need to add in a supersecret db password
        try:
            insert_cinderavail_zone = {'parameter':"storage_availability_zone",'param_value':"%s"%(input_dict['avail_zone']),'file_name':"cinder.conf",'node':"%s" %(input_dict['node_id'])}
            insert_cinder_db = {'parameter':"connection",'param_value':"postgresql://transuser:%s@%s/cinder"%(config.MASTER_PWD,input_dict['cc_data_ip']),'file_name':"cinder.conf",'node':"%s" %(input_dict['node_id'])}
            insert_cinder_rabbit = {'parameter':"rabbit_host",'param_value':"%s"%(input_dict['cc_data_ip']),'file_name':"cinder.conf",'node':"%s" %(input_dict['node_id'])}
            insert_cinder_auth_host = {'parameter':"auth_host",'param_value':"%s"%(input_dict['cc_data_ip']),'file_name':"cinder.conf",'node':"%s" %(input_dict['node_id'])}
            insert_cinder_auth_host_api = {'parameter':"auth_host",'param_value':"%s"%(input_dict['cc_data_ip']),'file_name':"api-paste.ini",'node':"%s" %(input_dict['node_id'])}
            insert_cinder_auth_uri = {'parameter':"auth_uri",'param_value':"%s:5000"%(input_dict['cc_data_ip']),'file_name':"cinder.conf",'node':"%s" %(input_dict['node_id'])}
            insert_cinder_auth_uri_api = {'parameter':"auth_uri",'param_value':"%s:5000"%(input_dict['cc_data_ip']),'file_name':"api-paste.ini",'node':"%s" %(input_dict['node_id'])}
            cinder_array = [insert_cinder_db,insert_cinderavail_zone,insert_cinder_rabbit,insert_cinder_auth_host,insert_cinder_auth_uri,insert_cinder_auth_uri_api,insert_cinder_auth_host_api]
            for cinder in cinder_array:
                db.pg_transaction_begin()
                db.pg_insert('cinder_node',cinder)
                db.pg_transaction_commit()
        except:
            db.pg_transaction_rollback()
            logger.sql_error("Could not insert node specific cinder config into TransCirrus db.")
            return 'ERROR'

        #set the spindle_node flag in the system config table to 1 if new disks are spindle
        check_spindle = util.get_spindle_node_enabled()
        if((input_dict['node_gluster_disks'] == 'spindle') and (check_spindle == '0')):
            controller = util.get_cloud_controller_name()
            set_spindle = {'system_name':"%s"%(controller),'parameter':"spindle_node",'param_value':"1"}
            input_array = [set_spindle]
            set_param = util.update_system_variables(input_array)
            if(set_param == 'ERROR'):
                logger.sql_error("Could not set add the spindle node to the TransCirrus cloud.")

    if((input_dict['node_type'] == 'cn') or (input_dict['node_type'] == 'cc')):
        try:
            insert_nova_ip = {"parameter":"my_ip","param_value":"%s" %(input_dict['node_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_host = {"parameter":"host","param_value":"%s" %(input_dict['node_name']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_novncproxy = {"parameter":"novncproxy_base_url","param_value":"http://%s:6080/vnc_auto.html"%(cc_uplink_ip),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_xvpvncproxy = {"parameter":"xvpvncproxy_base_url","param_value":"http://%s:6081/console"%(cc_uplink_ip),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_spice = {"parameter":"html5proxy_base_url","param_value":"http://%s:6082/spice_auto.html"%(cc_uplink_ip),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_vncproxy = {"parameter":"vncserver_proxyclient_address","param_value":"%s" %(input_dict['node_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_spiceproxy = {"parameter":"server_proxyclient_address","param_value":"%s" %(input_dict['node_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_vnclisten = {"parameter":"vncserver_listen","param_value":"0.0.0.0",'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_avail_zone = {'parameter':"default_availability_zone",'param_value':"%s"%(input_dict['avail_zone']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_node_virt = {'parameter':"virt_type",'param_value':"%s"%(input_dict['node_virt_type']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_rabbit = {'parameter':"rabbit_host",'param_value':"%s"%(input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_metadata = {'parameter':"metadata_listen",'param_value':"%s"%(input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_db = {"parameter":"connection","param_value":"postgresql://transuser:%s@%s/nova"%(config.MASTER_PWD,input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_metadata_host = {'parameter':"metadata_host",'param_value':"%s"%(input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_neutron_host = {'parameter':"neutron_url",'param_value':"http://%s:9696"%(input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_neutron_admin = {'parameter':"neutron_admin_auth_url",'param_value':"http://%s:35357/v2.0"%(input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_auth = {"parameter":"auth_host","param_value":"%s"%(input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_auth_uri = {"parameter":"auth_uri","param_value":"%s:5000"%(input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_memcached = {"parameter":"memcached_servers","param_value":"%s:11211"%(input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_neu_ten_id = {"parameter":"neutron_admin_tenant_id","param_value":"%s"%(service_tenant),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_ec2workers = {'parameter':'ec2_workers',"param_value":"%s"%(proc_info['total_cores']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_ec2_url = {'parameter':'keystone_ec2_url',"param_value":"http://%s:5000/v2.0/ec2tokens"%(cc_uplink_ip),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_s3_url = {'parameter':'s3_host',"param_value":"%s"%(input_dict['node_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_nworkers = {'parameter':'notification_workers',"param_value":"%s"%(proc_info['total_cores']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_mworkers = {'parameter':'metadata_workers',"param_value":"%s"%(proc_info['total_cores']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_workers = {'parameter':'workers',"param_value":"%s"%(proc_info['total_cores']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_glance = {'parameter':'glance_host',"param_value":"%s"%(input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_glance_api = {'parameter':'glance_api_servers',"param_value":"http://%s:9292"%(input_dict['cc_data_ip']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_dhcp_domain = {'parameter':'dhcp_domain',"param_value":"%s"%(domains['uplink_domain_name']),'file_name':"nova.conf",'node':"%s" %(input_dict['node_id'])}

            nova_array = [insert_nova_db,insert_nova_ip,insert_vncproxy,insert_vnclisten,insert_novncproxy,insert_avail_zone,insert_node_virt,insert_nova_rabbit,insert_nova_metadata,insert_metadata_host,
                          insert_neutron_host,insert_neutron_admin,insert_nova_auth,insert_nova_auth_uri,insert_nova_memcached,insert_nova_neu_ten_id,insert_nova_ec2workers,insert_nova_nworkers,
                          insert_nova_mworkers,insert_nova_workers,insert_spice,insert_spiceproxy,insert_nova_ec2_url,insert_nova_glance,insert_nova_glance_api,insert_nova_s3_url,insert_nova_dhcp_domain,
                          insert_nova_host,insert_xvpvncproxy,cpu_mode]
            for nova in nova_array:
                db.pg_transaction_begin()
                db.pg_insert('nova_node',nova)
                db.pg_transaction_commit()
        except Exception as e:
            db.pg_transaction_rollback()
            logger.sql_error("Could not insert node specific nova config into Transcirrus db. %s"%(e))
            return 'ERROR'
        try:
            insert_neutron_region = {"parameter":"auth_region","param_value":input_dict['node_cloud_name'],'file_name':"metadata_agent.ini",'node':"%s" %(input_dict['node_id'])}
            insert_neutron_localip = {"parameter":"local_ip","param_value":input_dict['node_data_ip'],'file_name':"ovs_neutron_plugin.ini",'node':"%s" %(input_dict['node_id'])}
            insert_neutron_rabbit = {"parameter":"rabbit_host","param_value":'%s'%(input_dict['cc_data_ip']),'file_name':"neutron.conf",'node':"%s" %(input_dict['node_id'])}
            insert_neutron_db = {"parameter":"connection","param_value":"postgresql://transuser:%s@%s/neutron"%(config.MASTER_PWD,input_dict['cc_data_ip']),'file_name':"neutron.conf",'node':"%s" %(input_dict['node_id'])}
            insert_neutron_auth = {'parameter':"auth_url",'param_value':"http://%s:35357/v2.0"%(input_dict['cc_data_ip']),'file_name':"metadata_agent.ini",'node':"%s" %(input_dict['node_id'])}
            insert_meta_ip = {'parameter':"nova_metadata_ip",'param_value':"%s"%(input_dict['cc_data_ip']),'file_name':"metadata_agent.ini",'node':"%s" %(input_dict['node_id'])}
            insert_nova_url = {'parameter':"nova_url",'param_value':"http://%s:8774/v2"%(input_dict['cc_data_ip']),'file_name':"neutron.conf",'node':"%s" %(input_dict['node_id'])}
            insert_nova_auth_url = {'parameter':"nova_admin_auth_url",'param_value':"http://%s:35357/v2.0"%(input_dict['cc_data_ip']),'file_name':"neutron.conf",'node':"%s" %(input_dict['node_id'])}
            insert_neutron_auth_host = {"parameter":"auth_host","param_value":"%s"%(input_dict['cc_data_ip']),'file_name':"neutron.conf",'node':"%s" %(input_dict['node_id'])}
            insert_neutron_auth_uri = {"parameter":"auth_uri","param_value":"%s:5000"%(input_dict['cc_data_ip']),'file_name':"neutron.conf",'node':"%s" %(input_dict['node_id'])}
            insert_neutron_ml_ip = {"parameter":"local_ip","param_value":"%s"%(input_dict['node_data_ip']),'file_name':"ml2_conf.ini",'node':"%s" %(input_dict['node_id'])}
            insert_neu_nova_ten_id = {"parameter":"nova_admin_tenant_id","param_value":"%s"%(service_tenant),'file_name':"neutron.conf",'node':"%s" %(input_dict['node_id'])}
            insert_neu_mworkers = {'parameter':'metadata_workers',"param_value":"%s"%(proc_info['total_cores']),'file_name':"metadata_agent.ini",'node':"%s" %(input_dict['node_id'])}
            insert_neu_dhcp = {'parameter':'dhcp_domain',"param_value":"%s"%(domains['uplink_domain_name']),'file_name':"dhcp_agent.ini",'node':"%s" %(input_dict['node_id'])}
            neutron_array = [insert_neutron_region,insert_neutron_localip,insert_neutron_rabbit,insert_neutron_db,insert_neutron_auth,insert_meta_ip,insert_nova_url,insert_nova_auth_url,insert_neutron_auth_host,
                             insert_neutron_auth_uri,insert_neutron_ml_ip,insert_neu_nova_ten_id,insert_neu_mworkers,insert_neu_dhcp]
            for neutron in neutron_array:
                db.pg_transaction_begin()
                db.pg_insert('neutron_node',neutron)
                db.pg_transaction_commit()
        except:
            db.pg_transaction_rollback()
            logger.sys_error("Could not insert node specific neutron config into Transcirrus db.")
            return 'ERROR'

    try:
        insert_dict = {'node_id':input_dict['node_id'],'node_name':input_dict['node_name'],'node_type':input_dict['node_type'],'node_data_ip':input_dict['node_data_ip'],'node_mgmt_ip':input_dict['node_mgmt_ip'],
                       'node_controller':input_dict['node_controller'],'node_cloud_name':input_dict['node_cloud_name'],'node_nova_zone':input_dict['avail_zone'],'node_fault_flag':'0',
                       'node_ready_flag':'1','node_gluster_peer':input_dict['node_gluster_peer'],'node_gluster_disks':input_dict['node_gluster_disks']}
        db.pg_transaction_begin()
        db.pg_insert('trans_nodes',insert_dict)
        db.pg_transaction_commit()
        db.pg_close_connection()
        return 'OK'
    except:
        db.pg_transaction_rollback()
        logger.sys_error("Could not insert the new node in the DB.")
        return 'ERROR'

def list_nodes():
    """
    DESC: List the nodes in the Transcirrus DB
    INPUT: input_dict - cloud_name - op - not implemented
                      - controller_name - op - not implemented
    OUTPUT: array of r_dict - node_name
                            - node_id
                            - node_type
                            - status OK/ERROR
    ACCESS: Wide open
    NOTES: The input dict is optional if no input is given then it is assumed that all nodes in
           the dictionary are to be returned. pushed to alpo.1
    """
    logger.sys_info('\n**List the nkdes. Component: Database Def: list_nodes**\n')
    #connect to the DB
    db = util.db_connect()
    r_array = []
    try:
        nodes = {'select':"node_name,node_id,node_type",'from':"trans_nodes"}
        node_list = db.pg_select(nodes)
    except:
        logger.sql_error("Could not get the list of nodes from the Transcirrus DB")
        r_array.append('ERROR')

    
    for node in node_list:
        r_dict = {'node_name':node[0],'node_id':node[1],'node_type':node[2]}
        r_array.append(r_dict)

    if(len(r_array) >= 1):
        r_array.append('OK')
    else:
        r_array.append('ERROR')

    #disconnect from db
    db.pg_close_connection()

    return r_array

def delete_node(node_id):
    """
    DESC: Remove a node from the transcirrus db
    INPUT: node_id
    OUTPUT: OK if successful
            ERROR if not successful
            NA if not found
            raise error
    ACCESS: wide open
    NOTES: This function will only delete the node from the DB it will not actually
           remove a node fromthe openstack cloud.
           The function will check the db to see if the node exists before the deletion.
           If the node is not there then an NA is returned.
    """
    logger.sys_info('\n**Delete a node from the system. Component: Database Def: delete_node**\n')
    #check if the node is in the DB
    check = check_node_exists(node_id)

    if(check == 'OK'):
    #connect to the DB
        #db = db_connect(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        db = util.db_connect()
        try:
            db.pg_transaction_begin()
            del_dict = {"table":'trans_nodes',"where":"node_id='%s'" %(node_id)}
            db.pg_delete(del_dict)
            
            del_dict2 = {"table":'cinder_node',"where":"node='%s'" %(node_id)}
            db.pg_delete(del_dict2)
            
            del_dict3 = {"table":'nova_node',"where":"node='%s'" %(node_id)}
            db.pg_delete(del_dict3)
            
            del_dict4 = {"table":'neutron_node',"where":"node='%s'" %(node_id)}
            db.pg_delete(del_dict4)
            
            del_dict5 = {"table":'swift_node',"where":"node='%s'" %(node_id)}
            db.pg_delete(del_dict5)
            db.pg_transaction_commit()
            db.pg_close_connection()
        except:
            db.pg_transaction_rollback()
            logger.sql_error("Could delete the node with node_id %s from the db." %(node_id))
            return 'ERROR'
    else:
        return 'NA'

    #disconnect from db
    db.pg_close_connection()

    return 'OK'


def update_node(update_dict):
    """
    DESC: Update a nodes info in the transcirrus DB.
    INPUT: update_dict - node_id - req - transcirrus assigned node_id
                      - node_name - op
                      - node_type - op
                      - node_mgmt_ip - op
                      - node_data_ip - op
                      - node_controller - op
                      - node_cloud_name - op
                      - node_avail_zone - op
                      - node_gluster_peer - op
    OUTPUT: OK if successful
            ERROR if not successful
    ACCESS: wide open
    NOTES: This function will not update the physical node, only the DB.
    """
    logger.sys_info('\n**Update the node info. Component: Database Def: update_node**\n')
    if(('node_id' not in update_dict) or (update_dict['node_id'] == "")):
        logger.sys_error("No node_id was given for update operation.")
        raise Exception("No node_id was given for update operation.")

    #get the current values in the DB
    check_node = check_node_exists(update_dict['node_id'])

    if(check_node == 'OK'):
        update = []
        if(('node_name' in update_dict) and update_dict['node_name'] != ""):
            name = "node_name='%s'" %(update_dict['node_name'])
            update.append(name)
        if(('node_type' in update_dict) and update_dict['node_type'] != ""):
            node_type = "node_type='%s'" %(update_dict['node_type'])
            update.append(node_type)
        if(('node_mgmt_ip' in update_dict) and update_dict['node_mgmt_ip'] != ""):
            mgmt_ip = "node_mgmt_ip='%s'" %(update_dict['node_mgmt_ip'])
            update.append(mgmt_ip)
        if(('node_data_ip' in update_dict) and update_dict['node_data_ip'] != ""):
            data_ip = "node_data_ip='%s'" %(update_dict['node_data_ip'])
            update.append(data_ip)
        if(('node_controller' in update_dict) and update_dict['node_controller'] != ""):
            cont = "node_controller='%s'" %(update_dict['node_controller'])
            update.append(cont)
        if(('node_cloud_name' in update_dict) and update_dict['node_cloud_name'] != ""):
            cloud_name = "node_cloud_name='%s'" %(update_dict['node_cloud_name'])
            update.append(cloud_name)
        if(('node_avail_zone' in update_dict) and update_dict['node_avail_zone'] != ""):
            zone = "node_nova_zone='%s'" %(update_dict['node_avail_zone'])
            update.append(zone)
        if(('node_gluster_peer' in update_dict) and update_dict['node_gluster_peer'] != ""):
            peer = "node_gluster_peer='%s'" %(update_dict['node_gluster_peer'])
            update.append(peer)

        #hard code nova_zone to nova
        #if(('avail_zone' in update_dict) and update_dict['avail_zone'] != ""):
        #    update.append('avail_zone=nova')

        db = util.db_connect()
        updater = ",".join(update)
        try:
            db.pg_transaction_begin()
            up = {'table':"trans_nodes",'set':'%s' %(updater),'where':"node_id='%s'" %(update_dict['node_id'])}
            db.pg_update(up)
            db.pg_transaction_commit()
            db.pg_close_connection()
            return 'OK'
        except:
            db.pg_transaction_rollback()
            logger.sql_error("Could update node %s" %(update_dict['node_id']))
            return 'ERROR'
    else:
        return check_node

def update_node_master_pass(new_password):
    """
    DESC: Used to update the mster password for openstack services in the TransCirrus config database. 
    INPUT: new_password
    OUTPUT: OK - success
            ERROR - fail
            NA - unknown
    ACCESS: Wide open
    NOTE: This will update the master password in the database. It will not re-write the config files.
    """
    if(new_password == ''):
        logger.sys_error('The master password can not be blank.')
        raise Exception('The master password can not be blank.')

    db = util.db_connect()

    #update heat
    try:
        heat_updates = [{'table':"heat_default",'set':"param_value='%s'"%(new_password),'where':"parameter='rabbit_password'"},
                        {'table':"heat_default",'set':"param_value='%s'"%(new_password),'where':"parameter='admin_password'"}]
        for heat_update in heat_updates:
            db.pg_transaction_begin()
            db.pg_update(heat_update)
            db.pg_transaction_commit()
    except:
        db.pg_transaction_rollback()
        logger.sgl_error("Could not update Heat master password.")
        return 'ERROR'

    try:
        ceil_updates = [{'table':"ceilometer_default",'set':"param_value='%s'"%(new_password),'where':"parameter='rabbit_password'"},
                        {'table':"ceilometer_default",'set':"param_value='%s'"%(new_password),'where':"parameter='admin_password'"},
                        {'table':"ceilometer_default",'set':"param_value='%s'"%(new_password),'where':"parameter='os_password'"}]
        for ceil_update in ceil_updates:
            db.pg_transaction_begin()
            db.pg_update(ceil_update)
            db.pg_transaction_commit()
    except:
        db.pg_transaction_rollback()
        logger.sgl_error("Could not update Ceilometer master password.")
        return 'ERROR'

    try:
        cinder_updates = [{'table':"cinder_default",'set':"param_value='%s'"%(new_password),'where':"parameter='rabbit_password'"},
                        {'table':"cinder_default",'set':"param_value='%s'"%(new_password),'where':"parameter='admin_password'"}]
        for cinder_update in cinder_updates:
            db.pg_transaction_begin()
            db.pg_update(cinder_update)
            db.pg_transaction_commit()
    except:
        db.pg_transaction_rollback()
        logger.sgl_error("Could not update Cinder master password.")
        return 'ERROR'

    try:
        glance_updates = [{'table':"glance_defaults",'set':"param_value='%s'"%(new_password),'where':"parameter='rabbit_password'"},
                        {'table':"glance_defaults",'set':"param_value='%s'"%(new_password),'where':"parameter='admin_password'"}]
        for glance_update in glance_updates:
            db.pg_transaction_begin()
            db.pg_update(glance_update)
            db.pg_transaction_commit()
    except:
        db.pg_transaction_rollback()
        logger.sgl_error("Could not update Glance master password.")
        return 'ERROR'

    try:
        neutron_updates = [{'table':"neutron_default",'set':"param_value='%s'"%(new_password),'where':"parameter='rabbit_password'"},
                           {'table':"neutron_default",'set':"param_value='%s'"%(new_password),'where':"parameter='admin_password'"},
                           {'table':"neutron_default",'set':"param_value='%s'"%(new_password),'where':"parameter='metadata_proxy_shared_secret'"},
                           {'table':"neutron_default",'set':"param_value='%s'"%(new_password),'where':"parameter='nova_admin_password'"}
                           ]
        for neutron_update in neutron_updates:
            db.pg_transaction_begin()
            db.pg_update(neutron_update)
            db.pg_transaction_commit()
    except:
        db.pg_transaction_rollback()
        logger.sgl_error("Could not update Neutron master password.")
        return 'ERROR'

    try:
        nova_updates = [{'table':"neutron_default",'set':"param_value='%s'"%(new_password),'where':"parameter='rabbit_password'"},
                           {'table':"neutron_default",'set':"param_value='%s'"%(new_password),'where':"parameter='admin_password'"},
                           {'table':"neutron_default",'set':"param_value='%s'"%(new_password),'where':"parameter='neutron_metadata_proxy_shared_secret'"},
                           {'table':"neutron_default",'set':"param_value='%s'"%(new_password),'where':"parameter='neutron_admin_password'"}
                           ]
        for nova_update in nova_updates:
            db.pg_transaction_begin()
            db.pg_update(nova_update)
            db.pg_transaction_commit()
    except:
        db.pg_transaction_rollback()
        logger.sgl_error("Could not update Nova master password.")
        return 'ERROR'

    return 'OK'


def get_node_nova_config(node_id):
    """
    DESC: Pull the nova config information out of the nova config DB.
    INPUT: node_id
    OUTPUT: Array of file descriptors containing file entries,write operations, and file name.
            raise error on failure
    ACCESS: wide open
    NOTES: This will return the nova config info from the db based on the
           node id. util.write_new_config_file can thenbe used to write
           out the new config file if desired
           default file operation can be new(write new file) or append(append to existing)
    """
    logger.sys_info('\n**Get the config info of a node. Component: Database Def: get_node_nova_config**\n')
    if(node_id == ""):
        logger.sys_error("The node id was not specified")
        raise Exception("The node id was not specified")

    #get the node type based on the node ID
    node_info = get_node(node_id)

    db = util.db_connect()

    #query the novaconf table in transcirrus db
    #first get the nova.conf configs
    try:
        get_nova_dict = {'select':"parameter,param_value",'from':"nova_default",'where':"file_name='nova.conf'"}
        defraw = db.pg_select(get_nova_dict)
        get_node_dict = {'select':"parameter,param_value",'from':"nova_node",'where':"file_name='nova.conf'",'and':"node='%s'" %(node_id)}
        noderaw = db.pg_select(get_node_dict)
        novaraw = defraw + noderaw
    except:
        logger.sys_error('Could not get the nova.conf entries from the Transcirrus nova db.')
        raise Exception('Could not get the nova.conf entries from the Transcirrus nova db.')

    compraw = None
    if((node_info['node_type'] == 'cc') or (node_info['node_type'] == 'cn')):
        logger.sys_info("Node is a valid compute node or cloud in a can.")
        try:
            get_compute_dict = {'select':"parameter,param_value",'from':"nova_default",'where':"file_name='nova-compute.conf'"}
            compdefraw = db.pg_select(get_compute_dict)
            get_nodecomp_dict = {'select':"parameter,param_value",'from':"nova_node",'where':"file_name='nova-compute.conf'",'and':"node='%s'" %(node_id)}
            compnoderaw = db.pg_select(get_nodecomp_dict)
            #HACK that may not be neccessary
            #if (node_info['node_type'] == 'cn'):
            #    novnc_proxy = util.get_uplink_ip()
            #    print "HACK %s"%(novnc_proxy)
                #['libvirt_ovs_bridge', 'br-int']
            #    proxy = ['novncproxy_base_url']
            #    proxy.append(novnc_proxy + ":6080/vnc_auto.html")
            #    compnoderaw.append(proxy)
            compraw = compdefraw + compnoderaw
        except:
            logger.sys_error('Could not get the nova-compute.conf entries from the Transcirrus nova db.')
            raise Exception('Could not get the nova-compute.conf entries from the Transcirrus nova db.')
    else:
        logger.sys_error('Could not get nova entries, node type invalid.')
        raise Exception('Could not get nova entries, node type invalid.')

    try:
        #get the entries to append to api-paste.ini
        get_api_dict = {'select':"parameter,param_value",'from':"nova_default",'where':"file_name='api-paste.ini'"}
        defapiraw = db.pg_select(get_api_dict)
        get_nodeapi_dict = {'select':"parameter,param_value",'from':"nova_node",'where':"file_name='api-paste.ini'",'and':"node='%s'" %(node_id)}
        apinoderaw = db.pg_select(get_nodeapi_dict)
        apiraw = defapiraw + apinoderaw
    except:
        logger.sys_error('Could not get the api-paste.conf entries from the Transcirrus nova db.')
        raise Exception('Could not get the api-paste.conf entries from the Transcirrus nova db.')

    #disconnect from db
    db.pg_close_connection()

    #build out the dictionaries
    nova_con = []
    nova_conf = {}
    nova_con.append('[DEFAULT]')
    for x in novaraw:
        row = "=".join(x)
        nova_con.append(row)
    nova_conf['op'] = 'append'
    nova_conf['file_owner'] = 'nova'
    nova_conf['file_group'] = 'nova'
    nova_conf['file_perm'] = '644'
    nova_conf['file_path'] = '/etc/nova'
    nova_conf['file_name'] = 'nova.conf'
    nova_conf['file_content'] = nova_con

    r_array = [nova_conf]
    return r_array

def update_controller_config(update_dict):
    """
    DESC: used to update the controller node nova configuration.
    INPUT: update_dict - node_id
                       - mgmt_ip - op
                       - uplink_ip - op
                       - 
    OUTPUT: OK - success
            ERROR - fail
            NA - unknown
    ACCESS: wide open
    NOTES: Updates the controller node openstack config info if the uplink or mgmt(API) network
           info changes. If this is used new config files will need to be created for the control
           node. This function only works if the node is of type cc.  
    """
    #if((update_dict['node_id'] == "") or ('node_id' not in update_dict)):
        #logger.sys_error('The node_id was not specified')
        #raise Exception("The node_id was not specified.") 
    
    #get the current nova info needed
    #selet_nova = {'select':}

def get_node_neutron_config(node_id):
    """
    DESC: Pull the neutron(neutron) config information out of the  config DB.
    INPUT: node_id
    OUTPUT: Array of file descriptors containing file entries,write operations, and file name.
            raise error on failure
    ACCESS: wide open
    NOTES: This will return the neutron network config info from the db based on the
           node id. util.write_new_config_file can thenbe used to write
           out the new config file if desired
           default file operation can be new(write new file) or append(append to existing)
    """
    logger.sys_info('\n**Get the neutron config info. Component: Database Def: get_node_neutron_config**\n')
    if(node_id == ""):
        logger.sys_error("The node id was not specified")
        raise Exception("The node id was not specified")

    #get the node type based on the node ID
    node_info = get_node(node_id)

    #connect to the db
    db = util.db_connect()

    try:
        get_netdef_dict = {'select':"parameter,param_value",'from':"neutron_default",'where':"file_name='neutron.conf'"}
        netdefraw = db.pg_select(get_netdef_dict)
        get_netnode_dict = {'select':"parameter,param_value",'from':"neutron_node",'where':"file_name='neutron.conf'",'and':"node='%s'"%(node_id)}
        netnoderaw = db.pg_select(get_netnode_dict)
        netraw = netdefraw + netnoderaw
    except:
        logger.sys_error('Could not get the neutron.conf entries from the Transcirrus nuetron db.')
        raise Exception('Could not get the neutron.conf entries from the Transcirrus nuetron db.')

    logger.sys_info("Node is a valid compute node or cloud in a can.")
    try:
        get_ovsdef_dict = {'select':"parameter,param_value",'from':"neutron_default",'where':"file_name='ovs_neutron_plugin.ini'"}
        ovsdefraw = db.pg_select(get_ovsdef_dict)
        get_ovsnode_dict = {'select':"parameter,param_value",'from':"neutron_node",'where':"file_name='ovs_neutron_plugin.ini'",'and':"node='%s'"%(node_id)}
        ovsnoderaw = db.pg_select(get_ovsnode_dict)
        ovsraw = ovsdefraw + ovsnoderaw
    except:
        logger.sys_error('Could not get the ovs_neutron_plugin.ini entries from the Transcirrus neutron db.')
        raise Exception('Could not get the ovs_neutron_plugin.ini entries from the Transcirrus neutron db.')

    try:
        get_mldef_dict = {'select':"parameter,param_value",'from':"neutron_default",'where':"file_name='ml2_conf.ini'"}
        ml2defraw = db.pg_select(get_mldef_dict)
        get_ovsnode_dict = {'select':"parameter,param_value",'from':"neutron_node",'where':"file_name='ml2_conf.ini'",'and':"node='%s'"%(node_id)}
        ml2noderaw = db.pg_select(get_ovsnode_dict)
        mlraw = ml2defraw + ml2noderaw
    except:
        logger.sys_error('Could not get the ml2_conf.ini entries from the Transcirrus neutron db.')
        raise Exception('Could not get the ml2_conf.ini entries from the Transcirrus neutron db.')

    dhcpraw = None
    metaraw = None
    apiraw = None
    l3raw = None
    if((node_info['node_type'] == 'cc') or (node_info['node_type'] == 'nn')):
        logger.sys_info("Node is a valid network node or cloud in a can.")
        try:
            get_dhcpdef_dict = {'select':"parameter,param_value",'from':"neutron_default",'where':"file_name='dhcp_agent.ini'"}
            dhcpdefraw = db.pg_select(get_dhcpdef_dict)
            get_dhcpnode_dict = {'select':"parameter,param_value",'from':"neutron_node",'where':"file_name='dhcp_agent.ini'",'and':"node='%s'"%(node_id)}
            dhcpnoderaw = db.pg_select(get_dhcpnode_dict)
            dhcpraw = dhcpdefraw + dhcpnoderaw
        except:
            logger.sys_error('Could not get the dhcp_agent.ini entries from the Transcirrus neutron db.')
            raise Exception('Could not get the dhcp_agent.ini entries from the Transcirrus neutron db.')

        try:
            get_metadef_dict = {'select':"parameter,param_value",'from':"neutron_default",'where':"file_name='metadata_agent.ini'"}
            metadefraw = db.pg_select(get_metadef_dict)
            get_metanode_dict = {'select':"parameter,param_value",'from':"neutron_node",'where':"file_name='metadata_agent.ini'",'and':"node='%s'"%(node_id)}
            metanoderaw = db.pg_select(get_metanode_dict)
            metaraw = metadefraw + metanoderaw
        except:
            logger.sys_error('Could not get the dhcp_agent.ini entries from the Transcirrus neutron db.')
            raise Exception('Could not get the dhcp_agent.ini entries from the Transcirrus neutron db.')

        try:
            get_apidef_dict = {'select':"parameter,param_value",'from':"neutron_default",'where':"file_name='api-paste.ini'"}
            apidefraw = db.pg_select(get_apidef_dict)
            get_apinode_dict = {'select':"parameter,param_value",'from':"neutron_node",'where':"file_name='api-paste.ini'",'and':"node='%s'"%(node_id)}
            apinoderaw = db.pg_select(get_apinode_dict)
            apiraw = apidefraw + apinoderaw
        except:
            logger.sys_error('Could not get the api_paste.ini entries from the Transcirrus neutron db.')
            raise Exception('Could not get the api_paste.ini entries from the Transcirrus neutron db.')

        try:
            get_l3def_dict = {'select':"parameter,param_value",'from':"neutron_default",'where':"file_name='l3_agent.ini'"}
            l3defraw = db.pg_select(get_l3def_dict)
            get_l3node_dict = {'select':"parameter,param_value",'from':"neutron_node",'where':"file_name='l3_agent.ini'",'and':"node='%s'"%(node_id)}
            l3noderaw = db.pg_select(get_l3node_dict)
            l3raw = l3defraw + l3noderaw
        except:
            logger.sys_error('Could not get the dhcp_agent.ini entries from the Transcirrus neutron db.')
            raise Exception('Could not get the dhcp_agent.ini entries from the Transcirrus neutron db.')
    else:
        logger.sys_error('Could not get neutron entries, node type invalid.')
        #raise Exception('Could not get neutron entries, node type invalid.')

    #disconnect from db
    db.pg_close_connection()
    #NODE - check neutron version make path based on that.
    r_array = []
    net_con = []
    net_conf = {}
    for x in netraw:
        row = "=".join(x)
        net_con.append(row)
    net_conf['op'] = 'append'
    net_conf['file_owner'] = 'neutron'
    net_conf['file_group'] = 'neutron'
    net_conf['file_perm'] = '644'
    net_conf['file_path'] = '/etc/neutron'
    net_conf['file_name'] = 'neutron.conf'
    net_conf['file_content'] = net_con
    r_array.append(net_conf)

    ovs_con = []
    ovs_conf = {}
    for x in ovsraw:
        row = "=".join(x)
        ovs_con.append(row)
    ovs_conf['op'] = 'append'
    ovs_conf['file_owner'] = 'neutron'
    ovs_conf['file_group'] = 'neutron'
    ovs_conf['file_perm'] = '644'
    ovs_conf['file_path'] = '/etc/neutron/plugins/openvswitch'
    ovs_conf['file_name'] = 'ovs_neutron_plugin.ini'
    ovs_conf['file_content'] = ovs_con
    r_array.append(ovs_conf)

    ml_con = []
    ml_conf = {}
    for x in mlraw:
        row = "=".join(x)
        ml_con.append(row)
    ml_conf['op'] = 'append'
    ml_conf['file_owner'] = 'neutron'
    ml_conf['file_group'] = 'neutron'
    ml_conf['file_perm'] = '644'
    ml_conf['file_path'] = '/etc/neutron/plugins/ml2'
    ml_conf['file_name'] = 'ml2_conf.ini'
    ml_conf['file_content'] = ml_con
    r_array.append(ml_conf)

    if((node_info['node_type'] == 'cc') or (node_info['node_type'] == 'nn')):
        dhcp_con = []
        dhcp_conf = {}
        dhcp_con.append('[DEFAULT]')
        for x in dhcpraw:
            row = "=".join(x)
            dhcp_con.append(row)
        dhcp_conf['op'] = 'append'
        dhcp_conf['file_owner'] = 'neutron'
        dhcp_conf['file_group'] = 'neutron'
        dhcp_conf['file_perm'] = '644'
        dhcp_conf['file_path'] = '/etc/neutron'
        dhcp_conf['file_name'] = 'dhcp_agent.ini'
        dhcp_conf['file_content'] = dhcp_con
        r_array.append(dhcp_conf)

        meta_con = []
        meta_conf = {}
        meta_con.append('[DEFAULT]')
        for x in metaraw:
            row = "=".join(x)
            meta_con.append(row)
        meta_conf['op'] = 'append'
        meta_conf['file_owner'] = 'neutron'
        meta_conf['file_group'] = 'neutron'
        meta_conf['file_perm'] = '644'
        meta_conf['file_path'] = '/etc/neutron'
        meta_conf['file_name'] = 'metadata_agent.ini'
        meta_conf['file_content'] = meta_con
        r_array.append(meta_conf)

        l3_con = []
        l3_conf = {}
        for x in l3raw:
            row = "=".join(x)
            l3_con.append(row)
        l3_conf['op'] = 'append'
        l3_conf['file_owner'] = 'neutron'
        l3_conf['file_group'] = 'neutron'
        l3_conf['file_perm'] = '644'
        l3_conf['file_path'] = '/etc/neutron'
        l3_conf['file_name'] = 'l3_agent.ini'
        l3_conf['file_content'] = l3_con
        r_array.append(l3_conf)

    return r_array

def get_node_swift_config(node_id):
    """
    DESC: Get a cinder storage nodes cinder config from the Transcirrus db.
    INPUT: node_id
    OUTPUT:Array of file descriptors containing file entries,write operations, and file name.
            raise error on failure
    ACCESS: wide open
    NOTES: This will return the cinder config info from the db based on the
           node id. util.write_new_config_file can thenbe used to write
           out the new config file if desired
           default file operation can be new(write new file) or append(append to existing)
    """
    #this is pushed out, Swift will most likely come pre set up just like Keystone.
    #swift.conf
    #rsyncd.conf


def get_node_cinder_config(node_id):
    """
    DESC: Get a cinder storage nodes cinder config from the Transcirrus db.
    INPUT: node_id
    OUTPUT:Array of file descriptors containing file entries,write operations, and file name.
            raise error on failure
    ACCESS: wide open
    NOTES: This will return the cinder config info from the db based on the
           node id. util.write_new_config_file can thenbe used to write
           out the new config file if desired
           default file operation can be new(write new file) or append(append to existing)
    """
    logger.sys_info('\n**Get the ciner config info. Component: Database Def: get_node_cinder_config**\n')
    if(node_id == ""):
        logger.sys_error("The node id was not specified")
        raise Exception("The node id was not specified")

    #get the node type based on the node ID
    node_info = get_node(node_id)

    db = util.db_connect()

    cinraw = None
    apiraw = None
    if((node_info['node_type'] == 'cc') or (node_info['node_type'] == 'sn')):
        logger.sys_info("Node is a valid compute node or cloud in a can.")
        #query the novaconf table in transcirrus db
        #first get the nova.conf configs
        try:
            get_cindef_dict = {'select':"parameter,param_value",'from':"cinder_default",'where':"file_name='cinder.conf'"}
            cindefraw = db.pg_select(get_cindef_dict)
            get_cinnode_dict = {'select':"parameter,param_value",'from':"cinder_node",'where':"file_name='cinder.conf'",'and':"node='%s'"%(node_id)}
            cinnoderaw = db.pg_select(get_cinnode_dict)
            cinraw = cindefraw + cinnoderaw
        except:
            logger.sys_error('Could not get the cinder.conf entries from the Transcirrus cinder db.')
            raise Exception('Could not get the cinder.conf entries from the Transcirrus cinder db.')
        try:
            get_apidef_dict = {'select':"parameter,param_value",'from':"cinder_default",'where':"file_name='api-paste.ini'"}
            apidefraw = db.pg_select(get_apidef_dict)
            get_apinode_dict = {'select':"parameter,param_value",'from':"cinder_node",'where':"file_name='api-paste.ini'",'and':"node='%s'"%(node_id)}
            apinoderaw = db.pg_select(get_apinode_dict)
            apiraw = apidefraw + apinoderaw
        except:
            logger.sys_error('Could not get the api-paste.ini entries from the Transcirrus cinder db.')
            raise Exception('Could not get the api-paste.ini entries from the Transcirrus cinder db.')
    else:
        logger.sys_error('Could not get cinder entries, node type invalid.')
        raise Exception('Could not get cinder entries, node type invalid.')

    #disconnect from db
    db.pg_close_connection()

    cin_con = []
    cin_conf = {}
    cin_con.append('[DEFAULT]')
    for x in cinraw:
        row = "=".join(x)
        cin_con.append(row)
    cin_conf['op'] = 'append'
    cin_conf['file_owner'] = 'cinder'
    cin_conf['file_group'] = 'cinder'
    cin_conf['file_perm'] = '644'
    cin_conf['file_path'] = '/etc/cinder'
    cin_conf['file_name'] = 'cinder.conf'
    cin_conf['file_content'] = cin_con

    api_con = []
    api_conf = {}
    for x in apiraw:
        row = "=".join(x)
        api_con.append(row)
    api_conf['op'] = 'append'
    api_conf['file_owner'] = 'cinder'
    api_conf['file_group'] = 'cinder'
    api_conf['file_perm'] = '644'
    api_conf['file_path'] = '/etc/cinder'
    api_conf['file_name'] = 'api-paste.ini'
    api_conf['file_content'] = api_con

    r_array = [cin_conf,api_conf]
    return r_array

def get_glance_config():
    """
    DESC: Get the glance config from the db and write the config on the controller/ciac node.
    INPUT: None
    OUTPUT: File descriptor used to write the glance config file on the ciac node.
    ACCESS: wide open
    NOTES: As of now this function will only write the info to the controller/ciab node. In the
           future we will add the ability to move glance to a seperate node.
    """
    logger.sys_info('\n**Get glance config information. Component: Database Def: get_glance_config**\n')
    db = util.db_connect()
    logger.sys_info("Writing the Glance config file to the controller node.")

    try:
        get_api_dict = {'select':"parameter,param_value",'from':"glance_defaults",'where':"file_name='glance-api.conf'"}
        glance_api = db.pg_select(get_api_dict)
        get_reg_dict = {'select':"parameter,param_value",'from':"glance_defaults",'where':"file_name='glance-registry.conf'"}
        glance_reg = db.pg_select(get_reg_dict)
        get_scrub_dict = {'select':"parameter,param_value",'from':"glance_defaults",'where':"file_name='glance-scrubber.conf'"}
        glance_scrub = db.pg_select(get_scrub_dict)
    except:
        logger.sys_error('Could not get the Glance entries from the Transcirrus db.')
        raise Exception('Could not get the Glance entries from the Transcirrus db.')

    #disconnect from db
    db.pg_close_connection()

    r_array = []
    api = []
    api_conf = {}
    for x in glance_api:
        row = "=".join(x)
        api.append(row)
    api_conf['op'] = 'append'
    #find user/group/perms
    api_conf['file_owner'] = 'glance'
    api_conf['file_group'] = 'glance'
    api_conf['file_perm'] = '644'
    api_conf['file_path'] = '/etc/glance'
    api_conf['file_name'] = 'glance-api.conf'
    api_conf['file_content'] = api
    r_array.append(api_conf)

    reg = []
    reg_conf = {}
    for x in glance_reg:
        row = "=".join(x)
        reg.append(row)
    reg_conf['op'] = 'append'
    #find user/group/perms
    reg_conf['file_owner'] = 'glance'
    reg_conf['file_group'] = 'glance'
    reg_conf['file_perm'] = '644'
    reg_conf['file_path'] = '/etc/glance'
    reg_conf['file_name'] = 'glance-registry.conf'
    reg_conf['file_content'] = reg
    r_array.append(reg_conf)

    scrub = []
    scrub_conf = {}
    for x in glance_scrub:
        row = "=".join(x)
        scrub.append(row)
    scrub_conf['op'] = 'append'
    #find user/group/perms
    scrub_conf['file_owner'] = 'glance'
    scrub_conf['file_group'] = 'glance'
    scrub_conf['file_perm'] = '644'
    scrub_conf['file_path'] = '/etc/glance'
    scrub_conf['file_name'] = 'glance-scrubber.conf'
    scrub_conf['file_content'] = scrub
    r_array.append(scrub_conf)

    return r_array

def get_node_heat_config():
    """
    DESC: Get the heat config from the db and write the config on the controller/ciac node.
    INPUT: None
    OUTPUT: File descriptor used to write the heat config file on the ciac node.
    ACCESS: wide open
    NOTES: As of now this function will only write the info to the controller/ciab node. In the
           future we will add the ability to move heat to a seperate node.
    """
    logger.sys_info('\n**Get Heat config information. Component: Database Def: get_node_heat_config**\n')
    db = util.db_connect()
    logger.sys_info("Writing the Heat config file to the controller node.")

    try:
        get_dict = {'select':"parameter,param_value",'from':"heat_default",'where':"file_name='heat.conf'"}
        heat = db.pg_select(get_dict)
    except:
        logger.sys_error('Could not get the Heat entries from the Transcirrus db.')
        raise Exception('Could not get the Heat entries from the Transcirrus db.')

    #disconnect from db
    db.pg_close_connection()

    r_array = []
    heat_array = []
    heat_conf = {}
    for x in heat:
        row = "=".join(x)
        heat_array.append(row)
    heat_conf['op'] = 'append'
    #find user/group/perms
    heat_conf['file_owner'] = 'heat'
    heat_conf['file_group'] = 'heat'
    heat_conf['file_perm'] = '644'
    heat_conf['file_path'] = '/etc/heat'
    heat_conf['file_name'] = 'heat.conf'
    heat_conf['file_content'] = heat_array
    r_array.append(heat_conf)

    return r_array

def get_node_ceilometer_config(node_id):
    """
    DESC: Get the ceilometer config from the db and write the config on the controller/ciac node.
    INPUT: None
    OUTPUT: File descriptor used to write the ceilometer config file on the ciac node.
    ACCESS: wide open
    NOTES: 
    """
    logger.sys_info('\n**Get Ceilometer config information. Component: Database Def: get_node_ceilometer_config**\n')
    db = util.db_connect()
    logger.sys_info("Writing the Ceilometer config file to node %s."%(node_id))

    try:
        get_dict = {'select':"parameter,param_value",'from':"ceilometer_default",'where':"file_name='ceilometer.conf'"}
        ceildefraw = db.pg_select(get_dict)
    
        get_node_dict = {'select':"parameter,param_value",'from':"ceilometer_node",'where':"file_name='ceilometer.conf'",'and':"node='%s'"%(node_id)}
        ceilnoderaw = db.pg_select(get_node_dict)
        ceil = ceildefraw + ceilnoderaw
    except:
        logger.sys_error('Could not get the Ceilometer entries from the Transcirrus db.')
        raise Exception('Could not get the Ceilometer entries from the Transcirrus db.')

    #disconnect from db
    db.pg_close_connection()

    r_array = []
    ceil_array = []
    ceil_conf = {}
    for x in ceil:
        row = "=".join(x)
        ceil_array.append(row)
    ceil_conf['op'] = 'append'
    #find user/group/perms
    ceil_conf['file_owner'] = 'ceilometer'
    ceil_conf['file_group'] = 'ceilometer'
    ceil_conf['file_perm'] = '644'
    ceil_conf['file_path'] = '/etc/ceilometer'
    ceil_conf['file_name'] = 'ceilometer.conf'
    ceil_conf['file_content'] = ceil_array
    r_array.append(ceil_conf)

    return r_array