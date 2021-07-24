### This is meant to be a z implementation that better meets my needs

Git clone this somewhere then add this to .bashrc:

```
source /path/to/ezkl/ezkl.sh
```

Then `source ~/.bashrc`

Now use cd normally to remember paths

And use z to jump to locations

`cd /some/path`

`z something`

![](https://i.imgur.com/IFp9xtB.jpg)

Options appear when there are more than 1 path. 

Picking an option goes to that directory. 

Using d + number removes that path from the paths file.

If the answer in the prompt is not a number or d + number, it will use the  text to search for matches again.

I don't plan on adding flags/options, but instead aim to optimize/predict as much as possible what the user wants when jumping. It uses an algorithm to prioritize some paths over others. It will choose the exact parent location in case there's no better match, for instance /foo/ instead of /foo/that when using 'foo'. It uses a similarity check so the keyword provided doesn't have to be exact (scripz will match scripts) (Higher accuracy = Higher priority). It forgets paths (from paths.txt) that don't seem to exist anymore (including subpaths). It's possible to use multiple keywords to specify path hierarchy, "z code tetris" matches paths like `~/code/tetris`. If there are more than one suitable paths it will prompt the user to pick one.

I decided to write the logic in python since it's a lot easier than bash scripting. Bash is only used to wrap cd and add the z function. This allows more flexibility for advanced features.