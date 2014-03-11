#need to re-run the gluster swift ring create everytime a new project is added, also need to kick the proxy server
import sys
import subprocess
import os
import re

import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.service_control as service
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql

class gluster_ops:
    def __init__(self,user_dict):
        if(not user_dict):
            logger.sys_warning("No auth settings passed.")
            raise Exception("No auth settings passed")
        else:
            self.username = user_dict['username']
            self.password = user_dict['password']
            self.project_id = user_dict['project_id']
            if((self.project_id == 'NULL') or (not user_dict['project_id'])):
                logger.sys_error("No project ID was specified in the condtructor")
                raise Exception("No project ID was specified in the condtructor")
            self.token = user_dict['token']
            self.status_level = user_dict['status_level']
            self.user_level = user_dict['user_level']
            self.is_admin = user_dict['is_admin']
            self.user_id = user_dict['user_id']

            if(self.is_admin == 1):
                self.adm_token = user_dict['adm_token']
                if(self.adm_token == ''):
                    logger.sys_error('Admin user had no admin token passed.')
                    raise Exception('Admin user had no admin token passed.')
            else:
                self.adm_token = 'NULL'

            if 'sec' in user_dict:
                self.sec = user_dict['sec']
            else:
                self.sec = 'FALSE'

            #Retrieve all default values from the DB????
            #Screw a config file????
            #get the default cloud controller info
            self.controller = config.CLOUD_CONTROLLER
            self.api_ip = config.API_IP
            #self.db = user_dict['db']

        if((self.username == "") or (self.password == "")):
            logger.sys_error("Credentials not properly passed.")
            raise Exception("Credentials not properly passed.")

        if(self.token == 'error'):
            logger.sys_error("No tokens passed, or token was in error")
            raise Exception("No tokens passed, or token was in error")

        if((self.status_level > 2) or (self.status_level < 0)):
            logger.sys_error("Invalid status level passed for user: %s" %(self.username))
            raise Exception("Invalid status level passed for user: %s" %(self.username))

        self.db = util.db_connect()

    def create_gluster_swift_ring(self):
        """
        DESC: Build the gluster-swift ring. This needs to be run everytime a new project is added,
              or to rebuild the ring  tar.gz files in /etc/swift if they get corrupted.
        INPUT None
        OUTPUT: Ok - SUCCESS
                ERROR - FAIL
        ACCESS: Admin - can create a gluster swift ring
                PU - none
                User - none
        NOTE:
        """
        logger.sys_info('\n**Creating gluster swift ring. Common Def: create_gluster_swift_ring**\n')
        if(self.is_admin == 1):
            #get a list of projects
            get_projects = {'select':"proj_id",'from':"projects"}
            projects = self.db.pg_select(get_projects)
    
            #call the gluster-swift create ring
            #projects is an array of arrays
            string = ''
            for project_id in projects:
                #input_dict = {'volume_name':project_id[0],'gluster_dir_name':project_id[0]}
                #create_vol = self.create_gluster_volume(input_dict)
                string = string + project_id[0] + ' '

            ring = subprocess.Popen('sudo gluster-swift-gen-builders %s'%(string), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            create_ring = ring.stdout.readlines()
            #restart the swift processes - use gluster-swift operation
            service.gluster_swift('restart')
        else:
            logger.sys_error('Only admins can create gluster swift rings.')
            raise Exeption('Only admins can create gluster swift rings.')

        return 'OK'

    def create_gluster_volume(self,input_dict):
        """
        DESC: Create a new gluster volume
        INPUT input_dict - volume_name - req
                         - bricks[] - op
        OUTPUT: OK - SUCCESS
                ERROR - FAIL
        ACCESS: Admin - can create a gluster volumes directly
                PU - none
                User - none
        NOTE: This is not the same as useing the Cinder volume create, this def
              creates volumes using the gluster commands,
              bricks[172.38.24.11:/data/gluster/'volume_name']
        """
        logger.sys_info('\n**Creating gluster volume. Common Def: create_gluster_volume**\n')
        if(self.is_admin == 1):
            command = None
            if('bricks' in input_dict and len(input_dict['bricks']) >= 1):
                brick = ' '.join(input_dict['bricks'])
                #print brick
                command = 'sudo gluster volume create %s transport tcp %s'%(input_dict['volume_name'],brick)
                #print command
            else:
                command = 'sudo gluster volume create %s transport tcp 172.38.24.10:/data/gluster/%s'%(input_dict['volume_name'],input_dict['volume_name'])
            #make a new directory for the gluster volume
            out = subprocess.Popen('%s'%(command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            make = out.stdout.readlines()
            print make
            if(len(make) == 0):
                logger.sys_error('Could not create a new Gluster volume.')
                return 'ERROR'

            out3 = subprocess.Popen('sudo gluster volume start %s'%(input_dict['volume_name']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            start = out3.stdout.readlines()
            print start
            if(len(start) == 0):
                logger.sys_error('Could not start the new Gluster volume.')
                return 'ERROR'
        else:
            logger.sys_error('Only admins can create gluster volumes.')
            raise Exeption('Only admins can create gluster volumes.')

        return 'OK'
    
    def delete_gluster_volume(self,volume_name):
        """
        DESC: Delete a Gluster volume
        INPUT volume_name
        OUTPUT: OK - SUCCESS
                ERROR - FAIL
        ACCESS: Admin - Delete any Gluster volume
                PU - none
                User - none
        NOTE: Deletes a Gluster volume.
        """
        logger.sys_info('\n**Deleteing a gluster volume. Common Def: delete_gluster_volume**\n')
        if(self.is_admin == 1):
            self.stop_gluster_volume('%s'%(volume_name))
            out = os.system('echo \''+'y'+'\n\' | sudo gluster volume delete %s'%(volume_name))
            if(out != 0):
                return 'ERROR'
        else:
            logger.sys_error('Only admins can delete Gluster volumes.')
            raise Exeption('Only admins can delete Gluster volumes.')

        return 'OK'

    def list_gluster_volumes(self):
        """
        DESC: List all of the glusterFS volumes on the system.
        INPUT: None
        OUTPUT: r_array - an array of gluster volumes
        ACCESS: Admin - Delete any Gluster volume
                PU - none
                User - none
        NOTE: 
        """
        logger.sys_info('\n**Listing all Gluster volumes. Common Def: list_gluster_volumes**\n')
        if(self.is_admin == 1):
            out = subprocess.Popen('sudo gluster volume list', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            vols = out.stdout.readlines()
            r_array = []
            for vol in vols:
                r_array.append(vol.rstrip())
            return r_array
        else:
            logger.sys_error('Only admins can list Gluster volumes.')
            raise Exeption('Only admins can list Gluster volumes.')

    def add_gluster_brick(self,input_dict):
        """
        DESC: Add a brick to a volume 
        INPUT: input_dict - volume_name
                          - brick
        OUTPUT: OK - SUCCESS
                ERROR - FAIL
        ACCESS: Admin - Can add a brick to the Gluster volume
                PU - none
                User - none
        NOTE: This is not the same as useing the Cinder volume create, this def
              adds gluster bricks to volumes using the gluster commands
              brick = "ip":/"path_to_brick"
        """
        logger.sys_info('\n**Adding Gluster brick to volumes. Common Def: add_gluster_brick**\n')
        if(self.is_admin == 1):
            out = os.system('sudo gluster volume add-brick %s %s'%(input_dict['volume_name'],input_dict['brick']))
            if(out != 0):
                return 'ERROR'
            else:
                self.rebalance_gluster_volume(input_dict['volume_name'])
        else:
            logger.sys_error('Only admins can add a gluster brick.')
            raise Exeption('Only admins can add a gluster brick.')

        return 'OK'

    def stop_gluster_volume(self,volume_name):
        """
        DESC: Stop a Gluster volume.
        INPUT: volume_name
        OUTPUT: OK - SUCCESS
                ERROR - FAIL
        ACCESS: Admin - Stop a Gluster volume.
                PU - none
                User - none
        NOTE: This is not the same as useing the Cinder volume delete, this def
              stops volumes using the gluster commands
        """
        logger.sys_info('\n**Stopping Gluster volume. Common Def: stop_gluster_volume**\n')
        if(self.is_admin == 1):
            out = os.system('echo \''+'y'+'\n\' | sudo gluster volume stop %s'%(volume_name))
            if(out != 0):
                return 'ERROR'
            else:
                return 'OK'
        else:
            logger.sys_error('Only admins can stop a Gluster volume.')
            raise Exeption('Only admins can stop a gluster volume.')
    
    def remove_gluster_brick(self,input_dict):
        """
        DESC: Remove a Gluster brick
        INPUT: input_dict - volume_name - req
                          - brick - req
        OUTPUT: OK - SUCCESS
                ERROR - FAIL
        ACCESS: Admin - Can remove a gluster brick from volumes.
                PU - none
                User - none
        NOTE: This operation uses the glusterfs commands.
        """
        logger.sys_info('\n**Removeing Gluster brick from volumes. Common Def: remove_gluster_brick**\n')
        if(self.is_admin == 1):
            out = os.system('sudo gluster volume remove-brick %s %s start'%(input_dict['volume_name'],input_dict['brick']))
            if(out != 0):
                logger.sys_error('Could not remove the gluster brick %s'%(input_dict['brick']))
                return 'ERROR'
            else:
                return 'OK'
        else:
            logger.sys_error('Only admins can remove Gluster bricks.')
            raise Exeption('Only admins can remove Gluster bricks.')

    def rebalance_gluster_volume(self,volume_name):
        """
        DESC: Reblance gluster volumes across bricks.
        INPUT: volume_name
        OUTPUT: OK - SUCCESS
                ERROR - FAIL
                NA - UNKNOWN
        ACCESS: Admin - Can rebalance volumes across bricks.
                PU - none
                User - none
        NOTE: Uses the glusterfs commands to rebalance volumes.
        """
        logger.sys_info('\n**Rebalanceing Gluster volumes. Common Def: rebalance_gluster_volume**\n')
        out = subprocess.Popen('sudo gluster volume rebalance %s start'%(volume_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        start = out.stdout.readlines()
        #print start
        if(len(start) == 0):
            logger.sys_error('Unknown output while rebalancing Gluster volume.')
            return 'NA'
        if(os.system("echo '%s' | grep 'success'"%(start[0])) == 0):
            logger.sys_info("Starting rebalance of gluster volume %s" %(volume_name))
            return 'OK'
        else:
            logger.sys_error('Could not rebalance the volume %s'%(volume_name))
            return 'ERROR'
    
    def replace_gluster_brick(self,input_dict):
        """
        DESC: Reblance gluster volumes across bricks.
        INPUT: input_dict - volume_name
                          - old_brick
                          - new_brick
        OUTPUT: OK - SUCCESS
                ERROR - FAIL
        ACCESS: Admin - Can replace GlusterFS bricks.
                PU - none
                User - none
        NOTE: Uses the GlusterFS commands
        """
        pass
    
    def attach_gluster_peer(self,server_ip):
        """
        DESC: Probe a new gluster server and add it to the gluster cluster
        INPUT: server_ip
        OUTPUT: OK - SUCCESS
                ERROR - FAIL
                NA - UNKNOWN
        ACCESS: Admin - Can probe potential peers
                PU - none
                User - none
        NOTE: Uses the GlusterFS commands
        """
        out = subprocess.Popen('sudo gluster peer probe %s'%(server_ip), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        probe = out.stdout.readlines()
        #this needs to be confirmed
        if(len(probe) == 1):
            try:
                update = {'table':"trans_nodes",'set':"node_gluster_peer='1'",'where':"node_data_ip='%s'"%(server_ip)}
                self.db.pg_update(update)
            except:
                logger.sys_error('Could not attach host with ip %s to Gluster storage network.'%(server_ip))
                self.delete_gluster_volume(server_ip)
                return 'NA'
            else:
                logger.sys_info('Successfuly added a new gluster peer %s'%(server_ip))
                return 'OK'
        else:
            logger.sys_error('Could not attach host with ip %s to Gluster storage network.'%(server_ip))
            return 'ERROR'

    def detach_gluster_peer(self,server_ip):
        """
        DESC: Detach a gluster peer from the cluster
        INPUT: server_ip
        OUTPUT: OK - SUCCESS
                ERROR - FAIL
        ACCESS: Admin - Can detach gluster peers.
                PU - none
                User - none
        NOTE: Uses the GlusterFS commands
        """
        out = subprocess.Popen('sudo gluster peer detach %s'%(server_ip), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        det = out.stdout.readlines()
        if(len(det) == 1):
            try:
                update = {'table':"trans_nodes",'set':"node_gluster_peer='0'",'where':"node_data_ip='%s'"%(server_ip)}
                self.db.pg_update(update)
            except:
                logger.sys_error('Could not dettach host with ip %s from Gluster storage network.'%(server_ip))
                self.delete_gluster_volume(server_ip)
                return 'NA'
            else:
                logger.sys_info('Successfuly detachedgluster peer %s'%(server_ip))
                return 'OK'
        else:
            logger.sys_error('Could not remove peer %s from Gluster storage network.'%(server_ip))
            return 'ERROR'

    def gluster_vol_status(self):
        pass

    def list_gluster_nodes(self):
        """
        DESC: List all of the Gluster storage nodes
        INPUT: None
        OUTPUT: r_array or r_dict - node_id
                                  - node_name
                                  - node_type
                                  - node_data_ip
                ERROR - fail
        ACCESS: Admin - Can list gluster peers.
                PU - none
                User - none
        NOTE:
        """
        if(self.is_admin == 1):
            try:
                select = {'select':"node_id,node_name,node_type,node_data_ip",'from':"trans_nodes",'where':"node_gluster_peer='1'"}
                peers = self.db.pg_select(select)
            except:
                logger.sys_error("Could not retrive any gluster peers")
                return 'ERROR'

            r_array = []
            for peer in peers:
                r_dict = {'node_id':peer[0],'node_name':peer[1],'node_type':peer[2],'node_data_ip':peer[3]}
                r_array.append(r_dict)
            return r_array
        else:
            logger.sys_error('Only admins can list Gluster peers.')
            return 'ERROR'