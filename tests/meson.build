## Test only dependencies

doctest_dep = dependency('doctest', required: true)

sources = files(
    'src/main.cxx',

    'src/natsort/natsort.cxx',

    'src/settings/property.cxx',

    'src/vfs/error.cxx',
    'src/vfs/trash.cxx',

    'src/vfs/utils/utils.cxx',
    'src/vfs/utils/file-ops.cxx',
)


test_suite_exe = executable(
    'test_suite',
    sources,
    include_directories: include_directories(['./src', '../src/apps/mcomix']),
    install: false,
    dependencies: [
        doctest_dep,

        base_dependencies,
        gtk_dependencies,
        vfs_dep,
    ],
    cpp_args: [
        '-DPACKAGE_NAME="mcomix"',
    ],
    cpp_pch: '../pch/pch.hxx',
)

test('Test Suite', test_suite_exe)
