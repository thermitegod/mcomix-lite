sources = files(
  'main.cxx',

  'commandline/commandline.cxx',

  'gui/main-window.cxx',
  'gui/menubar.cxx',
  'gui/statusbar.cxx',
  'gui/viewport.cxx',

  'gui/dialog/about.cxx',
  'gui/dialog/bookmarks.cxx',
  'gui/dialog/donate.cxx',
  'gui/dialog/preferences.cxx',
  'gui/dialog/properties.cxx',

  'gui/dialog/widgets/button-box.cxx',

  'settings/config.cxx',
)

spacefm = build_target(
    'webcomix',
    sources,
    target_type: 'executable',
    include_directories : include_directories('.'),
    install : true,
    install_dir : bindir,
    dependencies: [
        base_dependencies,
        gtk_dependencies,
        vfs_dep,
    ],
    cpp_pch: '../../../pch/pch.hxx',
)
