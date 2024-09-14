# MComix-Lite

## Description

MComix-Lite is a manga/comic reader written in Python3 / Gtk+3

MComix-Lite is a fork of MComix3 which is a fork of MComix which is a fork of Comix.

The main focus is **ONLY** on the reader and all other features, i.e. library, have been removed or could be subject to a future removal.

## Building the CPP module

This is optional, if this is not built there is a fallback python implementations

```bash
meson setup ./build
ninja -C build
```

## Usage

```bash
mcomix manga_or_comic.zip
```

There are scripts in the root of the repo to run mcomix without needing to install. These are mainly for development and users should install instead of using these.

```bash
mcomix-starter.py manga_or_comic.zip
```

## Supported Archive Formats

Should support all libarchive supported formats. Loose image files are also supported.

## Installing

```bash
pip install --user .
```

Gentoo ebuilds at

<https://github.com/thermitegod/overlay/tree/master/media-gfx/mcomix-lite>

## Forked from

<https://github.com/multiSnow/mcomix3>
<https://sourceforge.net/projects/mcomix>
