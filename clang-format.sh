#!/usr/bin/env bash

find \
    ./src \
    ./tests \
    -iname '*.cxx' -o -iname '*.hxx' | \
    clang-format -i --files=/dev/stdin
