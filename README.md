Git clone this somewhere then add this to .bashrc:

```
source /path/to/ezkl/ezkl.x.sh
```

Replace x with the appropriate shell.

Shells supported:

- bash
- fish
- zsh

Then source the shells' config file or restart the shell.

Now use cd normally to remember paths

And use z to jump to locations

`cd /some/path`

`z something`

![](https://i.imgur.com/TTkWt1V.gif)

It forgets paths (from paths.txt) that don't seem to exist anymore.

It's possible to use multiple keywords to specify path hierarchy:

"z code tetris" matches paths like `/code/something/tetris`. 

Using 'd' at a prompt removes that path from the paths file.