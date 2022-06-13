# Fish version

# Directory where the ezkl files are
set zdir (dirname (readlink -m (status --current-filename)))

function zforget
  python "$zdir"/ezkl.py forget
end

function zlist
  python "$zdir"/ezkl.py list
end

function zclear
  python "$zdir"/ezkl.py clear
end

function z
  if test -n "$argv"
    # Find a path to cd to
    set zpath (python "$zdir"/ezkl.py jump "$argv")

    if test -n "$zpath"
      # Try to cd to path
      cd "$zpath"

      # If cd was not ok then forget the path
      if [ $status != "0" ]
        python "$zdir"/ezkl.py forget "$zpath"
      end
    end
  else
    python "$zdir"/ezkl.py remember
  end
end