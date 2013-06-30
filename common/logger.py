import sys
import logging
import time
import os

#Input - message to be logged
#log file /var/log/caclogs/db/sql.log
def sql_info(message):
    logging.basicConfig(filename='/var/log/caclogs/system.log',level=logging.DEBUG)
    logging.info(" SQL INFO: %s" %(message))

def sql_warning(message):
    logging.basicConfig(filename='/var/log/caclogs/system.log',level=logging.DEBUG)
    logging.warning("SQL WARNING: %s" %(message))

def sql_debug(message):
    logging.basicConfig(filename='/var/log/caclogs/system.log',level=logging.DEBUG)
    logging.debug("SQL DEBUG: %s" %(message))

def sql_error(message):
    logging.basicConfig(filename='/var/log/caclogs/system.log',level=logging.DEBUG)
    logging.error("SQL ERROR: %s" %(message))


#Input - message to be logged
#log file /var/log/caclogs/system.log
def sys_info(message):
    logging.basicConfig(filename='/var/log/caclogs/system.log',level=logging.DEBUG)
    logging.info("SYS INFO: %s" %(message))

def sys_warning(message):
    logging.basicConfig(filename='/var/log/caclogs/system.log',level=logging.DEBUG)
    logging.warning("SYS WARNING: %s" %(message))

def sys_debug(message):
    logging.basicConfig(filename='/var/log/caclogs/system.log',level=logging.DEBUG)
    logging.debug("SYS DEBUG: %s" %(message))

def sys_error(message):
    logging.basicConfig(filename='/var/log/caclogs/system.log',level=logging.DEBUG)
    logging.error("SYS ERROR: %s" %(message))

#######Internal defs#######

#NEEDS WORK
#Desc: check to see if the file exists if it does check the size
#      if it does not create the file
#Input: filepath - fully qualified path to the log file
def check_log_file(filepath):
    log = os.path.isfile(filepath)
    #log = open(filepath)
    if (log == 'False'):
        #create a log
        with open(filepath, 'a'):
            os.utime(filepath, None)
    elif (log == 'True'):
        #check the log size
        size = os.path.getsize("%s") %(filepath)
        x = size.rstrip('\L')
        #if the size > 100meg role it
        if (x > 100000000):
            destination = "%s_full" %(filepath)
            os.rename(filepath,destination)
            with open(filepath, 'a'):
                os.utime(filepath, None)
    else:
        return