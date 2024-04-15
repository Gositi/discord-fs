#Provides interface between Discord bot and filesystem
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

import dc
import fat
import os
import discord
import json
import threading
import queue
import subprocess
import glob

class Ops:
    def __init__(self, temp, cache, channel, token, fatfile):
        self.temp = temp
        self.cache = cache

        #Load FAT handler
        self.fat = fat.Fat (fatfile)

        #Setup bot
        client = dc.Bot (intents = discord.Intents.default ())
        self.sq = queue.Queue ()
        self.rq = queue.Queue ()
        self.lock = threading.Event ()
        self.ready = threading.Event ()
        client.stp (channel, self.sq, self.rq, self.lock, self.ready, cache, temp)
        self.t = threading.Thread (target = client.run, args=(token,), kwargs={"log_handler": None})
        self.t.daemon = True
        self.ready.clear ()
        self.t.start ()

        #Wait for ready
        if self.ready.wait (timeout = 10):
            print ("Bot ready.")
        else:
            raise Exception ("Discord bot did not start properly.")

    #
    #   Bot interface
    #

    #Download files at specified message IDs
    def _download (self, msgIDs, name):
        #Download files
        self.lock.clear ()
        self.sq.put ({"task": "download", "id": msgIDs, "name": name})
        self.lock.wait ()

        #Join files
        filenames = self.rq.get ()
        with open (self.cache + name, "w") as f:
            subprocess.run (["cat"] + filenames, stdout = f)
        #Remove trace files after joining
        subprocess.run (["rm"] + filenames)

    #Upload specified files
    def _upload (self, name):
        #Split file
        maxSize = 25 * 1024 * 1024 #Discord file size limit
        size = os.path.getsize (self.cache + name)
        if size == 0:
            #Special case of split, has to be handled separately
            subprocess.run (["cp", self.cache + name, self.temp + name + "0"])
            num = 1
        else:
            #Hexadecimal file names, to get leeway for too large files
            subprocess.run (["split", "-b", str (maxSize), "-a", "1", "-x", self.cache + name, self.temp + name])
            num = -(-size // maxSize) #Ceiling integer division

        #Create array of filenames
        names = [name + str (i) for i in range (num)]

        #Upload files
        self.lock.clear ()
        self.sq.put ({"task": "upload", "names": names [:10]})
        self.lock.wait ()
        messages = self.rq.get ()

        #Remove trace files
        subprocess.run (["rm"] + glob.glob (self.temp + name + "?"))

        return messages

    #Remove specified message IDs
    def _remove (self, msgIDs):
        self.lock.clear ()
        self.sq.put ({"task": "delete", "id": msgIDs})
        self.lock.wait ()

    #
    #   FS functions
    #

    #Provide list of available files
    def readdir (self, path):
        for item in self.fat.getDir (path): yield item

    #Provide metadata about a certain file
    def getMetadata (self, path):
        return self.fat.getMetadata (path)

    #Change part of a files metadata
    def changeMetadata (self, path, key, value):
        self.fat.changeMetadata (path, key, value)
        self.fat.write ()

    #Remove file
    def remove (self, path):
        #Remove file at Discord
        self._remove (self.fat.getFile (path))
        #Update FAT
        self.fat.removeFile (path)
        self.fat.write ()

    #Make file available to cache
    def open (self, path):
        if not os.path.exists (self.cache + path):
            if self.fat.exists (path):
                self._download (self.fat.getFile (path), path)

    #Remove file from cache
    def close (self, path):
        #Remove old file
        self._remove (self.fat.getFile (path))
        #Upload new file
        messages = self._upload (path)
        #Update FAT
        self.fat.updateFile (path, messages = messages)
        self.fat.changeMetadata (path, "st_size", os.path.getsize (self.cache + path))
        self.fat.write ()

    #Make sure a certain file in cache also exists at source
    def sync (self, path):
        #Remove old file, if it exists
        if self.fat.exists (path):
            self._remove (self.fat.getFile (path))
        #Upload new file
        messages = self._upload (path)
        #Update FAT
        self.fat.updateFile (path, messages = messages)
        self.fat.changeMetadata (path, "st_size", os.path.getsize (self.cache + path))
        self.fat.write ()

    #Check for the existence of a specific file
    def exists (self, path):
        return self.fat.exists (path)

    #Rename a file
    def rename (self, old, new):
        self.fat.updateFile (new, file = self.fat.removeFile (old))
        self.fat.write ()

    #Shut down bot, exit
    def exit (self):
        self.ready.clear ()
        self.sq.put ({"task": "exit"})
        self.ready.wait ()
        print ("Bot closed.")

