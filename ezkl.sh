#!/bin/bash

# Directory where the ezkl files are
CCDIR="$( builtin cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

function cd () {
  # Use the actual cd
  builtin cd "$@"
  if [ $? -eq 0 ]; then
    # If cd was ok then save the path
    python3 "${CCDIR}"/ezkl.py remember "$@"
  else
    :
  fi
}

complete -A directory cd

function z () {
  # Check if there are no arguments
  if [ -z "$1" ]; then
    python3 "${CCDIR}"/ezkl.py info
  else
    # Check if argument starts with --
    if [[ "$1" == "--"* ]]; then
      python3 "${CCDIR}"/ezkl.py "$@"
    else
      # Find a path to jump to
      output=$(python3 "${CCDIR}"/ezkl.py jump "$1")
      # cd to the response
      builtin cd "$output"
      if [ $? -eq 0 ]; then
        :
      else
        # If cd was not ok then forget the path
        python3 "${CCDIR}"/ezkl.py forget "$output"
      fi
    fi
  fi
}

