# image sorter

The problem: I have pictures everywhere. Some from old drives that were moved to my NAS. Some on Google Drive from
 when it synced, and some in Dropbox, from syncing there. And they're everywhere. It's a mess.

This will take any number of source directories, and then move them all to a single directory, with subdirectories of
the year created in the EXIF data, or the file creation time.

i <3 python

## install:

How to install it:

```
pip3 -r requirements.txt
python3 sorter.py
```

## running

* edit the config.yml to the directories you want
* run with: `python3 sorter.py`

## TODO:

* move gifs to a dedicated folder
* rules based on exif (source, etc)
