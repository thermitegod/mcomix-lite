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

import io
from multiprocessing import Lock

_IOLock = Lock()


class LockedFileIO(io.BytesIO):
    def __init__(self, path):
        super().__init__()

        with _IOLock:
            with open(path, mode='rb') as f:
                super().__init__(f.read())
