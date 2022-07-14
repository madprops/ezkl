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

And maybe an alias for `ezkl remember` to use it quickly.

It's possible to use multiple keywords to specify path hierarchy:

`code tetris` matches paths like `/code/something/tetris`.

`ezkl forget` can be used to forget the current path. 

No argument uses the current dir, or it uses an argument path.

`ezkl clear` can be used to forget all the paths.

`ezkl list` can be used to list all remembered paths.

If more than one matches are found, rofi is shown to pick one.