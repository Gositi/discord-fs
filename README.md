# discord-fs
Discord as a filesystem.
Version `1.2.1`.

This is a simple, feature-sparse (for now) implementation of a program allowing you to use Discord as your free, unlimited cloud-storage.
You assign a channel, mount the filesystem and let the bot do the rest.

This is a hobby project of mine, forks and pull requests are welcome (following the roadmap below or not)!
If anything breaks, please tell me in a Github Issue so I can fix it.

Note that this is mainly an experimental program and not something made, or at least intended, to be used seriously.

## Usage
First off, you'll need Linux to run this (with FUSE and a modern version of Python installed, should already be installed by default on most distros).
If you have macOS, I think there is a way to get FUSE working there too which should enable you to run this project.

This project won't support Windows as it is a completely different platform.
However, https://github.com/DiscordFS/DiscordFS seems similar to what this is trying to do but for Windows (but I'm not affiliated with it in any way).

All testing and official support is for Ubuntu 23.10 with Python 3.11 and a bunch of usually preinstalled libraries.
If you have issues with another system I will of course try and look into it anyways.

Before using the program, you will need to do some setup.
I will assume you are techy enough to do this yourself, so this will be in broad terms what to do.
- Import libraries in `requirements.txt`
- Create (or use) a discord bot for the FS
- Fill in data in file `fat.json` (see below)

After this is done you should be good to go.
The program is started by executing `dc-fs.py` with a modern Python version, and closing it should be done by unmounting the filesystem.
You can optionally specify another mountpoint as a command-line argument, otherwise the default mountpoint in `fat.json` will be used.

### FAT file
The _File Allocation Table_, or FAT for short, along with the configuration data is stored in the file `fat.json`.
Replacing it will essentially replace the entire filesystem, corrupting or losing it will be irrecoverable in most cases.
If the file is not present it will be created at runtime and you will be prompted to fill in some data.

The data (in default order) which you need to fill in is the following:
- `token` - Bot token (string): The Discord bot token
- `mount` - Mountpoint (string/path): Absolute or relative path to the filesystem mountpoint, `./mnt/` by default
- `channel` - Filesystem channel (integer): The ID of the channel the filesystem operates in

If you have upgraded from an older version of the program it might be a good idea to run `convert.py`.
This will make sure the FAT is up-to-date and compatible with the newest program version, so you don't experience data loss.

### Limitations
I plan to fix many of these limitations in later versions of the program, but until then it is good if you know about them.
- The filesystem is, of course, quite slow (especially for large files)
- 250MiB max file size (10x Discord limit, max total size for a single message)
- No support for directories
- No file metadata stored, mode, permissions, etc. will be set to default
- Files are readable and downloadable by anyone with access to the filesystem channel
- FAT and config stored locally, two separate clients cannot operate on the same filesystem

## Bugs
Here is a list of all currently known bugs, prioritized by functionality impact.

### Critical
These bugs will be fixed in the next patch release.

### Important
These bugs will either be fixed in the next patch release or minor release.

### Other
These bugs will be fixed whenever there is time, but most likely in a future minor release.
- Copies of files in the FS channel that is unknown to the program may occur under very special conditions

## Roadmap
Updated versions of this program will be released continuously (whenever I decide to work on it).

Although I try not to, there is no guarantee that new versions won't break data stored in older versions.
However, _if_ something breaks (and I'm aware) it will be noted in the release notes.
The `convert.py` script should also be used after upgrading (especially if noted in release notes).

Below is how I currently plan on going forward with the project.

### Next patch release (patch branch)
- Fix bugs or minor issues as they appear

### Next minor release (dev branch)
- Store file metadata (size, mode, permissions, etc.)
- Allow the system to interact with metadata

### Future minor releases
- Unlimited file size by splitting into multiple messages
- Implement directories
- Cache files for a short while after closing them to save bandwidth on downloads
- Optionally saving files encrypted (with obfuscated filenames)

### Ideas for future major releases
- Store FAT at Discord, only saving its location locally
- Multiple clients connected to the same filesystem
- Asynchronized filesystem operations
- Allowing other ways of interacting with the filesystem
- Building a framework for using other applications as filesystems

## Legal
Copyright (C) 2024 Simon Bryntse

License (GPL 3.0) provided in file `LICENSE`

Partially derived from https://github.com/skorokithakis/python-fuse-sample/blob/master/passthrough.py

Copyright (C) 2016 Stavros Korokithakis

License (BSD-2-Clause) provided in file `LICENSE-2`

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

I am not responsible for any harm caused by using this program, including but not limited to loss of data or termination of your Discord account(s).
Additionally, I am not affiliated with Discord and this program is not endorsed by Discord in any way.
My personal interpretation of the Discord ToS is that this program is compliant, but I am not a lawyer and this does not constitute legal advice.
Also note that the Discord ToS are subject to change at any moment, so even if this program was compliant when created it might not be now.
