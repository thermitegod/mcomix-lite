#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

""" MComix installation routines.
Example usage:
    Normal installation (all files are copied into a directory in python/lib/site-packages/mcomix)
    $ ./setup.py install

    For distribution packaging (All files are installed relative to /tmp/mcomix)
    $ ./setup.py install --single-version-externally-managed --root /tmp/mcomix --prefix /usr
"""


APPNAME = 'MComix-Lite'
VERSION = '3.3.0.dev0'

setup(
        name=APPNAME.lower(),
        version=VERSION,
        python_requires='>=3.9',
        packages=['mcomix', 'mcomix.archive', 'mcomix.dialog', 'mcomix.lib',
                  'mcomix.providers', 'mcomix.sort'],
        package_data={'mcomix.images': ['mcomix.png']},
        entry_points={'console_scripts': ['mcomix = mcomix.main:main'],
                      'setuptools.installation': ['eggsecutable=mcomix.main:main'], },
        test_suite='test',
        requires=['Gtk (>=3.24.0)'],
        install_requires=['setuptools', 'pillow', 'urllib3', 'pygobject',
                          'libarchive-c', 'loguru', 'send2trash', 'pyyaml',
                          'xxhash'],
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
        ],

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
