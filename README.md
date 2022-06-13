Installing on Fish:

```
set -g EZKL_PATH "/home/yo/code/ezkl"
source /home/yo/code/ezkl/ezkl.fish
```

Installing on Nu:

```
let-env EZKL_PATH = "/home/yo/code/ezkl"
use /home/yo/code/ezkl/ezkl.nu *
```

---

Use `z` to remember paths (like bookmarking).

Use `zforget` to forget the current path.

Use z to jump to locations.

It forgets paths (from paths.txt) that don't seem to exist anymore.

It's possible to use multiple keywords to specify path hierarchy:

`z code tetris` matches paths like `/code/something/tetris`. 

`zlist` can be used to list all the remembered paths.

`zclear` can be used to empty the path file (forget all the paths).