# Fish version

# Directory where the ezkl files are
set zdir (dirname (readlink -m (status --current-filename)))

function zremember
  python "$zdir"/ezkl.py remember
end

function zforget
  python "$zdir"/ezkl.py forget
end

function zclearpaths
  python "$zdir"/ezkl.py clearpaths
end

function z
  # Find a path to cd to
  python "$zdir"/ezkl.py jump "$argv"

  if [ $status = "33" ]
    set zpath (head -n 1 "$HOME/.config/ezkl/paths.txt")

    # Try to cd to path
    cd "$zpath"

    # If cd was not ok then forget the path
    if [ $status != "0" ]
      python "$zdir"/ezkl.py forget "$zpath"
    end
  end
end