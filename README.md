# discord-fs
Discord as a filesystem.
Version `1.0.1`.

This is a simple, feature-sparse implementation of a program allowing you to use Discord as your free, unlimited cloud-storage.
You assign a channel, mount the filesystem and let the bot do the rest.

This is a hobby project of mine, forks and pull requests are welcome!
If anything breaks, please tell me in an Issue so I can fix it.

## Usage
Before using the FS, you'll need to fix some setup.
I will assume you are techy enough to do this yourself, so this will be in broad terms what to do.
- Create (or use) a discord bot for the FS
- Fill in data in file `config.json` (see below)
- Import libraries in `requirements.txt`

After this is done you should be good to go.
The FS is started by executing `dc-fs.py`, and closing it is done by unmounting the filesystem.
You can optionally specify another mountpoint as a command-line argument, and if you do you can also specify another FAT file.
Otherwise the default mountpoint and FAT file specified in `config.json` will be used.

If any of this is an issue for you (and you can't Google your way to it), this is too much of a hack and you shouldn't use it.

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

## Roadmap
Updated versions of this program will be released continuously, and there is no guarantee that new versions won't break data stored in older versions.

### TODO (for this release)
- Add more useful error messages/exceptions
- Fix bugs as they appear

### Plans (for next release)
- Handle larger files by splitting them
- Store more file information (mode, etc.) in FAT

### Ideas (for future releases)
- Implement directories
- Store FAT at Discord, only saving its location locally

## Legal
Copyright (C) 2024 Simon Bryntse

License (GPL 3.0) provided in file `LICENSE`

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

I am not responsible for any harm caused to you by using this program, including but not limited to deletion of uploaded files or termination of your Discord user account.
My interpretation of Discord ToS is that this program is compliant, but I am not a lawyer and this does not constitute legal advice.
Also note that Discord ToS are subject to change.
