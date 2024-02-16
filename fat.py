#Provides interface between filesystem functions and FAT
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

#TODO Most of this is a stub for the current single-level filesystem

import json
import os.path

class Fat:
    def __init__ (self, file):
        self.file = file

        #Load file
        if os.path.exists (self.fatfile):
            with open (self.fatfile, "r") as f:
                self.fat = json.load (f)
        else:
            self.fat = {"version": 0, "fat": {"files": {}, "dirs": {}, "metadata": {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 16877, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 0, 'st_uid': 1000}}}
            self.write ()

    #
    #   Helpers
    #

    #TODO Split a path into directory (as list) and filename
    def _splitPath (self, path):
        pass

    #TODO Return directory for the specified path
    def _descendPath (self, path):
        pass

    #TODO Return the file for the specified path
    def _descendFile (self, path):
        pass

    #
    #   Methods
    #

    #Write FAT to disk
    def write (self):
        with open (self.file, "w") as f:
            json.dump (self.fat, f)

    #Get file message ID from path to file
    def getFile (self, path):
        return self.fat ["fat"]["files"][path [1:]]["messages"]

    #If file exists: update it, if not: create it
    def updateFile (self, path, messages):
        if path [1:] in self.getDir ("/"):
            self.fat ["fat"]["files"][path [1:]]["messages"] = messages
        else:
            self.fat ["fat"]["files"][path [1:]] = {"messages": messages, "metadata": {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 33204, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 25 * 1024 * 1024 * 10, 'st_uid': 1000}}

    #Remove file (and return it)
    def removeFile (self, path):
        return self.fat ["fat"]["files"].pop (path [1:])

    #Get directory listing for directory
    def getDir (self, path):
        return self.fat ["fat"]["files"].keys ()
