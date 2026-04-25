#Provides class for FUSE filesystem functionality
#Copyright (C) 2024-2026 Gositi
#License (GPL 3.0) provided in file 'LICENSE'

#Derived from https://github.com/skorokithakis/python-fuse-sample
#Copyright (C) 2016 Stavros Korokithakis
#License (BSD-2-Clause) provided in file 'LICENSE-2'

import os
import errno
import mfusepy as fuse
import time

class Filesystem (fuse.Operations):
    def __init__ (self, DEBUG, cache, fat):
        self.use_ns = True
        self.DEBUG = DEBUG

        self.cache = cache
        self.fat = fat

        print ("FS ready.")

    #Function ran at unmount
    def destroy (self, path):
        print ("Unmount.")

    #Get basic filesystem info
    def statfs (self, path):
        return {"f_namemax": 128}   #Make renaming files in GUI possible

    #Get basic file attributes
    def getattr (self, path, fh=None):
        if not self.fat.exists (path):
            raise OSError (errno.ENOENT, "File does not exist")
        else:
            return self.fat.getMetadata (path)

    #Change mode of file
    def chmod (self, path, mode, fh=None):
        if self.DEBUG: print ("chmod", path)
        self.fat.changeMetadata (path, "st_mode", mode)
        self.fat.changeMetadata (path, "st_ctime", time.time_ns ())
        self.fat.write ()

    #Change owner of a file
    def chown (self, path, uid, gid, fh=None):
        if self.DEBUG: print ("chown", path)
        self.fat.changeMetadata (path, "st_uid", uid)
        self.fat.changeMetadata (path, "st_gid", gid)
        self.fat.changeMetadata (path, "st_ctime", time.time_ns ())
        self.fat.write ()

    #Change timestamps of a file
    def utimens (self, path, times = None, fh=None):
        if self.DEBUG:  print ("utimens", path)
        if not times: times = (time.time_ns (), time.time_ns ())
        self.fat.changeMetadata (path, "st_atime", times [0])
        self.fat.changeMetadata (path, "st_mtime", times [1])
        self.fat.changeMetadata (path, "st_ctime", time.time_ns ())
        self.fat.write ()

    #Get directory listing
    def readdir (self, path, fh):
        dirents = ['.', '..']
        dirents.extend (self.fat.getDir (path))
        for i in dirents:
            yield i

    #Remove file
    def unlink (self, path):
        if self.DEBUG: print ("unlink", path)
        self.fat.fetch(path).delete ()
        self.fat.removeFile (path)
        self.fat.write ()

    #Opening of file
    def open (self, path, flags):
        if self.DEBUG: print ("open", path)
        return self.fat.fetch(path).open (flags)
    
    #Write buffered file contents to the actual file
    def flush (self, path, fh):
        if self.DEBUG: print ("flush", path)
        return os.fsync (fh)
    def fsync (self, path, fdatasync, fh):
        if self.DEBUG: print ("fsync", path)
        return os.fsync (fh)

    #Close file
    def release (self, path, fh):
        if self.DEBUG: print ("release (close)", path)

        file = self.fat.fetch(path)
        #Close cached file
        ret = os.close (fh)
        #Update timestamps and filesize
        metadata = self.fat.getMetadata (path)
        atime = metadata ["st_atime"]
        mtime = metadata ["st_mtime"]
        if file.changed:
            mtime = time.time_ns ()
        if file.read:
            atime = time.time_ns ()
        self.utimens (path, times = (atime, mtime))
        self.fat.changeMetadata (path, "st_size", os.path.getsize (self.cache + file.uuid))
        #Close the file
        file.close ()
        self.fat.sync (path)
        #Return exit code
        return ret

    #Read data from file
    def read (self, path, length, offset, fh):
        if self.DEBUG: print ("read", path)
        os.lseek (fh, offset, os.SEEK_SET)
        self.fat.fetch(path).read = True
        return os.read (fh, length)

    #Write data to file
    def write (self, path, buf, offset, fh):
        if self.DEBUG: print ("write", path)
        os.lseek (fh, offset, os.SEEK_SET)
        self.fat.fetch(path).changed = True
        return os.write (fh, buf)

    #Truncate file
    def truncate (self, path, length, fh=None):
        if self.DEBUG: print ("truncate", path)
        file = self.fat.fetch(path)
        with open (self.cache + file.uuid, 'r+') as f:
            f.truncate (length)
        file.changed = True

    #Needed to create file
    def create (self, path, mode, fh=None):
        if self.DEBUG: print ("create", path)

        #Add file stub to FAT
        self.fat.createFile (path)
        file = self.fat.fetch(path)
        file.downloaded = True
        file.changed = True
        file.openCount = 1
        #Create file in cache
        uid, gid, pid = fuse.fuse_get_context ()
        fh = os.open (self.cache + file.uuid, os.O_WRONLY | os.O_CREAT, mode)
        os.chown (self.cache + file.uuid, uid, gid) #chown to context uid & gid
        #Set metadata in FAT
        self.chown (path, uid, gid)
        self.chmod (path, mode)
        self.utimens (path)
        #Return
        return fh

    #Rename file
    def rename (self, old, new, flags=0):
        if self.DEBUG: print ("rename", old, new)
        self.fat.rename (old, new)
        self.fat.changeMetadata (new, "st_ctime", time.time_ns ())
        self.fat.write ()
