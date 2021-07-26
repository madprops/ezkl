Git clone this somewhere then add this to .bashrc:

```
source /path/to/ezkl/ezkl.bash.sh
```

Shells supported:

- Bash
- Fish

Then `source ~/.bashrc`

Now use cd normally to remember paths

And use z to jump to locations

`cd /some/path`

`z something`

![](https://i.imgur.com/TTkWt1V.gif)

It forgets paths (from paths.txt) that don't seem to exist anymore.

It's possible to use multiple keywords to specify path hierarchy:

"z code tetris" matches paths like `/code/something/tetris`. 

Using 'd' at a prompt removes that path from the paths file.