#Provides interface between the filesystem and the Discord bot
#Copyright (C) 2024-2025 Gositi
#License (GPL 3.0) provided in file 'LICENSE'

import api
import os
import json
import subprocess
import glob
from cryptography.fernet import Fernet
import base64

class File:
    def __init__ (self, DEBUG, path, uuid, key, temp, cache, msgIDs, lock, discord):
        self.DEBUG = DEBUG

        self.path = path
        self.uuid = uuid
        if key:
            self.key = bytes (key, "ASCII")
        else:
            self.key = None

        self.temp = temp
        self.cache = cache

        self.msgIDs = msgIDs
        self.lock = lock
        self.discord = discord

        self.downloaded = False
        self.openCount = 0
        self.read = False
        self.changed = False

    #Download the file
    def _download (self):
        if self.downloaded:
            #Nothing to download
            return
        else:
            #Download files
            self.lock.acquire ()
            if self.DEBUG: print ("begin download", self.path)
            filenames = self.discord.download (self.msgIDs, self.uuid)
            if self.DEBUG: print ("finish download", self.path)
            self.lock.release ()

            if filenames:
                #Join files
                with open (self.temp + self.uuid, "w") as f:
                    subprocess.run (["cat"] + filenames, stdout = f)
                #Remove trace files after joining
                subprocess.run (["rm"] + filenames)
            else:
                subprocess.run (["touch", self.temp + self.uuid])

            #Toggle flag
            self.downloaded = True

        #Decrypt if a key is stored
        if self.key:
            fernet = Fernet (self.key)
            with open (self.temp + self.uuid, "rb") as f:
                encrypted = f.read ()
            decrypted = fernet.decrypt (base64.b64encode (encrypted, altchars=b"-_"))
            with open (self.cache + self.uuid, "wb") as f:
                f.write (decrypted)
            subprocess.run (["rm", self.temp + self.uuid])
        else:
            subprocess.run (["mv", self.temp + self.uuid, self.cache + self.uuid])

    #Upload the file to update Discord
    def _upload (self):
        if not self.downloaded:
            #Nothing to upload
            return
        else:
            #Create key if needed
            if not self.key:
                self.key = Fernet.generate_key ()
            #Encrypt file
            fernet = Fernet (self.key)
            with open (self.cache + self.uuid, "rb") as f:
                decrypted = f.read ()
            encrypted = base64.b64decode (fernet.encrypt (decrypted), altchars=b"-_")
            with open (self.temp + self.uuid, "wb") as f:
                f.write (encrypted)

            #Split file
            maxSize = 10 * 1024 * 1024 #Discord file size limit
            size = os.path.getsize (self.temp + self.uuid)
            if size == 0:
                #Special case of split, has to be handled separately
                subprocess.run (["cp", self.temp + self.uuid, self.temp + self.uuid + "0"])
            else:
                #Regular file splitting
                subprocess.run (["split", "-b", str (maxSize), "-d", self.temp + self.uuid, self.temp + self.uuid])
            subprocess.run (["rm", self.temp + self.uuid])

            #Create array of filenames
            files = glob.glob (self.uuid + "*", root_dir = self.temp)
            files.sort ()

            #Upload files
            messages = []
            batchSize = 10 #Discord message filecount limit
            if self.DEBUG: print ("begin upload", self.path)
            for batch in (files [i : i + batchSize] for i in range (0, len (files), batchSize)):
                if self.DEBUG: print ("upload", batch) 
                self.lock.acquire ()
                messages.append (self.discord.upload (batch))
                self.lock.release ()
            self.msgIDs = messages
            if self.DEBUG: print ("finish upload", self.path)

            #Remove trace files
            subprocess.run (["rm"] + [self.temp + filename for filename in files])

        #Untoggle flag
        self.changed = False

    #Remove file from Discord
    def _remove (self):
        #Delete from Discord
        self.lock.acquire ()
        self.discord.delete (self.msgIDs)
        self.lock.release ()

    #Remove file from cache
    def _uncache (self):
        if self.downloaded:
            os.unlink (self.cache + self.uuid)
            self.downloaded = False

    #Delete the file
    def delete (self):
        self._remove ()
        self._uncache ()

    #Open the file
    def open (self, flags):
        if not self.downloaded: self._download ()
        self.openCount += 1
        return os.open (self.cache + self.uuid, flags)

    #Close the file
    def close (self):
        self.openCount -= 1
        if self.openCount == 0:
            if self.changed and self.downloaded:
                self._remove ()
                self._upload ()
            self._uncache ()

    #Rename file
    def rename (self, newPath):
        self.path = newPath
