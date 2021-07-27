# Zsh version

# # Directory where the ezkl files are
zdir=${0:a:h}

function cd () {
  # Use the actual cd
  if builtin cd "$@"; then
    # If cd was ok then save the path
    python3 "${zdir}"/ezkl.py remember
  fi
}

function z () {
  # Find a path to cd to
  python3 "${zdir}"/ezkl.py jump "$@"
  zpath=$(head -n 1 "${zdir}/paths.txt")
  # Try to cd to path
  if ! builtin cd "$zpath"; then
  #   # If cd was not ok then forget the path
    python3 "${zdir}"/ezkl.py forget "$zpath"
  fi
}