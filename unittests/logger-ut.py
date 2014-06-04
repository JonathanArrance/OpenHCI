# UnitTest script for the Logger utility
#   This script will test all aspects of the Logger utility to verify that it is working correctly.
#   If there is an error in a test case, the test case number and message will be displayed.
#   At the end of the script, a PASS or FAIL message will be displayed to indicate if all tests passed or not.

import transcirrus.common.logger as logger
import logging
import time
import string
import os

# Verify that the last line in the given log file matches the given message.
def CheckResults(TestCaseNum, Msg, Level, Type, LogFile, User="notset", ID="0"):
    TimeStamp = time.strftime ("%Y-%m-%d %H:%M:%S")
    SysFile = open (LogFile, "r")
    Lines = SysFile.readlines()
    SysFile.close()
    LastLine = Lines[-1]
    LastLine = LastLine[0:len(LastLine)-1]
    TestMsg = "%s [%s] [User: %s - ID: %s] %s" % (Level, Type, User, ID, Msg)
    if not LastLine.startswith (TimeStamp):
        print "Time mismatch: found (%s)\n            expected (%s)" % (LastLine[0:len(TimeStamp)-1] , TimeStamp)
        print "Test case # %d failed\n" % TestCaseNum
        return True
    if not LastLine.endswith (TestMsg):
        print "Msg mismatch: found (%s)\n           expected (%s)" % (LastLine[len(TimeStamp)+5:], TestMsg)
        print "Test case # %d failed\n" % TestCaseNum
        return True
    return False

# Verify that the header was written correctly to the log file.
def CheckHeader(TestCaseNum, LogFile):
    SysFile = open (LogFile, "r")
    Lines = SysFile.readlines()
    SysFile.close()

    Now = time.time()
    HdrLine0 = "\n"
    HdrLine1 = "-------------------------------------------------------------------"
    HdrLine2 = "Log started: %s (%s)" % (time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(Now)), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(Now)))
    HdrLine3 = "  TransCirrus Version: %s  Build: %s" % ("alpha", "xxx")
    HdrLine2Len1 = HdrLine2.find ("+") - 3
    HdrLine2Len2 = len (HdrLine2) - HdrLine2Len1 + 8
    Lines[2] = Lines[2][0:len(Lines[2])-1]

    if not Lines[0] == HdrLine0:
        print "Header Line 1 mismatch: found (%s)" % Line[0]
        print "Test case # %d failed\n" % TestCaseNum
        return True
    if not Lines[1][0:len(Lines[1])-1] == HdrLine1:
        print "Header Line 2 mismatch: found (%s)\n                     expected (%s)" % (Lines[1], HdrLine1)
        print "Test case # %d failed\n" % TestCaseNum
        return True
    if not Lines[2].startswith (HdrLine2[0:HdrLine2Len1]):
        print "Header Line 3 mismatch: found (%s)\n                     expected (%s)" % (Lines[2][0:HdrLine2Len1], HdrLine2[0:HdrLine2Len1])
        print "Test case # %d failed\n" % TestCaseNum
        return True
    if not Lines[2].endswith (HdrLine2[HdrLine2Len2:]):
        print "Header Line 3 mismatch: found (%s)\n                     expected (%s)" % (Lines[2][HdrLine2Len2:], HdrLine2[HdrLine2Len2:])
        print "Test case # %d failed\n" % TestCaseNum
        return True
    if not Lines[3][0:len(Lines[3])-1] == HdrLine3:
        print "Header Line 4 mismatch: found (%s)\n                     expected (%s)" % (Lines[3], HdrLine3)
        print "Test case # %d failed\n" % TestCaseNum
        return True
    return False

# Start of the main testing script

print "Logger UnitTest script running"

# We will create/use our own log file for testing. We must include the ' around the name so it will get passed correctly to the parser.
# We remove the ' from around the name after we're done with it.
LogFile = "'system-ut.log'"

logger.EnableUT ("logging-ut.conf", LogFile, 10240, 2, "DEBUG")

LogFile = LogFile.replace ("'", "")

# Delete the current log file so we start off fresh.
if os.path.exists (LogFile):
    os.remove (LogFile)

logger.InitLogging()
logger.LogHeader()

syslog = logger.GetSysLogger()
sqllog = logger.GetSqlLogger()
rawlog = logger.GetRawLogger()

# Indicates if any test has failed.
FailedTest = False

# Keeps track of which test case we're on.
TestCaseNum = 0

# Test the LogHeader function
# Test #0
Failed = CheckHeader (TestCaseNum, LogFile)
if Failed: FailedTest = True

# Test the standard logging functions

# We will run these first tests without setting the user data in the logger which means the logger
# should be using the following values.
UserData = {"user" : "notset", "id" : "0"}

