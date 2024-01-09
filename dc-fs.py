#!/usr/bin/env python3

#Discord-fs, uses Discord as cloud storage accessed through a filesystem
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

import fs, dc
import fuse

#Spin up the system
def main():
    #Directory paths
    temp = "./tmp/"
    mount = "./mnt/"
    #Spin up system
    discord = dc.Discord (temp)
    fuse.FUSE(fs.Filesystem(discord, temp), mount, nothreads=True, foreground=True, allow_other=False)
    discord.exit ()

if __name__ == '__main__':
    main()
