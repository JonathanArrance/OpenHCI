#!/usr/bin/python2.7
import sys
import json
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.component.cinder.error as ec
import transcirrus.component.cinder.cinder_snapshot as cs
import transcirrus.component.cinder.cinder_volume as cv

def clone_volume(input_dict,auth_dict):
    """
    DESC: Create a new volume in a project from an exisiting snapshot in the project.
    All user levels can spin up new volumes.
    INPUTS: input_dict - volume_id - REQ
                       - project_id - REQ
            auth_dict - authentication dictionary
    OUTPUTS: r_dict - clone_name
                    - clone_id
                    - clone_type
                    - clone_size
    ACCESS: Cloud Admin - clone any volume
            Sub Admin - clone vols in the projects he owns
            PU - clone vols in the project they are a member of.
            User - clone vols they own.
    NOTE: snapshot id is the snapshot you want to create the clone from.
    """

    if(auth_dict['status_level'] < 2):
        raise Exception("Invalid status level passed for user: %s" %(auth_dict['username']))

    #connect to the DB
    db = util.db_connect()

    # get the vol info for the volume
    get_vol = None
    if(input_dict['user_level'] == 0):
        get_vol = {'select':'*','from':'trans_system_vols','where':"vol_id='%s'"%(input_dict['volume_id'])}
    elif(input_dict['user_level'] == 1):
        get_vol = {'select':'*','from':'trans_system_vols','where':"vol_id='%s'"%(input_dict['volume_id']),'and':"proj_id='%s'"%(input_dict['project_id'])}
    else:
        get_vol = {'select':'*','from':'trans_system_vols','where':"vol_id='%s'"%(input_dict['volume_id']),'and':"proj_id='%s' and user_id='%s'"%(input_dict['project_id'],input_dict['user_id'])}

    try:
        vol_info = db.pg_select(get_vol)
    except:
        logger.sql_error('Could not retrieve the volume info needed to create clone.')
        raise Exception('Could not retrieve the volume info needed to create clone.')

    #If vol is not attached
    volume_clone_input = {}
    #    vol create with the source-volid flag in cinder create
