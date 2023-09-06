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

import regex

# Split into float, int, and characters
NUMERIC_REGEXP = regex.compile(r'\d+[.]\d+|\d+|\D+')


class SortAlphanumeric:
    def __init__(self, filenames: list):
        """
        Do an in-place alphanumeric sort of the strings in <filenames>,
        such that for an example "1.jpg", "2.jpg", "10.jpg" is a sorted ordering
        """

        super().__init__()

        filenames.sort(key=self._keyfunc)

    def _isfloat(self, p):
        try:
            return 0, float(p)
        except ValueError:
            return 1, p.lower()

    def _keyfunc(self, s):
        x, y, z = str(s).rpartition('.')
        if z.isdigit():
            # extension with only digital is not extension
            x = f'{x}{y}{z}'
            z = ''
        return [self._isfloat(p) for p in (*NUMERIC_REGEXP.findall(x), z)]
