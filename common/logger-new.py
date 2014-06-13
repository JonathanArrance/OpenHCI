#
# Functions required for logging messages to the log file(s).
#
#  The normal sequence of functions to call to properly use the logging functions are:
#
#    Somewhere near init time in your application, call the following functions:
#      logger.InitLogging()
#      logger.LogHeader()
#      logger.StartConfigListener()
#
#    Before logging a message, an instance to the proper logger is required. There are 3 loggers currently but only 2
#    are normally used (sys and sql). The sys logger is for system messages and sql for sql messages. The 3rd logger
#    is called raw but should not normally be needed since it just logs messages without any additional formatting.
#    So normally you would just get an instance to each logger like this:
#      syslog = logger.GetSysLogger()
#      sqllog = logger.GetSqlLogger()
#
#    Now you can start logging messages with the stardard logger like:
#      logger.syslog.debug (Msg, extra=logger.GetUserDict())
#
#    The valid levels are debug, info, warning, error & critical. Since this is calling the standard python methods,
#    any of the additional parameters are supported (like having print args and exception info being added).
#    If you want a stack trace without having an exception, use the following:
#      import traceback
#      syslog.debug ("Something went wrong. Stacktrace: %s", traceback.format_stack(), logger.GetUserDict())
#
#    Lastly, the following function should be called before your application is shutdown/exits:
#      logger.StopConfigListener()
#

import logging
import logging.handlers
import logging.config
import time

# Some global variables.
User = {'user' : 'notset', 'id' : '0'}                                          # User info which is added to log messages
Thread = 0                                                                      # Thread used for listening for new configs
UT = False                                                                      # If we are in UnitTest mode; default is we aren't

#
# InitxxxLogging functions are normally not called because it is handled by the logging.conf file. These functions should only be called
# if there is an error in the logging.conf file. This should create the required handles that we need to continue logging our messages.
#
# Note: if any of the default values in logging.conf are changed, they should be reflected here just in case these functions are used.
#
CONFIG_FILE = "/usr/local/lib/python2.7/transcirrus/common/logging.conf"        # path & filename for the logging config file
LOG_FILE = "/var/log/caclogs/system.log"                                        # path & filename for the log file
LOG_FILE_MAX_BYTES = 5120000                                                    # Size in bytes before a new log file is created
LOG_FILE_BCKUP_CNT = 4                                                          # Number of previous versions of the log file to keep 
LOG_LEVEL = logging.DEBUG                                                       # Default logging level

def InitSysLogging():
    logger = logging.getLogger ('cac-sys')
    hdlr = logging.handlers.RotatingFileHandler (LOG_FILE, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BCKUP_CNT)
    formatter = logging.Formatter ('%(asctime)s %(levelname)s [SYS] [User: %(user)s - ID: %(id)s] %(message)s')
    hdlr.setFormatter (formatter)
    logger.addHandler (hdlr) 
    logger.setLevel (LOG_LEVEL)
    return logger

def InitSqlLogging():
    logger = logging.getLogger ('cac-sql')
    hdlr = logging.handlers.RotatingFileHandler (LOG_FILE, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BCKUP_CNT)
    formatter = logging.Formatter ('%(asctime)s %(levelname)s [SQL] [User: %(user)s - ID: %(id)s] %(message)s')
    hdlr.setFormatter (formatter)
    logger.addHandler (hdlr) 
    logger.setLevel (LOG_LEVEL)
    return logger

def InitRawLogging():
    logger = logging.getLogger ('raw')
    hdlr = logging.handlers.RotatingFileHandler (LOG_FILE, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BCKUP_CNT)
    formatter = logging.Formatter ('%(message)s')
    hdlr.setFormatter (formatter)
    logger.addHandler (hdlr) 
    logger.setLevel (logging.NOTSET)
    return logger

# Call this function only if you are unit testing this code. This will override the default values so you have more control over
# how/where messages will be logged.
def EnableUT(CfgFile, LogFile, MaxBytes, BackupCnt, Level):
    global CONFIG_FILE
    global LOG_FILE
    global LOG_FILE_MAX_BYTES
    global LOG_FILE_BCKUP_CNT
    global LOG_LEVEL
    global UT
    CONFIG_FILE = CfgFile
    LOG_FILE = LogFile
    LOG_FILE_MAX_BYTES = MaxBytes
    LOG_FILE_BCKUP_CNT = BackupCnt
    LOG_LEVEL = Level
    UT = True
    return


# Read the logging.conf file to create our handlers, formatters and set the logging levels.
# We include defaults but they will be ignored since they are defined in the production config file. In the unit testing config file,
# they are not defined so what is provided here will be used. This makes testing it much easier.
def InitLogging():
    try:
        logging.config.fileConfig (CONFIG_FILE, defaults={"DEF_LEVEL"          : LOG_LEVEL,
                                                          "DEF_LOGFILE"        : LOG_FILE,
                                                          "DEF_LOGFILE_SIZE"   : LOG_FILE_MAX_BYTES,
                                                          "DEF_LOGFILE_BCKCNT" : LOG_FILE_BCKUP_CNT})
        return
    except:
        print "Hit exception opening/parsing config file, using internal functions"
        InitSysLogging()
        InitSqlLogging()
        rawlog = InitRawLogging()
        rawlog.error ("\n**Error: problem opening or parsing logging configuration file, conf_file: %s", CONFIG_FILE)
        return

# Writer the starting header to our log file via the raw handler.
def LogHeader():
    Now = time.time()
    rawlogger = logging.getLogger ('raw')
    rawlogger.critical ("\n-------------------------------------------------------------------")
    rawlogger.critical ("Log started: %s (%s)", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(Now)), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(Now)))
    rawlogger.critical ("  TransCirrus Version: %s  Build: %s\n", "alpha", "xxx")
    return

# Set the User dict.
def SetUserDict(username, user_id):
    global User
    User = {'user' : username, 'id' : user_id}
    return

# Return the User dict.
def GetUserDict():
    return User

# Return an instance of the sys handler.
def GetSysLogger():
    logger = logging.getLogger ('cac-sys')
    return logger

# Return an instance of the sql handler.
def GetSqlLogger():
    logger = logging.getLogger ('cac-sql')
    return logger

# Return an instance of the raw handler.
def GetRawLogger():
    logger = logging.getLogger ('raw')
    return logger

def StartConfigListener():
    # Xreate and start the listener on default port
    global Thread
    Thread = logging.config.listen()
    Thread.start()
    return

def StopConfigListener():
    global Thread
    logging.config.stopListening()
    Thread.join()
    return

#
# Deprecated functions - please refrain from using!
# The following functions are only included for backwards compatibility.

def sql_debug(message):
    sqllog = GetSqlLogger()
    sqllog.debug (message, extra=User)
    return

def sql_info(message):
    sqllog = GetSqlLogger()
    sqllog.info (message, extra=User)
    return

def sql_warning(message):
    sqllog = GetSqlLogger()
    sqllog.warning (message, extra=User)
    return

def sql_error(message):
    sqllog = GetSqlLogger()
    sqllog.error (message, extra=User)
    return

def sys_debug(message):
    syslog = GetSysLogger()
    syslog.debug (message, extra=User)
    return

def sys_info(message):
    syslog = GetSysLogger()
    syslog.info (message, extra=User)
    return

def sys_warning(message):
    syslog = GetSysLogger()
    syslog.warning (message, extra=User)
    return

def sys_error(message):
    syslog = GetSysLogger()
    syslog.error (message, extra=User)
    return
