# Imports
import re
from sys import argv
from sys import stderr
from os import getenv
from typing import List
from pathlib import Path
from difflib import SequenceMatcher

# Matched paths and their accuracy
class Match:
  def __init__(self, path: str, acc: float):
    self.path = path
    self.acc = acc

  def level(self) -> int:
    return len(self.path.split("/"))

# List of matches
class MatchList:
  def __init__(self, items: List[Match] = []):
    self.items = items

  # Add an item
  def add(self, match: Match) -> None:
    self.items.append(match)

  # Remove unecessary items
  def filter(self, filters: List[str]) -> None:
    matches: List[Match] = []
    rstr = ".*" + ".*/.*".join(filters) + ".*"

    for m in self.items:
      add = True

      if add:
        for m2 in matches:
          if m.path == m2.path:
            add = False
            break

      if add:
        if not re.search(rstr, m.path.lower()):
          add = False

      if add:
        matches.append(m)

    self.items = matches

  # Sort the list by accuracy and path level
  def sort(self) -> None:
    self.items.sort(key=lambda x: (-x.acc, x.level()))

  # Used for debuggin purposes
  def to_string(self) -> None:
    for m in self.items:
      print(f"{m.path} -> {m.acc}")

  # Get first item
  def first(self) -> Match:
    return self.items[0]

  # Get number of matches
  def len(self) -> int:
    return len(self.items)

# Settings
min_accuracy: float = 0.66
max_paths: int = 250
max_hints: int = 5

# Globals
mode: str
keyw: str
paths: List[str]
filepath: Path
pwd: str

# Main function
def main() -> None:
  get_args()
  get_paths()

  if mode == "info":
    show_info()

  elif mode == "remember":
    update_file(filter_path(pwd))

  elif mode == "forget":
    update_file(forget_path(keyw))

  elif mode == "paths":
    show_paths(keyw)

  elif mode == "jump":
    matches = MatchList()
    kws = list(filter(lambda x: x != "", \
      re.split("\\s|/", keyw)))

    for kw in kws:
      matches.items += get_matches(kw).items
      matches.items += get_guesses(kw).items

    matches.filter(kws)
    matches.sort()
    num = matches.len()

    if num > 0:
      if num > 1:
        choose_path(matches)
      elif num:
        path = matches.first().path
        update_file(filter_path(path))
        print(path)

# Get arguments. Might exit here
def get_args() -> None:
  global mode
  global keyw

  args = argv[1:]
  mode = args[0] if len(args) > 0 else ""
  keyw = " ".join(args[1:]) if len(args) > 1 else ""

  if mode not in ["remember", "forget", "jump", "info", "paths"]:
    exit(0)

  if mode in ["forget", "jump"] and keyw == "":
    exit(0)

# Read the paths file plus other paths
def get_paths() -> None:
  global paths
  global filepath
  global pwd
  thispath = Path(__file__).parent.resolve()
  filepath = Path(thispath) / Path("paths.txt")
  filepath.touch(exist_ok=True)
  file = open(filepath, "r")
  paths = file.read().split("\n")
  paths = list(map(str.strip, paths))
  paths = list(filter(None, paths))
  file.close()
  pwd = clean_path(str(getenv("PWD")))

# Put path in first line
def filter_path(path: str) -> List[str]:
  pths = [path]

  for p in paths:
    if p == path:
      continue
    pths.append(p)

  return pths

# Remove path and subdirs
def forget_path(path: str) -> List[str]:
  pths: List[str] = []

  for p in paths:
    if p == path or p.startswith(path + "/"):
      continue
    pths.append(p)

  return pths

# Try to find a matching path
def get_matches(filter: str) -> MatchList:
  matches = MatchList()
  lowfilter = filter.lower()

  def add_match(path: str, acc: float) -> None:
    for m in matches.items:
      if m.path == path:
        return

    match = Match(path, acc)
    matches.add(match)

  for path in paths:
    split = path.split("/")
    parts: List[str] = []
    for part in split:
      parts.append(part)
      lowpart = part.lower()
      acc = similar(lowpart, lowfilter)
      if lowpart.startswith(lowfilter):
        add_match("/".join(parts), high_acc(lowfilter, lowpart))
      else:
        if acc >= min_accuracy:
          add_match("/".join(parts), acc)

  return matches

# Check if path or similar exists in directory
# It checks current directory and then home
def get_guesses(p: str) -> MatchList:
  guesses = MatchList()
  pths = [p, p.capitalize(), p.lower(), p.upper(), f".{p}"]

  for s in pths:
    dir = Path(pwd) / Path(s)
    if dir.is_dir():
      guesses.add(Match(str(dir), 0.9))

  if not at_home():
    for s in pths:
      dir = Path.home() / Path(s)
      if dir.is_dir():
        guesses.add(Match(str(dir), 0.9))

  return guesses

# Write paths to file
def update_file(paths: List[str]) -> None:
  lines: List[str] = paths[0:max_paths]
  file = open(filepath, "w")
  file.write("\n".join(lines).strip())
  file.close()

# Check string similarity from 0 to 1
def similar(a: str, b: str) -> float:
  return SequenceMatcher(None, a, b).ratio()

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# Show a hint
def show_hint(path: str, n: int) -> None:
  CRED = "\033[92m"
  CEND = "\033[0m"
  eprint(f"{CRED}({n}){CEND} {path}")

# Check if pwd is set to home
def at_home() -> bool:
  return Path(pwd) == Path(Path.home())

# Get an acc that is near max
# But that depends on length diff
def high_acc(a: str, b: str) -> float:
  diff: float = 0.01 * (max(len(a), len(b)) - min(len(a), len(b)))
  return 0.99 - diff

# Show some information
def show_info() -> None:
  info = f"""\nezkl is installed and ready to use
---------------------------------------------
Jump around directories. For instance 'z music'
Directories get remembered by using cd normally
Paths are saved in ezkl/paths.txt
Use 'z --paths' to show saved paths
---------------------------------------------
Minimum accuracy is set to {min_accuracy}
paths.txt has {len(paths)}/{max_paths} paths saved\n"""
  print(info)

# Show all paths
def show_paths(filter: str) -> None:
  hasfilter = filter != ""
  lowfilter = filter.lower()

  for path in paths:
    if hasfilter:
      if lowfilter not in path.lower():
        continue
    print(path)

# Show paths that might be relevant
def choose_path(matches: MatchList) -> None:
  n = 1
  for m in matches.items:
    show_hint(m.path, n)
    n += 1
    if n > max_hints:
      break
  try:
    print(matches.items[int(input()) - 1].path)
  except:
    pass

# Print to stderr
def eprint(s: str):
  print(s, file=stderr)

# Program starts here
if __name__ == "__main__": main()