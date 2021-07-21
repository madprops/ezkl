import os 
import sys
from pathlib import Path
from difflib import SequenceMatcher

args = [x for x in sys.argv[1:] if not x.startswith("-")]

if len(args) != 2:
  exit(0)

mode = args[0]
path = args[1]
pwd = os.getenv("PWD").rstrip("/")

thispath = os.path.dirname(os.path.realpath(__file__))
filepath = Path(thispath) / Path("paths.txt")
filepath.touch(exist_ok=True)
file = open(filepath, "r+")
paths = file.read().split("\n")
file.close()

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
      if acc >= 0.7:
        add_match(path, acc, part)

  if len(matches) > 0:
    matches.sort(key=lambda x: -x["acc"])

    for m in matches:
      for tpath in trimpaths(m["path"], m["match"]):
        if tpath != pwd:
          return tpath
  
  return ""

def checkhome(filter):
  dir = Path.home() / Path(filter)
  if os.path.isdir(dir):
    return str(dir)
  else:
    return ""
  
def updatefile(paths):
  lines = paths[0:500]
  file = open(filepath, "w")
  file.write("\n".join(lines).strip())
  file.close()

def similar(a, b):
  return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
  if mode == "remember":
    updatefile(filterpath(pwd))
  elif mode == "forget":
    updatefile(forgetpath(path))
  elif mode == "jump":
    p = path if path.startswith("/") \
      else findpath(path)
    if len(p) == 0:
      p = checkhome(path)
    if len(p) > 0:
      updatefile(filterpath(p))
      print(p)