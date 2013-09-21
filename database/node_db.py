from transcirrus.database.postgres import pgsql
import transcirrus.common.logger as logger
import transcirrus.common.config as config
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
    #connect to the database
    db = db_connect(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
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
                    - node_nova_zone
                    - node_iscsi_iqn
                    - node_swift_ring
                    - status
    ACCESS: Wide open
    NOTES: Return the r_dict with a status of OK, else status code of NA or ERROR is returned outside of the ductionary.
    """
    #connect to the database
    db = db_connect(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
    try:
        find_node_dict = {'select':"*",'from':"trans_nodes",'where':"node_id='%s'" %(node_id)}
        node = db.pg_select(find_node_dict)
        db.pg_close_connection()
        if(node[0][0] == node_id):
            r_dict = {'node_name':node[0][1],'node_type':node[0][2],'node_data_ip':node[0][4],'node_mgmt_ip':node[0][3],'node_controller':node[0][5],
                      'node_cloud_name':node[0][6],'node_nova_zone':node[0][7],'node_iscsi_iqn':node[0][8],'node_swift_ring':node[0][9],'status':"OK"}
        else:
            return'ERROR'
    except:
        logger.sql_error("Could not find the node with ID %s in the Transcirrus DB." %(node_id))
        return 'NA'

    return r_dict

def insert_node(input_dict):
    """
    DESC: Insert a new node into the Transcirrus DB.
    INPUT: input_dict - node_id - req - transcirrus assigned node_id
                      - node_name - req
                      - node_type - req
                      - node_mgmt_ip - req
                      - node_data_ip - req
                      - node_controller - req
                      - node_cloud_name - req
                      - node_nova_zone - default nova
                      - node_iscsi_iqn - default NULL
                      - node_swift_ring - default NULL
    OUTPUT: OK if successful
            ERROR if not successful
            raise error
    ACCESS: wide open
    NOTES: If node count in db is 20 or greater for a particular cloud_controller new nodes will not be added to the nodes db.
           The node types are cc - cloud in a can, sn - storage node, cn - compute node.
           The iscsi iqn must be specified with node type sn
           The swift ring will be set to NULL in alpo.0
           The nova zone will be set to nova in alpo.0
           This function does not add a node to the openstack cloud
    """
    #make sure none of the values are empty
    for key, val in input_dict.items():
        #skip over these
        if((key == 'node_nova_zone') or (key == 'node_iscsi_iqn') or (key == 'node_swift_ring')):
            continue
        if(val == ""):
            logger.sys_error("The value %s was left blank" %(val))
            raise Exception("The value %s was left blank" %(val))
        if(key not in input_dict):
            logger.sys_error("Node info not specified")
            raise Exception ("Node info not specified")

    #static assign nova availability zone for now
    input_dict['node_nova_zone'] = 'nova'
    input_dict['node_swift_ring'] = 'NULL'

    if((input_dict['node_iscsi_iqn'] == "") or ('node_iscsi_iqn' not in input_dict)):
        input_dict['node_iscsi_iqn'] = 'NULL'
    elif((input_dict['node_type'] == 'sn') and ('node_iscsi_iqn' not in input_dict)):
        logger.sys_error("Node type sn (Storage node) must have iscsi iqn specified")
        raise Exception("Node type sn (Storage node) must have iscsi iqn specified")

    #get the db connection
    db = db_connect(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)

    #count up the number of nodes attached to controller
    elem_dict = {'table':"trans_nodes",'where':"node_controller='%s'" %(input_dict['node_controller'])}
    count = db.count_elements(elem_dict)
    if(int(count) >= 20):
        logger.sys_error("The maximum limit of 20 nodes has been reached for controller %s" %(input_dict['node_controller']))
        raise Exception("The maximum limit of 20 nodes has been reached for controller %s" %(input_dict['node_controller']))
    else:
        logger.sys_info("Controller %s has %s nodes attached." %(input_dict['node_controller'],count))

    try:
        insert_dict = {'node_id':input_dict['node_id'],'node_name':input_dict['node_name'],'node_type':input_dict['node_type'],'node_data_ip':input_dict['node_data_ip'],'node_mgmt_ip':input_dict['node_mgmt_ip'],
                       'node_controller':input_dict['node_controller'],'node_cloud_name':input_dict['node_cloud_name'],'node_nova_zone':input_dict['node_nova_zone'],'node_iscsi_iqn':input_dict['node_iscsi_iqn'],'node_swift_ring':input_dict['node_swift_ring']}
        db.pg_transaction_begin()
        db.pg_insert('trans_nodes',insert_dict)
        db.pg_transaction_commit()
        db.pg_close_connection()
        return 'OK'
    except:
        db.pg_transaction_rollback()
        logger.sys_error("Could not insert the ne node in the DB.")
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
    #connect to the DB
    db = db_connect(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
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
    #check if the node is in the DB
    check = check_node_exists(node_id)

    if(check == 'OK'):
    #connect to the DB
        db = db_connect(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
        try:
            db.pg_transaction_begin()
            del_dict = {"table":'trans_nodes',"where":"node_id='%s'" %(node_id)}
            db.pg_delete(del_dict)
            db.pg_transaction_commit()
            db.pg_close_connection()
        except:
            db.pg_transaction_rollback()
            logger.sql_error("Could delete the node with node_id %s from the db." %(node_id))
            return 'ERROR'
    else:
        return 'NA'

    return 'OK'


def update_node(update_dict):
    """
    DESC: Update a nodes info in the transcirrus DB.
    INPUT: update_dict - node_id - req - transcirrus assigned node_id
                      - node_name
                      - node_type
                      - node_mgmt_ip
                      - node_data_ip
                      - node_controller
                      - node_cloud_name
                      - node_nova_zone - always nova
                      - node_iscsi_iqn
                      - node_swift_ring
    OUTPUT: OK if successful
            ERROR if not successful
    ACCESS: wide open
    NOTES: This function will not update the physical node, only the DB.
    """
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
        if(('node_iscsi_iqn' in update_dict) and update_dict['node_iscsi_iqn'] != ""):
            iqn = "node_iscsi_iqn='%s'" %(update_dict['node_iscsi_iqn'])
            update.append(iqn)
        if(('node_swift_ring' in update_dict) and update_dict['node_swift_ring'] != ""):
            ring = "node_swift_ring='%s'" %(update_dict['node_swift_ring'])
            update.append(ring)

        #hard code nova_zone to nova
        if(('node_nova_zone' in update_dict) and update_dict['node_nova_zone'] != ""):
            update.append('node_nova_zone=nova')

        db = db_connect(config.TRANSCIRRUS_DB,config.TRAN_DB_PORT,config.TRAN_DB_NAME,config.TRAN_DB_USER,config.TRAN_DB_PASS)
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

def get_node_nova_config():
    """
    DESC:
    INPUT:
    OUTPUT:
    ACCESS:
    NOTES:
    """
    print "not implemented"
    
def get_node_ovs_config():
    """
    DESC:
    INPUT:
    OUTPUT:
    ACCESS:
    NOTES:
    """
    print "not implemented"
    
def get_node_swit_config():
    """
    DESC:
    INPUT:
    OUTPUT:
    ACCESS:
    NOTES:
    """
    print "not implemented"
    
def get_node_cinder_config():
    """
    DESC:
    INPUT:
    OUTPUT:
    ACCESS:
    NOTES:
    """
    print "not implememted"

def db_connect(host,port,dbname,user,password):
    """
    DESC: Connect to the transcirrus db to perform node db functions.
    INPUT: host - db server
           port - deb port
           dbname - name of db to connect to
           user - username
           password - user password
    OUTPUT: db connection object
    ACCESS: Open to everything
    NOTES: This function is open to all, only the transcirrus db can be connected to.
    """
    #make sure that only the transcirrus db is connected to
    #NOTE!!! need to change this to transcirrus from cac_system
    if(dbname == 'cac_system'):
        try:
            db = pgsql(host,port,dbname,user,password)
            return db
        except:
            logger.sql_error("Could not connect to the Transcirrus db for node operations.")
            logger.sys_error("Could not connect to the Transcirrus db for node operations.")