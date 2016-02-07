#!/usr/local/bin/python2.7

import os
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
import sys
import getopt
import subprocess
import paramiko
import cmd
import transcirrus.operations.ssh_utils as ssh_utils
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
import transcirrus.common.logger as logger

# Global constants.
Username = "root"                                       # Default user to login in with
Password = config.TRAN_DB_PASS                          # Default password to login in with
RemotePath = "/tmp"                                     # Location on the remote host to put the sript file
InstallPath = "/usr/local/lib/python2.7/transcirrus/"   # Default TransCirrus install path

# Global vars that are used throughout the module and in unit testing.
Interactive = True                  # We default to interactive mode
AllNodes = True                     # Should all nodes be updated or just a single node
Node = ""                           # Single node to be updated
FileScript = ""                     # File name for script file to be executed
CmdLine = False                     # We are being run from the command line
EnableCache = False                 # Enable sending log messages to memcached
Cache = None                        # Handle to memcached
CacheKey = "TransCirrusService"     # Cache key to reference our messages


class RunCommand(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "ssh> "
        self.intro  = None
        self.hosts = []
        self.connections = []
        self.change_dir = False
        self.curr_dir_cmd = None
        return

    def add_host(self, name, ip_addr, username, password):
        host_data = {}
        host_data['name'] = name
        host_data['ip_addr'] = ip_addr
        host_data['username'] = username
        host_data['password'] = password
        self.hosts.append(host_data)
        return

    def connect(self):
        for host in self.hosts:
            try:
                print "-- Attempting connection to host %s..." % host['name'],
                client = None
                client = ssh_utils.SSHConnect(host['ip_addr'], Username=host['username'], Password=host['password'])
                self.connections.append(client)
                print "success"
            except Exception, e:
                print ""
                printmsg ("Exception msg: %s" % e)
                printmsg ("Could not connect to host %s due to the above error" % host['name'])
        if len(self.connections) == 0:
            print "Warning: could not connect to any host in the cloud"
        return

    def close(self):
        for conn in self.connections:
            ssh_utils.SSHDisconnect(conn)
        return

    def emptyline(self):    
        # Do nothing on an empty input line
        return

    def precmd(self, line):
        commands = line.split(';')
        for command in commands:
            if command.startswith("cd "):
                self.change_dir = True
        return line

    def default(self, command):
        if self.curr_dir_cmd != None:
            command = self.curr_dir_cmd + ";" + command

        if self.change_dir:
            commands = command.split(';')
            idx = -1
            i = 0
            for com in commands:
                if com.startswith("cd "):
                    idx = i
                i = i + 1
            if idx != -1:
                line = ""
                i = 0
                for com in commands:
                    line = line + com + ";"
                    if i == idx:
                        line = line + "echo 'cwd->'$(pwd);"
                    i = i + 1
                command = line

        for host, conn in zip(self.hosts, self.connections):
            print "%s:" % host['name'],
            try:
                stdout, stderr, exitstatus = ssh_utils.ExecRemoteCommand (command, host['name'], conn)
                if exitstatus == 0:
                    print "success"
                else:
                    print "exit: %d" % exitstatus
                if len(stdout) > 0:
                    for line in stdout.splitlines():
                        if self.change_dir and line.startswith("cwd->"):
                            self.curr_dir_cmd = "cd " + line.split('->')[1]
                            self.change_dir = False
                            continue
                        print "\t%s" % line
                if len(stderr) > 0:
                    print "  stderr:"
                    for line in stderr.splitlines():
                        print "    %s" % line
            except Exception, e:
                printmsg ("Error running command on remote host, exception: %s" % e)
                raise Exception ("Error running command on remote host, exception: %s" % e)
        return

    def do_restart(self, args):
        'Run the restart script on every node'
        command = InstallPath + "operations/restart.sh"
        self.default(args)
        return

    def do_exit(self, args):
        'Exit this application'
        self.close()
        return (-1)

    def do_quit(self, args):
        'Exit this application, same as exit'
        return (self.do_exit(args))

    def do_EOF(self, args):
        'Exit this application, same as exit'
        return (self.do_exit(args))

    def help_cmd(self):
        print "The first word of any command will be compared to the list of 'known'"
        print "commands. If a match is found then that action will be taken. If not"
        print "then the command assumed to be a bash command and will be executed"
        print "on all nodes in the cloud."
        return

    def do_help(self, args):
        '''
          help or ? with no arguments prints a list of commands for which help is available
          help <command> or ? <command> gives help on <command>'''
        return(cmd.Cmd.do_help(self, args))


# Handle logging of print messages (console, logfile and memcached).
def printmsg (msg):
    if CmdLine:
        print msg

    logger.sys_info ("Service script: " + msg)

    if EnableCache and Cache != None:
        Data = Cache.get(CacheKey)
        NumMessages = int(Data['num_messages'])
        Data['num_messages'] = NumMessages + 1
        Data['msg%s' % NumMessages] = msg
        Cache.set (CacheKey, Data)
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

# Copies the given script to the remote host.
# Returns the full path to the retrieved file.
def CopyScript (ScriptFile, Host, Handle):
    RemoteFile = RemotePath + "/" + ExtractFilename (ScriptFile)
    try:
        ssh_utils.PutFile (ScriptFile, RemoteFile, Host, Handle)
    except Exception, e:
        printmsg ("Error copying script file to remote node, exception: %s" % e)
        raise Exception ("Error copying script file to remote node, exception: %s" % e)
    return (RemoteFile)

# Runs the script that was placed on the remote host.
def RunScript (ScriptFile, Host, Handle):
    RemoteScript = RemotePath + "/" + ExtractFilename (ScriptFile)
    try:
        RunCommand = "chmod 777 " + RemoteScript + "; " + RemoteScript
        STDout, STDerr, ExitStatus = ssh_utils.ExecRemoteCommand (RunCommand, Host, Handle)
        if ExitStatus != 0:
            printmsg ("Error running script %s on remote host, exit status: %d" % (ExtractFilename(ScriptFile), ExitStatus))
            printmsg ("stdout text: %s" % STDout)
            printmsg ("stderr text: %s" % STDerr)
            raise Exception ("Error running script %s on remote host, exit status: %d" % (ExtractFilename(ScriptFile), ExitStatus))
        return
    except Exception, e:
        printmsg ("Error running script on remote host, exception: %s" % e)
        raise Exception ("Error running script on remote host, exception: %s" % e)

# Goes through the database and returns a dict of all nodes with the node's name and data IP address.
def FindNodes (Nodename=None):
    try:
        handle = pgsql (config.TRANSCIRRUS_DB, config.TRAN_DB_PORT, config.TRAN_DB_NAME, config.TRAN_DB_USER, config.TRAN_DB_PASS)
    except Exception as e:
        printmsg ("Could not connect to db with error: %s" % e)
        raise Exception ("Could not connect to db with error: %s" % e)

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

# Do all the steps required to run the script on remote host(s).
def HandleScript():
    global ScriptFile

    # Get all the nodes from the DB or just use the one given on the command line.
    if AllNodes:
        NodesToRunOn = FindNodes()
    else:
        # Determine if we were given a name or IP address.
        if Node.split('.')[-1].isdigit():
            # We have an IP address so just use it for the name and address.
            NodesToRunOn = []
            NodesToRunOn.append ({'node_name': Node, 'node_data_ip': Node})
        else:
            # We have a name so go lookup the the IP address in the database.
            NodesToRunOn = FindNodes (Node)

    if ScriptFile != "":
        # The user gave us a path to a local script file to use so make sure it exists.
        if not os.path.exists (ScriptFile):
            if CmdLine:
                printmsg ("File not found: %s" % ScriptFile)
                sys.exit(2)
            else:
                raise Exception ("File not found: %s" % ScriptFile)
    else:
        # Go get the default script file.
        ScriptFile = DefaultScriptFile

    # Loop through the host(s) and performed the required steps to run the script on each one.
    for Host in NodesToRunOn:
        Hostname = Host['node_name']
        HostIP   = Host['node_data_ip']
        print ""
        printmsg ("Attempting to execute script on node %s (%s)" % (Hostname, HostIP))

        try:
            printmsg ("--Connecting to remote host")
            Handle = None
            Handle = ssh_utils.SSHConnect (HostIP, Username=Username, Password=Password)
            printmsg ("--Copying script file to remote host")
            RemoteFile = CopyScript (ScriptFile, Hostname, Handle)
            printmsg ("--Running script file on remote host")
            RunScript (RemoteFile, Hostname, Handle)
            printmsg ("--Node %s has successfully run the script" % Hostname)
        except Exception, e:
            printmsg ("Exception msg: %s" % e)
            printmsg ("Node %s did not run the script due to the above error" % Hostname)
        finally:
            if Handle != None:
                ssh_utils.SSHDisconnect (Handle)
    return

def HandleInteractive():
    print "Welcome to the TransCirrus Cloud console..."
    print ""
    print "Type either a bash command to be executed on all nodes in the cloud or"
    print "type help for assistance on application specific commands."
    print "Warning: All commands are run as root and the current directory is /root"
    print ""

    Console = RunCommand()

    if AllNodes:
        NodesToRunOn = FindNodes()
    else:
        if Node.split('.')[-1].isdigit():
            NodesToRunOn = []
            NodesToRunOn.append ({'node_name': Node, 'node_data_ip': Node})
        else:
            NodesToRunOn = FindNodes (Node)
    for Host in NodesToRunOn:
        Console.add_host(Host['node_name'], Host['node_data_ip'], Username, Password)
    Console.connect()
    Console.cmdloop()
    return

# Output how to use this script.
def PrintHelp():
    print "This application will allow you to run commands interactively or"
    print "run a given script on all nodes or a specific node in the cloud"
    print " arguments:"
    print "  -h                    -- this help text"
    print "  -i                    -- default, run commands interactively on the cloud"
    print "  -f <script-filename>  -- run a local script instead of interactive mode"
    print "  -n <host>             -- optional argument, only run commands/script on this"
    print "                           specific host; specify host IP address or name"
    return

# Process the command line args and determine what the user wants.
def ProcessCmdLine (argv):
    global AllNodes
    global Node
    global ScriptFile
    global Interactive

    try:
        opts, args = getopt.getopt (argv, "hin:f:", "")
    except getopt.GetoptError:
        PrintHelp()
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":                         # wants help
            PrintHelp()
            return (0)
        elif opt == "-i":                       # interactive mode
            Interactive = True
        elif opt == "-n":                       # run script only on the given node
            AllNodes = False
            Node = arg
        elif opt == "-f":                       # use this local script file
            Interactive = False
            ScriptFile = arg
    return (-1)

# Main function when used from the command line.
if __name__ == "__main__":
    paramiko.util.log_to_file("paramiko.log")       # paramiko needs a log file to log messages to
    CmdLine = True
    Status = ProcessCmdLine (sys.argv[1:])
    if Status != -1:
        sys.exit (Status)
    if Interactive:
        HandleInteractive()
    else:
        HandleScript()
    sys.exit()
