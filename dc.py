#!/usr/bin/env python3

#Provides class for Discord connection and interface
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

import os
import discord
import json
import multiprocessing as mp
import time

class Bot (discord.Client):
    def stp (self, channelID, q, e):
        self.channelID = channelID
        self.q = q
        self.e = e

    async def on_ready (self):
        channel = self.get_channel (self.channelID)
        self.q.put ("Ready.")
        msg = "Startup :)"
        while msg != "exit":
            await channel.send (msg)
            self.e.set ()
            msg = self.q.get ()
        self.e.set ()
        await channel.send ("Shutdown :(")
        await self.close ()

#Simulates a Discord connection, by implementing a lot of basic filesystem functionality
class Discord:
    def __init__(self, temp):
        self.source = "./ref/"
        self.temp = temp

    #Provide list of files available
    def readdir (self, path):
        dirents = []
        if os.path.isdir(self.source + path):
            dirents.extend(os.listdir(self.source + path))
        for r in dirents:
            yield r

    #Remove source file
    def remove (self, path):
        os.unlink (self.source + path)

    #Make file available to temp
    def open (self, path):
        if not os.path.exists (self.temp + path):
            if os.path.exists (self.source + path):
                os.system ("cp " + self.source + path + " " + self.temp + path)

    #Remove file from temp
    def close (self, path):
        os.system ("mv " + self.temp + path + " " + self.source + path)

    #Make sure a certain file in temp also exists at source
    def sync (self, path):
        os.system ("cp " + self.temp + path + " " + self.source + path)

    #Check for the existence of a specific file
    def exists (self, path):
        return os.path.exists (self.source + path)

    #Rename a file
    def rename (self, old, new):
        os.rename (self.source + old, self.source + new)

#Testing function
def main ():
    with open ("config", "r") as f:
        conf = json.load (f)
    intents = discord.Intents.default ()
    client = Bot (intents = intents)
    q = mp.Queue ()
    e = mp.Event ()
    client.stp (conf ["channel"], q, e)
    p = mp.Process (target = client.run, args = (conf ["token"],))
    p.start ()
    q.get ()
    msg = ""
    while msg != "exit":
        e.wait ()
        e.clear ()
        msg = input ("Message to send: ")
        q.put (msg)

if __name__ == "__main__":
    main ()
