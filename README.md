### This is meant to be a z.sh replacement that better meets my needs

Git clone this somewhere then add this to .bashrc:

```
source /path/to/ezkl/ezkl.sh
```

Now use cd normally to remember paths

And use z to jump to locations

`cd /some/path`

`z something`

If you have z.sh stuff sourced from before you might need to start a new bash session.

I don't plan on adding flags/options, but instead aim to optimize/predict as much as possible what the user wants when jumping. It uses an algorithm to prioritize some paths over others. It will choose the exact parent location in case there's no better match, for instance /foo/ instead of /foo/that when using 'foo'. Jumping again will ignore the current path so it goes to the next best match (if any) instead of doing nothing. It uses a similarity check so the keyword provided doesn't have to be exact (scripz will match scripts) (Higher accuracy = Higher priority). It forgets paths (from paths.txt) that don't seem to exist anymore (including subpaths).

I decided to write the logic in python since it's a lot easier than bash scripting. Bash is only used to wrap cd and add the z function. This allows more flexibility for advanced features.