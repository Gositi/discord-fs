#!/usr/bin/env python3

#Discord-fs, uses Discord as cloud storage accessed through a filesystem
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

import fs, ops
import fuse
import sys
import os
import subprocess
import json

#Spin up the system
def main():
    print ("""
    Discord-fs (dc-fs): Discord as cloud storage, in your filesystem.
    Copyright (C) 2024  Simon Bryntse

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
            fat = json.load (f)

        #Read config from FAT "header"
        token = fat ["token"]
        mount = fat ["mount"]
        channel = fat ["channel"]
        
    #Write FAT with defaults
    else:
        #Default FAT
        fat = {
            "version": 0,
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
            json.dump (fat, f, indent = 4)

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
    files = ops.Ops (temp, cache, channel, token, "./fat.json")
    fuse.FUSE (fs.Filesystem (files, cache), mount, nothreads = True, foreground = True, allow_other = False)

    #Gracefully shut down after unmount
    files.exit ()

    #Remove cache and temp directories
    subprocess.run (["rm", "-r", cache])
    subprocess.run (["rm", "-r", temp])
    
    print ("Exit.")

if __name__ == '__main__':
    main()
