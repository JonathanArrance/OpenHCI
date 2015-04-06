#
# nfs specific config functions
#

import os
import pwd
import grp
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
    os.mkdir (NFS_MOUNTPOINT_BASE)
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
