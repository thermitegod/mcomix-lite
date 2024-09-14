#!/bin/bash

find mcomix/ -iname '*.cpp' -o -iname '*.hpp' | xargs clang-format -i
