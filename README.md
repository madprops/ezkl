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

Use `z keyword` to jump to locations.

It's possible to use multiple keywords to specify path hierarchy:

`z code tetris` matches paths like `/code/something/tetris`.

`zforget` can be used to forget the current path.

`zclear` can be used to forget all the paths.

`zlist` can be used to list all remembered paths.