#!/bin/bash

CCDIR="$( builtin cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

function cd () {
  builtin cd "$@"
  if [ $? -eq 0 ]; then
    python3 "${CCDIR}"/ezkl.py remember "$@"
  else
    :
  fi
}

complete -A directory cd

function z () {
  if [ -z "$1" ]; then
    python3 "${CCDIR}"/ezkl.py info
  else
    output=$(python3 "${CCDIR}"/ezkl.py jump "$1")
    builtin cd "$output"
    if [ $? -eq 0 ]; then
      :
    else
      python3 "${CCDIR}"/ezkl.py forget "$output"
    fi
  fi
}

