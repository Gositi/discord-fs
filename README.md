# discord-fs
Discord as a filesystem.
Version `1.4.0`.

This is a program/bot allowing you to use Discord as your free, unlimited cloud-storage.
You assign a channel, mount the filesystem and let the bot do the rest.

Note that this is mainly an experimental program and not something made, or at least intended, to be used seriously.

## Usage
You will need Linux to run this, or at least a system where FUSE is available.
Before using the program you need to do some setup.
I assume you are techy enough to do this yourself, so this will be in broad terms what to do:
- Make sure a modern version of Python is installed
- Make sure the package `python3-fuse` (in the case of the Ubuntu repos) is installed
- Import libraries in `requirements.txt` using `pip install -r requirements.txt`
- Create (or use) a discord bot for the FS
- Fill in data in file `fat.json`, see below

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
- `channel` - Filesystem channel (string): The ID of the channel the filesystem operates in

### Limitations
I plan to fix many of these limitations in later versions of the program, but until then it is good if you know about them.
- The filesystem is, of course, quite slow (especially for large files)
- No support for directories
- Files are fully accessible by anyone with access to the filesystem channel
- Multiple clients cannot operate on the same filesystem
- No file permissions checks supported, that is considered out of scope

## Bugs
Here is a list of all currently known bugs and issues, prioritized by functionality impact.

### Critical
These bugs will be fixed in the next patch release.

### Important
These bugs will either be fixed in the next patch release or minor release.

### Other
These bugs will be fixed whenever there is time, but most likely in a future minor release.

## Roadmap
Updated versions of this program will be released continuously (whenever I decide to work on it).
Please read the release notes for each new release, they might contain important information.

Below is how I currently plan on going forward with the project.

### Next patch release (patch branch)
- Fix bugs or minor issues as they appear

### Next minor release (dev branch)
- Encryption of files (with obfuscation of filenames) and file integrity verification

### Future minor releases
- Increase performance
    - Only download the parts of files that are actually being used
    - Asynchronous file uploads
    - Some caching of files (or file segments) after closing them
- Implement directories

### Ideas for future major releases
- Asynchronized filesystem operations
- Generalizing the concept for more hosts or access methods
- Multiple clients connected to the same filesystem

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
