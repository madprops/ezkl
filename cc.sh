#!/bin/bash

CCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

function cc {
  builtin cd "$1" 2> /dev/null
  if [ $? -eq 0 ]; then
    python3 "${CCDIR}"/cc.py 1 "$1"
  else
    output=$(python3 "${CCDIR}"/cc.py 2 "$1")
    builtin cd "$output"
  fi
}

complete -A directory cc