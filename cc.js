const os = require("os")
const fs = require("fs")
const _path = require("path")

const args = process.argv.slice(2)
const mode = args[0]
const path = args[1]
const dirpath = args[2]

const pathsfile = _path.resolve(__dirname, "paths.txt")

let paths = []
if (fs.existsSync(pathsfile)) {
  paths = fs.readFileSync(pathsfile, "utf8").trim().split("\n").filter(x => x.trim() !== "")
}

const new_paths = []

if (mode === "1") {
  let clean_path = ""

  if (path.startsWith("/") ) {
    clean_path = path
  } else if (path.startsWith("~")) {
    clean_path = path.replace("~", os.homedir())
  } else {
    clean_path = _path.resolve(dirpath, path)
  }

  clean_path = clean_path.replace(/\/$/, "")
  lines_filter(clean_path, paths)
  overwrite_paths()
} else if (mode === "2") {
  find_path(path, paths)
}

function lines_filter (filter, paths) {
  new_paths.push(filter)

  for (let path of paths) {
    if (path === filter) {
      continue
    }

    new_paths.push(path)
  }
}

function find_path (filter, paths) {
  const matches = []

  for (let path of paths) {
    if (path.includes(filter)) {
      let match = {path:path}
      let split = path.split("/")
      for (let i=0; i<split.length; i++) {
        if (split[i] === filter) {
          match.level = i
          matches.push(match)
          break
        }
      }
    }
  }

  if (matches.length) {
    matches.sort((a, b)=> {
      if (a.level === b.level){
        return a.path.length < b.path.length ? -1 : 1
      } else {
        return a.level < b.level ? -1 : 1
      }
    })
    
    lines_filter(matches[0].path, paths)
    overwrite_paths()

    // Output for cd
    console.log(matches[0].path)
  }
}

function overwrite_paths () {
  const max_lines = 500
  const content = new_paths.slice(0, max_lines).join("\n")
  fs.writeFileSync(pathsfile, content, {encoding:"utf8", flag:"w"})
} 