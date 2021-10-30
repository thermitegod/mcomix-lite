#!/usr/bin/python3

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
