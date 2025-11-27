#!/usr/bin/env bash

find \
    ./src \
    -iname '*.cxx' -o -iname '*.hxx' | \
    clang-format -i --files=/dev/stdin
