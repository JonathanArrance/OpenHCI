#!/usr/bin/python2.7
import sys
import json
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.component.cinder.error as ec


# If vol is attached to vm 
#    1. snapshot the volume if attached force
#    2. create a new volume with the clone vol name


If vol is not attached
    vol create with the source-volid flag in cinder create
    
If clone from exisitng snap
    vol create with the --snapshot-id flag
    
    
