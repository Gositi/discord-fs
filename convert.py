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
        convert ("fat.json")
    else:
        print ("No FAT found, exiting.")

#Convert the specified FAT file
def convert (name):
    #Open FAT
    with open (name, "r") as f:
        fat = json.load (f)

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

#TODO convert a FAT in the oldest format
def convertOld (fat):
    newFat = {"version": 0, "fat": {"files": {}, "dirs": {}, "metadata": {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 16877, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 0, 'st_uid': 1000}}}
    for file in fat.keys ():
        newFat ["fat"]["files"][file [1:]] = {"messages": [fat [file]], "metadata": {'st_atime': 0.0, 'st_ctime': 0.0, 'st_gid': 1000, 'st_mode': 33204, 'st_mtime': 0.0, 'st_nlink': 1, 'st_size': 25 * 1024 * 1024 * 10, 'st_uid': 1000}}
    return newFat
    
if __name__ == "__main__":
    main ()
