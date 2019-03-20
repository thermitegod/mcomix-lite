#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import glob
import setuptools

from mcomix import constants

""" MComix installation routines.

Example usage:
    Normal installation (all files are copied into a directory in python/lib/site-packages/mcomix)
    $ ./setup.py install

    For distribution packaging (All files are installed relative to /tmp/mcomix)
    $ ./setup.py install --single-version-externally-managed --root /tmp/mcomix --prefix /usr
"""


def get_data_patterns(directory, *patterns):
    """ Build a list of patterns for all subdirectories of <directory>
    to be passed into package_data. """

    olddir = os.getcwd()
    os.chdir(os.path.join(constants.BASE_PATH, directory))
    allfiles = []
    for dirpath, subdirs, files in os.walk("."):
        for pattern in patterns:
            current_pattern = os.path.normpath(os.path.join(dirpath, pattern))
            if glob.glob(current_pattern):
                # Forward slashes only for distutils.
                allfiles.append(current_pattern.replace('\\', '/'))
    os.chdir(olddir)
    return allfiles


# Filter unnecessary image files. Replace wildcard pattern with actual files.
images = get_data_patterns('mcomix/images', '*.png')
images.remove('*.png')
images.extend([os.path.basename(img)
               for img in glob.glob(os.path.join(constants.BASE_PATH, 'mcomix/images', '*.png'))
               if os.path.basename(img) not in
               ('mcomix-large.png',)])

setuptools.setup(
        name=constants.APPNAME.lower(),
        version=constants.VERSION,
        packages=['mcomix', 'mcomix.archive', 'mcomix.images'],
        package_data={
            'mcomix.images': images},
        entry_points={
            'console_scripts': ['mcomix = mcomix.run:run'],
            'setuptools.installation': ['eggsecutable=mcomix.run:run'],
        },
        test_suite="test",
        # requires=['pygtk (>=2.12.0)', 'PIL (>=1.15)'],
        install_requires=['setuptools'],
        zip_safe=False,

        # Various MIME files that need to be copied to certain system locations on Linux.
        # Note that these files are only installed correctly if
        # --single-version-externally-managed is used as argument to "setup.py install".
        # Otherwise, these files end up in a MComix egg directory in site-packages.
        # (Thank you, setuptools!)
        data_files=[
            ('share/man/man1', ['man/mcomix.1']),
            ('share/applications', ['mime/mcomix.desktop']),
            ('share/appdata', ['mime/mcomix.appdata.xml']),
            ('share/mime/packages', ['mime/mcomix.xml']),
            ('share/icons/hicolor/48x48/apps', ['mcomix/images/48x48/mcomix.png']),
            ('share/icons/hicolor/48x48/mimetypes',
             ['mime/icons/48x48/application-x-cbz.png',
              'mime/icons/48x48/application-x-cbr.png'])],

        # Package metadata
        maintainer='Ark',
        maintainer_email='https://sourceforge.net/u/aaku/profile/',
        url='http://mcomix.sourceforge.net',
        description='GTK comic book viewer',
        long_description='MComix is a user-friendly, customizable image viewer. '
                         'It is specifically designed to handle comic books (both Western comics and manga) '
                         'and supports a variety of container formats (including 7Z, ZIP, RAR, CBR, CBZ, CB7, LHA, and PDF). '
                         'Mcomix3 is a fork of MComix which is a fork of Comix.',
        license="License :: OSI Approved :: GNU General Public License (GPL)",
        download_url="http://sourceforge.net/projects/mcomix/files",
        platforms=['Operating System :: POSIX :: Linux',
                   'Operating System :: POSIX :: BSD'],
)
