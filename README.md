# discord-fs
An attempt at using Discord as a filesystem, using FUSE.

This is a simple working implementation, lacking much functionality (such as subdirectories or large files).

## Usage
Before using the FS, you'll need to fix some setup.
I'll assume you are techy enough to do this yourself, so I'll just tell you in broad terms what to do.
- Create (or use) a discord bot for the FS
- Fill in bot token and FS channel ID in file `config`
- Import libraries in `requirements.txt`

After this is done you should be good to go.
The FS is started by executing `dc-fs.py`.

## TODO
- Store FAT at Discord too
- Store more file information (mode, etc.) in FAT

## Plans and ideas for future
- Handle larger files by splitting them
- Multi-user functionality
- Implement directories
