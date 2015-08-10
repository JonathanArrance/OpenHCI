#
# nfs specific config functions
#

import os
import pwd
import grp
import subprocess
import transcirrus.operations.third_party_storage.common as common

# Constants
NFS_NAME = "nfs"
NFS_SHARES_CONF = "/etc/cinder/shares_nfs.conf"
#NFS_SHARES_CONF = "shares_nfs.conf"
NFS_MOUNTPOINT_BASE = "/mnt/nfs-vols/cinder-volume"


def add_nfs_to_cinder():
    if not common.add_backend (NFS_NAME):
        return (False)
    add_nfs_stanza()
    return (True)


def update_nfs_conf (mountpoints):
    delete_nfs_conf()
    add_nfs_conf (mountpoints)
    return (True)


def add_nfs_stanza():
    curr_file = common.CINDER_CONF
    outfile = open (curr_file, 'a')

    outfile.writelines ("\n")
    outfile.writelines ("[" + NFS_NAME + "]\n")
    outfile.writelines ("# static data\n")
    outfile.writelines ("volume_group=cinder-volume-nfs\n")
    outfile.writelines ("volume_backend_name=" + NFS_NAME + "\n")
    outfile.writelines ("volume_driver=cinder.volume.drivers.nfs.NfsDriver\n")
    outfile.writelines ("nfs_shares_config=" + NFS_SHARES_CONF + "\n")
    outfile.writelines ("nfs_mount_point_base=" + NFS_MOUNTPOINT_BASE + "\n")

    outfile.close()
    return


def add_nfs_conf (mountpoints):
    curr_file = NFS_SHARES_CONF
    outfile = open (curr_file, 'w')

    outfile.writelines ("# data below is customer supplied\n")
    for mntpt in mountpoints:
        outfile.writelines (mntpt + "\n")

    outfile.close()
    return


def add_base_mountpoint():
    if os.path.isdir (NFS_MOUNTPOINT_BASE):
        return
    os.makedirs (NFS_MOUNTPOINT_BASE)
    uid = pwd.getpwnam("cinder").pw_uid
    gid = grp.getgrnam("cinder").gr_gid
    os.chown (NFS_MOUNTPOINT_BASE, uid, gid)
    return


def get_nfs_data():
    curr_file = NFS_SHARES_CONF
    infile = open (curr_file, 'rU')

    row = infile.readlines()

    mountpoints = []
    for line in row:
        if line[0] == "#":
            continue
        mountpoints.append (line.replace("\n", ""))

    infile.close()
    return (mountpoints)


def delete_nfs_conf():
    if not os.path.exists (NFS_SHARES_CONF):
        return
    os.remove (NFS_SHARES_CONF)
    return


def validate_mountpoints (mountpoints):
    mount_dir = "/tmp/nfs_test"
    if not os.path.isdir (mount_dir):
        os.makedirs (mount_dir)

    mount_failure = False
    mountpoint_msgs = []

    for mntpt in mountpoints:
        command = "sudo mount " + mntpt + " " + mount_dir + " -o retry=0,timeo=50"
        subproc = subprocess.Popen (command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = subproc.communicate()

        if subproc.returncode != 0:
            mount_failure = True
            mountpoint_msgs.append([mntpt, stderr])
        else:
            command = "sudo touch " + mount_dir + "/test.file"
            subproc = subprocess.Popen (command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = subproc.communicate()

            if subproc.returncode != 0:
                mount_failure = True
                mountpoint_msgs.append([mntpnt, "Error attempting to create file on %s - %s" % (mntpt, stderr)])
            else:
                mountpoint_msgs.append([mntpt, ""])
                command = "sudo rm -fr " + mount_dir + "/test.file"
                subproc = subprocess.Popen (command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                stdout, stderr = subproc.communicate()

            command = "sudo umount " + mount_dir
            subproc = subprocess.Popen (command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = subproc.communicate()
    
    return (not mount_failure, mountpoint_msgs)
