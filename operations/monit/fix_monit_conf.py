#!/usr/local/bin/python2.7
import os
import sys
import subprocess
import socket
import transcirrus.common.node_stats as node_stats

MONIT_CONF_LOC = "/usr/local/lib/python2.7/transcirrus/operations/monit/"
CC_CONF = "core-only.conf"
CN_CONF = "compute-only.conf"
SN_CONF = "storage-only.conf"
DK_CONF = "disks.conf"

# Fix the conf files based on the type of node we were given. There are specific conf files
# that are only required when running on a specific node type.
#   cc - core
#   cn - compute
#   sn - storage
def fix_conf_files (node_type):
    # Core node so delete the compute and storage only conf files.
    if node_type == "cc":
        if os.path.isfile (MONIT_CONF_LOC + CN_CONF):
            os.remove (MONIT_CONF_LOC + CN_CONF)
        if os.path.isfile (MONIT_CONF_LOC + SN_CONF):
            os.remove (MONIT_CONF_LOC + SN_CONF)
        return

    # Compute node so delete the core and storage only conf files.
    if node_type == "cn":
        if os.path.isfile (MONIT_CONF_LOC + CC_CONF):
            os.remove (MONIT_CONF_LOC + CC_CONF)
        if os.path.isfile (MONIT_CONF_LOC + SN_CONF):
            os.remove (MONIT_CONF_LOC + SN_CONF)
        return

    # Storage node so delete the core and compute only conf files.
    if node_type == "sn":
        if os.path.isfile (MONIT_CONF_LOC + CC_CONF):
            os.remove (MONIT_CONF_LOC + CC_CONF)
        if os.path.isfile (MONIT_CONF_LOC + CN_CONF):
            os.remove (MONIT_CONF_LOC + CN_CONF)
        return


# Determine what storage is attached and fix the disk.conf file so monit
# can properly monitor the storage.
# We use the mount command to list the mount points and then look for a line with xfs since
# the only xfs mount point will be the disk(s) we want to monitor. Example:
#   /dev/sdc1 on /data/gluster type xfs (rw)
def add_storage_conf():
    command = "mount | grep xfs"

    sub_proc = subprocess.Popen (command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    std_out, std_err = sub_proc.communicate()

    if sub_proc.returncode != 0:
        if sub_proc.returncode == 1:
            return
        print "Error getting mount points, exit status: %d" % sub_proc.returncode
        print "Error message: %s" % std_err
        return

    # Update the disks.conf file with the mount points we will find.
    # To do this we read the disks.conf file until we get to the
    # line with "# Start" and then write/overwrite with each
    # mount point we found.
    handle = open (MONIT_CONF_LOC + DK_CONF, 'r+')
    line = handle.readline()
    while line:
        if line.find("# Start") >= 0:
            break
        line = handle.readline()

    # Loop through the output (line by line) and extract the mount point(s)
    # and add them to our disks.conf file.
    lines = std_out.split("\n")
    for line in lines:
        # Skip blank lines
        if len(line) < 1:
            continue

        # Extract the mount point and short name from the output. The output looks like:
        #    /dev/sdc1 on /data/gluster type xfs (rw)
        #  mountpoint = /data/gluster
        #  name = gluster
        mountpoint = line.split()[2]
        name = mountpoint.split("/")[2]

        handle.write ("check filesystem %s with path %s\n" % (name, mountpoint))
        handle.write ("  if space usage > 80% then alert\n")
        handle.write ("  if inode usage > 80% then alert\n\n")

    handle.truncate()
    handle.close()
    return


# Return the node type that we are running on:
#   cc - core node
#   cn - compute node
#   sn - storage node
def get_node_type():
    node_list = node_stats.get_list_of_nodes(socket.gethostname())
    return (node_list[0]['node_type'])


# Main entry point for this script.
# is passed in and call the routine that will find the gluster volume(s) to the disks.conf
# file so monit can start monitoring it.
if __name__ == "__main__":
    # If we aren't given a node type then go figure it out else use what we were given.
    if len(sys.argv) == 1:
        node_type = get_node_type()
    else:
        node_type = sys.argv[1]
    print "node_type: %s" % node_type
    fix_conf_files (node_type)
    add_storage_conf()
    sys.exit()
