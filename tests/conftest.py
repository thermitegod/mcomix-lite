import pytest

# do GTK/GDK import test here to avoid having to do them for every
# test that has some GTK import
try:
    import gi
    gi.require_version('PangoCairo', '1.0')
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    from gi.repository import GLib, Gdk, Gtk
except (ValueError, ImportError):
    raise SystemExit('GTK+ 3.0 import error')

# from mcomix.preferences import config


@pytest.fixture
def mcomix_config(scope='session'):
    # return config
    pass
