#!/usr/bin/env python3

import json
import requests as rq

#TODO: Find a good implementation using concurrent downloads

class API:
    def __init__ (self, DEBUG, channel, token, lock, cache, temp):
        self.DEBUG = DEBUG
        self.url = "https://discord.com/api/channels/" + str (channel) + "/messages"
        self.headers = {"Authorization": "Bot " + token}
        self.cache = cache
        self.temp = temp

    #Download files
    def download (self, messages, name):
        files = []
        i = 0
        for message in messages:
            r = rq.get (self.url + "/" + str (message), headers=self.headers)

            if not r.status_code == 200:
                if self.DEBUG: print (r.text)
                raise RuntimeError ("File download failed. An error WILL occur because of this.")

            for attach in r.json ()["attachments"]:
                with open (self.temp + name + str (i), "wb") as f:
                    for chunk in rq.get (attach["url"]).iter_content (1024**2):
                        f.write (chunk)
                files.append (self.temp + name + str (i))
                i += 1

        return files

    #Upload files
    def upload (self, names):
        files = {"file[" + str (i) + "]": open (self.temp + name, "rb") for i, name in enumerate (names)}

        r = rq.post (self.url, headers=self.headers, files=files)

        for f in files.values (): f.close ()

        if not r.status_code == 200:
            if self.DEBUG: print (r.text)
            raise RuntimeError ("File upload failed. An error WILL occur because of this.")

        return r.json ()["id"]

    #Delete files
    def delete (self, messages):
        for message in messages:
            r = rq.delete (self.url + "/" + str (message), headers=self.headers)

            if self.DEBUG and not r.status_code == 200:
                print (r.text)

