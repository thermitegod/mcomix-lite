#!/usr/bin/python3

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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'build'))

import cProfile
import pstats
from pathlib import Path

from mcomix.main import main

with cProfile.Profile() as pr:
    main()

stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
# stats.sort_stats(pstats.SortKey.CALLS)

# print to terminal
stats.print_stats()

# write to file
profile_file = Path('/tmp/mcomix.prof')
if profile_file.is_file():
    profile_file.unlink()
stats.dump_stats(filename=profile_file)

# view file in web browser
# $ snakeviz /tmp/mcomix.prof
