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
    #Basic setup
    def stp (self, channelID, sq, rq, e, temp):
        self.channelID = channelID
        self.sq = sq
        self.rq = rq
        self.e = e
        self.temp = temp

    #Main thread function, handling up- and download of files
    async def on_ready (self):
        self.channel = self.get_channel (self.channelID)
        self.rq.put ("Ready.")
        task = {"task": None}

        while task ["task"] != "exit":
            #Handle task
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

        #Shutdown
        self.e.set ()
        await self.close ()

    #Function to download attached file to a certain message
    async def download (self, msgID, name):
        msg = await self.channel.fetch_message (msgID)
        await msg.attachments [0].save (fp = self.temp + name)

    #Function to upload message with file attached
    async def upload (self, name):
        with open (self.temp + name, "rb") as f:
            msg = await self.channel.send (content="File upload", file=discord.File (f, filename = name))
        return msg.id

    #Function to delete message
    async def delete (self, msgID):
        msg = await self.channel.fetch_message (msgID)
        await msg.delete ()

#Simulates a Discord connection, by implementing a lot of basic filesystem functionality
class Discord:
    def __init__(self, temp):
        self.temp = temp

        #Load config file
        if os.path.exists ("config"):
            with open ("config", "r") as f:
                self.conf = json.load (f)
        else:
            with open ("config", "w") as f:
                self.conf = {"token": "BOT TOKEN", "channel": 0}
                json.dump (self.conf, f)
                print ("Fill in newly created config file with bot token and filesystem channel ID.")
                exit ()

        #Load FAT file
        if os.path.exists ("fat"):
            with open ("fat", "r") as f:
                self.fat = json.load (f)
        else:
            self.fat = {}

        #Setup bot
        client = Bot (intents = discord.Intents.default ())
        self.sq = queue.Queue ()
        self.rq = queue.Queue ()
        self.e = threading.Event ()
        client.stp (self.conf ["channel"], self.sq, self.rq, self.e, temp)
        self.t = threading.Thread (target = client.run, args=(self.conf ["token"],), kwargs={"log_handler": None})
        self.t.daemon = True
        self.t.start ()

        #Wait for ready
        self.rq.get ()

    #Provide list of files available
    def readdir (self, path):
        for key in self.fat.keys ():
            yield key [1:]

    #Remove source file
    def remove (self, path):
        self.e.clear ()
        self.sq.put ({"task": "delete", "id": self.fat [path]})
        self.e.wait ()
        self.fat.pop (path)
        with open ("fat", "w") as f:
            json.dump (self.fat, f)

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
        self.fat [path] = self.rq.get ()
        #Write new FAT
        with open ("fat", "w") as f:
            json.dump (self.fat, f)

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
        self.fat [path] = self.rq.get ()
        #Write new FAT
        with open ("fat", "w") as f:
            json.dump (self.fat, f)

    #Check for the existence of a specific file
    def exists (self, path):
        return (path in self.fat.keys ()) or (path == "/")

    #Rename a file
    def rename (self, old, new):
        self.fat [new] = self.fat.pop (old)
        with open ("fat", "w") as f:
            json.dump (self.fat, f)

    #Shut down bot, exit
    def exit (self):
        self.e.clear ()
        self.sq.put ({"task": "exit"})
        self.e.wait ()
        self.t.join ()
