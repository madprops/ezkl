# Imports
import re
import curses
from sys import argv
from os import getenv
from typing import List, Match
from pathlib import Path

# Code to return
return_code = 0

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

  # Stop the curses screen
  def stop(self) -> None:
    curses.endwin()

  # Print a higlighted option
  def print_reverse(self, y: int, path: str) -> None:
    self.screen.addstr(y, 2, path, curses.A_REVERSE)

  # Print a normal option
  def print_normal(self, y: int, path: str) -> None:
    self.screen.addstr(y, 2, path, curses.A_NORMAL)

  # Print the options again
  # Highlight the current one
  def refresh(self) -> None:
    self.screen.clear()

    for i, path in enumerate(self.options):
      try:
        if i == self.pos:
          self.print_reverse(i + 1, path)
        else:
          self.print_normal(i + 1, path)
      except:
        self.options = self.options[0:i]
        return

  # Key detection loop
  def key_listener(self) -> None:
    try:
      while True:
        char = self.screen.getch()
        if char in [ord('q'), ord('Q'), 27]:
          self.stop()
          break
        elif char == ord('D'):
          forget_path(self.options[self.pos], True)
          update_file()
          self.remove_option()
          if len(self.options) == 0:
            self.stop()
            break
          if self.pos >= len(self.options):
            self.on_up()

        elif char in [curses.KEY_UP, curses.KEY_BACKSPACE, ord('k')]:
          self.on_up()
        elif char in [curses.KEY_DOWN, ord(' '), ord('j')]:
          self.on_down()
        elif char == 10:
          self.stop()
          self.on_enter()
          break
    except:
      self.stop()

  # Index of the last option
  def last(self) -> int:
    return len(self.options) - 1

  # Up arrow
  def on_up(self) -> None:
    self.pos -= 1
    if self.pos < 0:
      self.pos = self.last()
    self.refresh()

  # Down arrow
  def on_down(self) -> None:
    self.pos += 1
    if self.pos > self.last():
      self.pos = 0
    self.refresh()

  # When an option gets selected
  def on_enter(self) -> None:
    global return_code
    update_paths(self.options[self.pos])
    return_code = 33
  
  # When an option is set to be removed
  def remove_option(self) -> None:
    new_options = []
    for option in self.options:
      if option != self.options[self.pos]:
        new_options.append(option)
    self.options = new_options
    self.refresh()

# Settings
max_paths: int = 500
max_matches: int = 10

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

  if mode == "remember":
    filter_path(pwd)
    update_file()
    info("Path remembered")

  elif mode == "forget":
    if keyw != "":
      forget_path(keyw, True)
    else:
      forget_path(pwd, True)
    update_file()
    info("Path forgotten")
  
  elif mode == "clearpaths":
    ans = input("Are you sure? (y/n): ")
    if ans == "y":
      clear_paths()

  elif mode == "jump":
    jump()
  
  exit(return_code)

# Get arguments. Might exit here
def get_args() -> None:
  global mode
  global keyw

  args = argv[1:]
  mode = args[0] if len(args) > 0 else ""

  if mode not in ["remember", "forget", "jump", "clearpaths"]:
    exit(1)

  keyw = " ".join(args[1:]) if len(args) > 1 else ""

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

# Get the parts of a path
def get_parts(path: str) -> List[str]:
  return list(filter(lambda x: x != "", path.split("/")))

def check_syms(list_1: MatchList, list_2: MatchList) -> None:
  for p in list_1.items:
    if p not in list_2.items:
      continue
    px = Path(p)
    res = px.resolve()
    for pp in list_2.items:
      ppx = Path(pp)
      if px == ppx:
        continue
      if ppx == res:
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
  lines: List[str] = paths[0:max_paths]
  file = open(filepath, "w")
  file.write("\n".join(lines).strip())
  file.close()

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# Save the paths file
def update_paths(path: str) -> None:
  if paths[0] != path:
    filter_path(path)
    update_file()
  if is_pwd(path):
    info("Already at path")

def clear_paths() -> None:
  global paths
  paths = []
  update_file()
  info("Paths cleared")

# Check if path is the current directory
def is_pwd(path: str) -> bool:
  return Path(path) == Path(pwd)

# Main jump function
def jump() -> None:
  global return_code

  if len(paths) == 0:
    info("No paths remembered yet")
    exit(1)

  keywords = list(filter(lambda x: x != "", \
    re.split("\\s|/", keyw)))

  if len(keywords) == 0:
    Prompt(paths[0:max_matches]).start()
  else:
    matches = get_matches(keywords)
    if not matches.empty():
      if matches.len() > 1:
        Prompt(matches.slice(max_matches)).start()
      else:
        path = matches.first()
        update_paths(path)
        return_code = 33
    else:
      info("No paths found")

# Show a message
def info(msg: str) -> None:
  print(f"ezkl: {msg}")

# Check if path is valid
def is_valid_path(path: str, keywords: List[str], mode: int) -> bool:
  lowkeywords = map(lambda x: x.lower(), keywords)

  if mode == 1:
    # Mode for startswith
    rstr = "/" + ".*/".join(lowkeywords) + ".*"

  elif mode == 2:
    # Mode for x in y
    rstr = "/.*" + ".*/.*".join(lowkeywords) + ".*"

  else:
    return False

  return bool(re.search(rstr, path.lower()))

# Program starts here
if __name__ == "__main__": main()