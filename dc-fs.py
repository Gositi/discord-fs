#!/usr/bin/env python3

#Discord-fs, uses Discord as cloud storage accessed through a filesystem
#Copyright (C) 2024-2025 Gositi
#License (GPL 3.0) provided in file 'LICENSE'

import fs, fat, api
import fuse
import sys
import os
import subprocess
import json
import threading

#Spin up the system
def main(DEBUG = False):
    if DEBUG: print ("Debug mode on.")

    print ("""
    Discord-fs (dc-fs): Discord as cloud storage, in your filesystem.
    Copyright (C) 2024-2025  Gositi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    """)

    print ("Startup.")

    #Load FAT to access configs
    if os.path.exists ("fat.json"):
        #Load data
        with open ("fat.json", "r") as f:
            fatData = json.load (f)

        #Read config from FAT "header"
        token = fatData ["token"]
        mount = fatData ["mount"]
        channel = fatData ["channel"]
        
    #Write FAT with defaults
    else:
        #Default FAT
        fatData = {
            "version": 1,
            "token": "BOT TOKEN",
            "mount": "./mnt/",
            "channel": 0,
            "fat": {
                "files": {},
                "dirs": {},
                "metadata": {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 16877, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 0, 'st_uid': 1000}
                }
            }

        #Write data
        with open ("fat.json", "w") as f:
            json.dump (fatData, f, indent = 4)

        #Tell user to fill in neccessary fields
        printString = """
        Please fill in newly created FAT file (fat.json) with:
        - "token":\tbot token,
        - "mount":\tmount directory path,
        - "channel":\tfilesystem channel ID.
        See documentation (README.md) for more details.
        """
        print (printString)

        exit ()
    
    #Read directory paths from CLI
    args = sys.argv
    if len (args) >= 2:
        mount = args [1]

    #Validate/fix directory paths
    if not os.path.isdir (mount):
        print ("Specified mount directory does not exist, attempting creating it.")
        os.mkdir (mount)
    if mount [-1] != "/":
        mount += "/"

    #Create/clean cache dir
    cache = "./.dcfscache/"
    if os.path.isdir (cache):
        subprocess.run (["rm", "-r", cache])
    os.mkdir (cache)

    #Create/clean temp dir
    temp = "./.dcfstmp/"
    if os.path.isdir (temp):
        subprocess.run (["rm", "-r", temp])
    os.mkdir (temp)

    #Spin up system
    lock = threading.Lock ()
    discord = api.API (DEBUG, channel, token, lock, cache, temp)
    files = fat.Fat (DEBUG, "./fat.json", temp, cache, lock, discord)
    fuse.FUSE (fs.Filesystem (DEBUG, cache, files), mount, nothreads = True, foreground = True, allow_other = False)

    #Gracefully destroy system
    lock.acquire ()
    files.write ()

    #Remove cache and temp directories
    subprocess.run (["rm", "-r", cache])
    subprocess.run (["rm", "-r", temp])
    
    print ("Exit.")

if __name__ == '__main__':
    main (DEBUG = True)
