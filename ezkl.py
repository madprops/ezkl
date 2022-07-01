# Imports
import re
from sys import argv, stderr
from os import getenv
from typing import List, Match
from pathlib import Path

# Globals
mode: str
keyw: str
paths: List[str]
filepath: Path
pwd: str

# List of matches
class MatchList:
  items: List[str]

  def __init__(self) -> None:
    self.items = []

  # Add an item
  def add(self, match: str) -> None:
    self.items.append(match)

  # Append two lists
  def join(self, matches: "MatchList") -> None:
    for item in matches.items:
      if item not in self.items:
        self.items.append(item)

  # Get a slice of matches
  def slice(self, max: int) -> List[str]:
    paths: List[str] = []

    for m in self.items[0:max]:
      paths.append(m)

    return paths

  # Get first item
  def first(self) -> str:
    return self.items[0]

  # Get number of matches
  def len(self) -> int:
    return len(self.items)

  # Check if list has item
  def has(self, match: str) -> bool:
    for m in self.items:
      if m == match:
        return True
    return False

  # Check if there are no items
  def empty(self) -> bool:
    return len(self.items) == 0

# Get arguments. Might exit here
def get_args() -> None:
  global mode
  global keyw

  args = argv[1:]
  mode = args[0] if len(args) > 0 else ""

  if mode not in ["remember", "forget", "jump", "list", "clear"]:
    exit(1)

  keyw = " ".join(args[1:]) if len(args) > 1 else ""
  
  if mode == "jump" and keyw == "":
    exit(1)

# Read the paths file plus other paths
def get_paths() -> None:
  global paths
  global filepath
  global pwd

  configdir = Path("~/.config/ezkl").expanduser()
  
  if not configdir.exists():
    configdir.mkdir(parents=True)

  filepath = configdir / Path("paths.txt")
  filepath.touch(exist_ok=True)

  file = open(filepath, "r")
  paths = file.read().split("\n")
  paths = list(map(str.strip, paths))
  paths = list(filter(None, paths))
  file.close()
  pwd = clean_path(str(getenv("PWD")))

# Put path in first line
def filter_path(path: str) -> None:
  global paths
  pths = [path]

  for p in paths:
    if p == path:
      continue
    pths.append(p)

  paths = pths

# Remember path
def remember_path(path: str) -> None:
  if path in paths:
    info("Path already remembered")
  else:
    filter_path(path)
    update_file()
    info("Path remembered")

# Remove path and subdirs
def forget_path(path: str, subpaths: bool) -> None:
  global paths

  if path not in paths:
    info("Path is not remembered")
  else:
    pths: List[str] = []

    for p in paths:
      if subpaths:
        if p == path or p.startswith(path + "/"):
          continue
      else:
        if p == path:
          continue

      pths.append(p)

    paths = pths

    update_file()
    info("Path forgotten")

# Get the parts of a path
def get_parts(path: str) -> List[str]:
  return list(filter(lambda x: x != "", path.split("/")))

# Remove similar items
def check_syms(list_1: MatchList, list_2: MatchList) -> None:  
  pwd_2 = Path(pwd)

  for p in list_1.items:
    if p not in list_2.items:
      continue
      
    px = Path(p)
    rslv = px.resolve()
    
    if px == pwd or px == pwd_2 or rslv == pwd or rslv == pwd_2:
      list_2.items.remove(p)

    for pp in list_2.items:
      ppx = Path(pp)
      if px == ppx:
        continue
      if ppx == rslv:
        list_2.items.remove(pp)
        break

# Find matching paths
# Exact parts, startswith, and includes
def get_matches(keywords: List[str]) -> MatchList:
  p_exact = MatchList()
  p_starts = MatchList()
  p_includes = MatchList()

  for keyword in keywords:
    lowkeyword = keyword.lower()
    for path in paths:
      parts = get_parts(path)
      partlist: List[str] = []
      for part in parts:
        partlist.append(part)
        lowpart = part.lower()
        partjoin = "/" + "/".join(partlist)
        if lowkeyword == lowpart:
          if not p_exact.has(partjoin):
            if is_valid_path(partjoin, keywords, 1):
              p_exact.add(partjoin)
        elif lowpart.startswith(lowkeyword):
          if not p_starts.has(partjoin):
            if is_valid_path(partjoin, keywords, 1):
              p_starts.add(partjoin)
        elif lowkeyword in lowpart:
          if not p_includes.has(partjoin):
            if is_valid_path(partjoin, keywords, 2):
              p_includes.add(partjoin)
  
  exact = MatchList()
  starts = MatchList()
  includes = MatchList()

  exact.items = p_exact.items[:]
  starts.items = p_starts.items[:]
  includes.items = p_includes.items[:]
  
  check_syms(p_exact, exact)
  check_syms(p_starts, starts)
  check_syms(p_includes, includes)

  if exact.len() > 0:
    if exact.len() == 1:
      return exact
    else:
      exact.join(starts)
      exact.join(includes)
      return exact

  elif starts.len() > 0:
    if starts.len() == 1:
      return starts
    else:
      starts.join(includes)
      return starts

  elif includes.len() > 0:
    return includes

  return MatchList()

# Write paths to file
def update_file() -> None:
  file = open(filepath, "w")
  file.write("\n".join(paths).strip())
  file.close()

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# List the paths file
def list_paths() -> None:
  for path in paths:
    print(path)

# Clear the paths file
def clear_paths() -> None:
  global paths

  ans = input("Forget all paths? (y/n): ")
  
  if ans == "y":
    paths = []
    update_file()
    info("Paths cleared")

# Check if path is the current directory
def is_pwd(path: str) -> bool:
  return Path(path) == Path(pwd)

# Main jump function
def jump() -> None:
  if len(paths) == 0:
    info("No paths remembered yet")
    exit(1)

  keywords = list(filter(lambda x: x != "", \
    re.split("\\s|/", keyw)))
  
  matches = get_matches(keywords)
  if not matches.empty(): 
    if len(matches.items) > 1:
      for m in matches.items[1:]:
        info(m, "Also")

    print(matches.first())
  else:
    info("No path found")

# Show a message
def info(msg: str, title = "ezkl") -> None:
  print(f"{title}: {msg}", file=stderr)

# Check if path is valid
def is_valid_path(path: str, keywords: List[str], mode: int) -> bool:
  lowkeywords = map(lambda x: x.lower().replace(".", ""), keywords)

  if mode == 1:
    # Mode for startswith
    rstr = "/" + ".*/".join(lowkeywords) + ".*"

  elif mode == 2:
    # Mode for x in y
    rstr = "/.*" + ".*/.*".join(lowkeywords) + ".*"

  else:
    return False

  p = path.lower().replace(".", "")
  return bool(re.search(rstr, p))

# Main function
def main() -> None:
  get_args()
  get_paths()

  if mode == "remember":
    remember_path(pwd)

  elif mode == "forget":
    if keyw != "":
      forget_path(keyw, True)
    else:
      forget_path(pwd, True)

  elif mode == "list":
    list_paths()    
  
  elif mode == "clear":
    clear_paths()

  elif mode == "jump":
    jump()
  
# Program starts here
if __name__ == "__main__": main()