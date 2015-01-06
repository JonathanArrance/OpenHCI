#!/usr/local/bin/python2.7
#need to re-run the gluster swift ring create everytime a new project is added, also need to kick the proxy server
import sys
import subprocess
import os
import re
from pprint import pprint

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
        elif('obj' in user_dict and user_dict['obj'] == 1):
            self.username = user_dict['username']
            self.is_admin = user_dict['is_admin']
            self.user_level = user_dict['user_level']
        elif('obj' not in user_dict):
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
        self.data_ip = util.get_node_data_ip()

    def get_gluster_brick(self, node_type = None):
        """
        DESC: Get the gluster brick name of the current storage or core node
        INPUT None
        OUTPUT: brick_path
                ERROR - FAIL
        ACCESS: Admin - can get the gluster brick names
                PU - none
                User - none
        NOTE: This does not get the brick name for a remote node.
        """
        if(self.is_admin == 1):
            brick_path = None
            #node_type = util.get_node_type()
            if( node_type == 'cn'):
                logger.sys_error('Compute nodes can not be used as Gluster bricks.')
                raise Exception('Compute nodes can not be used as Gluster bricks.')
            elif(node_type == 'sn'):
                brick_path = util.get_node_data_ip() + ":/data/gluster-" + util.get_system_name()
            else:
                brick_path = util.get_node_data_ip() + ":/data/gluster"

            return brick_path

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
        #this needs to be forked to the background or a better way needs to be found could be just this version of gluster swift sucks
        if(self.is_admin == 1):
            #get a list of projects
            get_projects = {'select':"proj_id",'from':"projects"}
            projects = self.db.pg_select(get_projects)
            #call the gluster-swift create ring
            #projects is an array of arrays
            string = ''
            os.system('mv /transcirrus/gluster-object-mount /transcirrus/gluster-object-mount.bak')
            os.system('touch /transcirrus/gluster-object-mount; chmod 777 /transcirrus/gluster-object-mount')
            for project_id in projects:
                string = string + project_id[0] + ' '
                #add the new drive to a mount file so it can be remouted if the system is rebooted.
                out = os.system('echo sudo mount.glusterfs localhost:%s /mnt/gluster-object/%s >> /transcirrus/gluster-object-mount'%(project_id[0],project_id[0]))
                if(out != 0):
                    logger.sys_warn('Could not add object Gluster mount entry. Check /transcirrus/gluster-object-mount')

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
                         - volume_type - op spindle/ssd
                         - bricks[] - op
                         - mount_node - op 
        OUTPUT: OK - SUCCESS
                ERROR - FAIL
        ACCESS: Admin - can create a gluster volumes directly
                PU - none
                User - none
        NOTE: This is not the same as useing the Cinder volume create, this def
              creates volumes using the gluster commands,
              bricks[172.38.24.11:/data/gluster/'volume_name']
              This may need to be expaned on as we add in a spindle based node.
              Mount Node is optional the gluster vol will be mounted on 172.12.24.10 by default unless a differnt node specified.
              volume_type will default to ssd if nothing is specified.
        """
        logger.sys_info('\n**Creating gluster volume. Common Def: create_gluster_volume**\n')
        self.state = 'OK'
        self.gluster = 'gluster'
        if('volume_type' in input_dict):
            self.type = str(input_dict['volume_type']).lower()
            if(self.type == 'ssd'):
                self.gluster = 'gluster'
            elif(self.type == 'spindle'):
                self.gluster = 'gluster-spindle'
            else:
                logger.sys_error('Invalid volume type %s given.'%(self.type))
                raise Exception('Invalid volume type %s given.'%(self.type))
        if(self.is_admin == 1):
            command = None
            if('bricks' in input_dict and len(input_dict['bricks']) >= 1):
                brick = ' '.join(input_dict['bricks'])
                command = 'sudo gluster volume create %s transport tcp %s'%(input_dict['volume_name'],brick)
            else:
                input_dict['bricks'] = ["172.12.24.10:/data/%s/%s"%(self.gluster,input_dict['volume_name'])]
                command = 'sudo gluster volume create %s transport tcp 172.12.24.10:/data/%s/%s'%(input_dict['volume_name'],self.gluster,input_dict['volume_name'])
            #make a new directory for the gluster volume
            out = subprocess.Popen('%s'%(command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
            vol = out.stdout.readlines()
            if(len(vol) == 0):
                logger.sys_error('Could not create a new Gluster volume.')
                self.state = 'ERROR'

            out3 = subprocess.Popen('sudo gluster volume start %s'%(input_dict['volume_name']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
            start = out3.stdout.readlines()
            if(len(start) == 0):
                logger.sys_error('Could not start the new Gluster volume.')
                self.state = 'ERROR'
                self.vol_state = "Stop"
            else:
                self.vol_state = "Start"

            #mount the new gluster volume
            make = os.system('sudo mkdir -p /mnt/gluster-vols/%s' %(input_dict['volume_name']))
            if(make != 0):
                logger.sys_error('Could not create the GlusterFS mount point.')
                self.state = 'ERROR'

            #If mount node not specified use 172.12.24.10
            if('mount_node' not in input_dict):
                input_dict['mount_node'] = '172.12.24.10'

            out4 = subprocess.Popen('sudo mount.glusterfs %s:/%s /mnt/gluster-vols/%s'%(input_dict['mount_node'],input_dict['volume_name'],input_dict['volume_name']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            mount = out4.stdout.readlines()
            #print mount
            if(len(mount) != 0):
                logger.sys_error('Could not mount the Gluster volume.')
                self.state = 'ERROR'

            #add the new drive to a mount file so it can be remouted if the system is rebooted.
            out = os.system('echo sudo mount.glusterfs 172.12.24.10:/%s /mnt/gluster-vols/%s >> /transcirrus/gluster-mounts'%(input_dict['volume_name'],input_dict['volume_name']))
            if(out != 0):
                logger.sys_warn('Could not add object Gluster mount entry. Check /transcirrus/gluster-object-mount')

        else:
            logger.sys_error('Only admins can create gluster volumes.')
            raise Exeption('Only admins can create gluster volumes.')

        #add everything to the 
        for brick in input_dict['bricks']:
            try:
                self.db.pg_transaction_begin()
                insert_vol = {"gluster_vol_name":"%s"%(input_dict['volume_name']),"gluster_brick_name":"%s"%(brick),"gluster_vol_sync_state":"OK","gluster_vol_state":"%s"%(self.vol_state)}
                self.db.pg_insert("trans_gluster_vols",insert_vol)
            except:
                logger.sys_error('Gluster volume info for %s could not be set.'%(input_dict['volume_name']))
                self.db.pg_transaction_rollback()
            else:
                logger.sys_info('Gluster volume info for %s set.'%(input_dict['volume_name']))
                self.db.pg_transaction_commit()

        return self.state
    
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
        #do not remove system level gluster vols.
        if(volume_name == 'instances' or volume_name == 'glance' or volume_name == 'cinder-volume-ssd' or volume_name == 'cinder-volume-spindle'):
            return 'ERROR'

        if(self.is_admin == 1):
            #unmount the volume to be deleted
            logger.sys_info('Unmounting volume %s, preparing to delete.'%(volume_name))
            umount = os.system('sudo umount 172.12.24.10:/%s'%(volume_name))
            if(umount != 0):
                logger.sys_warning('Could not unmount GlusterFS volume %s'%(volume_name))
            self.stop_gluster_volume('%s'%(volume_name))
            logger.sys_info('Deleteing volume %s.'%(volume_name))
            out = os.system('echo \''+'y'+'\n\' | sudo gluster volume delete %s'%(volume_name))
            if(out != 0):
                logger.sys_error('Deleteing volume %s failed.'%(volume_name))
                return 'ERROR'
            else:
                #remove the entry from gluster-mounts
                #note this will have to change when we start mounting volumes on other storage nodes.
                vol_entry = 'sudo mount.glusterfs 172.12.24.10:/%s /mnt/gluster-vols/%s'%(volume_name,volume_name)
                gluster_mounts = open("/transcirrus/gluster-mounts","r")
                vol_lines = gluster_mounts.readlines()
                gluster_mounts.close()
                gluster_mounts = open("/transcirrus/gluster-mounts","w")
                for line in vol_lines:
                    if line!=vol_entry+"\n":
                        gluster_mounts.write(line)
                gluster_mounts.close()

                #remove the entry from gluster-object-mount
                obj_entry = 'sudo mount.glusterfs localhost:%s /mnt/gluster-object/%s'%(volume_name,volume_name)
                gluster_obj_mounts = open("/transcirrus/gluster-object-mount","r")
                obj_lines = gluster_obj_mounts.readlines()
                gluster_obj_mounts.close()
                gluster_obj_mounts = open("/transcirrus/gluster-object-mount","w")
                for line in obj_lines:
                    if line!=obj_entry+"\n":
                        gluster_obj_mounts.write(line)
                gluster_obj_mounts.close()

                #remove the physical space from /data/gluster on all bricks
                #1. get a list of bricks from db
                #2. delete from all bricks useing zero connect to loop through
                #3. check to see if one brick is core if so then delete
                #os.system('rm -rf /data/gluster/testvol')

                try:
                    self.db.pg_transaction_begin()
                    del_vol = {"table":'trans_gluster_vols',"where":"gluster_vol_name='%s'"%(volume_name)}
                    self.db.pg_delete(del_vol)
                except:
                    logger.sys_error('Gluster volume info for %s could not be removed.'%(volume_name))
                    self.db.pg_transaction_rollback()
                else:
                    logger.sys_info('Gluster volume info for %s removed.'%(volume_name))
                    self.db.pg_transaction_commit()
        else:
            logger.sys_error('Only admins can delete Gluster volumes.')
            raise Exeption('Only admins can delete Gluster volumes.')

        return 'OK'

    def cleanup_gluster_space(self):
        pass

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

    def check_gluster_volume(self, gluster_vol_name):
        get_vol = {'select':"gluster_vol_id",'from':"trans_gluster_vols",'where':"gluster_vol_name='%s'"%(gluster_vol_name)}
        vol_id = None
        vol_id = self.db.pg_select(get_vol)
        if(vol_id):
            self.status = {'status':'OK','vol_id':'%s'}%(vol_id)
        else:
            self.status = {'status':'ERROR','vol_id':'None'}
        return self.status

    def get_gluster_vol_info(self,volume_name=None):
        pass
        """
        DESC: Get the detailed information for a gluster volume
        INPUT: volume_name
        OUTPUT: 
        ACCESS: Admin - Can get the info for any volume
                PU - can get volume info for volumes in their project
                User - van get volume info for volumes they own
        NOTE: This is not the same as geting the info from cinder for a cinder volume.
        
        logger.sys_info('\n**Getting Gluster volume detailed info. Common Def: get_gluster_vol_info**\n')
        if(volume_name):
            out = check_gluster_volume(volume_name)
            if(out['status'] == 'ERROR'):
                logger.sys_error('Volume %s does not exist')%(volume_name)
                raise Exception('Volume %s does not exist')%(volume_name)

            if(self.user_level == 0):
                command = 'gluster volume status %s detail'%(volume_name)
                os.system('%s')%(command)
            elif(self.user_level == 1):
                input_dict = {'project_id':'%s','volume_id':'%s'}%(self.project_id,out['vol_id'])
                cinder.get_volume(input_dict)
            elif(self.user_level == 2):
                pass
        else:
            logger.sys_error('No volume name given, can not get volume info.')
            raise Exception('No volume name given, can not get volume info.')
        """

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
              brick = "ip":/"brick name"
              EX. Gluster command: volume add-brick cinder-volume 172.38.24.12:/data/gluster/cinder-volume
              brick = /data/gluster/cinder-volume
              brick IP = 172.38.24.12
              
        """
        logger.sys_info('\n**Adding Gluster brick to volumes. Common Def: add_gluster_brick**\n')
        if(self.is_admin == 1):
            out = os.system('sudo gluster volume add-brick %s %s'%(input_dict['volume_name'],input_dict['brick']))
            if(out != 0):
                return 'ERROR'
            else:
                #add the new vol brick to the DB
                try:
                    self.db.pg_transaction_begin()
                    insert_brick = {"gluster_vol_name":"%s"%(input_dict['volume_name']),"gluster_brick_name":"%s"%(input_dict['brick']),"gluster_vol_sync_state":"NA","gluster_vol_state":"Start"}
                    self.db.pg_insert("trans_gluster_vols",insert_brick)
                except:
                    self.db.pg_transaction_rollback()
                    logger.sys_warn("Could not add the brick info into the database for %s"%(input_dict['volume_name']))
                else:
                    self.db.pg_transaction_commit()
                    logger.sys_info("Added the brick info into the database for %s"%(input_dict['volume_name']))
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
            """
            Not sure this actually matters since we only stop when we are going to delete.
            else:
                #update the vol state
                try:
                    self.db.pg_transaction_begin()
                    update_flag = {'table':"trans_gluster_vols",'set':"gluster_vol_state='Stop'",'where':"gluster_vol_name='%s'"%(volume_name),"and":"gluster_brick_name='%s'"%(input_dict['brick'])}
                    self.db.pg_update(update_flag)
                except:
                    logger.sys_error('State for %s could not be set.'%(volume_name))
                    self.db.pg_transaction_rollback()
                else:
                    logger.sys_error('State for %s set to Stop.'%(volume_name))
                    self.db.pg_transaction_commit()
                    return 'OK'
            """
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
              brick = 172.38.24.11:/data/gluster-sn-12602/"vol-name"
        """
        logger.sys_info('\n**Removeing Gluster brick from volumes. Common Def: remove_gluster_brick**\n')
        if(self.is_admin == 1):
            out = os.system('sudo gluster volume remove-brick %s %s start'%(input_dict['volume_name'],input_dict['brick']))
            if(out != 0):
                logger.sys_error('Could not remove the gluster brick %s'%(input_dict['brick']))
                return 'ERROR'
            else:
                #we need to commit the rmoval to make it take hold
                out = os.system('echo \''+'y'+'\n\' | sudo gluster volume remove-brick %s %s commit'%(input_dict['volume_name'],input_dict['brick']))
                if(out != 0):
                    logger.sys_error('Could not remove the gluster brick %s'%(input_dict['brick']))
                    try:
                        self.db.pg_transaction_begin()
                        update_flag = {'table':"trans_gluster_vols",'set':"gluster_vol_sync_state='ERROR'",'where':"gluster_vol_name='%s'"%(volume_name),"and":"gluster_brick_name='%s'"%(input_dict['brick'])}
                        self.db.pg_update(update_flag)
                    except:
                        logger.sys_error('Sync state for %s could not be set.'%(volume_name))
                        self.db.pg_transaction_rollback()
                    else:
                        logger.sys_error('Sync state for %s set to NA.'%(volume_name))
                        self.db.pg_transaction_commit()
                    return 'ERROR'
                #remove the vol brick from the db
                #this is removeing all entries from db with the vol name in them.
                try:
                    self.db.pg_transaction_begin()
                    del_vol = {"table":'trans_gluster_vols',"where":"gluster_brick_name='%s'"%(input_dict['brick'])}
                    self.db.pg_delete(del_vol)
                except:
                    logger.sys_error('Gluster brick info for %s could not be removed.'%(input_dict['brick']))
                    self.db.pg_transaction_rollback()
                else:
                    logger.sys_error('Gluster brick info for %s removed.'%(input_dict['brick']))
                    self.db.pg_transaction_commit()
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
        #get the vol ID based on name and project_id
        self.sync_state = None
        if(len(start) == 0):
            logger.sys_error('Unknown output while rebalancing Gluster volume.')
            self.sync_state = 'NA'
        if(os.system("echo '%s' | grep 'success'"%(start[0])) == 0):
            logger.sys_info("Starting rebalance of gluster volume %s" %(volume_name))
            self.sync_state = 'OK'
        else:
            logger.sys_error('Could not rebalance the volume %s'%(volume_name))
            self.sync_state = 'ERROR'

        if(self.sync_state == 'OK'):
            try:
                self.db.pg_transaction_begin()
                update_flag = {'table':"trans_gluster_vols",'set':"gluster_vol_sync_state='%s'"%(self.sync_state),'where':"gluster_vol_name='%s'"%(volume_name)}
                self.db.pg_update(update_flag)
            except:
                logger.sys_error('Sync state for %s could not be set.'%(volume_name))
                self.db.pg_transaction_rollback()
            else:
                logger.sys_error('Sync state for %s set to NA.'%(volume_name))
                self.db.pg_transaction_commit()

        return self.sync_state

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
        out = subprocess.Popen('sudo gluster peer detach %s force'%(server_ip), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

    def add_default_gluster_cinder_params(self,volume_name):
        #these are the default and standard volume values
        #used to add values to the spindle node volumes for now sort of a HACK
        logger.sys_info('Adding the default GlusterFS parameters to the new cinder volume %s'%(volume_name))
        os.system('sudo gluster vol set %s storage.owner-uid 165'%(volume_name))
        os.system('sudo gluster vol set %s storage.owner-gid 165'%(volume_name))
        os.system('sudo gluster vol set %s network.remote-dio enable'%(volume_name))
        os.system('sudo gluster vol set %s cluster.eager-lock enable'%(volume_name))
        os.system('sudo gluster vol set %s performance.stat-prefetch off'%(volume_name))
        os.system('sudo gluster vol set %s performance.read-ahead off'%(volume_name))
        os.system('sudo gluster vol set %s performance.quick-read off'%(volume_name))
        os.system('sudo gluster vol set %s performance.io-cache off'%(volume_name))
        os.system('sudo gluster vol set %s server.allow-insecure on'%(volume_name))

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