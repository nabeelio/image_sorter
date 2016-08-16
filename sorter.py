#
import os
import sys
import arrow
import hashlib
from pprint import pprint
from PIL import Image, ExifTags
from collections import defaultdict


class App(object):

    DRY_RUN = True

    MODE = 'copy'
    BLOCKSIZE = 65536
    DELETE_ORIGINAL = False
    DELETE_DUPLICATES = False
    DT_FORMAT = 'YYYY:MM:DD HH:mm:ss'

    def __init__(self, args):

        self.sources_file = args[0]

        self.src_dirs = []
        self.dest_dir = args[1]

        self.hashes = {}

        self.counters = defaultdict(lambda: 0)

        # read all the source paths in
        with open(self.sources_file, 'r') as fp:
            for line in fp.readlines():
                line = line.strip()
                self.src_dirs.append(line)

    def _get_hash(self, image_path):
        """ generate a hash for the file """
        hasher = hashlib.md5()
        with open(image_path, 'rb') as afile:
            buf = afile.read(self.BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(self.BLOCKSIZE)
        return hasher.hexdigest()

    def _move_file(self, exif, image_path):
        """
        Transfer to file, to the correct subdir based on image metadata
        exif['DateTime'] = '2011:06:18 10:26:33'
        exif['DateTimeDigitized'] = '2011:06:18 10:26:33'
        exif['DateTimeOriginal'] = '2011:06:18 10:26:33'
        """
        dt = None
        fields = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
        for f in fields:
            if f not in exif:
                continue

            dtvalue = exif.get(f)
            if not dtvalue:
                continue

            try:
                dt = arrow.get(dtvalue, self.DT_FORMAT)
                break
            except Exception as e:
                continue

        if not dt:  # dunno the date for some reason, just stick in root
            dest_dir = os.path.join(self.DEST_DIR)
        else:
            # create a year subfolder within the destination dir
            dest_dir = os.path.join(self.DEST_DIR, dt.format('YYYY'))

        print('Moving {f} to {d}'.format(f=image_path, d=dest_dir))

        if self.DRY_RUN:
            return

        # TODO: Move the file, figure out what the destination path *should* be

    def _parse_file(self, image_path):
        """ figure out some details about this image """
        exif = {}
        try:
            with Image.open(image_path) as img:
                exif = {
                    ExifTags.TAGS[k]: v
                    for k, v in img._getexif().items()
                    if k in ExifTags.TAGS
                }
        except AttributeError:
            (_, _, _, _, _, _, _, atime, mtime, ctime) = os.stat(image_path)
            dt = arrow.get(mtime).format(self.DT_FORMAT)
            exif = {
                'DateTime': dt,  # fill with modified date/time
            }
        except IOError:
            return

        self.counters['total_images'] += 1

        fhash = self._get_hash(image_path)
        if fhash not in self.hashes:
            self.hashes[fhash] = image_path
            self._move_file(exif, image_path)
        else:

            if self.DELETE_DUPLICATES:
                # TODO: Delete the duplicate
                pass

            self.counters['duplicates'] += 1
            print('Duplicates found! {a}, {b}'.format(
                a=self.hashes[fhash], b=image_path
            ))

    def run(self):
        """ traverse through all of the source directories """
        for sdir in self.src_dirs:
            for root, dirs, files in os.walk(sdir):
                for file in files:
                    image_path = os.path.join(root, file)
                    self._parse_file(image_path)

        pprint(self.counters.items())


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('sorter.py <source> <dest_path>')
        print('    source: file with directories listed')
        exit(-1)
    app = App(sys.argv[1:])
    app.run()
