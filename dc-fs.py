#!/usr/bin/env python3

import fs, dc
import fuse

#Spin up the system
def main():
    #Directory paths
    temp = "./tmp/"
    mount = "./mnt/"
    #Spin up system
    discord = dc.Discord (temp) #TODO make Discord interface
    fuse.FUSE(fs.Filesystem(discord, temp), mount, nothreads=True, foreground=True, allow_other=False)

if __name__ == '__main__':
    main()
