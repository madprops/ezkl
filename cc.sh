#!/bin/bash

CCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

function cc {
  DIRPATH=$(pwd)
  builtin cd "$1" 2> /dev/null
  if [ $? -eq 0 ]; then
    python "${CCDIR}"/cc.py 1 "$1" "$DIRPATH"
  else
    output=$(python "${CCDIR}"/cc.py 2 "$1" "$DIRPATH")
    builtin cd "$output"
  fi
}

complete -A directory cc