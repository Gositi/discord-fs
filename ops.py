#Provides interface between Discord bot and filesystem
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

import api
import fat
import os
import json
import threading
import subprocess
import glob

class Ops:
    def __init__(self, DEBUG, temp, cache, channel, token, fatfile):
        self.temp = temp
        self.cache = cache
        self.DEBUG = DEBUG

        #Load FAT handler
        self.fat = fat.Fat (fatfile)

        #Setup Discord API connection
        self.lock = threading.Lock ()
        self.discord = api.API (self.DEBUG, channel, token, self.lock, self.cache, self.temp)

    #
    #   Bot interface
    #

    #Download files at specified message IDs
    def _download (self, msgIDs, name):
        #Download files
        self.lock.acquire ()
        if self.DEBUG: print ("begin download", name)
        filenames = self.discord.download (msgIDs, name)
        if self.DEBUG: print ("finish download", name)
        self.lock.release ()

        #Join files
        with open (self.cache + name, "w") as f:
            subprocess.run (["cat"] + filenames, stdout = f)
        #Remove trace files after joining
        subprocess.run (["rm"] + filenames)

    #Upload specified files
    def _upload (self, name):
        #Split file
        maxSize = 10 * 1024 * 1024 #Discord file size limit
        size = os.path.getsize (self.cache + name)
        if size == 0:
            #Special case of split, has to be handled separately
            subprocess.run (["cp", self.cache + name, self.temp + name + "0"])
        else:
            #Regular file splitting
            subprocess.run (["split", "-b", str (maxSize), "-d", self.cache + name, self.temp + name])

        #Create array of filenames
        names = glob.glob (name [1:] + "*", root_dir = self.temp)
        names.sort ()

        #Upload files
        messages = []
        batchSize = 10 #Discord message filecount limit
        if self.DEBUG: print ("begin upload", name)
        for subnames in [names [i : i + batchSize] for i in range (0, len (names), batchSize)]:
            if self.DEBUG: print ("batch", subnames) 
            self.lock.acquire ()
            messages.append (self.discord.upload (subnames))
            self.lock.release ()
        if self.DEBUG: print ("finish upload", name)

        #Remove trace files
        subprocess.run (["rm"] + [self.temp + name for name in names])

        return messages

    #Remove specified message IDs
    def _remove (self, msgIDs):
        self.lock.acquire ()
        self.discord.delete (msgIDs)
        self.lock.release ()

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
        #Remove target if it already exists
        if self.fat.exists (new):
            self._remove (self.fat.getFile (new))
        #Rename file
        self.fat.updateFile (new, file = self.fat.removeFile (old))
        self.fat.write ()

    #Shut down bot, exit
    def exit (self):
        self.lock.acquire ()
        print ("Bot closed.")

