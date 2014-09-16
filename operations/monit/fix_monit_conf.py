#!/usr/local/bin/python2.7
import os
import sys
import subprocess

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
        os.remove (MONIT_CONF_LOC + CN_CONF)
        os.remove (MONIT_CONF_LOC + SN_CONF)
        return

    # Compute node so delete the core and storage only conf files.
    if node_type == "cn":
        os.remove (MONIT_CONF_LOC + CC_CONF)
        os.remove (MONIT_CONF_LOC + SN_CONF)
        return

    # Storage node so delete the core and compute only conf files.
    if node_type == "sn":
        os.remove (MONIT_CONF_LOC + CC_CONF)
        os.remove (MONIT_CONF_LOC + CN_CONF)
        return


# This is a storage node so determine what storage is attached and fix the conf file so monit
# can properly monitor the storage.
# We use the mount command to list the mount points and then look for a line with xfs since
# the only xfs mount point will be the drive we want to monitor. Example:
#   /dev/sdc1 on /data/gluster type xfs (rw) 
def fix_storage_conf():
    command = "mount | grep xfs"

    sub_proc = subprocess.Popen (command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    std_out, std_err = sub_proc.communicate()

    if sub_proc.returncode != 0:
        print "Error getting mount points, exit status: %d" % sub_proc.returncode
        print "Error message: %s" % std_err
        return

    # Extract the device name from the output. The output looks like:
    #    /dev/sdc1 on /data/gluster type xfs (rw)
    dev = std_out.split()[0]

    # Update the disks.conf file with our device.
    handle = open (MONIT_CONF_LOC + DK_CONF, 'a')
    handle.write ("check filesystem sn-gluster-vol with path %s\n" % dev)
    handle.write ("  if space usage > 80% then alert\n")
    handle.write ("  if inode usage > 80% then alert\n")
    handle.close()
    return


# Main entry point for this script.
# Call the routine that will delete the un-needed conf files which is based on the node type which is passed in.
# Also if this is a storage node, then call the routine that will find the gluster volume and set is in the conf
# file so monit can start monitoring it.
if __name__ == "__main__":
    node_type = sys.argv[1]
    fix_conf_files (node_type)
    if node_type == "sn":
        fix_storage_conf()
    sys.exit()
