#!/usr/bin/env python3

from setuptools import setup

from mcomix.enum.mcomix import Mcomix

""" MComix installation routines.
Example usage:
    Normal installation
    $ ./setup.py install --user

    For distribution packaging (All files are installed relative to /tmp/mcomix)
    $ ./setup.py install --single-version-externally-managed --root /tmp/mcomix --prefix /usr
"""


APPNAME = Mcomix.APP_NAME.value
VERSION = Mcomix.VERSION.value

setup(
        name=APPNAME.lower(),
        version=VERSION,
        python_requires='>=3.10',
        packages=['mcomix', 'mcomix.archive', 'mcomix.dialog', 'mcomix.lib', 'mcomix.enum',
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
                         'Supports all archive formats supported by libarchive. '
                         'MComix-Lite is a fork of MComix3 which is a fork of MComix which is a fork of Comix.',
        license="License :: OSI Approved :: GNU General Public License (GPL)",
        platforms=['Operating System :: POSIX :: Linux',
                   'Operating System :: POSIX :: BSD'],
)
