import paramiko
import transcirrus.common.logger as logger

# Create a ssh connection to the specified host. Without a username/password, it will default to trying the
# various methods that a normal ssh client would try.
# Returns a handle to be used with other functions that do useful stuff on the remote node.
def SSHConnect (Host, Username=None, Password=None):
    Handle = None
    try:
        Handle = paramiko.SSHClient()
        Handle.set_missing_host_key_policy(paramiko.AutoAddPolicy())    # automatically accept the remote host's key
        Handle.load_system_host_keys()
        Handle.connect (Host, username=Username, password=Password)
        return (Handle)
    except Exception, e:
        ErrMsg = "SSH failed to connect to host %s with username (%s); msg: %s" % (Host, Username, e)
        logger.sys_error (ErrMsg)
        raise Exception (ErrMsg)

# Execute a command on the remote host.
# Returns stdout, stderr and exit status
def ExecRemoteCommand (Command, Host, Handle):
    try:
        stdin, stdout, stderr = Handle.exec_command (Command)
        ExitStatus = stdout.channel.recv_exit_status()
        stdin.close()
        STDout = stdout.read()
        STDerr = stderr.read()
        stdout.close()
        stderr.close()
        return (STDout, STDerr, ExitStatus)
    except Exception, e:
        ErrMsg = "SSH failed to execute command on host %s with command [%s]; msg: %s" % (Host, Command, e)
        logger.sys_error (ErrMsg)
        raise Exception (ErrMsg)

# Retrieves the source file from the remote host and places it in the destination location.
def GetFile (SrcFile, DestFile, Host, Handle):
    try:
        sftp = Handle.open_sftp()
        sftp.get(SrcFile, DestFile)
        sftp.close()
        return
    except Exception, e:
        ErrMsg = "SSH failed to get remote file [%s --> %s] on host %s; msg: %s" % (SrcFile, DestFile, Host, e)
        logger.sys_error (ErrMsg)
        raise Exception (ErrMsg)

# Pushes the source file to the destination location on the remote host.
def PutFile (SrcFile, DestFile, Host, Handle):
    try:
        sftp = Handle.open_sftp()
        sftp.put(SrcFile, DestFile)
        sftp.close()
        return
    except Exception, e:
        ErrMsg = "SSH failed to put remote file [%s --> %s] on host %s; msg: %s" % (SrcFile, DestFile, Host, e)
        logger.sys_error (ErrMsg)
        raise Exception (ErrMsg)

# Closes the ssh connection.
def SSHDisconnect (Handle):
    Handle.close()
    Handle = None
    return
