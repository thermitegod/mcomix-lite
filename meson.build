project(
    'mcomix-lite',
    'cpp',
    version: '3.4.0-dev',
    default_options: [
        'cpp_std=c++23',
    ],
)

incdir = include_directories(['mcomix'])

prefix = get_option('prefix')
datadir = join_paths(prefix, get_option('datadir'))

pybind11_dep = dependency('pybind11', required : true)
magic_enum_dep = dependency('magic_enum', required : true, version: '>=0.9.7')

py = import('python').find_installation(pure: false)
py.extension_module(
    'mcomix_compiled',
    [
        'mcomix/bindings.cpp',

        'mcomix/box.cpp',
        'mcomix/layout.cpp',
        'mcomix/zoom.cpp',

        'mcomix/sort/sort.cpp',
        'mcomix/sort/utils.cpp',
        'mcomix/sort/natsort/strnatcmp.cpp',
    ],
    include_directories: incdir,
    install: true,
    dependencies : [
        pybind11_dep,
        magic_enum_dep,
    ],
)

subdir('mcomix')

if get_option('tests')
    pytest = find_program('pytest', required : true)
    test('pytest', pytest, args : [meson.project_source_root()])
endif

# meson-python requires all files to be installed in the wheel.
# workaround this by installing system config files in the ebuild

# meson-python: error: Could not map installation path to an equivalent wheel directory: '{prefix}/share/applications'
# install_man('man/mcomix.1')
# install_subdir('data/applications', install_dir: datadir)
# install_subdir('data/applications', install_dir: join_paths(datadir, 'applications'))
# install_subdir('data/icons', install_dir: datadir)
# install_subdir('data/metainfo', install_dir: datadir)
# install_subdir('data/mime', install_dir: datadir)
