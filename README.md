# discord-fs
Discord as a filesystem.
Version `1.0.3`.

This is a simple, feature-sparse (for now) implementation of a program allowing you to use Discord as your free, unlimited cloud-storage.
You assign a channel, mount the filesystem and let the bot do the rest.

This is a hobby project of mine, forks and pull requests are welcome (following the roadmap below or not)!
If anything breaks, please tell me in an Issue so I can fix it.

## Usage
First off, you'll need Linux to run this (with FUSE and a modern version of Python installed, should already be installed by default on most distros).
If you have macOS, I think there is a way to get FUSE working there too which should enable you to run this project.
For Windows, this project won't support it as it is a too different platform.
However, https://github.com/DiscordFS/DiscordFS looks relevant (but I'm not affiliated with it in any way).
This project will only ever officially support Linux, and all testing is done on the latest Ubuntu (23.10).

Before using the FS, you'll need to fix some setup.
I will assume you are techy enough to do this yourself, so this will be in broad terms what to do.
- Create (or use) a discord bot for the FS
- Fill in data in file `config.json` (see below)
- Import libraries in `requirements.txt`

After this is done you should be good to go.
The FS is started by executing `dc-fs.py`, and closing it is done by unmounting the filesystem.
You can optionally specify another mountpoint as a command-line argument, otherwise the default mountpoint specified in `config.json` will be used.

If any of this is an issue for you (and you can't Google your way to it), you shouldn't use it.
This project is still in a too early development stage for me to recommend it for people not familiar with Python or Discord bots.

### Config file
Most data required by the program at runtime is stored as JSON in the file `config.json`.
If the file is not present it will be created and you will be prompted to fill it with data.
The data (in order) is the following:
- `token` - Bot token (string): The Discord bot token
- `channel` - Filesystem channel (integer): The ID of the channel the filesystem operates in
- `mount` - Mountpoint (string/path): Absolute or relative path to the filesystem mountpoint, `./mnt/` by default
- `fat` - FAT file (string/path): Absolute or relative path to file containing the FAT, `fat.json` by default

### Limitations
- It is, of course, very slow
- Max file size is 25MB (Discord limit)
- No support for directories
- No file metadata stored, mode and permissions will be set to default
- Files are readable and downloadable by anyone with access to the filesystem channel
- FAT stored locally, two clients cannot operate on the same filesystem

## Bugs
Here is a list of all known bugs, prioritized in functionality impact.

### Critical
These bugs will be fixed in the next patch release.

### Important
These bugs will either be fixed in the next patch release or minor release.

### Other
These bugs will be fixed whenever there is time, but most likely in a future minor release.

## Roadmap
Updated versions of this program will be released continuously, and there is no guarantee that new versions won't break data stored in older versions.
I will try and keep to semantic versioning though, so patch releases _should_ generally be safe.
Be sure to read the release notes for any release though, because _if_ something breaks (and I'm aware) it will be noted there.
Below is how I currently plan on going forward with the project.

### Next patch release (patch branch)
- Fix bugs as they appear

### Next minor release (dev branch)
- Handle larger files by splitting them (in the same message)
- Store more file information (mode, etc.) in FAT

### Next major release (next branch)
- Rethink handling of FAT/config
- Unlimited file size by splitting into multiple messages
- Implement directories

### Ideas for future
- Store FAT at Discord, only saving its location locally
- Multiple clients connected to the same filesystem
- Asynchronized file up- and downloads

## Legal
Copyright (C) 2024 Simon Bryntse

License (GPL 3.0) provided in file `LICENSE`

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

I am not responsible for any harm caused to you by using this program, including but not limited to deletion of uploaded files or termination of your Discord user account.
My interpretation of Discord ToS is that this program is compliant, but I am not a lawyer and this does not constitute legal advice.
Also note that Discord ToS are subject to change.
