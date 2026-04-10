## Test only dependencies

doctest_dep = dependency('doctest', required : true)

# main source files
test_sources = files(
  '../src/logger.cxx',

  '../src/vfs/error.cxx',
  '../src/vfs/trash-can.cxx',
  '../src/vfs/user-dirs.cxx',

  '../src/vfs/utils/sort.cxx',
  '../src/vfs/utils/utils.cxx',
  '../src/vfs/utils/natsort/strnatcmp.cxx',
)

# test source files
test_sources += files(
    'src/main.cxx',

    'src/vfs/error.cxx',
    'src/vfs/trash.cxx',

    'src/vfs/utils/utils.cxx',
    'src/vfs/utils/file-ops.cxx',
    'src/vfs/utils/natsort.cxx',
)

## Build

test_suite = build_target(
    'test_suite',
    sources: test_sources,
    target_type: 'executable',
    include_directories: include_directories(['./src', '../src']),
    install: false,
    dependencies: [
        doctest_dep,

        dependencies,
    ],
    cpp_pch: '../pch/pch.hxx',
)

test('Test Suite', test_suite)
