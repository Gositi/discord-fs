#!/usr/bin/env python3

import os
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

    #Remove source file
    def remove (self, path):
        os.unlink (self.source + path)

    #Make file available to temp
    def open (self, path):
        if not os.path.exists (self.temp + path):
            if os.path.exists (self.source + path):
                os.system ("cp " + self.source + path + " " + self.temp + path)

    #Remove file from temp
    def close (self, path):
        os.system ("mv " + self.temp + path + " " + self.source + path)

    #Sync file from temp
    def sync (self, path):
        os.system ("cp " + self.temp + path + " " + self.source + path)

    #Check for the existence of a specific file
    def exists (self, path):
        return os.path.exists (self.source + path)

class Passthrough (Operations):
    def __init__(self, source, temp):
        self.source = source
        self.temp = temp
        self.dc = Discord (source, temp)
        self.list = {}
 
    #Get basic file attributes
    def getattr (self, path, fh=None):
        if not self.dc.exists (path):
            raise OSError (errno.ENOENT, "File does not exist") #Makes filesystem well-behaved
        elif path != "/":
            return {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 33204, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 25000000, 'st_uid': 1000}
        else:
            return {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 16877, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 0, 'st_uid': 1000}

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
        return ret

    #Read data from file
    def read (self, path, length, offset, fh):
        print ("re")
        os.lseek (fh, offset, os.SEEK_SET)
        return os.read (fh, length)

    #Write data to file
    def write (self, path, buf, offset, fh):
        print ("wr")
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    #Needed to create file
    def create(self, path, mode, fi=None):
        print ("cr")
        #Create file in temp
        uid, gid, pid = fuse_get_context()
        fd = os.open(self.temp + path, os.O_WRONLY | os.O_CREAT, mode)
        os.chown(self.temp + path, uid, gid) #chown to context uid & gid
        #Sync file to source
        self.dc.sync (path)
        #Add file to list
        self.list [path] = 1
        return fd

def main():
    source = "./ref/"
    temp = "./temp/"
    mountpoint = "./testdir/"
    FUSE(Passthrough(source, temp), mountpoint, nothreads=True, foreground=True, allow_other=False)

if __name__ == '__main__':
    main()
