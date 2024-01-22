# discord-fs
Discord as a filesystem.
Version `1.1.0`.

This is a simple, feature-sparse (for now) implementation of a program allowing you to use Discord as your free, unlimited cloud-storage.
You assign a channel, mount the filesystem and let the bot do the rest.

This is a hobby project of mine, forks and pull requests are welcome (following the roadmap below or not)!
If anything breaks, please tell me in a Github Issue so I can fix it.

## Usage
First off, you'll need Linux to run this (with FUSE and a modern version of Python installed, should already be installed by default on most distros).
If you have macOS, I think there is a way to get FUSE working there too which should enable you to run this project.
This project won't support Windows as it is a completely different platform.
However, https://github.com/DiscordFS/DiscordFS looks relevant (but I'm not affiliated with it in any way).
All testing and official support is for Ubuntu 23.10 with Python 3.11, but if you have issues with another system I will try and look into it anyways.

Before using the FS, you'll need to fix some setup.
I will assume you are techy enough to do this yourself, so this will be in broad terms what to do.
- Create (or use) a discord bot for the FS
- Fill in data in file `config.json` (see below)
- Import libraries in `requirements.txt`

After this is done you should be good to go.
The FS is started by executing `dc-fs.py` with a modern Python version, and closing it is done by unmounting the filesystem.
You can optionally specify another mountpoint as a command-line argument, otherwise the default mountpoint specified in `config.json` will be used.

If any of this is an issue for you (and you can't Google your way to it), you shouldn't use it.
This project is still in a too early development stage for me to recommend it for people not familiar with Python or Discord bots.

### Config file
Most data required by the program at runtime is stored as JSON in the file `config.json`.
If the file is not present it will be created and you will be prompted to fill it with data.
The data (in default order) is the following:
- `token` - Bot token (string): The Discord bot token
- `channel` - Filesystem channel (integer): The ID of the channel the filesystem operates in
- `mount` - Mountpoint (string/path): Absolute or relative path to the filesystem mountpoint, `./mnt/` by default

### Limitations
I plan to fix many of these limitations in later versions of the program.
- It is, of course, very slow
- Max file size is 250MiB (10x Discord limit, max total size for a single message)
- No support for directories
- No file metadata stored, mode and permissions will be set to default
- Files are readable and downloadable by anyone with access to the filesystem channel
- FAT stored locally, two clients cannot operate on the same filesystem

## Bugs
Here is a list of all known bugs, prioritized by functionality impact.

### Critical
These bugs will be fixed in the next patch release.

### Important
These bugs will either be fixed in the next patch release or minor release.

### Other
These bugs will be fixed whenever there is time, but most likely in a future minor release.
- In very special conditions, ghost uploads of files may occur (copies of files unknown to the FS)

## Roadmap
Updated versions of this program will be released continuously, and there is no guarantee that new versions won't break data stored in older versions.
Therefore, be sure to read the release notes for any release, because _if_ something breaks (and I'm aware) it will be noted there.
Below is how I currently plan on going forward with the project.

### Next patch release (patch branch)
- Rename files and classes to better reflect their purpose
- Fix bugs as they appear

### Next minor release (dev branch)
- Rethink FAT (preparation for future releases)

### Future minor releases
- Store file metadata (mode, permissions, etc.)
- Unlimited file size by splitting into multiple messages
- Implement directories

### Ideas for future major releases
- Store FAT at Discord, only saving its location locally
- Multiple clients connected to the same filesystem
- Asynchronized filesystem operations

## Legal
Copyright (C) 2024 Simon Bryntse

License (GPL 3.0) provided in file `LICENSE`

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

I am not responsible for any harm caused by using this program, including but not limited to loss of uploaded files or termination of your Discord user account.
Additionally, I am not affiliated with Discord and this program is not endorsed by Discord in any way.
My personal interpretation of the Discord ToS is that this program is compliant, but I am not a lawyer and this does not constitute legal advice.
Also note that the Discord ToS are subject to change at any moment.