# Test #1
Msg = "test %d: system debug message" % TestCaseNum
syslog.debug (Msg, extra=UserData)
Failed = CheckResults (TestCaseNum, Msg, "DEBUG", "SYS", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #2
Msg = "test %d: sql debug message" % TestCaseNum
sqllog.debug (Msg, extra=UserData)
Failed = CheckResults (TestCaseNum, Msg, "DEBUG", "SQL", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #3
Msg = "test %d: system infomation message" % TestCaseNum
syslog.info (Msg, extra=UserData)
Failed = CheckResults (TestCaseNum, Msg, "INFO", "SYS", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #4
Msg = "test %d: sql infomation message" % TestCaseNum
sqllog.info (Msg, extra=UserData)
Failed = CheckResults (TestCaseNum, Msg, "INFO", "SQL", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #5
Msg = "test %d: system warning message" % TestCaseNum
syslog.warning (Msg, extra=UserData)
Failed = CheckResults (TestCaseNum, Msg, "WARNING", "SYS", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #6
Msg = "test %d: sql warning message" % TestCaseNum
sqllog.warning (Msg, extra=UserData)
Failed = CheckResults (TestCaseNum, Msg, "WARNING", "SQL", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #7
Msg = "test %d: system error message" % TestCaseNum
syslog.error (Msg, extra=UserData)
Failed = CheckResults (TestCaseNum, Msg, "ERROR", "SYS", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #8
Msg = "test %d: sql error message" % TestCaseNum
sqllog.error (Msg, extra=UserData)
Failed = CheckResults (TestCaseNum, Msg, "ERROR", "SQL", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #9
Msg = "test %d: system critical message" % TestCaseNum
syslog.critical (Msg, extra=UserData)
Failed = CheckResults (TestCaseNum, Msg, "CRITICAL", "SYS", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #10
Msg = "test %d: sql critical message" % TestCaseNum
sqllog.critical (Msg, extra=UserData)
Failed = CheckResults (TestCaseNum, Msg, "CRITICAL", "SQL", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test the deprecated logging functions

# Jump way ahead in our case number just to seperate them from above.
# Test #50
TestCaseNum = 50
Msg = "test %d: deprecated function syslog.debug test - system message" % TestCaseNum
logger.sys_debug (Msg)
Failed = CheckResults (TestCaseNum, Msg, "DEBUG", "SYS", LogFile)
if Failed: FailedTest = True

# Test #51
Msg = "test %d: deprecated function syslog.debug test - system message" % TestCaseNum
logger.sys_debug (Msg)
Failed = CheckResults (TestCaseNum, Msg, "DEBUG", "SYS", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #52
Msg = "test %d: deprecated function syslog.debug test - sql message" % TestCaseNum
logger.sql_debug (Msg)
Failed = CheckResults (TestCaseNum, Msg, "DEBUG", "SQL", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #53
Msg = "test %d: deprecated function syslog.debug test - system message" % TestCaseNum
logger.sys_info (Msg)
Failed = CheckResults (TestCaseNum, Msg, "INFO", "SYS", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #54
Msg = "test %d: deprecated function syslog.debug test - sql message" % TestCaseNum
logger.sql_info (Msg)
Failed = CheckResults (TestCaseNum, Msg, "INFO", "SQL", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #55
Msg = "test %d: deprecated function syslog.debug test - system message" % TestCaseNum
logger.sys_warning (Msg)
Failed = CheckResults (TestCaseNum, Msg, "WARNING", "SYS", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #56
Msg = "test %d: deprecated function syslog.debug test - sql message" % TestCaseNum
logger.sql_warning (Msg)
Failed = CheckResults (TestCaseNum, Msg, "WARNING", "SQL", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #57
Msg = "test %d: deprecated function syslog.debug test - system message" % TestCaseNum
logger.sys_error (Msg)
Failed = CheckResults (TestCaseNum, Msg, "ERROR", "SYS", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #58
Msg = "test %d: deprecated function syslog.debug test - sql message" % TestCaseNum
logger.sql_error (Msg)
Failed = CheckResults (TestCaseNum, Msg, "ERROR", "SQL", LogFile)
if Failed: FailedTest = True
TestCaseNum += 1

# We will run the same test of cases from above (50 - 58) but with setting the user data in the logger.

# Test #59 - verify that Set/GetUserDict works correctly.
Username = "admin"
UserID = "21fde2f5aa93441ebddc2665570f8dc6"

logger.SetUserDict (Username, UserID)
UserData = logger.GetUserDict()
if UserData['user'] != Username:
    print "User mismatch: found (%s) - expected (%s)" % (UserData['user'], Username)
    FailedTest = True
if UserData['id'] != UserID:
    print "UserID mismatch: found (%s) - expected (%s)" % (UserData['id'], UserID)
    FailedTest = True
TestCaseNum += 1

# Test #60
Msg = "test %d: deprecated function syslog.debug test - system message" % TestCaseNum
logger.sys_debug (Msg)
Failed = CheckResults (TestCaseNum, Msg, "DEBUG", "SYS", LogFile, Username, UserID)
if Failed: FailedTest = True

# Test #61
Msg = "test %d: deprecated function syslog.debug test - system message" % TestCaseNum
logger.sys_debug (Msg)
Failed = CheckResults (TestCaseNum, Msg, "DEBUG", "SYS", LogFile, Username, UserID)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #62
Msg = "test %d: deprecated function syslog.debug test - sql message" % TestCaseNum
logger.sql_debug (Msg)
Failed = CheckResults (TestCaseNum, Msg, "DEBUG", "SQL", LogFile, Username, UserID)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #63
Msg = "test %d: deprecated function syslog.debug test - system message" % TestCaseNum
logger.sys_info (Msg)
Failed = CheckResults (TestCaseNum, Msg, "INFO", "SYS", LogFile, Username, UserID)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #64
Msg = "test %d: deprecated function syslog.debug test - sql message" % TestCaseNum
logger.sql_info (Msg)
Failed = CheckResults (TestCaseNum, Msg, "INFO", "SQL", LogFile, Username, UserID)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #65
Msg = "test %d: deprecated function syslog.debug test - system message" % TestCaseNum
logger.sys_warning (Msg)
Failed = CheckResults (TestCaseNum, Msg, "WARNING", "SYS", LogFile, Username, UserID)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #66
Msg = "test %d: deprecated function syslog.debug test - sql message" % TestCaseNum
logger.sql_warning (Msg)
Failed = CheckResults (TestCaseNum, Msg, "WARNING", "SQL", LogFile, Username, UserID)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #67
Msg = "test %d: deprecated function syslog.debug test - system message" % TestCaseNum
logger.sys_error (Msg)
Failed = CheckResults (TestCaseNum, Msg, "ERROR", "SYS", LogFile, Username, UserID)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #68
Msg = "test %d: deprecated function syslog.debug test - sql message" % TestCaseNum
logger.sql_error (Msg)
Failed = CheckResults (TestCaseNum, Msg, "ERROR", "SQL", LogFile, Username, UserID)
if Failed: FailedTest = True
TestCaseNum += 1


# Test creating a listener to accept a new confilg that we send to it.
import socket
import sys
import struct

logger.StartConfigListener()

with open ("logging-ut.conf", 'rb') as File:
    Buf = File.read()
File.close()

LogFile = "test.log"

# Delete the log file so we start off fresh.
if os.path.exists (LogFile):
    os.remove (LogFile)

# Remove the comment char from our defaults so we have the defaults now defined.
# Change the debugging level and log file so we can verify that this test has worked.
Buf = Buf.replace ("#DEF_LEVEL",          "DEF_LEVEL", 1)
Buf = Buf.replace ("#DEF_LOGFILE",        "DEF_LOGFILE", 1)
Buf = Buf.replace ("#DEF_LOGFILE_SIZE",   "DEF_LOGFILE_SIZE", 1)
Buf = Buf.replace ("#DEF_LOGFILE_BCKCNT", "DEF_LOGFILE_BCKCNT", 1)
Buf = Buf.replace ("DEBUG",               "ERROR", 1)
Buf = Buf.replace ("system.log",          LogFile, 1)

# Create the socket to be used to send the config file over.
Sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

# Connect to the default logging port on this host.
# NOTE: The config listener will ONLY listen to local connections.
HOST = 'localhost'
PORT = logging.config.DEFAULT_LOGGING_CONFIG_PORT
Sock.connect((HOST, PORT))

# Pack the data with a 4 byte length field and send the data to the listener and close the connection.
Sock.send(struct.pack('>L', len(Buf)))
Sock.send(Buf)
Sock.close()

# Wait for the listener to do its job before we proceed with our tests.
time.sleep(5)

# Jump way ahead in our case number just to seperate them from above.
TestCaseNum = 100

# Test #100 - This test should work.
Msg = "test %d: system error message" % TestCaseNum
syslog.error (Msg, extra=logger.GetUserDict())
Failed = CheckResults (TestCaseNum, Msg, "ERROR", "SYS", LogFile, Username, UserID)
if Failed: FailedTest = True
TestCaseNum += 1

# Test #101 - This message should not be written because the log level is set to Debug; therefore the previous msg
# should be the last one in the log file.
Msg1 = "test %d: system infomation message" % TestCaseNum
syslog.info (Msg1, extra=logger.GetUserDict())
Failed = CheckResults (TestCaseNum, Msg, "ERROR", "SYS", LogFile, Username, UserID)
if Failed: FailedTest = True
TestCaseNum += 1

logger.StopConfigListener()

#
# Display final results
if FailedTest:
    print "FAIL"
else:
    print "PASS"
