# Fish version

# Directory where the ezkl files are
set CCDIR (dirname (readlink -m (status --current-filename)))

function cd
  # Use the actual cd
  if builtin cd $argv;
    # If cd was ok then save the path
    python3 "$CCDIR"/ezkl.py remember
  end
end

complete --command cd --arguments '(__fish_complete_directories)'

function z
  # Find a path to cd to
  python3 "$CCDIR"/ezkl.py jump "$argv"
  set path (head -n 1 "$CCDIR/paths.txt")
  # Try to cd to path
  if ! builtin cd "$path"; then
    # If cd was not ok then forget the path
    python3 "$CCDIR"/ezkl.py forget "$path"
  end
end