#!/bin/bash

CCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

function cc {
  DIRPATH=$(pwd)
  builtin cd "$1" 2> /dev/null
  if [ $? -eq 0 ]; then
    node "${CCDIR}"/cc.js 1 "$1" "$DIRPATH"
  else
    output=$(node "${CCDIR}"/cc.js 2 "$1" "$DIRPATH")
    builtin cd "$output"
  fi
}

complete -A directory cc