project(
    'rcomix', ['c', 'cpp'],
    version : '4.0.0-dev',
    license : 'GPL3',
    default_options : [
        'cpp_std=c++26',
        'buildtype=debugoptimized',
        'warning_level=3',
        'optimization=2',
        'prefix=/usr',
        'sysconfdir=/etc',
    ],
    meson_version : '>= 1.7.0'
)

build_root = meson.project_build_root()
source_root = meson.project_source_root()

incdir = include_directories('src')

package = meson.project_name()
version = meson.project_version()
prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
libdir = join_paths(prefix, get_option('libdir'), package)
sysconfdir = get_option('sysconfdir')
localedir = join_paths(prefix, get_option('localedir'))
mandir = join_paths(prefix, get_option('mandir'))

## compiler stuff

cc = meson.get_compiler('c')
cpp = meson.get_compiler('cpp')

# message(cc.get_id())
# message(cpp.get_id())

flags = []

if get_option('buildtype') == 'debug' or get_option('buildtype') == 'debugoptimized'
    flags += cpp.get_supported_arguments([
        '-ggdb3',
        '-pedantic',
        '-pedantic-errors',
        '-fno-omit-frame-pointer',
        '-mno-omit-leaf-frame-pointer',
        '-fasynchronous-unwind-tables',
        # '-ftime-trace',
        # '-fsave-optimization-record',

        '-Wfatal-errors',

        # '-Werror',
        '-Werror=date-time',
        '-Werror=unguarded-availability-new',
    ])
endif

if get_option('buildtype') == 'release'
    flags += cpp.get_supported_arguments([])
endif

# Default
flags += cpp.get_supported_arguments([
    '-fexceptions',

    '-finput-charset=UTF-8',
    '-fexec-charset=UTF-8',

    '-fno-delete-null-pointer-checks',
    '-fno-strict-aliasing',
    '-fno-strict-overflow',

    '-ftrivial-auto-var-init=zero',
    '-fzero-init-padding-bits=all',
])

# Hardening
flags += cpp.get_supported_arguments([
    '-Wformat=2',
    '-Wformat-overflow=2',
    '-Wformat-truncation',
    '-Werror=format-security',

    '-fstack-protector-strong',
    '-fstack-clash-protection',
    '-fcf-protection=full',

    '-Wp,-U_FORTIFY_SOURCE,-D_FORTIFY_SOURCE=3',

    # GCC libstdc++
    # '-Wp,-D_GLIBCXX_DEBUG',
    '-Wp,-D_GLIBCXX_ASSERTIONS',

    # LLVM libc++
    # '-Wp,-D_LIBCPP_ASSERT',
    # '-Wp,-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST',
])

# Warnings
flags += cpp.get_supported_arguments([
    '-Walloca',
    '-Walloc-zero',
    '-Warray-bounds=2',
    '-Warray-compare',
    '-Wattribute-alias=2',
    '-Wbidi-chars=any',
    '-Wcast-align',
    '-Wcast-qual',
    '-Wchar-subscripts',
    '-Wcomment',
    '-Wconversion',
    '-Wdate-time',
    '-Wdisabled-optimization',
    '-Wdouble-promotion',
    '-Wduplicated-branches',
    '-Wduplicated-cond',
    # '-Wextra-semi', // TODO warnings from glibmm
    '-Wfloat-equal',
    '-Wignored-qualifiers',
    '-Wimplicit-fallthrough',
    '-Wimport',
    '-Winit-self',
    '-Wint-conversion',
    '-Wmissing-field-initializers',
    '-Wmissing-format-attribute',
    '-Wmissing-include-dirs',
    '-Wmissing-noreturn',
    '-Wnon-virtual-dtor',
    '-Wnull-dereference',
    # '-Wold-style-cast', // TODO warnings from glibmm
    '-Woverloaded-virtual',
    '-Wparentheses',
    '-Wpointer-arith',
    '-Wsequence-point',
    '-Wshadow',
    '-Wsign-compare',
    '-Wsign-conversion',
    '-Wstack-protector',
    '-Wstrict-aliasing',
    '-Wstring-compare',
    # '-Wstringop-overflow=4',
    '-Wswitch',
    '-Wswitch-enum',
    '-Wtrampolines',
    '-Wtrigraphs',
    '-Wundef',
    '-Wuninitialized',
    '-Wunknown-pragmas',
    '-Wunreachable-code',
    '-Wunused',
    '-Wunused-function',
    '-Wunused-label',
    '-Wunused-macros',
    '-Wunused-parameter',
    '-Wunused-result',
    '-Wunused-value',
    '-Wunused-variable',
    '-Wvariadic-macros',
    '-Wvla',
    '-Wwrite-strings',
    '-Wzero-length-bounds',
])

# Disabled Warnings
flags += cpp.get_supported_arguments([
    '-Wno-cast-align',
    '-Wno-double-promotion', # warns when using NAN
    '-Wno-cast-function-type-mismatch',

    # '-Wno-deprecated-declarations',
])

# Disabled GCC Warnings
if cpp.get_id() == 'gcc'
    flags += cpp.get_supported_arguments([
        '-Wno-cast-function-type',
        '-Wno-cast-qual',
        '-Wno-maybe-uninitialized',
        '-Wno-shadow',  # gcc is a lot stricter than clang
    ])
endif

# Disabled Clang Warnings
if cpp.get_id() == 'clang'
    flags += cpp.get_supported_arguments([])
endif

# Linker

link_flags = []
link_flags += cpp.get_supported_link_arguments([
    '-Wl,-O1',
    '-Wl,--as-needed',
    '-Wl,--sort-common',
    '-Wl,-z,relro',
    '-Wl,-z,now',
    '-Wl,-z,pack-relative-relocs',
    '-Wl,-z,noexecstack',
    '-Wl,-z,defs',
])

