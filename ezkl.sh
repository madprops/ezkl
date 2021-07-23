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
    python3 "${CCDIR}"/ezkl.py info
  else
    # Show paths if command is --paths
    # Second argument is used as filter
    if [[ "$1" == "--paths" ]]; then
      python3 "${CCDIR}"/ezkl.py paths "$2"
    else
      # Else find a path to jump to
      output=$(python3 "${CCDIR}"/ezkl.py jump "$1")
      while IFS= read -r line; do
        # If output starts with slash...
        # This means it's a path
        if [[ "$line" == "/"* ]]; then
          # cd to the response
          builtin cd "$line"
          if [ $? -eq 0 ]; then
            :
          else
            # If cd was not ok then forget the path
            python3 "${CCDIR}"/ezkl.py forget "$line"
          fi
        else
          if [ -z "$line" ]; then
            :
          else
            echo "$line"
          fi
        fi
      done <<< "$output"
    fi
  fi
}

