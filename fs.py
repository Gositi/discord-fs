#!/usr/bin/env python3

#Provides class for FUSE filesystem functionality
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

#Derived from https://github.com/skorokithakis/python-fuse-sample
#Copyright (C) 2016 Stavros Korokithakis
#License (BSD-2-Clause) provided in file 'LICENSE-2'

import os
import errno
import fuse

class Filesystem (fuse.Operations):
    def __init__ (self, dc, temp):
        self.dc = dc
        self.temp = temp
        self.list = {}
 
    #Get basic file attributes
    def getattr (self, path, fh=None):
        if path == "/":
            return {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 16877, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 0, 'st_uid': 1000}
        elif not self.dc.exists (path):
            raise OSError (errno.ENOENT, "File does not exist") #Tells programs that the file doesn't exist
        else:
            return {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 33204, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 25000000, 'st_uid': 1000}

    #Get directory listing
    def readdir (self, path, fh):
        dirents = ['.', '..']
        dirents.extend (self.dc.readdir (path))
        for i in dirents:
            yield i

    #Remove file
    def unlink (self, path):
        print ("rm")
        self.dc.remove (path)
        if os.path.exists (self.temp + path):
            os.unlink (self.temp + path)

    #Opening of file
    def open (self, path, flags):
        print ("op")
        self.dc.open (path)
        if not path in self.list.keys ():
            self.list [path] = 0
        self.list [path] += 1
        return os.open (self.temp + path, flags)
    
    #Write buffered file contents to the actual file
    def flush (self, path, fh):
        print ("fl")
        return os.fsync (fh)
    def fsync (self, path, fdatasync, fh):
        return self.flush (path, fh)

    #Close file
    def release (self, path, fh):
        print ("cl")
        #Close file
        ret = os.close (fh)
        self.list [path] -= 1
        #Remove file from temp if it isn't used anymore
        if self.list [path] <= 0:
            self.list.pop (path)
            self.dc.close (path)
            os.unlink (self.temp + path)
        return ret

    #Read data from file
    def read (self, path, length, offset, fh):
        print ("re")
        os.lseek (fh, offset, os.SEEK_SET)
        return os.read (fh, length)

    #Write data to file
    def write (self, path, buf, offset, fh):
        print ("wr")
        os.lseek (fh, offset, os.SEEK_SET)
        return os.write (fh, buf)

    #Needed to create file
    def create (self, path, mode, fi=None):
        print ("cr")
        #Create file in temp
        uid, gid, pid = fuse.fuse_get_context ()
        fd = os.open (self.temp + path, os.O_WRONLY | os.O_CREAT, mode)
        os.chown (self.temp + path, uid, gid) #chown to context uid & gid
        #Sync file to source
        self.dc.sync (path)
        #Add file to list
        self.list [path] = 1
        return fd

    #Rename file
    def rename (self, old, new):
        print ("mv")
        #Rename in temp
        if os.path.exists (self.temp + old):
            os.rename (self.temp + old, self.temp + new)
        #Rename at source
        self.dc.rename (old, new)
        #Make change in list of open files
        if old in self.list.keys ():
            self.list [new] = self.list.pop (old)
