#!/usr/bin/env python3

import os
import sys
import errno

from fuse import FUSE, FuseOSError, Operations, fuse_get_context

#TODO Provide the connection to Discord
#Simulates the Discord connection, by implementing a lot of basic filesystem functionality
class Discord:
    def __init__(self, source, temp):
        self.source = source
        self.temp = temp

    #Provide list of files available
    def readdir (self, path):
        dirents = []
        if os.path.isdir(self.source + path):
            dirents.extend(os.listdir(self.source + path))
        for r in dirents:
            yield r

class Passthrough (Operations):
    def __init__(self, source, temp):
        self.source = source
        self.temp = temp
        self.dc = Discord (source, temp)
 
    #Get basic file attributes
    def getattr (self, path, fh=None):
        st = os.lstat(self.source + path)
        if path != "/":
            return {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 33204, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 0, 'st_uid': 1000}
        else:
            return {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 16877, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 0, 'st_uid': 1000}

    #Get directory listing
    def readdir (self, path, fh):
        dirents = ['.', '..']
        dirents.extend (self.dc.readdir (path))
        for i in dirents:
            yield i

def main(mountpoint):
    source = "./ref/"
    temp = "./temp/"
    FUSE(Passthrough(source, temp), mountpoint, nothreads=True, foreground=True, allow_other=False)


if __name__ == '__main__':
    main(sys.argv[1])
