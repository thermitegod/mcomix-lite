#!/usr/bin/env fish
for f in $XDG_CACHE_HOME/mcomix/*
    # echo $f
    mcomix $f/* &
end
