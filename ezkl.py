# Imports
import re
import curses
from sys import argv
from os import getenv
from typing import List
from typing import Optional
from pathlib import Path

# List of matches
class MatchList:
  def __init__(self, items: Optional[List[str]] = None):
    self.items = items if items is not None else []

  # Add an item
  def add(self, match: str) -> None:
    self.items.append(match)

  # Append a list of items
  def add_list(self, items: List[str]) -> None:
    self.items += items

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

  # Forget options from paths
  # and from the current options
  def forget(self) -> None:
    if self.pos < 0 or self.pos > len(self.options) - 1:
      return

    forget_path(self.options[self.pos], False)
    update_file()
    del self.options[self.pos]

    if len(self.options) == 0:
      self.stop()
      exit()

    self.pos = min(self.pos, len(self.options) - 1)
    self.refresh()

  # Key detection loop
  def key_listener(self) -> None:
    try:
      while True:
        char = self.screen.getch()
        if char in [ord('q'), 27]:
          self.stop()
          break
        elif char == ord('d'):
          self.forget()
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
    update_paths(self.options[self.pos])

# Settings
max_paths: int = 250
max_matches: int = 10

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
    if pwd != "":
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
    exit()

  if mode in ["forget"] and keyw == "":
    exit()

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

# Get the parts of a path
def get_parts(path: str) -> List[str]:
  return list(filter(lambda x: x != "", path.split("/")))

# Find matching paths
# There are 4 lists
# Roots, exact parts, startswith, and includes
def get_matches(keywords: List[str]) -> MatchList:
  roots = MatchList()
  exact = MatchList()
  starts = MatchList()
  includes = MatchList()

  for keyword in keywords:
    lowkeyword = keyword.lower()
    for path in paths:
      parts = get_parts(path)
      for i, part in enumerate(parts):
        lowpart = part.lower()
        if lowkeyword == lowpart:
          if i == len(parts) - 1:
            if not roots.has(path):
              if is_valid_path(path, keywords, 1):
                roots.add(path)
          else:
            if not exact.has(path):
              if is_valid_path(path, keywords, 1):
                exact.add(path)
        elif lowpart.startswith(lowkeyword):
          if not starts.has(path):
            if is_valid_path(path, keywords, 1):
              starts.add(path)
        elif lowkeyword in lowpart:
          if not includes.has(path):
            if is_valid_path(path, keywords, 2):
              includes.add(path)

  if roots.len() > 0:
    return roots
  elif exact.len() > 0:
    return exact
  elif starts.len() > 0:
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

# Check if path is the current directory
def is_pwd(path: str) -> bool:
  return Path(path) == Path(pwd)

# Main jump function
def jump() -> None:
  if len(paths) == 0:
    print("No paths remembered yet")
    exit()

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
    else:
      info("No paths found")

# Show a message
def info(msg: str) -> None:
  print(f"\n{msg}\n")

# Check if path is valid
def is_valid_path(path: str, keywords: List[str], mode: int) -> bool:
  lowkeywords = map(lambda x: x.lower(), keywords)

  rstr = ""

  if mode == 1:
    # Mode for startswith
    rstr = "/" + ".*/".join(lowkeywords) + ".*"
  elif mode == 2:
    # Mode for x in y
    rstr = "/.*" + ".*/.*".join(lowkeywords) + ".*"

  return bool(re.search(rstr, path.lower()))

# Program starts here
if __name__ == "__main__": main()