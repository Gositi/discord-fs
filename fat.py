#Provides interface between Discord bot and filesystem
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

import dc
import os
import discord
import json
import threading
import queue

class Fat:
    def __init__(self, temp, cache, channel, token, fatfile):
        self.temp = temp
        self.cache = cache
        self.fatfile = fatfile

        #Load FAT file
        if os.path.exists (self.fatfile):
            with open (self.fatfile, "r") as f:
                self.fat = json.load (f)
        else:
            self.fat = {}

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

    #Write to FAT file
    def writefat (self):
        with open (self.fatfile, "w") as f:
            json.dump (self.fat, f)

    #Provide list of available files
    def readdir (self, path):
        for key in self.fat.keys ():
            yield key [1:] #Removes "/" before filename

    #Remove file
    def remove (self, path):
        #Remove file at Discord
        self.e.clear ()
        self.sq.put ({"task": "delete", "id": self.fat [path]})
        self.e.wait ()
        #Update FAT
        self.fat.pop (path)
        self.writefat ()

    #Make file available to cache
    def open (self, path):
        if not os.path.exists (self.cache + path):
            if path in self.fat.keys ():
                self.e.clear ()
                self.sq.put ({"task": "download", "id": self.fat [path], "name": path})
                self.e.wait ()

    #Remove file from cache
    def close (self, path):
        #Remove old file
        self.e.clear ()
        self.sq.put ({"task": "delete", "id": self.fat [path]})
        self.e.wait ()
        #Upload new file
        self.e.clear ()
        self.sq.put ({"task": "upload", "name": path})
        self.e.wait ()
        #Update FAT
        self.fat [path] = self.rq.get ()
        self.writefat ()

    #Make sure a certain file in cache also exists at source
    def sync (self, path):
        #Remove old file, if it exists
        if path in self.fat.keys ():
            self.e.clear ()
            self.sq.put ({"task": "delete", "id": self.fat [path]})
            self.e.wait ()
        #Upload new file
        self.e.clear ()
        self.sq.put ({"task": "upload", "name": path})
        self.e.wait ()
        #Update FAT
        self.fat [path] = self.rq.get ()
        self.writefat ()

    #Check for the existence of a specific file
    def exists (self, path):
        return path in self.fat.keys ()

    #Rename a file
    def rename (self, old, new):
        self.fat [new] = self.fat.pop (old)
        self.writefat ()

    #Shut down bot, exit
    def exit (self):
        self.r.clear ()
        self.sq.put ({"task": "exit"})
        self.r.wait ()
        print ("Bot closed.")

