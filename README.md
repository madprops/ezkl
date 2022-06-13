News: Now it doesn't remember automatically, z with no arguments remembers path

News: It now uses ~/.config/ezkl/paths.txt

---

Git clone this somewhere, then add this to your shell's config file:

```
source /path/to/ezkl/ezkl.x.sh
```

Replace x with the appropriate shell.

---

Shells supported:

- fish

- nushell

---

For nushell add something like this to config.nu

```
let-env EZKL_PATH = "/home/yo/code/ezkl"
use /home/yo/code/ezkl/ezkl.nu *
```

Then source the file or restart the shell.

Use `z` to remember paths (like bookmarking).

Use `zforget` to forget the current path.

And use z to jump to locations

`cd /some/path`

`z something`

It forgets paths (from paths.txt) that don't seem to exist anymore.

It's possible to use multiple keywords to specify path hierarchy:

`z code tetris` matches paths like `/code/something/tetris`. 

`zlist` can be used to list all the remembered paths.

`zclear` can be used to empty the path file (forget all the paths).