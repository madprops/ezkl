#!/bin/bash

CCDIR="$( builtin cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

function cd () {
  builtin cd "$@"
  if [ $? -eq 0 ]; then
    python3 "${CCDIR}"/ezkl.py 1 "$1"
  fi
}

complete -A directory cd

function z () {
  output=$(python3 "${CCDIR}"/ezkl.py 2 "$1")
  builtin cd "$output"
}