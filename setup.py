#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os

from setuptools import setup

from mcomix.constants import Constants

""" MComix installation routines.
Example usage:
    Normal installation (all files are copied into a directory in python/lib/site-packages/mcomix)
    $ ./setup.py install

    For distribution packaging (All files are installed relative to /tmp/mcomix)
    $ ./setup.py install --single-version-externally-managed --root /tmp/mcomix --prefix /usr
"""


BASE_PATH = os.path.dirname(os.path.realpath(__file__))


def get_data_patterns(directory, *patterns):
    """ Build a list of patterns for all subdirectories of <directory>
    to be passed into package_data. """
    olddir = os.getcwd()
    os.chdir(os.path.join(BASE_PATH, directory))
    allfiles = []
    for dirpath, subdirs, files in os.walk('.'):
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
               for img in glob.glob(os.path.join(BASE_PATH, 'mcomix/images', '*.png'))])

setup(
        name=Constants.APPNAME.lower(),
        version=Constants.VERSION,
        python_requires='>=3.8',
        packages=['mcomix', 'mcomix.archive', 'mcomix.images', 'mcomix.lib', 'mcomix.providers'],
        package_data={'mcomix.images': images},
        entry_points={'console_scripts': ['mcomix = mcomix.main:main'],
                      'setuptools.installation': ['eggsecutable=mcomix.main:main'], },
        test_suite='test',
        requires=['Gtk (>=3.24.0)'],
        install_requires=['setuptools', 'pillow', 'pygobject', 'loguru', 'send2trash', 'pyyaml', 'xxhash'],
        zip_safe=False,

        # Various MIME files that need to be copied to certain system locations on Linux.
        # Note that these files are only installed correctly if
        # --single-version-externally-managed is used as argument to "setup.py install".
        # Otherwise, these files end up in a MComix egg directory in site-packages.
        # (Thank you, setuptools!)
        data_files=[
            ('share/man/man1', ['man/mcomix.1']),
            ('share/applications', ['mime/mcomix.desktop']),
            ('share/metainfo', ['mime/mcomix.appdata.xml']),
            ('share/mime/packages', ['mime/mcomix.xml']),
            ('share/icons/hicolor/48x48/apps', ['mcomix/images/48x48/mcomix.png']),
            ('share/icons/hicolor/48x48/mimetypes',
             ['mime/icons/48x48/application-x-cbz.png',
              'mime/icons/48x48/application-x-cb7.png',
              'mime/icons/48x48/application-x-cbr.png'])],

        # Package metadata
        maintainer='thermitegod',
        url='https://github.com/thermitegod/mcomix-lite',
        description='GTK comic book viewer',
        long_description='MComix-Lite is a manga/comic reader.'
                         'Supports archive formats are 7Z, ZIP, RAR, TAR, CBR, CBZ, CB7, CBT. '
                         'MComix-Lite is a fork of MComix3 which is a fork of MComix which is a fork of Comix.',
        license="License :: OSI Approved :: GNU General Public License (GPL)",
        platforms=['Operating System :: POSIX :: Linux',
                   'Operating System :: POSIX :: BSD'],
)
