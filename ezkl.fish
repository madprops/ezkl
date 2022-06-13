function zforget
  python "$EZKL_PATH"/ezkl.py forget
end

function zlist
  python "$EZKL_PATH"/ezkl.py list
end

function zclear
  python "$EZKL_PATH"/ezkl.py clear
end

function z
  if test -n "$argv"
    set zpath (python "$EZKL_PATH"/ezkl.py jump "$argv")

    if test -n "$zpath"
      cd "$zpath"

      if [ $status != "0" ]
        python "$EZKL_PATH"/ezkl.py forget "$zpath"
      end
    end
  else
    python "$EZKL_PATH"/ezkl.py remember
  end
end