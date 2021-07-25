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
  # Check if there are no arguments
  if [ -z "$1" ]; then
    python3 "${CCDIR}"/ezkl.py top &&
    path=$(head -n 1 "${CCDIR}/paths.txt") &&
    builtin cd "$path"
  else
    # Show paths if command is --paths
    # Second argument is used as filter
    if [[ "$1" == "--paths" ]]; then
      python3 "${CCDIR}"/ezkl.py paths "$2"
    else
      # Else find a path to jump to
      python3 "${CCDIR}"/ezkl.py jump "$@" &&
      path=$(head -n 1 "${CCDIR}/paths.txt") &&
      builtin cd "$path"
    fi
  fi
}