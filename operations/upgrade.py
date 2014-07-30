#!/usr/local/bin/python2.7

import os
import sys
import getopt
import ssh_utils
import subprocess
import paramiko
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql

# Global constants.
Username = "root"                                     # Default user to login in with, must be root to rpm install
Password = config.TRAN_DB_PASS                        # Default password to login in with, transuser and root have same pwd
RemoteRPMPath = "/tmp"                                  # Location on the remote host to put the rpm file
RemoteInstallPath = "/usr/local/lib/python2.7"          # Location to install the software in
RemoteInstallDir = RemoteInstallPath + "/transcirrus"   # Full path to transcirrus softare
WgetURL = "http://www.transcirrus.com/download/repo/"   # URL for retrieving rpm files
WgetDownloadToDir = "/home/transuser"                   # Location to put retrieved rpm files

# Global vars that are used throughout the module and in unit testing.
AllNodes = True                     # Should all nodes be updated or just a single node
Node = ""                           # Single node to be updated
RPMFileToInstall = ""               # File name for rpm file to be installed
Force = False                       # Should be for the install even if the version is older
CmdLine = False                     # We are being run from the command line
ReleaseToDownload = "stable"        # The default release to download from the website

# Return the version string extracted from the given filename.
# The version string is in the format of xx.xx-xx
def ExtractVersion (RPMFile):
    Parts = RPMFile.strip().split('-')
    Version = Parts[1] + "-" + Parts[2].split('.')[0]
    return (Version)

# Return the major version number from the given version string.
# The version string is in the format of xx.xx-xx
def GetMajorNumber (Ver):
    Parts = Ver.strip().split('.')
    return (Ver.strip().split('.')[0])

# Return the minor version number from the given version string.
# The version string is in the format of xx.xx-xx
def GetMinorNumber (Ver):
    Parts = Ver.strip().split('.')
    return (Parts[1].split('-')[0])

# Return the release number from the given version string.
# The version string is in the format of xx.xx-xx
def GetReleaseNumber (Ver):
    return (Ver.strip().split('-')[1])

# Compares to version strings.
#    0 -- versions are equal
#    1 -- ver1 > ver2
#   -1 -- ver1 < ver2
def CompareVersions (Ver1, Ver2):
    if Ver1 == Ver2:
        return (0)
    if int(GetMajorNumber(Ver1)) < int(GetMajorNumber(Ver2)):
        return (-1)
    elif int(GetMajorNumber(Ver1)) > int(GetMajorNumber(Ver2)):
        return (1)
    else:
        if int(GetMinorNumber(Ver1)) < int(GetMinorNumber(Ver2)):
            return (-1)
        elif int(GetMinorNumber(Ver1)) > int(GetMinorNumber(Ver2)):
            return (1)
        else:
            if int(GetReleaseNumber(Ver1)) < int(GetReleaseNumber(Ver2)):
                return (-1)
            else:
                return (1)

# Returns just a filename given a fully qualified path.
def ExtractFilename (Name):
    Path = Name.strip().split('/')
    Num = len(Path)
    return (Path[Num-1])

# Return the transcirrus version that is installed on a remote host.
def GetRemoteVersion (Host, Handle):
    try:
        STDout, STDerr, ExitStatus = ssh_utils.ExecRemoteCommand ("rpm -qa transcirrus", Host, Handle)
        if ExitStatus != 0:
            print "Error retrieving current version on remote node, exit status:  %d" % ExitStatus
            print "stdout text: %s" % STDout
            print "stderr text: %s" % STDerr
            raise Exception ("GetRemoteVersion error")
        if STDout == "":
            return ("0.0-0")                    # No version installed so we default to this.
        return (ExtractVersion (STDout))
    except Exception, e:
        print "Error retrieving current version on remote node, exception: %s" % e
        raise

# Copies the given rpm to the remote host.
# Returns the full path to the retrieved file.
def CopyRPM (RPMFile, Host, Handle):
    RemoteRPMFile = RemoteRPMPath + "/" + ExtractFilename (RPMFile)
    try:
        ssh_utils.PutFile (RPMFile, RemoteRPMFile, Host, Handle)
    except Exception, e:
        print "Error copying rpm file to remote node, exception: %s" % e
        raise
    return (RemoteRPMFile)

