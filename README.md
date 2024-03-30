There is an aur package.

Use `ezkl remember` to remember paths (like bookmarking).

No argument uses the current dir, or it uses an argument path.

Use `ezkl jump` to jump to locations.

The actual command to jump is:

`cd $(ezkl jump something)`

But that's a bit long so you should make an alias function in your shell.

This is a fish function, for example:

```
function z
  set p $(ezkl jump "$argv")

  if test -n "$p"
    cd "$p"

    if test $status != 0
      ezkl forget "$p"
    end
  end
end
```

`ezkl forget` can be used to forget the current path.

No argument uses the current dir, or it uses an argument path.

`ezkl clear` can be used to forget all the paths.

`ezkl list` can be used to list all remembered paths.

If more than one matches are found, rofi is shown to pick one.

## Chains

You can chain using multiple keywords.

The first keyword is the root, which has to be a known path.

The rest of the keywords are subdirs inside of it.

For example say you have the dir `~/code/ezkl/bin/trees`

You can do `z ezk bi tre` and it should find it.

This would require `~/code/ezkl` to be a remembered path.

It picks the first subdirs that match so it might not work in all cases due to ambiguity.