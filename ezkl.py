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
    lowfilters = map(lambda x: x.lower(), filters)
    rstr = ".*" + ".*/.*".join(lowfilters) + ".*"

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

  # Get a slice of raw paths
  def slice(self, max: int) -> List[str]:
    paths: List[str] = []

    for m in self.items[0:max]:
      paths.append(m.path)

    return paths

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

# Show relevant paths to pick from
# Up/Down arrows and Enter
class Prompt:
  def __init__(self, options: List[str]) -> None:
    self.options = options
    self.pos = 0

  # Start the curses screen
  def start(self) -> None:
    self.screen = curses.initscr()
    self.screen.keypad(True)
    curses.noecho()
    curses.curs_set(0)
    self.refresh()
    self.key_listener()
    curses.endwin()

  # Print the options again
  # Underline the current one
  def refresh(self) -> None:
    self.screen.clear()

    for i, path in enumerate(self.options):
      if i == self.pos:
        self.screen.addstr(i, 0, path, curses.A_UNDERLINE)
      else:
        self.screen.addstr(i, 0, path, curses.A_NORMAL)

  # Forget options from paths
  # and from the current options
  def forget(self) -> None:
    if self.pos < 0 or self.pos > len(self.options) - 1:
      return

    forget_path(self.options[self.pos], False)
    update_file()
    del self.options[self.pos]

    if len(self.options) == 0:
      curses.endwin()
      exit(1)

    self.pos = min(self.pos, len(self.options) - 1)
    self.refresh()

  # Key detection loop
  def key_listener(self) -> None:
    try:
      while True:
        char = self.screen.getch()
        if char == ord('q'):
          break
        elif char == ord('d'):
          self.forget()
        elif char in [curses.KEY_UP, curses.KEY_BACKSPACE, ord('k')]:
          self.on_up()
        elif char in [curses.KEY_UP, ord(' '), ord('j')]:
          self.on_down()
        elif char == 10:
          self.on_enter()
          break
    except:
      curses.endwin()

  # Index of the last option
  def last(self) -> int:
    return len(self.options) - 1
  
  def on_up(self):
    self.pos -= 1
    if self.pos < 0:
      self.pos = self.last()
    self.refresh()
  
  # Down arrow
  def on_down(self):
    self.pos += 1
    if self.pos > self.last():
      self.pos = 0
    self.refresh()

  # When an option gets selected
  def on_enter(self) -> None:
    update_paths(self.options[self.pos])

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

  if mode == "remember":
    filter_path(pwd)
    update_file()

  elif mode == "forget":
    forget_path(keyw, True)
    update_file()

  elif mode == "jump":
    jump()

# Get arguments. Might exit here
def get_args() -> None:
  global mode
  global keyw

  args = argv[1:]
  mode = args[0] if len(args) > 0 else ""
  keyw = " ".join(args[1:]) if len(args) > 1 else ""

  if mode not in ["remember", "forget", "jump"]:
    exit(1)

  if mode in ["forget"] and keyw == "":
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
def filter_path(path: str) -> None:
  global paths
  pths = [path]

  for p in paths:
    if p == path:
      continue
    pths.append(p)

  paths = pths

# Remove path and subdirs
def forget_path(path: str, subpaths: bool) -> None:
  global paths
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
def update_file() -> None:
  lines: List[str] = paths[0:max_paths]
  file = open(filepath, "w")
  file.write("\n".join(lines).strip())
  file.close()

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# Parse string to number
def to_number(s: str) -> int:
  num = re.sub("[^0-9]", "", s)
  if len(num) > 0:
    return int(num)
  return 0

# Save the paths file
def update_paths(path: str) -> None:
  if Path(path) != Path(pwd):
    filter_path(path)
    update_file()
    exit(0)
  else:
    exit(1)

# Main jump function
def jump() -> None:
  keywords = list(filter(lambda x: x != "", \
    re.split("\\s|/", keyw)))

  if len(keywords) == 0:
    Prompt(paths[0:max_options]).start()
  else:
    matches = MatchList()

    for kw in keywords:
      matches.items += get_matches(kw).items

    matches.filter(keywords, max_options)

    if matches.len() > 0:
      if matches.len() > 1:
        Prompt(matches.slice(max_options)).start()
      else:
        path = matches.first().path
        update_paths(path)
    else:
      exit(1)

# Program starts here
if __name__ == "__main__": main()