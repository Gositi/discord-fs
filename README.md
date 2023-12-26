# discord-fs
An attempt at using Discord as a filesystem, using FUSE.

The current goal is to make files stored on Discord available through FUSE at all.

## TODO
- [DONE] Make FUSE work
- Make the Discord connection work
- [DONE] Stitch them together

### Bot - FUSE connection
- [DONE] FUSE POC
- Connect to Discord

### Bot - Discord connection
- File up-/download POC
- [DONE] API to FUSE

## Plans for future
- Handle larger files by splitting them
- More advanced filesystem operations
- Multi-user functionality
