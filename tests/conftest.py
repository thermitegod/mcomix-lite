# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(Path(__file__).parent), 'build'))

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
