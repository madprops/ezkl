#!/bin/bash

# Directory where the ezkl files are
CCDIR="$( builtin cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

function cd () {
  # Use the actual cd
  builtin cd "$@"
  if [ $? -eq 0 ]; then
    # If cd was ok then save the path
    python3 "${CCDIR}"/ezkl.py remember
  else
    :
  fi
}

complete -A directory cd

function z () {
  # Find a path to cd to
  python3 "${CCDIR}"/ezkl.py jump "$@" &&
  path=$(head -n 1 "${CCDIR}/paths.txt") &&
  builtin cd "$path"
  if [ $? -eq 0 ]; then
    :
  else
    # If cd was not ok then forget the path
    python3 "${CCDIR}"/ezkl.py forget "$path"
  fi
}