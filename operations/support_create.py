#!/usr/local/bin/python2.7

import os
import sys
import getopt
import ssh_utils
import subprocess
import signal
import time
import paramiko
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
import transcirrus.common.logger as logger
import transcirrus.common.memcache as cache

# Global constants.
Username = "root"                                                                       # Default user to login in with, must be root to collect support data
Password = config.TRAN_DB_PASS                                                          # Default password to login in with, transuser and root have same pwd
RemotePath = "/tmp"                                                                     # Location on the remote host that has the support data
LocalPath = "/tmp"                                                                      # Location on the local host to store the support data
WputURL = "http://www.transcirrus.com/cgi-bin/upload.cgi"                               # URL for uploading files
DefScriptFile = "/usr/local/lib/python2.7/transcirrus/operations/support-collect.sh"    # Default script file for collecting support data
ExpiredProcFileTimeMinutes = 15                                                         # If a proc file is older than this value in minutes then its expired
SubProcTimeoutSecs = 10 * 60                                                            # Max time in seconds we should wait for the subprocess that is collecting data before we kill it
PollIntervalSecs = 30                                                                   # Time in seconds that we sleep between polling to see if a subprocess has completed yet

# Global vars that are used throughout the module and in unit testing.
AllNodes = True                     # Should all nodes be updated or just a single node
Node = ""                           # Single node to be updated
Force = False                       # Should be for the install even if the version is older
ScriptFile = ""                     # Script file to run on the remote host
CmdLine = False                     # We are being run from the command line
EnableCache = False                 # Enable sending log messages to memcached
Cache = None                        # Handle to memcached
CacheKey = "TransCirrusPhoneHome"   # Cache key to reference our messages


# Enable parameters for running on the internal TransCirrus network that can't reach transcirrus.com.
def EnableSim ():
    global WputURL
    WputURL = "http://192.168.10.5/cgi-bin/upload.cgi"
    return

# Handle logging of print messages (console, logfile and memcached).
def printmsg (msg):
    if CmdLine:
        print msg

    logger.sys_info ("PhoneHome script: " + msg)

    if EnableCache and Cache != None:
        Data = Cache.get(CacheKey)
        NumMessages = int(Data['num_messages'])
        Data['num_messages'] = NumMessages + 1
        Data['msg%s' % NumMessages] = msg
    return

# Turn on caching of messages to memcached.
def EnableCaching():
    global EnableCache
    global Cache

    EnableCache = True
    Cache = cache.Client(['127.0.0.1:11211'], debug=0)
    Cache.set (CacheKey, {'num_messages': 0})
    return

# Turn off caching of messages to memcached.
def DisableCaching():
    global EnableCache
    global Cache

    EnableCache = False
    Cache.delete(CacheKey)
    Cache = None
    return

# Returns just a filename given a fully qualified path.
def ExtractFilename (Name):
    Path = Name.strip().split('/')
    Num = len(Path)
    return (Path[Num-1])

# Copies the given file to the remote host.
def PutRemoteFile (File, Host, Handle):
    RemoteFile = RemotePath + "/" + ExtractFilename (File)
    try:
        ssh_utils.PutFile (File, RemoteFile, Host, Handle)
    except Exception, e:
        printmsg ("Error copying file to remote node, exception: %s" % e)
        raise
    return

# Copies the given file from the remote host.
def GetRemoteFile (File, Host, Handle):
    RemoteFile = RemotePath + "/" + ExtractFilename (File)
    LocalFile = LocalPath + "/" + ExtractFilename (File)
    try:
        ssh_utils.GetFile (RemoteFile, LocalFile, Host, Handle)
    except Exception, e:
        printmsg ("Error copying file from remote node, exception: %s" % e)
        raise
    return

# Determine if the remote host is already in the process of collecting support data.
def HostAlreadyCollecting (Host, Handle):
    RemoteProcFile = RemotePath + "/phproc*"
    try:
        Command = "stat -c %y " + RemoteProcFile
        STDout, STDerr, ExitStatus = ssh_utils.ExecRemoteCommand (Command, Host, Handle)
        if ExitStatus != 0:
            return (False)
        else:
            # We got a good status which means a proc file already exists on the remote host.
            # STDout has the file's last modification time. We will use that to determine if the
            # proc file was left over from a previous collection that went bad.
            FileTime = time.strptime (STDout.split('.')[0], "%Y-%m-%d %H:%M:%S")
            Now = time.localtime()
            ExpiredTime = time.mktime(Now) - (ExpiredProcFileTimeMinutes * 60)      # convert to seconds

            if time.mktime(FileTime) < ExpiredTime:
                # This is an old proc file so go delete it.
                Command = "rm -f " + RemoteProcFile
                ssh_utils.ExecRemoteCommand (Command, Host, Handle)
                return (False)
            else:
                # The proc file time is within the time limit so there must be a collection already happening on the host.
                return (True)
    except Exception, e:
        printmsg ("Error detecting support process on remote host, exception: %s" % e)
        raise

