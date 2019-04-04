# coding: utf-8

import hashlib
import locale
import os
import re
import shutil
import sys
import tempfile
import unittest

from . import MComixTest, get_testfile_path

from mcomix import process
from mcomix.archive import archive_recursive, pdf, rar, sevenzip, zip
import mcomix


class UnsupportedFormat(Exception):

    def __init__(self, format):
        super(UnsupportedFormat, self).__init__('unsuported %s format' % format)


class UnsupportedOption(Exception):

    def __init__(self, format, option):
        super(UnsupportedOption, self).__init__('unsuported option for %s format: %s' % (format, option))


def md5(path):
    hash = hashlib.md5()
    hash.update(open(path, 'rb').read())
    return hash.hexdigest()


class ArchiveFormatTest(object):
    skip = None
    handler = None
    format = ''
    solid = False
    password = None
    header_encryption = False
    contents = ()
    archive = None

    @classmethod
    def _ask_password(cls, archive):
        if cls.password:
            return cls.password
        raise Exception('asked for password on unprotected archive!')

    @classmethod
    def setUpClass(cls):
        if cls.skip is not None:
            raise unittest.SkipTest(cls.skip)
        cls.archive_path = '%s.%s' % (get_testfile_path('archives', cls.archive), cls.format)
        cls.archive_contents = dict([
            (archive_name, filename)
            for name, archive_name, filename
            in cls.contents
        ])
        mcomix.archive.ask_for_password = cls._ask_password
        if os.path.exists(cls.archive_path):
            return

    def setUp(self):
        super(ArchiveFormatTest, self).setUp()
        self.dest_dir = tempfile.mkdtemp(prefix='extract.')
        self.archive = None

    def tearDown(self):
        if self.archive is not None:
            self.archive.close()
        super(ArchiveFormatTest, self).tearDown()

    def test_init_not_unicode(self):
        self.assertRaises(AssertionError, self.handler, 'test')

    def test_archive(self):
        self.archive = self.handler(self.archive_path)
        self.assertEqual(self.archive.archive, self.archive_path)

    def test_list_contents(self):
        self.archive = self.handler(self.archive_path)
        contents = self.archive.list_contents()
        self.assertItemsEqual(contents, self.archive_contents.keys())

    def test_iter_contents(self):
        self.archive = self.handler(self.archive_path)
        contents = []
        for name in self.archive.iter_contents():
            contents.append(name)
        self.assertItemsEqual(contents, self.archive_contents.keys())

    def test_is_solid(self):
        self.archive = self.handler(self.archive_path)
        self.archive.list_contents()
        self.assertEqual(self.solid, self.archive.is_solid())

    def test_iter_is_solid(self):
        self.archive = self.handler(self.archive_path)
        list(self.archive.iter_contents())
        self.assertEqual(self.solid, self.archive.is_solid())

    def test_extract(self):
        self.archive = self.handler(self.archive_path)
        contents = self.archive.list_contents()
        self.assertItemsEqual(contents, self.archive_contents.keys())
        # Use out-of-order extraction to try to trip implementation.
        for name in reversed(contents):
            self.archive.extract(name, self.dest_dir)
            path = os.path.join(self.dest_dir, name)
            self.assertTrue(os.path.isfile(path))
            extracted_md5 = md5(path)
            original_md5 = md5(get_testfile_path(self.archive_contents[name]))
            self.assertEqual((name, extracted_md5), (name, original_md5))

    def test_iter_extract(self):
        self.archive = self.handler(self.archive_path)
        contents = self.archive.list_contents()
        self.assertItemsEqual(contents, self.archive_contents.keys())
        extracted = []
        for name in self.archive.iter_extract(reversed(contents), self.dest_dir):
            extracted.append(name)
            path = os.path.join(self.dest_dir, name)
            self.assertTrue(os.path.isfile(path))
            extracted_md5 = md5(path)
            original_md5 = md5(get_testfile_path(self.archive_contents[name]))
            self.assertEqual((name, extracted_md5), (name, original_md5))
        # Entries must have been extracted in the order they are listed in the archive.
        # (necessary to prevent bad performances on solid archives)
        self.assertEqual(extracted, contents)


class RecursiveArchiveFormatTest(ArchiveFormatTest):
    base_handler = None

    def handler(self, archive):
        main_archive = self.base_handler(archive)
        return archive_recursive.RecursiveArchive(main_archive, self.dest_dir)


