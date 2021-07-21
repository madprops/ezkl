import os
import sys
from pathlib import Path
from difflib import SequenceMatcher

def filterpath(filter):
  pths = [filter]

  for path in paths:
    if path == filter:
      continue
    pths.append(path)

  return pths

def forgetpath(filter):
  pths = []

  for path in paths:
    if path == filter or path.startswith(filter + "/"):
      continue
    pths.append(path)

  return pths

def trimpaths(path, match):
  tpaths = []
  split = path.split("/")
  parts = []
  for part in split:
    parts.append(part)
    if part == match:
      tpaths.append("/".join(parts))
  return tpaths

def findpath(filter):
  matches = []

  def add_match(path, acc, match):
    match = {"path":path, "acc":acc, "match":match}
    matches.append(match)

  checkslash = "/" in filter

  for path in paths:
    if checkslash and filter in path:
      add_match(path, 1, filter)
    split = path.split("/")
    for part in split:
      acc = similar(part, filter)
      if acc >= min_accuracy or filter in part:
        add_match(path, acc, part)

  if len(matches) > 0:
    matches.sort(key=lambda x: -x["acc"])

    for m in matches:
      for tpath in trimpaths(m["path"], m["match"]):
        if tpath != pwd:
          return tpath

  return ""

def checkhome(filter):
  dir1 = str(Path.home() / Path(filter))
  dir2 = str(Path.home() / Path(filter.capitalize()))
  dir3 = str(Path.home() / Path(filter.lower()))
  dir4 = str(Path.home() / Path(filter.upper()))

  if os.path.isdir(dir1):
    return dir1
  elif os.path.isdir(dir2):
    return dir2
  elif os.path.isdir(dir3):
    return dir3
  elif os.path.isdir(dir4):
    return dir4
  else:
    return ""

def updatefile(paths):
  lines = paths[0:max_paths]
  file = open(filepath, "w")
  file.write("\n".join(lines).strip())
  file.close()

def similar(a, b):
  return SequenceMatcher(None, a, b).ratio()

def cleanpath(path):
  return path.rstrip("/")

if __name__ == "__main__":
  args = [x for x in sys.argv[1:] if not x.startswith("-")]

  if len(args) != 2:
    exit(0)

  mode = args[0]
  keyword = args[1]
  pwd = cleanpath(os.getenv("PWD"))
  min_accuracy = 0.6
  max_paths = 300

  thispath = Path(__file__).parent.resolve()
  filepath = Path(thispath) / Path("paths.txt")
  filepath.touch(exist_ok=True)
  file = open(filepath, "r+")
  paths = file.read().split("\n")
  file.close()

  if mode == "remember":
    updatefile(filterpath(pwd))
  elif mode == "forget":
    updatefile(forgetpath(keyword))
  elif mode == "jump":
    if keyword.startswith("/"):
      path = cleanpath(keyword)
    else:
      path = findpath(keyword)
    if len(path) == 0:
      path = checkhome(keyword)
    if len(path) > 0:
      updatefile(filterpath(path))
      print(path)