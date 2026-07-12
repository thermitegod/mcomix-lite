# logger static library

spdlog_dep = dependency('spdlog', required: true)

logger_sources = files(
  'logger/logger.cxx',
)

logger_lib = static_library(
    'logger',
    sources : logger_sources,
    include_directories : include_directories('./logger'),
    dependencies : spdlog_dep,
    install: false,
)

logger_dep = declare_dependency(
    link_with : logger_lib,
    include_directories : include_directories('./logger'),
    dependencies : spdlog_dep,
)

# vfs static library

vfs_sources = files(
  'vfs/bookmarks.cxx',
  'vfs/error.cxx',
  'vfs/extractor.cxx',
  'vfs/file-handler.cxx',
  'vfs/file-provider.cxx',
  'vfs/file-supported.cxx',
  'vfs/image-files.cxx',
  'vfs/image-handler.cxx',
  'vfs/trash-can.cxx',
  'vfs/user-dirs.cxx',

  'vfs/utils/sort.cxx',
  'vfs/utils/utils.cxx',
  'vfs/utils/natsort/strnatcmp.cxx',

  'vfs/libarchive/entry.cxx',
  'vfs/libarchive/reader.cxx',

  'vfs/crash/crash.cxx',

  'vfs/image-tools/image-tools.cxx',
)

vfs_dependencies = [
    gtk_dependencies,

    logger_dep,

    botan_dep,
    libarchive_dep,
]

vfs_lib = static_library(
    'vfs',
    vfs_sources,
    include_directories : include_directories('.'),
    dependencies : vfs_dependencies,
    install: false,
    cpp_pch: '../../pch/pch.hxx',
)

vfs_dep = declare_dependency(
    link_with : vfs_lib,
    include_directories : include_directories('.'),
    dependencies : vfs_dependencies,
)
