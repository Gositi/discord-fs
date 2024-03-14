#Provides class for FUSE filesystem functionality
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

#Derived from https://github.com/skorokithakis/python-fuse-sample
#Copyright (C) 2016 Stavros Korokithakis
#License (BSD-2-Clause) provided in file 'LICENSE-2'

import os
import errno
import fuse
import time

class Filesystem (fuse.Operations):
    def __init__ (self, ops, cache):
        self.ops = ops
        self.cache = cache
        self.list = {}
        print ("FS ready.")

    #Function ran at unmount
    def destroy (self, path):
        print ("Unmount.")

    #TODO Create access function

    #Get basic file attributes
    def getattr (self, path, fh=None):
        if not self.ops.exists (path):
            raise OSError (errno.ENOENT, "File does not exist") #Tells programs that the file doesn't exist
        else:
            return self.ops.getMetadata (path)

    #Change mode of file
    def chmod (self, path, mode):
        print ("cm")
        self.ops.changeMetadata (path, "st_mode", mode)
        self.ops.changeMetadata (path, "st_ctime", time.time ())

    #Change owner of a file
    def chown (self, path, uid, gid):
        print ("co")
        self.ops.changeMetadata (path, "st_uid", uid)
        self.ops.changeMetadata (path, "st_gid", gid)
        self.ops.changeMetadata (path, "st_ctime", time.time ())

    #Change timestamps of a file
    def utimens (self, path, times = None):
        print ("ut")
        if not times:
            times = (time.time (), time.time ())
        self.ops.changeMetadata (path, "st_atime", times [0])
        self.ops.changeMetadata (path, "st_mtime", times [1])

    #Get directory listing
    def readdir (self, path, fh):
        dirents = ['.', '..']
        dirents.extend (self.ops.readdir (path))
        for i in dirents:
            yield i

    #Remove file
    def unlink (self, path):
        print ("rm")
        self.ops.remove (path)
        if os.path.exists (self.cache + path):
            os.unlink (self.cache + path)

    #Opening of file
    def open (self, path, flags):
        print ("op")
        self.ops.open (path)
        if not path in self.list.keys ():
            self.list [path] = [0, False, False]
        self.list [path][0] += 1
        return os.open (self.cache + path, flags)
    
    #Write buffered file contents to the actual file
    def flush (self, path, fh):
        print ("fl")
        return os.fsync (fh)
    def fsync (self, path, fdatasync, fh):
        print ("fs")
        return os.fsync (fh)

    #Close file
    def release (self, path, fh):
        print ("cl")
        #Close file
        ret = os.close (fh)
        self.list [path][0] -= 1
        #Update timestamps accordingly
        metadata = self.ops.getMetadata (path)
        atime = metadata ["st_atime"]
        mtime = metadata ["st_mtime"]
        if self.list [path][1]:
            mtime = time.time ()
        if self.list [path][2]:
            atime = time.time ()
        self.utimens (path, times = (atime, mtime))
        #Remove file from cache if it isn't used anymore
        if self.list [path][0] <= 0:
            if self.list [path][1]: self.ops.close (path)   #Write to Discord if file has been written
            self.list.pop (path)
            os.unlink (self.cache + path)
        return ret

    #Read data from file
    def read (self, path, length, offset, fh):
        print ("re")
        os.lseek (fh, offset, os.SEEK_SET)
        self.list [path][2] = True
        return os.read (fh, length)

    #Write data to file
    def write (self, path, buf, offset, fh):
        print ("wr")
        os.lseek (fh, offset, os.SEEK_SET)
        self.list [path][1] = True
        return os.write (fh, buf)

    #Truncate file
    def truncate (self, path, length, fh = None):
        print ("tr")
        with open (self.cache + path, 'r+') as f:
            f.truncate (length)
        self.list [path][1] = True

    #Needed to create file
    def create (self, path, mode, fi=None):
        print ("cr")
        #Create file in cache
        uid, gid, pid = fuse.fuse_get_context ()
        fd = os.open (self.cache + path, os.O_WRONLY | os.O_CREAT, mode)
        os.chown (self.cache + path, uid, gid) #chown to context uid & gid
        #Sync file to source
        self.ops.sync (path)
        #Add file to list
        self.list [path] = [1, False, False]
        #Change metadata for FS
        self.chown (path, uid, gid)
        self.utimens (path)
        return fd

    #Rename file
    def rename (self, old, new):
        print ("mv")
        #Rename in cache
        if os.path.exists (self.cache + old):
            os.rename (self.cache + old, self.cache + new)
        #Rename at source
        self.ops.rename (old, new)
        #Make change in list of open files
        if old in self.list.keys ():
            self.list [new] = self.list.pop (old)
        self.ops.changeMetadata (path, "st_ctime", time.time ())