# Makes a tar file of the current transcirrus software.
def BackupFiles (Version, Host, Handle):
    try:
        TarCommand = "tar czf " + RemoteInstallPath + "/transcirrus-" + Version + ".bck.tar.gz -C " + RemoteInstallPath + " transcirrus"
        STDout, STDerr, ExitStatus = ssh_utils.ExecRemoteCommand (TarCommand, Host, Handle)
        if ExitStatus != 0:
            print "Error backing up remote transcirrus directory, exit status:  %d" % ExitStatus
            print "stdout text: %s" % STDout
            print "stderr text: %s" % STDerr
            raise Exception ("BackupFiles error")
        return
    except Exception, e:
        print "Error retrieving current version on remote node, exception: %s" % e
        raise

# Installs the rpm that was placed on the remote host.
def InstallRPM (RPMFile, Host, Handle):
    RemoteRPMFile = RemoteRPMPath + "/" + ExtractFilename (RPMFile)
    try:
        RPMCommand = "rpm -Uvh --force " + RemoteRPMFile
        STDout, STDerr, ExitStatus = ssh_utils.ExecRemoteCommand (RPMCommand, Host, Handle)
        if ExitStatus != 0:
            print "Error installing rpm package %s on remote host, exit status:  %d" % (ExractFilename(RPMFile), ExitStatus)
            print "stdout text: %s" % STDout
            print "stderr text: %s" % STDerr
            raise Exception ("InstallRPM error")
        return
    except Exception, e:
        print "Error installing rpm package on remote host, exception: %s" % e
        raise

# Goes through the database and returns a dict of all nodes with the node's name and data IP address.
def FindNodesToUpgrade():
    try:
        handle = pgsql (config.TRANSCIRRUS_DB, config.TRAN_DB_PORT, config.TRAN_DB_NAME, config.TRAN_DB_USER, config.TRAN_DB_PASS)
    except Exception as e:
        print "Could not connect to db with error: %s" % (e)
        raise Exception ("Could not connect to db with error: %s" %(e))

    select_nodes = {'select':'node_name,node_data_ip','from':'trans_nodes'}
    nodes = handle.pg_select (select_nodes)
    if (nodes == ''):
        db.pg_close_connection()
        print "No other nodes where found in the database"
        raise Exception ("No other nodes where found in the database")

    Nodes = []
    for node in nodes:
        Nodes.append(node)

    handle.pg_close_connection()
    return (Nodes)