for name, handler, is_available, format, not_solid, solid, password, header_encryption in (
    ('7z (external)'    , sevenzip.SevenZipArchive, sevenzip.SevenZipArchive.is_available(), '7z'     , True , True , True , True ),
    ('7z (external) lha', sevenzip.SevenZipArchive, sevenzip.SevenZipArchive.is_available(), 'lha'    , True , False, False, False),
    ('7z (external) rar', sevenzip.SevenZipArchive, sevenzip.SevenZipArchive.is_available(), 'rar'    , True , True , True , True ),
    ('7z (external) zip', sevenzip.SevenZipArchive, sevenzip.SevenZipArchive.is_available(), 'zip'    , True , False, True , False),
    ('rar (external)'   , rar.RarArchive          , rar.RarArchive.is_available()          , 'rar'    , True , True , True , True ),
    ('rar (dll)'        , rar.RarArchive          , rar.RarArchive.is_available()          , 'rar'    , True , True , True , True ),
    ('zip'              , zip.ZipArchive          , True                                   , 'zip'    , True , False, True , False),
):
    base_class_name = 'ArchiveFormat'
    base_class_name += ''.join([part.capitalize() for part in re.sub(r'[^\w]+', ' ', name).split()])
    base_class_name += '%sTest'
    base_class_dict = {
        'name'   : name,
        'handler': handler,
        'format' : format,
    }

    skip = None
    if not is_available:
        skip = 'support for %s format with %s not available' % (format, name)
    base_class_dict['skip'] = skip

    base_class_list = []
    if not_solid:
        base_class_list.append(('', {}))
    if solid:
        base_class_list.append(('Solid', {'solid': True}))

    class_list = []

    if password:
        for variant, params in base_class_list:
            variant += 'Encrypted'
            params = dict(params)
            params['password'] = 'password'
            params['contents'] = (
                ('arg.jpeg', 'arg.jpeg', 'images/01-JPG-Indexed.jpg'),
                ('foo.JPG', 'foo.JPG', 'images/04-PNG-Indexed.png'),
                ('bar.jpg', 'bar.jpg', 'images/02-JPG-RGB.jpg'),
                ('meh.png', 'meh.png', 'images/03-PNG-RGB.png'),
            )
            class_list.append((variant, params))
            if header_encryption:
                variant += 'Header'
                params = dict(params)
                params['header_encryption'] = True
                class_list.append((variant, params))
    else:
        assert not header_encryption

    for sub_variant, is_supported, contents in (
            ('Flat', True, (
                    ('arg.jpeg', 'arg.jpeg', 'images/01-JPG-Indexed.jpg'),
                    ('foo.JPG', 'foo.JPG', 'images/04-PNG-Indexed.png'),
                    ('bar.jpg', 'bar.jpg', 'images/02-JPG-RGB.jpg'),
                    ('meh.png', 'meh.png', 'images/03-PNG-RGB.png'),
            )),
            ('Tree', True, (
                    ('dir1/arg.jpeg', 'dir1/arg.jpeg', 'images/01-JPG-Indexed.jpg'),
                    ('dir1/subdir1/foo.JPG', 'dir1/subdir1/foo.JPG', 'images/04-PNG-Indexed.png'),
                    ('dir2/subdir1/bar.jpg', 'dir2/subdir1/bar.jpg', 'images/02-JPG-RGB.jpg'),
                    ('meh.png', 'meh.png', 'images/03-PNG-RGB.png'),
            )),
            ('Unicode', True, (
                    ('1-قفهسا.jpg', '1-قفهسا.jpg', 'images/01-JPG-Indexed.jpg'),
                    ('2-רדןקמא.png', '2-רדןקמא.png', 'images/04-PNG-Indexed.png'),
                    ('3-りえsち.jpg', '3-りえsち.jpg', 'images/02-JPG-RGB.jpg'),
                    ('4-щжвщджл.png', '4-щжвщджл.png', 'images/03-PNG-RGB.png'),
            )),
            # Check we don't treat an entry name as an option or command line switch.
            ('OptEntry', True, (
                    ('-rg.jpeg', '-rg.jpeg', 'images/01-JPG-Indexed.jpg'),
                    ('--o.JPG', '--o.JPG', 'images/04-PNG-Indexed.png'),
                    ('+ar.jpg', '+ar.jpg', 'images/02-JPG-RGB.jpg'),
                    ('@eh.png', '@eh.png', 'images/03-PNG-RGB.png'),
            )),
            # Check an entry name is not used as glob pattern.
            ('GlobEntries', True, (
                    ('[rg.jpeg', '[rg.jpeg', 'images/01-JPG-Indexed.jpg'),
                    ('[]rg.jpeg', '[]rg.jpeg', 'images/02-JPG-RGB.jpg'),
                    ('*oo.JPG', '*oo.JPG', 'images/04-PNG-Indexed.png'),
                    ('?eh.png', '?eh.png', 'images/03-PNG-RGB.png'),
                    # ('\\r.jpg'             , '\\r.jpg'             , 'images/blue.png'          ),
                    # ('ba\\.jpg'            , 'ba\\.jpg'            , 'images/red.png'           ),
            )),
    ):
        if not is_supported:
            continue
        contents = [
            map(lambda s: s.replace('/', os.sep), names)
            for names in contents
        ]
        for variant, params in base_class_list:
            variant += sub_variant
            params = dict(params)
            params['contents'] = contents
            class_list.append((variant, params))

    for variant, params in class_list:
        class_name = base_class_name % variant
        class_dict = dict(base_class_dict)
        class_dict.update(params)
        class_dict['archive'] = variant
        globals()[class_name] = type(class_name, (ArchiveFormatTest, MComixTest), class_dict)
        class_name = 'Recursive' + class_name
        class_dict = dict(class_dict)
        class_dict['base_handler'] = class_dict['handler']
        del class_dict['handler']
        globals()[class_name] = type(class_name, (RecursiveArchiveFormatTest, MComixTest), class_dict)


