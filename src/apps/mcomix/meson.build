sources = files(
  'main.cxx',

  'commandline/commandline.cxx',

  'gui/main-window.cxx',
  'gui/menubar.cxx',
  'gui/statusbar.cxx',
  'gui/thumbbar.cxx',
  'gui/viewport.cxx',

  'gui/dialog/about.cxx',
  'gui/dialog/bookmarks.cxx',
  'gui/dialog/donate.cxx',
  'gui/dialog/pageselect.cxx',
  'gui/dialog/preferences.cxx',
  'gui/dialog/properties.cxx',

  'gui/dialog/widgets/button-box.cxx',

  'gui/lib/thumbnailer.cxx',
  'gui/lib/view-state.cxx',

  'settings/config.cxx',
)

spacefm = build_target(
    'mcomix',
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