# Get the nodeid of the remote node.
def GetRemoteNodeID (Host, Handle):
    File = "/etc/nodeid"
    try:
        Command = "cat " + File
        STDout, STDerr, ExitStatus = ssh_utils.ExecRemoteCommand (Command, Host, Handle)
        if ExitStatus != 0:
            return ("")
        else:
            NodeID = STDout.split('\n')[0]
            return (NodeID)
    except Exception, e:
        printmsg ("Error getting nodeid on remote host, exception: %s" % e)
        raise

# Run the support collect script on the remote host.
def StartCollecting (Script, TimeStamp, Host, Handle):
    RemoteScriptFile = RemotePath + "/" + ExtractFilename (Script)
    try:
        Command = "chmod 777 " + RemoteScriptFile + "; " + RemoteScriptFile + " " + Host + " " + TimeStamp
        Command = Command + " >>" + RemotePath + "/ph_" + TimeStamp + ".log 2>&1"
        STDout, STDerr, ExitStatus = ssh_utils.ExecRemoteCommand (Command, Host, Handle)
        if ExitStatus != 0:
            printmsg ("Error collecting support data on remote host, exit status:  %d" % ExitStatus)
            printmsg ("stdout: %s" % STDout)
            printmsg ("stderr: %s" % STDerr)
            raise Exception ("CollectSupport error")
        return
    except Exception, e:
        printmsg ("Error collecting support data on remote host, exception: %s" % e)
        raise

# Goes through the database and returns a dict of all nodes with the node's name and data IP address.
def FindNodes (Nodename=None):
    try:
        handle = pgsql (config.TRANSCIRRUS_DB, config.TRAN_DB_PORT, config.TRAN_DB_NAME, config.TRAN_DB_USER, config.TRAN_DB_PASS)
    except Exception as e:
        printmsg ("Could not connect to db with error: %s" % e)
        raise Exception ("Could not connect to db with error: %s" % e)

    # Get all nodes or get the data just for the given node.
    if Nodename == None:
        select_nodes = {'select':'node_name,node_data_ip','from':'trans_nodes'}
    else:
        select_nodes = {'select':'node_name,node_data_ip','from':'trans_nodes','where':"node_name='%s'" %(Nodename)}
    nodes = handle.pg_select (select_nodes)
    if len(nodes) == 0:
        handle.pg_close_connection()
        if Nodename == None:
            printmsg ("No other nodes where found in the database")
        else:
            printmsg ("Could not find a node in the database with a name of %s" % Nodename)
        Nodes = []
        return (Nodes)

    Nodes = []
    for node in nodes:
        Nodes.append(node)

    handle.pg_close_connection()
    return (Nodes)

