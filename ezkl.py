#!/usr/bin/env python
from sys import argv, stderr
from os import getenv
from typing import List
from pathlib import Path
from subprocess import Popen, PIPE


class Match:
    def __init__(self, path: str) -> None:
        self.path = path
        self.level = 0


class MatchList:
    items: List[Match]

    def __init__(self) -> None:
        self.items = []

    def add(self, match: Match) -> None:
        self.items.append(match)

    def first(self) -> Match:
        return self.items[0]

    def empty(self) -> bool:
        return len(self.items) == 0

    def sort(self, keyword: str) -> None:
        kw = keyword.lower()

        for item in self.items:
            parts = item.path.split("/")
            parts.reverse()
            level = 0

            for i, p in enumerate(parts):
                pl = p.lower()
                if pl == kw:
                    level += 10 + (len(parts) - i)
                elif kw in pl:
                    level += 5 + (len(parts) - i)

            item.level = level

        self.items.sort(key=lambda x: x.path, reverse=False)
        self.items.sort(key=lambda x: x.level, reverse=True)

    def paths(self) -> List[str]:
        return [x.path for x in self.items]


class Args:
    mode = ""
    keyword = ""
    extra: List[str] = []

    @staticmethod
    def get_args() -> None:
        args = argv[1:]
        Args.mode = args[0] if len(args) > 0 else ""

        if Args.mode == "":
            info("remember = remember path")
            info("jump arg = jump to path")
            info("forget = forget path")
            info("list = list paths")
            info("clear = forget all paths")
            info("----")
            info("Create an alias in your shell for 'cd $(ezkl jump something)'")
            exit(0)

        if Args.mode not in ["remember", "forget", "jump", "list", "clear"]:
            exit(1)

        Args.keyword = " ".join(args[1:]) if len(args) > 1 else ""
        cd_split = Args.keyword.split(" ")

        if len(cd_split) > 1:
            Args.keyword = cd_split[0]
            Args.extra = cd_split[1:]

        if Args.mode == "jump" and Args.keyword == "":
            exit(0)


class Paths:
    pwd = ""
    filepath = Path("")
    paths: List[str] = []

    @staticmethod
    def get_pwd() -> None:
        Paths.pwd = Paths.clean_path(str(getenv("PWD")))

    @staticmethod
    def get_paths() -> None:
        configdir = Path("~/.config/ezkl").expanduser()

        if not configdir.exists():
            configdir.mkdir(parents=True)

        Paths.filepath = configdir / Path("paths.txt")
        Paths.filepath.touch(exist_ok=True)

        file = open(Paths.filepath, "r")
        Paths.paths = file.read().split("\n")
        Paths.paths = list(map(str.strip, Paths.paths))
        Paths.paths = list(filter(None, Paths.paths))
        file.close()

    @staticmethod
    def filter_path(path: str) -> None:
        paths = [path]

        for p in Paths.paths:
            if p == path:
                continue

            paths.append(p)

        Paths.paths = paths

    @staticmethod
    def remember_path(path: str) -> None:
        if path in Paths.paths:
            info("Path already remembered")
        else:
            Paths.filter_path(path)
            update_file()
            info("Path remembered")

    @staticmethod
    def forget_path(path: str) -> None:
        if path not in Paths.paths:
            info("Path is not remembered")
            return

        paths: List[str] = []

        for p in Paths.paths:
            if p == path:
                continue

            paths.append(p)

        Paths.paths = paths

        update_file()
        info("Path forgotten")

    @staticmethod
    def clean_path(path: str) -> str:
        return path.rstrip("/")

    @staticmethod
    def list_paths() -> None:
        for path in Paths.paths:
            print(path)

    @staticmethod
    def clear_paths() -> None:
        try:
            ans = input("Forget all paths? (y/N): ")

            if ans == "y":
                Paths.paths = []
                update_file()
                info("Paths cleared")
        except KeyboardInterrupt:
            pass


def get_matches(keyword: str) -> MatchList:
    matches = MatchList()
    lowkeyword = keyword.lower()

    for path in Paths.paths:
        if lowkeyword in path.lower():
            matches.add(Match(path))

    matches.sort(keyword)
    return matches


def update_file() -> None:
    file = open(Paths.filepath, "w")
    file.write("\n".join(Paths.paths).strip())
    file.close()


def select_match(matches: MatchList) -> None:
    cmd = 'rofi -dmenu -markup-rows -p "Select Match (Alt+1 Forget)"'
    proc = Popen(cmd, stdout=PIPE, stdin=PIPE, shell=True, text=True)
    ans = proc.communicate("\n".join(matches.paths()))[0].strip()

    if ans != "":
        code = proc.returncode
        if code == 10:
            Paths.forget_path(ans)
            return
        else:
            print(ans)


def jump() -> None:
    if len(Paths.paths) == 0:
        info("No paths remembered yet")
        exit(1)

    matches = get_matches(Args.keyword)

    if not matches.empty():
        if len(matches.items) > 1:
            select_match(matches)
        else:
            path = matches.first().path

            if Args.extra:
                for dir in Args.extra:
                    for p in Path(path).iterdir():
                        if p.is_dir() and p.name.startswith(dir):
                            path += "/" + p.name
                            break

            print(path)
    else:
        info("No path found")


def info(msg: str, title: str = "ezkl") -> None:
    print(f"{title}: {msg}", file=stderr)


def main() -> None:
    Paths.get_pwd()
    Args.get_args()
    Paths.get_paths()

    if Args.mode == "remember":
        Paths.remember_path(Paths.pwd)

    elif Args.mode == "forget":
        Paths.forget_path(Args.keyword or Paths.pwd)

    elif Args.mode == "list":
        Paths.list_paths()

    elif Args.mode == "clear":
        Paths.clear_paths()

    elif Args.mode == "jump":
        jump()


if __name__ == "__main__":
    main()
