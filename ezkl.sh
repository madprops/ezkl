#!/bin/bash

CCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

function cd () {
  builtin cd "$1" 2> /dev/null
  if [ $? -eq 0 ]; then
    python3 "${CCDIR}"/ezkl.py 1 "$1"
  else
    output=$(python3 "${CCDIR}"/ezkl.py 2 "$1")
    builtin cd "$output"
  fi
}

complete -A directory cc