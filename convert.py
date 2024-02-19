#!/usr/bin/env python3

#Converts a dc-fs FAT in an older format to the newest format
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

import json
import os

#This program is built with the ability to adapt to newer FAT formats, should they be created.
#Therefore it is quite extensive for the current situation (with one old and one new format).

#Start the program
def main ():
    if os.path.exists ("fat.json"):
        with open (name, "r") as f:
            fat = json.load (f)
    else:
        fat = {}    #Safest option, cannot go wrong

    fat = convert (fat)

    #Save new FAT
    with open (name, "w") as f:
        json.write (fat, f, indent = 4)

#Convert the specified FAT file
def convert (fat):
    #Decide on which version the FAT is
    if "version" in fat.keys ():
        #Is this a file called version or an actual version indicator?
        if fat ["version"] in [0]:

            #Version 0 FAT
            if fat ["version"] == 0:
                newFat = fat    #Newest version

        else:
            #Not a version indicator hence oldest version
            newFat = convertOld (fat)
    else:
        #Oldest version
        newFat = convertOld (fat)

    return newFat

#Convert a FAT in the oldest format
def convertOld (oldFat):
    #Default layout of FAT
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

    #Populate new FAT with files from old FAT
    for file in oldFat.keys ():
        fat ["fat"]["files"][file [1:]] = {
            "messages": [oldFat [file]],
            "metadata": {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 33204, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 25 * 1024 * 1024 * 10, 'st_uid': 1000}
        }

    #If config file exists, load config into new FAT and cleanup
    if os.path.exists ("config.json"):
        with open ("config.json", "r") as f:
            conf = json.load (f)

        fat ["token"] = conf ["token"]
        fat ["mount"] = conf ["mount"]
        fat ["channel"] = conf ["channel"]

        os.system ("rm config.json")

    #Otherwise, tell user to fill in neccessary fields
    else:
        printString = """
        Please fill in new FAT file (fat.json) with:
        - "token":\tbot token,
        - "mount":\tmount directory path,
        - "channel":\tfilesystem channel ID.
        See documentation (README.md) for more details.
        """
        print (printString)
    
    return fat
    
if __name__ == "__main__":
    main ()