# Gets the given file from the webserver and puts in the desired location.
# Returns the full path to the retrieved file. If there is an error then the filename is "".
def WgetFile (File):
    Filename = ""

    try:
        Command = "wget --content-disposition -nv -t 3 -P " + WgetDownloadToDir + " " + WgetURL + File

        Subproc = subprocess.Popen (Command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        StdOut, StdErr = Subproc.communicate()

        # For some strange reason all the output ends up in StdErr
        StdOut = StdErr
        if Subproc.returncode != 0:
            print "Error downloading rpm file from www.transcirrus.com, exit status: %d" % Subproc.returncode
            print "Error message: %s" % StdErr
            return (Filename)

        # Extract the path from the output. The output looks like:
        #    xxxxxxxxxx -> "full path to file" xxxxxxxxxx
        i = StdOut.find ('->') + 4
        x = StdOut.find ('"', i)
        Filename = StdOut[i:x]

    except Exception, e:
        print "Error downloading rpm file from www.transcirrus.com, exception: %s" % e

    return (Filename)

# Do all the steps required to get, backup and install the software on remote host(s).
def DoUpgrade():
    global RPMFileToInstall

    # Get all the nodes from the DB or just use the one given on the command line.
    if AllNodes:
        NodesToUpgrade = FindNodesToUpgrade()
    else:
        NodesToUpgrade = []
        NodesToUpgrade.append ({'node_name': Node, 'node_data_ip': Node})

    if RPMFileToInstall != "":
        # The user gave us a path to a local rpm file to use so make sure it exists.
        if not os.path.exists (RPMFileToInstall):
            print "File not found: %s" % RPMFileToInstall
            sys.exit(2)
    else:
        # Go get the rpm file that the user wants from the website. We need to delete it if already exists since
        # wget will rename the new one that we download.
        File = WgetDownloadToDir + "/" + ReleaseToDownload
        if os.path.exists (File):
            os.remove (File)
        print "Downloading %s from %s" % (ReleaseToDownload, WgetURL)
        RPMFileToInstall = WgetFile (ReleaseToDownload)
        if RPMFileToInstall == "":
            sys.exit(2)

    # Get the version are we installing.
    NewVersion = ExtractVersion (RPMFileToInstall)

    # Loop through the host(s) and performed the required steps to upgrade each one.
    for Host in NodesToUpgrade:
        Hostname = Host['node_name']
        HostIP   = Host['node_data_ip']
        print ""
        print "Attempting to upgrade node %s (%s) to transcirrus version %s" % (Hostname, HostIP, NewVersion)

        try:
            print "--Connecting to remote host"
            Handle = ssh_utils.SSHConnect (HostIP, Username=Username, Password=Password)
            print "--Determining remote version"
            RemoteVersion = GetRemoteVersion (Hostname, Handle)
            if Force or CompareVersions (RemoteVersion, NewVersion) < 0:
                print "--Copying rpm file to remote host"
                RemoteRPMFile = CopyRPM (RPMFileToInstall, Hostname, Handle)
                print "--Saving off previous version"
                BackupFiles (RemoteVersion, Hostname, Handle)
                print "--Installing rpm file on remote host"
                InstallRPM (RemoteRPMFile, Hostname, Handle)
                ssh_utils.SSHDisconnect (Handle)
                print "--Node %s has been upgraded to version %s" % (Hostname, NewVersion)
            else:
                print "Node %s is already at version %s and will not be upgraded" % (Hostname, RemoteVersion)
                print "Use the -o option to override version checking and force the install"
        except Exception, e:
            print "Exception msg: %s" % e
            print "Node %s was not upgraded due to the above error" % Hostname
    return

# Output how to use this script.
def PrintHelp():
    print "This script will update all nodes or a specific node attached to this controller"
    print " arguments:"
    print "  -h                 -- this help text"
    print "  -r <release>       -- optional argument for which release to download"
    print "                        possible values are:"
    print "                          stable  - most stable release; this is the default"
    print "                          latest  - last development build"
    print "                          <a specific rpm file to download>"
    print "  -f <rpm-filename>  -- optional argument for a local rpm path/filename"
    print "                        not valid if -r is given"
    print "  -n <host>          -- optional argument, only used if a specific host is"
    print "                        is to be upgraded; specify host IP address or name"
    print "  -o                 -- override version checking and install even if a"
    print "                        newer version is already installed"
    return

# Determine if we were given an valid rpm file name. The format would be
#   aaaaaa-xx.xx-xx.bbbbb.rpm  where .bbbbb is not required
def ValidRPMFilename (Name):
    if not Name.endswith(".rpm"):
        return (False)
    try:
        Version = ExtractVersion (Name)
        if GetMajorNumber (Version) == "":
            return (False)
        if GetMinorNumber (Version) == "":
            return (False)
        if GetReleaseNumber (Version) == "":
            return (False)
    except Exception, e:
        return (False)
    return (True)

# Determine if we were given a valid rpm or release name. Valid names are:
#   stable
#   latest
#   aaaaaa-xx.xx-xx.bbbbb.rpm
def ValidReleaseArg (Name):
    if Name == "stable" or Name == "latest":
        return (True)
    if ValidRPMFilename (Name):
        return (True)

    print "Error: invalid release parameter -r %s" % Name
    print "Valid values are: stable or latest or a valid rpm file name"
    return False

# Process the command line args and determine what the user wants.
def ProcessCmdLine (argv):
    global Force
    global ReleaseToDownload
    global AllNodes
    global Node
    global RPMFileToInstall
    global WgetURL

    try:
        opts, args = getopt.getopt (argv, "hor:n:f:u:", "")
    except getopt.GetoptError:
        PrintHelp()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':                         # wants help
            PrintHelp()
            return (0)
        elif opt == '-o':                       # wants to override version checking
            Force = True
        elif opt in ("-r"):                     # wants a specific release
            if not ValidReleaseArg (arg):
                return (2)
            ReleaseToDownload = arg
        elif opt in ("-n"):                     # install only on this node
            AllNodes = False
            Node = arg
        elif opt in ("-f"):                     # use this local rpm file
            if not ValidRPMFilename (arg):
                print "Error: invalid rpm file name -f %s" % arg
                print "File names must be in the form of name-#.#-#.noarch.rpm"
                return (2)
            RPMFileToInstall = arg
        elif opt in ("-u"):                     # use this url, undocumented in help
            WgetURL = arg
    return (-1)

# Main function when used from the command line.
if __name__ == "__main__":
    paramiko.util.log_to_file("filename.log")       # paramiko needs a log file to log messages to
    CmdLine = True
    Status = ProcessCmdLine (sys.argv[1:])
    if Status != -1:
        sys.exit (Status)
    DoUpgrade()
    sys.exit()