# Custom tests for recursive archives support.

class RecursiveArchiveFormatRedAndBluesTest(RecursiveArchiveFormatTest):

    @classmethod
    def setUpClass(cls):
        skip = None
        if not cls.is_available:
            raise unittest.SkipTest('support for archive format not available')
        if not os.path.exists(cls.archive_path):
            skip = 'archive is missing: %s' % cls.archive_path
        if skip is not None:
            raise unittest.SkipTest(skip)
        cls.archive_contents = dict([
            (archive_name.replace('/', os.sep),
             get_testfile_path(filename))
            for archive_name, filename in
            cls.contents])


class RecursiveArchiveFormat7zRedAndBluesTest(RecursiveArchiveFormatRedAndBluesTest, MComixTest):
    base_handler = sevenzip.SevenZipArchive
    is_available = rar.RarArchive.is_available()
    archive_path = get_testfile_path('archives', 'red_and_blues.7z')
    contents = (
        ('blues.rar/blue0.png', 'images/blue.png'),
        ('blues.rar/blue1.png', 'images/blue.png'),
        ('blues.rar/blue2.png', 'images/blue.png'),
        ('red.png', 'images/red.png'),
    )
    solid = True


class RecursiveArchiveFormatExternalRarRedAndBluesTest(RecursiveArchiveFormatRedAndBluesTest, MComixTest):
    base_handler = rar.RarArchive
    is_available = rar.RarArchive.is_available()
    archive_path = get_testfile_path('archives', 'red_and_blues.rar')
    contents = (
        ('blues.7z/blue0.png', 'images/blue.png'),
        ('blues.7z/blue1.png', 'images/blue.png'),
        ('blues.7z/blue2.png', 'images/blue.png'),
        ('red.png', 'images/red.png'),
    )
    solid = True


class RecursiveArchiveFormatExternalRarEmbeddedRedAndBluesRarTest(RecursiveArchiveFormatExternalRarRedAndBluesTest):
    archive_path = get_testfile_path('archives', 'embedded_red_and_blues_rar.rar')
    contents = (
        ('red_and_blues.rar/blues.7z/blue0.png', 'images/blue.png'),
        ('red_and_blues.rar/blues.7z/blue1.png', 'images/blue.png'),
        ('red_and_blues.rar/blues.7z/blue2.png', 'images/blue.png'),
        ('red_and_blues.rar/red.png', 'images/red.png'),
    )


class RecursiveArchiveFormatRarRedAndBluesTest(RecursiveArchiveFormatExternalRarRedAndBluesTest):
    base_handler = rar.RarArchive
    is_available = rar.RarArchive.is_available()


class RecursiveArchiveFormatRarEmbeddedRedAndBluesRarTest(RecursiveArchiveFormatExternalRarEmbeddedRedAndBluesRarTest):
    base_handler = rar.RarArchive
    is_available = rar.RarArchive.is_available()


xfail_list = [
    # No password support when using some external tools.
    ('ZipExternalEncrypted', 'test_extract'),
    ('ZipExternalEncrypted', 'test_iter_extract'),
]

# Expected failures.
for test, attr in xfail_list:
    for name in (
            'ArchiveFormat%sTest' % test,
            'RecursiveArchiveFormat%sTest' % test,
    ):
        if name not in globals():
            continue
        klass = globals()[name]
        setattr(klass, attr, unittest.expectedFailure(getattr(klass, attr)))
