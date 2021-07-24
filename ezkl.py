# Imports
import re
from sys import argv
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

  @staticmethod
  def filter(matches: "List[Match]", filters: List[str]) -> "List[Match]":
    matches2: List[Match] = []
    rstr = ".*" + ".*/".join(filters) + ".*"

    matches.sort(key=lambda x: (-x.acc, x.level()))
    for m in matches:
      add = True
      for m2 in matches2:
        if m.path == m2.path:
          add = False
          break

      if not re.search(rstr, m.path.lower()):
        add = False

      if add:
        matches2.append(m)
    return matches2

  @staticmethod
  def sort(matches: "List[Match]") -> "List[Match]":
    matches.sort(key=lambda x: (-x.acc, x.level()))
    return matches

# Settings
min_accuracy: float = 0.66
max_paths: int = 250
max_hints: int = 3

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
    path = ""
    matches: List[Match] = []

    if keyw.startswith("/"):
      path = clean_path(keyw.replace(" ", ""))

    else:
      kw = keyw.split(" ")

      for w in kw:
        matches += get_matches(w) \
          + get_guesses(w)

      matches = Match.sort(Match.filter(matches, kw))

      for m in matches:
        if m.path != pwd:
          path = m.path
          break

    show_hints(matches, path)

    if len(path) > 0:
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
def get_matches(filter: str) -> List[Match]:
  matches: List[Match] = []

  def add_match(path: str, acc: float) -> None:
    for match in matches:
      if match.path == path:
        return
    match: Match = Match(path, acc)
    matches.append(match)

  checkslash = "/" in filter
  lowfilter = filter.lower()

  for path in paths:
    lowpath = path.lower()
    if checkslash and lowfilter in lowpath:
      add_match(path, 0.99)
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
def get_guesses(p: str) -> List[Match]:
  guesses: list[Match] = []
  pths = [p, p.capitalize(), p.lower(), p.upper(), f".{p}"]

  for s in pths:
    dir = Path(pwd) / Path(s)
    if dir.is_dir():
      guesses.append(Match(str(dir), 0.9))

  if not at_home():
    for s in pths:
      dir = Path.home() / Path(s)
      if dir.is_dir():
        guesses.append(Match(str(dir), 0.9))

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

# Print a path hint
def path_hint(path: str) -> None:
  CRED = "\033[92m"
  CEND = "\033[0m"
  print(f"{CRED}[Hint]{CEND} {path}")

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
Use 'z --paths' to print saved paths
---------------------------------------------
Minimum accuracy is set to {min_accuracy}
paths.txt has {len(paths)}/{max_paths} paths saved\n"""
  print(info)

# Print all paths
def show_paths(filter: str) -> None:
  hasfilter = filter != ""
  lowfilter = filter.lower()

  for path in paths:
    if hasfilter:
      if lowfilter not in path.lower():
        continue
    print(path)

# Show path hints
def show_hints(matches: List[Match], path: str) -> None:
  if len(matches) == 0:
    return
  n = 0
  hinted = False
  p = path if len(path) > 0 else pwd
  for m in matches:
    if m.path != p:
      if p.startswith(f"{m.path}/") \
        or m.path.startswith(f"{p}/"):
          break
      if not hinted:
        print(" ")
        hinted = True
      path_hint(m.path)
      n += 1
      if n == max_hints:
        break
  if hinted:
    print(" ")

# Program starts here
if __name__ == "__main__": main()