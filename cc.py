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
  global paths
  new_paths = [filter]

  for path in paths:
    if path == filter:
      continue
    new_paths.append(path)
  
  return new_paths

def findpath(filter):
  global paths
  matches = []

  for path in paths:
    split = path.split("/")
    level = 1
    for part in split:
      acc = similar(part, filter)
      if acc >= 0.6:
        match = {"path":path, "level":level, "acc":acc}
        matches.append(match)
      level += 1

  if len(matches) > 0:
    matches.sort(key=lambda x: len(x["path"]), reverse=False)
    matches.sort(key=operator.itemgetter("level"), reverse=False)
    matches.sort(key=operator.itemgetter("acc"), reverse=True)

    updatefile(linefilter(matches[0]["path"]))
    print(matches[0]["path"])
  
def updatefile(paths):
  lines = paths[0:500]
  file = open(filepath, "w")
  file.write("\n".join(lines).strip())
  file.close()

def clean_path(path):
  cpath = os.getcwd()
  cpath = cpath.rstrip("/")
  return cpath

def similar(a, b):
  return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
  if mode == "1":
    cpath = clean_path(path)
    new_paths = linefilter(cpath)
    updatefile(new_paths)
  elif mode == "2":
    findpath(path)