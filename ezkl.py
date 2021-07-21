import os 
import sys
import operator
from pathlib import Path
from difflib import SequenceMatcher

mode = sys.argv[1]
path = sys.argv[2]
pwd = os.getenv("PWD").rstrip("/")

thispath = os.path.dirname(os.path.realpath(__file__))
filepath = Path(thispath) / Path("paths.txt")
filepath.touch(exist_ok=True)
file = open(filepath, "r+")
paths = file.read().split("\n")
file.close()

def filterpath(filter):
  new_paths = [filter]

  for path in paths:
    if path == filter:
      continue
    new_paths.append(path)
  
  return new_paths

def forgetpath(filter):
  new_paths = []

  for path in paths:
    if path == filter or path.startswith(filter + "/"):
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
      if acc >= 0.6:
        add_match(path, acc, part)

  if len(matches) > 0:
    matches.sort(key=operator.itemgetter("acc"), reverse=True)

    for m in matches:
      for tpath in trimpaths(m["path"], m["match"]):
        if tpath != pwd:
          updatefile(filterpath(tpath))
          print(tpath)
          return
  
def updatefile(paths):
  lines = paths[0:500]
  file = open(filepath, "w")
  file.write("\n".join(lines).strip())
  file.close()

def similar(a, b):
  return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
  if mode == "remember":
    new_paths = filterpath(pwd)
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
      findpath(path)