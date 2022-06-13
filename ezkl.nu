def script_path [] {
  echo ($env.EZKL_PATH | path join "ezkl.py")
}

def-env change_dir [path] {
  cd $path
}

export def zforget [] {
  python (script_path) forget
}

export def zlist [] {
  python (script_path) list
}

export def zclear [] {
  python (script_path) clear
}

export def-env z [arg = ""] {
  let ans = (if $arg != "" {
    let zpath = (python (script_path) jump $arg)
    
    if $zpath != "" {
      $zpath
    } else {
      $env.PWD
    }
  } else {
    python (script_path) remember
    $env.PWD
  })

  cd $ans
}