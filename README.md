News: Now it doesn't remember automatically, it uses zremember and zforget.

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

---

Then source the file or restart the shell.

Use zremember to remember paths (like bookmarking).

Use zforget to forget the current path.

And use z to jump to locations

`cd /some/path`

`z something`

---

![](https://i.imgur.com/TTkWt1V.gif)

---

It forgets paths (from paths.txt) that don't seem to exist anymore.

It's possible to use multiple keywords to specify path hierarchy:

"z code tetris" matches paths like `/code/something/tetris`. 

'D' (shift + d) removes an entry from the file while on the prompt.

"zlistpaths" can be used to list all the remembered paths.

"zclearpaths" can be used to empty the path file (forget all the paths).