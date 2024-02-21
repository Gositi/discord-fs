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
        self.e = threading.Event ()
        self.r = threading.Event ()
        client.stp (channel, self.sq, self.rq, self.e, self.r, cache, temp)
        self.t = threading.Thread (target = client.run, args=(token,), kwargs={"log_handler": None})
        self.t.daemon = True
        self.r.clear ()
        self.t.start ()

        #Wait for ready
        if self.r.wait (timeout = 10):
            print ("Bot ready.")
        else:
            raise Exception ("Discord bot did not start properly.")

    #Provide list of available files
    def readdir (self, path):
        for item in self.fat.getDir (path): yield item

    #Remove file
    def remove (self, path):
        #Remove file at Discord
        self.e.clear ()
        self.sq.put ({"task": "delete", "id": self.fat.getFile (path)})
        self.e.wait ()
        #Update FAT
        self.fat.removeFile (path)
        self.fat.write ()

    #Make file available to cache
    def open (self, path):
        if not os.path.exists (self.cache + path):
            if self.fat.exists (path):
                self.e.clear ()
                self.sq.put ({"task": "download", "id": self.fat.getFile (path), "name": path})
                self.e.wait ()

    #Remove file from cache
    def close (self, path):
        #Remove old file
        self.e.clear ()
        self.sq.put ({"task": "delete", "id": self.fat.getFile (path)})
        self.e.wait ()
        #Upload new file
        self.e.clear ()
        self.sq.put ({"task": "upload", "name": path})
        self.e.wait ()
        #Update FAT
        self.fat.updateFile (path, messages = self.rq.get ())
        self.fat.write ()

    #Make sure a certain file in cache also exists at source
    def sync (self, path):
        #Remove old file, if it exists
        if self.fat.exists (path):
            self.e.clear ()
            self.sq.put ({"task": "delete", "id": self.fat.getFile (path)})
            self.e.wait ()
        #Upload new file
        self.e.clear ()
        self.sq.put ({"task": "upload", "name": path})
        self.e.wait ()
        #Update FAT
        self.fat.updateFile (path, messages = self.rq.get ())
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
        self.r.clear ()
        self.sq.put ({"task": "exit"})
        self.r.wait ()
        print ("Bot closed.")

