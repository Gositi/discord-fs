#Provides interface between filesystem functions and FAT
#Copyright (C) 2024-2025 Gositi
#License (GPL 3.0) provided in file 'LICENSE'

#TODO Most of this is a stub for the current single-level filesystem

import file
import json
import os.path
import uuid

class Fat:
    def __init__ (self, DEBUG, fatFile, temp, cache, lock, discord):
        #Variables needed for file class
        self.DEBUG = DEBUG
        self.temp = temp
        self.cache = cache
        self.lock = lock
        self.discord = discord

        #Files actually needed for FAT
        self.files = {}
        self.fatFile = fatFile
        with open (self.fatFile, "r") as f:
            self.fat = json.load (f)

    #Write FAT to disk
    def write (self):
        #Update message IDs
        for path, file in self.files.items ():
            self.fat ["fat"]["files"][file.path [1:]]["messages"] = file.msgIDs
        #Write FAT
        with open (self.fatFile, "w") as f:
            json.dump (self.fat, f, indent = 4)

    #Sync file between FAT and list
    def sync (self, path):
        if path in self.files: self.fat ["fat"]["files"][path [1:]]["messages"] = self.files[path].msgIDs

    #Check if a path exists
    def exists (self, path):
        return path [1:] in self.getDir ("/") or path == "/"

    #Create empty file
    def createFile (self, path):
        if path [1:] in self.getDir ("/"):
            raise RuntimeError ("File already exists") 
        else:
            self.fat ["fat"]["files"][path [1:]] = {"messages": [], "metadata": {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 33204, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 0, 'st_uid': 1000}, "uuid": str(uuid.uuid4 ())}

    #Create the file object associated with a certain path
    def fetch (self, path):
        if not path in self.files:
            f = self.fat ["fat"]["files"][path [1:]]
            self.files[path] = file.File (self.DEBUG, path, f["uuid"], self.temp, self.cache, f["messages"], self.lock, self.discord)
        return self.files[path]

    #Remove file (and return it)
    def removeFile (self, path):
        if path in self.files:
            self.files.pop (path)
        return self.fat ["fat"]["files"].pop (path [1:])

    #Rename a file or directory
    def rename (self, old, new):
        self.fat ["fat"]["files"][new [1:]] = self.fat ["fat"]["files"].pop (old [1:])
        if old in self.files:
            self.files[old].rename (new)
            self.files[new] = self.files.pop (old)

    #Get directory listing for directory
    def getDir (self, path):
        return self.fat ["fat"]["files"].keys ()

    #Get metadata of file/directory
    def getMetadata (self, path):
        if path == "/":
            return self.fat ["fat"]["metadata"]
        else:
            return self.fat ["fat"]["files"][path [1:]]["metadata"]

    #Change metadata values of file/directory
    def changeMetadata (self, path, key, value):
        if path == "/":
            self.fat ["fat"]["metadata"][key] = value
        else:
            self.fat ["fat"]["files"][path [1:]]["metadata"][key] = value
