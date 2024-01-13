#!/usr/bin/env python3

#Discord-fs, uses Discord as cloud storage accessed through a filesystem
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

import fs, dc
import fuse
import sys
import os
import json

#Spin up the system
def main():
    #Load config file
    if os.path.exists ("config.json"):
        with open ("config.json", "r") as f:
            conf = json.load (f)
        #Read directory paths from config file
        mount = conf ["mount"]
        fat = conf ["fat"]
    else:
        #Write file with defaults
        with open ("config.json", "w") as f:
            conf = {"token": "BOT TOKEN", "channel": 0, "mount": "./mnt/", "fat": "./fat.json"}
            json.dump (conf, f)
            print ("Fill in newly created config file with bot token, filesystem channel ID and directory paths for filesystem.")
            print ("See documentation (README.md) for more details.")
            exit ()

    #Read directory paths from CLI
    args = sys.argv
    if len (args) >= 2:
        mount = args [1]
    if len (args) == 3:
        fat = args [2]

    #Validate/fix directory paths
    if not os.path.isdir (mount):
        raise NotADirectoryError ("Specified mount directory does not exist.")
    elif mount [-1] != "/":
        mount += "/"

    #Create temp dir
    temp = "./.tmp/"
    if os.path.isdir (temp):
        raise IsADirectoryError ("Tempdir (" + temp + ") already exists, remove it and run the program again.")
    else:
        os.mkdir (temp)

    #Spin up system
    discord = dc.Discord (temp, conf ["channel"], conf ["token"], fat)
    fuse.FUSE(fs.Filesystem(discord, temp), mount, nothreads=True, foreground=True, allow_other=False)

    #Gracefully shut down after unmount
    discord.exit ()
    try:
        os.rmdir ("./.tmp/")
    except:
        print ("Could not remove tempdir (" + temp + "), possibly because it contains trace files. Please remove it manually.")
    print ("Exit (unmount)")

if __name__ == '__main__':
    main()
