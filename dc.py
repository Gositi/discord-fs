#Provides class for the Discord connection/bot
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

import os
import subprocess
import glob
import discord

class Bot (discord.Client):
    #Basic setup (passing arguments to bot)
    def stp (self, channelID, sq, rq, lock, ready, cache, temp):
        self.channelID = channelID
        self.sq = sq
        self.rq = rq
        self.lock = lock
        self.ready = ready
        self.cache = cache
        self.temp = temp
        self.task = None

    #Main thread function, handling up- and download of files
    async def on_ready (self):
        #Prepare
        try:
            self.channel = self.get_channel (self.channelID)
        except discord.NotFound:
            print ("The filesystem channel does not exist. Make sure that the config file has proper data.")
            return

        self.lock.clear ()
        self.ready.set () #Signal the bot is ready
        if self.task == None:
            self.task = self.sq.get () #Get first task

        #Main loop
        while self.task ["task"] != "exit":
            task = self.task
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
            self.lock.set ()
            self.task = self.sq.get ()

        #Signal bot ready for shutdown
        self.ready.set ()

    #Function to download attached file to a certain message
    async def download (self, msgIDs, name):
        try:
            #Download files
            msg = await self.channel.fetch_message (msgIDs [0])
            args = []
            for i, attach in enumerate (msg.attachments):
                await attach.save (fp = self.temp + name + str (i))
                args.append (self.temp + name + str (i))

            #Join files
            with open (self.cache + name, "w") as f:
                subprocess.run (["cat"] + args, stdout = f)
            #Remove trace files
            subprocess.run (["rm"] + args)

        except discord.NotFound:
            print ("The message requested does not exist and an error will occur because of this. This is an unreachable state and will thus not be handled any further.")

    #Function to upload message with file attached
    async def upload (self, name):
        #Split file
        maxSize = 25 * 1024 * 1024 #Discord file size limit
        size = os.path.getsize (self.cache + name)
        if size == 0:
            #Special case of split, has to be handled separately
            subprocess.run (["cp", self.cache + name, self.temp + name + "0"])
            numFiles = 1
        else:
            #Hexadecimal file names, to get leeway for too large files
            subprocess.run (["split", "-b", str (maxSize), "-a", "1", "-x", self.cache + name, self.temp + name])
            numFiles = -(-size // maxSize) #Ceiling integer division

        #Upload files
        files = [] 
        for i in range (0, min (7, numFiles)): #Cut off at max file count and forget about the rest
            with open (self.temp + name + str (i), "rb") as f:
                files.append (discord.File (f, filename = name + str (i)))
        msg = await self.channel.send (content = "File upload", files = files)

        #Remove trace files
        subprocess.run (["rm"] + glob.glob (self.temp + name + "?"))

        #Return
        return [msg.id]

    #Function to delete message
    async def delete (self, msgIDs):
        try:
            msg = await self.channel.fetch_message (msgIDs [0])
            await msg.delete ()
        except discord.NotFound:
            return #Message already doesn't exist - weird, but that is what we want to achieve here anyways
