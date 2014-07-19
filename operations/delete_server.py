#!/usr/local/bin/python2.7
import transcirrus.common.logger as logger
from transcirrus.component.nova.server import server_ops

def delete(auth_dict, server_dict):
    nova = server_ops(auth_dict)
    logger.sys_info("Instantiated server_ops object")