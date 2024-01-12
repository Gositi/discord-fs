#!/usr/bin/env python3

#Provides class for Discord connection and interface
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

import os
import discord
import json
import threading
import queue
import time

#Class for the actual bot, made to be run in a separate process
class Bot (discord.Client):
    #Basic setup (passing arguments to bot)
    def stp (self, channelID, sq, rq, e, temp):
        self.channelID = channelID
        self.sq = sq
        self.rq = rq
        self.e = e
        self.temp = temp

    #Main thread function, handling up- and download of files
    async def on_ready (self):
        #Prepare
        self.channel = self.get_channel (self.channelID)
        self.rq.put ("Bot ready.")
        task = {"task": None}

        #Main loop
        while task ["task"] != "exit":
            #Handle tasks
            if task ["task"] == "download":
                await self.download (task ["id"], task ["name"])
            elif task ["task"] == "upload":
                self.rq.put (await self.upload (task ["name"]))
            elif task ["task"] == "delete":
                await self.delete (task ["id"])
            else:
                pass

            #Finish and get next task
            self.e.set ()
            task = self.sq.get ()

        #Signal bot ready for shutdown
        self.e.set ()

    #Function to download attached file to a certain message
    async def download (self, msgID, name):
        try:
            msg = await self.channel.fetch_message (msgID)
            await msg.attachments [0].save (fp = self.temp + name)
        except discord.error.NotFound:
            return #TODO This should be handled much more gracefully!

    #Function to upload message with file attached
    async def upload (self, name):
        with open (self.temp + name, "rb") as f:
            msg = await self.channel.send (content="File upload", file=discord.File (f, filename = name))
        return msg.id

    #Function to delete message
    async def delete (self, msgID):
        try:
            msg = await self.channel.fetch_message (msgID)
            await msg.delete ()
        except discord.error.NotFound:
            return

#Layer between Filesystem (fs.py) and Bot, handling the actual communications with the bot
class Discord:
    def __init__(self, temp, channel, token, fatfile):
        self.temp = temp
        self.fatfile = fatfile

        #Load FAT file
        if os.path.exists (self.fatfile):
            with open (self.fatfile, "r") as f:
                self.fat = json.load (f)
        else:
            self.fat = {}

        #Setup bot
        client = Bot (intents = discord.Intents.default ())
        self.sq = queue.Queue ()
        self.rq = queue.Queue ()
        self.e = threading.Event ()
        client.stp (channel, self.sq, self.rq, self.e, temp)
        self.t = threading.Thread (target = client.run, args=(token,), kwargs={"log_handler": None})
        self.t.daemon = True
        self.t.start ()

        #Wait for ready
        print (self.rq.get ())

    #Write to FAT file
    def writefat (self):
        with open (self.fatfile, "w") as f:
            json.dump (self.fat, f)

    #Provide list of available files
    def readdir (self, path):
        for key in self.fat.keys ():
            yield key [1:] #Removes "/" before filename

    #Remove file
    def remove (self, path):
        #Remove file at Discord
        self.e.clear ()
        self.sq.put ({"task": "delete", "id": self.fat [path]})
        self.e.wait ()
        #Update FAT
        self.fat.pop (path)
        self.writefat ()

    #Make file available to temp
    def open (self, path):
        if not os.path.exists (self.temp + path):
            if path in self.fat.keys ():
                self.e.clear ()
                self.sq.put ({"task": "download", "id": self.fat [path], "name": path})
                self.e.wait ()

    #Remove file from temp
    def close (self, path):
        #Remove old file
        self.e.clear ()
        self.sq.put ({"task": "delete", "id": self.fat [path]})
        self.e.wait ()
        #Upload new file
        self.e.clear ()
        self.sq.put ({"task": "upload", "name": path})
        self.e.wait ()
        #Update FAT
        self.fat [path] = self.rq.get ()
        self.writefat ()

    #Make sure a certain file in temp also exists at source
    def sync (self, path):
        #Remove old file, if it exists
        if path in self.fat.keys ():
            self.e.clear ()
            self.sq.put ({"task": "delete", "id": self.fat [path]})
            self.e.wait ()
        #Upload new file
        self.e.clear ()
        self.sq.put ({"task": "upload", "name": path})
        self.e.wait ()
        #Update FAT
        self.fat [path] = self.rq.get ()
        self.writefat ()

    #Check for the existence of a specific file
    def exists (self, path):
        return path in self.fat.keys ()

    #Rename a file
    def rename (self, old, new):
        self.fat [new] = self.fat.pop (old)
        self.writefat ()

    #Shut down bot, exit
    def exit (self):
        self.e.clear ()
        self.sq.put ({"task": "exit"})
        self.e.wait ()
