# Imports
import re
import curses
from sys import argv
from os import getenv
from typing import List
from typing import Optional
from pathlib import Path

# Matched paths
class Match:
  def __init__(self, path: str):
    self.path = path

  def level(self) -> int:
    return len(self.path.split("/"))

# List of matches
class MatchList:
  def __init__(self, items: Optional[List[Match]] = None):
    self.items = items if items is not None else []

  # Add an item
  def add(self, match: Match) -> None:
    self.items.append(match)

  # Remove unecessary items
  def filter(self, filters: List[str], max: int) -> None:
    matches: List[Match] = []
    rstr = ".*" + ".*/.*".join(filters) + ".*"

    for m in self.items:
      add = True

      for m2 in matches:
        if m.path == m2.path:
          add = False
          break

      if add:
        if not re.search(rstr, m.path.lower()):
          add = False

      if add:
        matches.append(m)
        if len(matches) == max:
          break

    self.items = matches

  # Used for debuggin purposes
  def to_string(self) -> None:
    for m in self.items:
      print(f"Path: {m.path}")

  # Get first item
  def first(self) -> Match:
    return self.items[0]

  # Get number of matches
  def len(self) -> int:
    return len(self.items)

  # Check if list has item
  def has(self, match: Match) -> bool:
    for m in self.items:
      if m.path == match.path:
        return True
    return False

# Settings
max_paths: int = 250
max_options: int = 10

# Globals
mode: str
keyw: str
paths: List[str]
thispath: Path
filepath: Path
pwd: str

# Main function
def main() -> None:
  get_args()
  get_paths()

  if mode == "top":
    show_top()

  elif mode == "remember":
    update_file(filter_path(pwd))

  elif mode == "forget":
    update_file(forget_path(keyw, True))

  elif mode == "paths":
    show_paths(keyw)

  elif mode == "jump":
    jump(keyw)

# Get arguments. Might exit here
def get_args() -> None:
  global mode
  global keyw

  args = argv[1:]
  mode = args[0] if len(args) > 0 else ""
  keyw = " ".join(args[1:]) if len(args) > 1 else ""

  if mode not in ["remember", "forget", "jump", "top", "paths"]:
    exit(1)

  if mode in ["forget", "jump"] and keyw == "":
    exit(1)

# Read the paths file plus other paths
def get_paths() -> None:
  global paths
  global thispath
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
def forget_path(path: str, subpaths: bool) -> List[str]:
  pths: List[str] = []

  for p in paths:
    if subpaths:
      if p == path or p.startswith(path + "/"):
        continue
    else:
      if p == path:
        continue

    pths.append(p)

  return pths

# Try to find a matching path
def get_matches(filter: str) -> MatchList:
  matches = MatchList()
  lowfilter = filter.lower()

  for path in paths:
    split = path.split("/")
    for part in split:
      lowpart = part.lower()
      if lowpart.startswith(lowfilter):
        match = Match(path)
        if not matches.has(match):
          matches.add(match)

  return matches

# Write paths to file
def update_file(paths: List[str]) -> None:
  lines: List[str] = paths[0:max_paths]
  file = open(filepath, "w")
  file.write("\n".join(lines).strip())
  file.close()

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

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
# Pick one by number. d is used to forget
def show_options(matches: MatchList) -> None:
  num = len(matches.items)
  screen = curses.initscr()
  screen.keypad(True)
  curses.noecho()
  curses.curs_set(0)

  for i, m in enumerate(matches.items[0:max_options]):
    screen.addstr(i, 0, m.path)
  
  screen.refresh()
  pos = 0

  def highlight():
    for i, m in enumerate(matches.items[0:max_options]):
      if i == pos:
        screen.addstr(i, 0, m.path, curses.A_UNDERLINE)
      else:
        screen.addstr(i, 0, m.path, curses.A_NORMAL)
  
  highlight()
  enter = False

  try:
    while True:
      char = screen.getch()
      if char == ord('q'):
        break      
      elif char == curses.KEY_UP: 
        pos = (pos - 1) if pos > 0 else pos
        highlight()
      elif char == curses.KEY_DOWN:
        pos = (pos + 1) if pos < num -1 else pos
        highlight()
      elif char == 10:
        enter = True
        break
  except:
    curses.nocbreak()
    curses.echo()
    curses.endwin()
  
  curses.endwin()
  if not enter: exit(1)

  m = matches.items[pos]
  update_paths(m.path)

# Parse string to number
def to_number(s: str) -> int:
  num = re.sub("[^0-9]", "", s)
  if len(num) > 0:
    return int(num)
  return 0

# Save the paths file
def update_paths(path: str) -> None:
  if Path(path) != Path(pwd):
    update_file(filter_path(path))

# Main jump function
def jump(keywords: str) -> None:
  matches = MatchList()
  kws = list(filter(lambda x: x != "", \
    re.split("\\s|/", keywords)))

  for kw in kws:
    matches.items += get_matches(kw).items

  matches.filter(kws, max_options)
  num = matches.len()

  if num > 0:
    if num > 1:
      show_options(matches)
    else:
      path = matches.first().path
      update_paths(path)

# Show the first paths
def show_top() -> None:
  matches = MatchList()
  for path in paths[0:max_options]:
    matches.add(Match(path))
  show_options(matches)

# Program starts here
if __name__ == "__main__": main()