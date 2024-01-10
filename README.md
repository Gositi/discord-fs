# discord-fs
An attempt at using Discord as a filesystem, using FUSE.
Version 0.9.0.

This is a simple working implementation, lacking much functionality (such as subdirectories or large files).

## Usage
Before using the FS, you'll need to fix some setup.
I will assume you are techy enough to do this yourself, so this will be in broad terms what to do.
- Create (or use) a discord bot for the FS
- Fill in bot token and FS channel ID in file `config`
- Import libraries in `requirements.txt`

After this is done you should be good to go.
The FS is started by executing `dc-fs.py`, and closing it is done by unmounting the filesystem.

If any of this is an issue for you (and you can't Google your way to it), this is too much of a hack and you shouldn't use it.

## TODO, plans and ideas
### TODO
- [WIP] Prepare project for going public
- Rethink FAT to enable implementation of some of the ideas/plans

### Plans
- Handle larger files by splitting them
- Store more file information (mode, etc.) in FAT

### Ideas
- Implement directories
- Store FAT at Discord, only saving its location locally
