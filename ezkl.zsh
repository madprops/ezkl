function zforget () {
  python "$EZKL_PATH"/ezkl.py forget
}

function zlist () {
  python "$EZKL_PATH"/ezkl.py list
}

function zclear () {
  python "$EZKL_PATH"/ezkl.py clear
}

function z () {
  if [ $# -gt 0 ]; then
    zpath=$(python "$EZKL_PATH"/ezkl.py jump "$@")

    if [ -n "$zpath" ]; then
      if ! cd "$zpath"; then
        python "$EZKL_PATH"/ezkl.py forget "$zpath"
      fi
    fi
  else
    python "$EZKL_PATH"/ezkl.py remember
  fi
}