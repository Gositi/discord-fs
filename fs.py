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
    def __init__ (self, DEBUG, ops, cache):
        self.DEBUG = DEBUG
        self.ops = ops
        self.cache = cache
        self.list = {}
        print ("FS ready.")

    #Function ran at unmount
    def destroy (self, path):
        print ("Unmount.")

    #Get basic filesystem info
    def statfs (self, path):
        return {"f_namemax": 128} #Only return namemax, in order to make renaming files in GUI possible

    #Get basic file attributes
    def getattr (self, path, fh=None):
        if not self.ops.exists (path):
            raise OSError (errno.ENOENT, "File does not exist")
        else:
            return self.ops.getMetadata (path)

    #Change mode of file
    def chmod (self, path, mode):
        if self.DEBUG: print ("chmod", path)

        self.ops.changeMetadata (path, "st_mode", mode)
        self.ops.changeMetadata (path, "st_ctime", time.time ())

    #Change owner of a file
    def chown (self, path, uid, gid):
        if self.DEBUG: print ("chown", path)

        self.ops.changeMetadata (path, "st_uid", uid)
        self.ops.changeMetadata (path, "st_gid", gid)
        self.ops.changeMetadata (path, "st_ctime", time.time ())

    #Change timestamps of a file
    def utimens (self, path, times = None):
        if self.DEBUG:  print ("utimens", path)

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
        if self.DEBUG: print ("unlink", path)

        self.ops.remove (path)
        if os.path.exists (self.cache + path):
            os.unlink (self.cache + path)

    #Opening of file
    def open (self, path, flags):
        if self.DEBUG: print ("open", path)

        self.ops.open (path)
        if not path in self.list.keys ():
            self.list [path] = [0, False, False]
        self.list [path][0] += 1
        return os.open (self.cache + path, flags)
    
    #Write buffered file contents to the actual file
    def flush (self, path, fh):
        if self.DEBUG: print ("flush", path)
        return os.fsync (fh)
    def fsync (self, path, fdatasync, fh):
        if self.DEBUG: print ("fsync", path)
        return os.fsync (fh)

    #Close file
    def release (self, path, fh):
        if self.DEBUG: print ("release", path)

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
        os.lseek (fh, offset, os.SEEK_SET)
        self.list [path][2] = True
        return os.read (fh, length)

    #Write data to file
    def write (self, path, buf, offset, fh):
        os.lseek (fh, offset, os.SEEK_SET)
        self.list [path][1] = True
        return os.write (fh, buf)

    #Truncate file
    def truncate (self, path, length, fh = None):
        if self.DEBUG: print ("truncate", path)

        with open (self.cache + path, 'r+') as f:
            f.truncate (length)
        self.list [path][1] = True

    #Needed to create file
    def create (self, path, mode, fi=None):
        if self.DEBUG: print ("create", path)

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
        self.chmod (path, mode)
        self.utimens (path)
        return fd

    #Rename file
    def rename (self, old, new):
        if self.DEBUG: print ("rename", old, new)

        #Rename in cache
        if os.path.exists (self.cache + old):
            os.rename (self.cache + old, self.cache + new)
        #Rename at source
        self.ops.rename (old, new)
        #Make change in list of open files
        if old in self.list.keys ():
            self.list [new] = self.list.pop (old)
        self.ops.changeMetadata (new, "st_ctime", time.time ())
