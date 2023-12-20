#!/usr/bin/env python3

#Taken from https://github.com/skorokithakis/python-fuse-sample/blob/master/passthrough.py

import os
import sys
import errno

from fuse import FUSE, FuseOSError, Operations, fuse_get_context

class Passthrough(Operations):
    def __init__(self, root):
        self.root = root

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    #Needed for basic filesystem access
    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        if path != "/":
            return {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 33204, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 0, 'st_uid': 1000}
        else:
            return {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 16877, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 0, 'st_uid': 1000}

    #Needed for directory listings
    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    #Needed for file removal
    def unlink(self, path):
        return os.unlink(self._full_path(path))

    # File methods
    # ============

    #Needed to use file 
    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    #Needed to create file
    def create(self, path, mode, fi=None):
        uid, gid, pid = fuse_get_context()
        full_path = self._full_path(path)
        fd = os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)
        os.chown(full_path,uid,gid) #chown to context uid & gid
        return fd

    #Needed to read file
    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    #Needed to write file
    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    #TODO Is this needed??
    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    #Needed to make sure changes are put in practice
    #Might see use in later applications (e.g. forcing write of metadata)
    def flush(self, path, fh):
        return os.fsync(fh)

    #Needed to use file
    def release(self, path, fh):
        return os.close(fh)

    #See flush
    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


def main(mountpoint, root):
    FUSE(Passthrough(root), mountpoint, nothreads=True, foreground=True, allow_other=False)


if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