# Makes a tar file of the collected support files.
def TarSupportFiles (TimeStamp):
    TarFile = LocalPath + "/phsupport_" + TimeStamp + ".tar.gz"

    # We need sudo since some of the files are owned by root and we need to change the ownership so we
    # can retrieve the file later.
    TarCommand = "sudo tar -czf " + TarFile + " -C " + LocalPath + " " + LocalPath + "/phonehome_*" + TimeStamp + "*"
    TarCommand = TarCommand + "; sudo chown transuser:transuser " + TarFile

    try:
        Subproc = subprocess.Popen (TarCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        StdOut, StdErr = Subproc.communicate()

        if Subproc.returncode != 0:
            printmsg ("Error tarring support files, exit status: %d" % Subproc.returncode)
            printmsg ("Error message: %s" % StdErr)
            raise Exception ("Tar error")
    except Exception, e:
        printmsg ("Error tarring support files, exception: %s" % e)
        raise Exception ("Tar error")
    return (TarFile)

# Puts (pushes) the given file to the webserver.
def WputFile (File):
    Command = "curl -F filename=@" + File + " " + WputURL
    try:
        Subproc = subprocess.Popen (Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        StdOut, StdErr = Subproc.communicate()

        if Subproc.returncode != 0:
            printmsg ("Error uploading support file to %s, exit status: %d" % (WputURL, Subproc.returncode))
            printmsg ("Error message: %s" % StdErr)
            raise Exception ("Upload error")
        else:
            # Even though we got a successful return status, there could have been an
            # error in the cgi script that would show up in the htlm output. So we
            # search stdout for the word 'Error:'
            Pos = StdOut.find("Error:")
            if Pos != -1:
                MsgEnd = StdOut.find("^", Pos)
                printmsg ("Error uploading support file to %s" % WputURL)
                printmsg ("Error message: %s" % StdOut[Pos:MsgEnd])
                raise Exception ("Upload error")
    except Exception, e:
        printmsg ("Error uploading support file to %s, exception: %s" % (WputURL, e))
        raise Exception ("Upload error")
    return

# Create a file that contains the data for why we could not get data for a remote host.
def IndidateNoDataFromNode (TimeStamp, Host, Status, Msg):
    File = LocalPath + "/phonehome_" + Host + "_" + TimeStamp + ".no-data"
    with open (File, "a") as handle:
        handle.write("Exit status: %d\n" % Status)
        handle.write("Exit msg: %s\n" % Msg)
        handle.close()
    return

# Do all the steps required to push the script file to the remote host(s), execute the script file,
# retrieve the results, tar up the results and upload the tar file.
def DoCreate():
    global ScriptFile

    # Get all the nodes from the DB or just use the one given on the command line.
    if AllNodes:
        Nodes = FindNodes()
    else:
        # Determine if we were given a name or IP address.
        if Node.split('.')[-1].isdigit():
            # We have an IP address so just use it for the name and address.
            Nodes = []
            Nodes.append ({'node_name': Node, 'node_data_ip': Node})
        else:
            # We have a name so go lookup the the IP address in the database.
            Nodes = FindNodes (Node)

    if ScriptFile == "":
        # Use the default script file.
        ScriptFile = DefScriptFile

    # Make sure the script file exists before we try to use it.
    if not os.path.exists (ScriptFile):
        if CmdLine:
            printmsg ("Script file not found: %s" % ScriptFile)
            sys.exit(2)
        else:
            raise Exception ("Script file not found: %s" % ScriptFile)

    TimeStamp = time.strftime("%Y%m%d%H%M%S", time.localtime())

    # List of child processes.
    ChildProcesses = []

    print ""

    # Loop through the host(s) and fork a subprocess to performed the required steps to collect the support data from each one.
    for Host in Nodes:
        Hostname = Host['node_name']
        HostIP   = Host['node_data_ip']
        printmsg ("Attempting to collect support data from node %s (%s)" % (Hostname, HostIP))

        ChildPid = os.fork()
        if ChildPid == 0:
            # This is the child process running which will call the functions that will do everything we need on the
            # remote host and then exit.
            try:
                ExitStatus = -1
                ExitMsg = ""
                Handle = None
                Handle = ssh_utils.SSHConnect (HostIP, Username=Username, Password=Password)
                NodeID = GetRemoteNodeID (Hostname, Handle)
                RemoteName = "phonehome_" + Hostname + "_" + NodeID + "_" + TimeStamp

                if Force or not HostAlreadyCollecting (Hostname, Handle):
                    PutRemoteFile (ScriptFile, Hostname, Handle)
                    StartCollecting (ScriptFile, TimeStamp, Hostname, Handle)
                    ExitStatus = 0
                else:
                    ExitStatus = -2
                    ExitMsg = "Node %s is already collecting support data" % (Hostname)
                    printmsg (ExitMsg)
                    print "Use the -o option to override checking"
            except Exception, e:
                ExitStatus = -3
                ExitMsg = "Exception msg: %s" % e
                printmsg (ExitMsg)
                printmsg ("Support data was not collected on node %s due to the above error" % Hostname)
            finally:
                if Handle != None:
                    ssh_utils.SSHDisconnect (Handle)
                if ExitStatus != 0:
                    IndidateNoDataFromNode (TimeStamp, Hostname, ExitStatus, ExitMsg)
                os._exit (ExitStatus)                                       # Child process has to exit now.

        # The parent process continues from here so add the PID to the list.
        ChildProcesses.append ({'pid':ChildPid, 'node_name':Hostname, 'node_data_ip':HostIP})

    # Wait for the child processes to complete.
    MaxWait = time.time() + SubProcTimeoutSecs - 0.01
    NodesStatus = []

    # Loop until we have run out of time or there are no more children running.
    while time.time() < MaxWait:
        if len(ChildProcesses) == 0:
            break                                                   # No more kids running so jump out of our loop
        else:
            time.sleep (PollIntervalSecs)                           # Sleep our poll interval amount

        # Check each child to see who is still running.
        for Child in ChildProcesses:
            Pid, ExitStatus = os.waitpid (Child['pid'], os.WNOHANG)
            if Pid == Child['pid']:
                # This child has finished so add him to the NodesStatus list and remove him from the ChildProcesses list
                # since we don't need to check him again.
                NodesStatus.append ({'node_name':Child['node_name'], 'node_data_ip':Child['node_data_ip'], 'exit_status':((ExitStatus >> 8) & 0x7f)})
                ChildProcesses.remove (Child)

    # If there are any kids still running then we need to go kill them because something must be wrong with them.
    if len(ChildProcesses) != 0:
        for Child in ChildProcesses:
            ExitStatus = -4
            ExitMsg = "Collection terminated because it exceeded the max runtime of %d" % SubProcTimeoutSecs
            IndidateNoDataFromNode (TimeStamp, Child['node_name'], ExitStatus, ExitMsg)
            NodesStatus.append ({'node_name':Child['node_name'], 'node_data_ip':"0.0.0.0", 'exit_status':ExitStatus})
            os.kill (Child['pid'], signal.SIGQUIT)
            printmsg ("Support data was not collected on node %s because it exceeded the maximum collection time" % Child['node_name'])

    # Retrieve the support tar.gz files from each host that we successfully got data for.
    # We have to skip the host this script is running on so it doesn't try to overwrite the file with
    # itself and leave us with nothing for this host.
    for Host in NodesStatus:
        Hostname   = Host['node_name']
        HostIP     = Host['node_data_ip']
        ExitStatus = Host['exit_status']

        if ExitStatus != 0:                     # Skip any nodes that we didn't get the support data for.
            continue

        if os.uname()[1] == Hostname:           # Skip this host because it is the host we're running on.
            continue

        printmsg ("Retrieving support file from node %s (%s)" % (Hostname, HostIP))

        try:
            Handle = None
            Handle = ssh_utils.SSHConnect (HostIP, Username=Username, Password=Password)
            NodeID = GetRemoteNodeID (Hostname, Handle)
            RemoteName = "phonehome_" + Hostname + "_" + NodeID + "_" + TimeStamp + ".tar.gz"
            GetRemoteFile (RemoteName, Hostname, Handle)
        except Exception, e:
            IndidateNoDataFromNode (Hostname, -5, "Exception msg: %s" % e)
            printmsg ("Exception msg: %s" % e)
            printmsg ("Could not retrieve remote support data from node %s due to the above error" % Hostname)
        finally:
            if Handle != None:
                ssh_utils.SSHDisconnect (Handle)

    # Tar up the files we retrieved from each host into a single tgz and then upload that file to the webserver.
    try:
        TarFile = TarSupportFiles (TimeStamp)
        WputFile (TarFile)
        printmsg ("Support data was successfully uploaded")
    except:
        if CmdLine:
            printmsg ("Support data was not uploaded to support site")
        else:
            raise Exception ("Support data was not uploaded to support site")
    return

# Output how to use this script.
def PrintHelp():
    print "This script will collect support data from all nodes or a specific node attached to this controller"
    print " arguments:"
    print "  -h                 -- this help text"
    print "  -s <script-file>   -- optional argument, path to a local script file that"
    print "                        is copied to the remote host to collect support data"
    print "  -n <host>          -- optional argument, only used if a specific host is"
    print "                        is to have its support data captured"
    print "  -u <url>           -- optional argument, alternate location to upload"
    print "                        the captured support data to"
    print "  -o                 -- optional argument, override checking if a capture"
    print "                        is already in progress"
    print " "
    return

# Process the command line args and determine what the user wants.
def ProcessCmdLine (argv):
    global Force
    global AllNodes
    global Node
    global ScriptFile
    global WputURL

    try:
        opts, args = getopt.getopt (argv, "hos:n:u:", "")
    except getopt.GetoptError:
        PrintHelp()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':                         # wants help
            PrintHelp()
            return (0)
        elif opt == '-o':                       # wants to override capture checking
            Force = True
        elif opt in ("-n"):                     # capture only from this node
            AllNodes = False
            Node = arg
        elif opt in ("-u"):                     # use this url to upload the data to
            WputURL = arg
        elif opt in ("-s"):                     # use this script file to collect the data with
            ScriptFile = arg
    return (-1)

# Main function when used from the command line.
if __name__ == "__main__":
    paramiko.util.log_to_file("paramiko.log")       # paramiko needs a log file to log messages to
    CmdLine = True
    Status = ProcessCmdLine (sys.argv[1:])
    if Status != -1:
        sys.exit (Status)
    DoCreate()
    sys.exit()