add_global_arguments(flags, language: ['c', 'cpp'])
add_global_link_arguments(link_flags, language: ['c', 'cpp'])

## dependencies

botan_dep = dependency('botan-3', required: true)
cli11_dep = dependency('CLI11', required: true)
libarchive_dep = dependency('libarchive', required : true)
magic_enum_dep = dependency('magic_enum', required: true, version: '>=0.9.7')

# Gtk4 CPP
gtkmm_dep = dependency('gtkmm-4.0', required: true)
glibmm_dep = dependency('glibmm-2.68', required: true)
giomm_dep = dependency('giomm-2.68', required: true)
sigc_dep = dependency('sigc++-3.0', required : true)

dependencies = [
    gtkmm_dep,
    giomm_dep,
    glibmm_dep,
    sigc_dep,

    botan_dep,
    cli11_dep,
    magic_enum_dep,
    libarchive_dep,
]

if get_option('with-system-glaze')
    glaze_dep = dependency('glaze', required: true, version: '>=6.3.0')
    dependencies += glaze_dep
else
    incdir += include_directories('subprojects/glaze/include')
endif

if get_option('with-system-spdlog')
    spdlog_dep = dependency('spdlog', required: true)
    dependencies += spdlog_dep
else
    cmake = import('cmake')
    # use std::format over bundled fmt::format
    cmake_opt_var = cmake.subproject_options()
    cmake_opt_var.add_cmake_defines({'SPDLOG_USE_STD_FORMAT': '1'})
    spdlog_proj = cmake.subproject('spdlog', required: true, options: cmake_opt_var)
    spdlog_dep = spdlog_proj.dependency('spdlog')
    dependencies += spdlog_dep
endif

if get_option('with-system-ztd')
    ztd_dep = dependency('ztd', required: true)
    dependencies += ztd_dep
else
    ztd_proj = subproject('ztd', required: true)
    ztd_dep = ztd_proj.get_variable('ztd_dep')
    dependencies += ztd_dep
endif

## preprocessor features
features = []

if get_option('dev')
    features += '-DDEV_MODE'
endif

## preprocessor static

preprocessor = [
    '-DPACKAGE_NAME="mcomix"',
    '-DPACKAGE_NAME_FANCY="MComix"',
    '-DPACKAGE_VERSION="@0@"'.format(meson.project_version()),
    '-DPACKAGE_GITHUB="https://www.github.com/thermitegod/mcomix-lite"',
    '-DPACKAGE_BUGREPORT="https://www.github.com/thermitegod/mcomix-lite/issues"',
    '-DPACKAGE_ONLINE_DOCS="TODO"',

    # data paths
    '-DPACKAGE_IMAGES="/usr/share/mcomix/images"',
    '-DPACKAGE_IMAGES_LOCAL="@0@"'.format(join_paths(meson.current_source_dir(), 'share/mcomix/images')),

    # test data paths
    '-DTEST_DATA_PATH="@0@"'.format(join_paths(meson.current_source_dir(), 'tests/test_data')),
]

if get_option('dev')
    preprocessor += [
        # GTKMM
        # '-DGTKMM_DISABLE_DEPRECATED', # TODO Gdk::Pixbuf
        # '-DGDKMM_DISABLE_DEPRECATED', # TODO Gdk::Pixbuf
        '-DGLIBMM_DISABLE_DEPRECATED',
        '-DGIOMM_DISABLE_DEPRECATED',
    ]
endif

foreach a : preprocessor
    add_project_arguments(a, language : ['c', 'cpp'])
endforeach

## Source files

sources = files(
  'src/logger.cxx',
  'src/main.cxx',

  'src/commandline/commandline.cxx',

  'src/gui/main-window.cxx',
  'src/gui/menubar.cxx',
  'src/gui/statusbar.cxx',
  'src/gui/thumbbar.cxx',
  'src/gui/viewport.cxx',

  'src/gui/dialog/about.cxx',
  'src/gui/dialog/bookmarks.cxx',
  'src/gui/dialog/donate.cxx',
  'src/gui/dialog/pageselect.cxx',
  'src/gui/dialog/preferences.cxx',
  'src/gui/dialog/properties.cxx',

  'src/gui/lib/image-tools.cxx',
  'src/gui/lib/thumbnailer.cxx',
  'src/gui/lib/view-state.cxx',

  'src/vfs/bookmarks.cxx',
  'src/vfs/error.cxx',
  'src/vfs/extractor.cxx',
  'src/vfs/file-handler.cxx',
  'src/vfs/file-provider.cxx',
  'src/vfs/file-supported.cxx',
  'src/vfs/image-files.cxx',
  'src/vfs/image-handler.cxx',
  'src/vfs/trash-can.cxx',
  'src/vfs/user-dirs.cxx',

  'src/vfs/utils/sort.cxx',
  'src/vfs/utils/utils.cxx',
  'src/vfs/utils/natsort/strnatcmp.cxx',

  'src/settings/config-load.cxx',
  'src/settings/config-save.cxx',

  'src/vfs/libarchive/entry.cxx',
  'src/vfs/libarchive/reader.cxx',

  'src/crash/crash.cxx',
)

spacefm = build_target(
    'mcomix',
    sources,
    target_type: 'executable',
    include_directories: incdir,
    install : true,
    install_dir : bindir,
    dependencies: dependencies,
    cpp_pch: 'pch/pch.hxx',
)

# if get_option('tests')
#     subdir('tests')
# endif

install_subdir('share/applications', install_dir: datadir)
install_subdir('share/icons', install_dir: datadir)
install_subdir('share/mcomix', install_dir: datadir)
install_subdir('share/metainfo', install_dir: datadir)
install_subdir('share/mime', install_dir: datadir)
