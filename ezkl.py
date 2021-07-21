import os 
import sys
import operator
from pathlib import Path
from difflib import SequenceMatcher

mode = sys.argv[1]
path = sys.argv[2]
thispath = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(thispath, "paths.txt")

myfile = Path(filepath)
myfile.touch(exist_ok=True)
file = open(filepath, "r+")
paths = file.read().split("\n")
file.close()

def linefilter(filter):
  new_paths = [filter]

  for path in paths:
    if path == filter:
      continue
    new_paths.append(path)
  
  return new_paths

def forgetpath(filter):
  new_paths = []

  for path in paths:
    if path == filter or (filter + "/") in path:
      continue
    new_paths.append(path)
  
  return new_paths

def trimpaths(path, match):
  tpaths = []
  split = path.split("/")
  parts = []
  for part in split:
    parts.append(part)
    if part == match:
      tpaths.append("/".join(parts))
  return tpaths

def findpath(filter, path2):
  matches = []

  def add_match(path, level, acc, match):
    match = {"path":path, "level":level, "acc":acc, "match":match}
    matches.append(match)
  
  checkslash = "/" in filter

  for path in paths:
    if checkslash and filter in path:
      add_match(path, 1, 1, filter)
    split = path.split("/")
    level = 1
    for part in split:
      acc = similar(part, filter)
      if acc >= 0.6:
        add_match(path, level, acc, part)
      level += 1

  if len(matches) > 0:
    matches.sort(key=lambda x: len(x["path"]), reverse=False)
    matches.sort(key=operator.itemgetter("level"), reverse=False)
    matches.sort(key=operator.itemgetter("acc"), reverse=True)

    for m in matches:
      for tpath in trimpaths(m["path"], m["match"]):
        if tpath != path2:
          updatefile(linefilter(tpath))
          print(tpath)
          return
  
def updatefile(paths):
  lines = paths[0:500]
  file = open(filepath, "w")
  file.write("\n".join(lines).strip())
  file.close()

def clean_path(path):
  cpath = os.getenv("PWD")
  cpath = cpath.rstrip("/").strip()
  return cpath

def similar(a, b):
  return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
  path2 = clean_path(path)
  if mode == "remember":
    new_paths = linefilter(path2)
    updatefile(new_paths)
  elif mode == "forget":
    new_paths = forgetpath(path)
    updatefile(new_paths)
  elif mode == "jump":
    if path.startswith("-"):
      exit(0)
    elif path == "/":
      print("/")
    else:
      findpath(path, path2)