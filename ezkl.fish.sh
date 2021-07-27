# Fish version

# Directory where the ezkl files are
set zdir (dirname (readlink -m (status --current-filename)))

function cd
  # Use the actual cd
  if builtin cd $argv;
    # If cd was ok then save the path
    python3 "$zdir"/ezkl.py remember
  end
end

complete --command cd --arguments '(__fish_complete_directories)'

function z
  # Find a path to cd to
  python3 "$zdir"/ezkl.py jump "$argv"
  set zpath (head -n 1 "$zdir/paths.txt")
  # Try to cd to path
  if ! builtin cd "$zpath";
    # If cd was not ok then forget the path
    python3 "$zdir"/ezkl.py forget "$zpath"
  end
end