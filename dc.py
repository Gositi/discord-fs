#Provides class for the Discord connection/bot
#Copyright (C) 2024 Simon Bryntse
#License (GPL 3.0) provided in file 'LICENSE'

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

        self.lock.set ()
        self.ready.set () #Signal the bot is ready
        if self.task == None:
            self.task = self.sq.get () #Get first task

        #Main loop
        while self.task ["task"] != "exit":
            task = self.task
            #Handle tasks
            if task ["task"] == "download":
                self.rq.put (await self.download (task ["id"], task ["name"]))
            elif task ["task"] == "upload":
                self.rq.put (await self.upload (task ["names"]))
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
        files = []

        try:
            #Download files
            i = 0
            for msgID in msgIDs:
                msg = await self.channel.fetch_message (msgID)
                for attach in msg.attachments:
                    await attach.save (fp = self.temp + name + str (i))
                    files.append (self.temp + name + str (i))
                    i += 1

        except discord.NotFound:
            print ("A requested message does not exist and an error WILL occur because of this. This program does not know how to handle this.")

        finally:
            return files

    #Function to upload message with file attached
    async def upload (self, names):
        #Upload files
        files = []
        for name in names:
            with open (self.temp + name, "rb") as f:
                files.append (discord.File (f, filename = name))
        try:
            msg = await self.channel.send (content = "File upload", files = files)
            return msg.id
        except discord.HTTPException:
            print ("An error occured and the whole or parts of the file will not be uploaded. Please report this, along with file size, to the author.")

    #Function to delete message
    async def delete (self, msgIDs):
        for msgID in msgIDs:
            try:
                msg = await self.channel.fetch_message (msgID)
                await msg.delete ()
            except discord.NotFound:
                pass #Message already doesn't exist - weird, but that is what we want to achieve here anyways
