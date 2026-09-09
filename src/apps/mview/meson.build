sources = files(
  'main.cxx',

  'commandline/commandline.cxx',

  'gui/main-window.cxx',
  'gui/menubar.cxx',
  'gui/statusbar.cxx',
  'gui/viewport.cxx',

  'gui/dialog/about.cxx',
  'gui/dialog/donate.cxx',
  'gui/dialog/preferences.cxx',

  'gui/dialog/widgets/button-box.cxx',
)

mview_exe = executable(
    'mview',
    sources,
    include_directories: include_directories('.'),
    install: true,
    install_dir: bindir,
    dependencies: [
        base_dependencies,
        gtk_dependencies,
        vfs_dep,
    ],
    cpp_args: [
        '-DPACKAGE_NAME="mview"',
        '-DPACKAGE_NAME_FANCY="MView"',
    ],
    cpp_pch: '../../../pch/pch.hxx',
)
