#!/usr/bin/env python3
"""Create standalone RTL projects, verify library assets, or install this skill."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from rtl_flow import identifier

ROOT = Path(__file__).resolve().parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(destination):
    manifest = json.loads((ROOT / "resources/library.json").read_text())
    destination.mkdir(parents=True, exist_ok=True)
    for item in manifest["files"]:
        target = destination / Path(item["path"]).name
        if target.exists():
            if digest(target) != item["sha256"]:
                raise ValueError("Checksum mismatch; existing file preserved: " + str(target))
            print("Verified " + str(target))
            continue
        url = manifest["base_url"] + "/" + manifest["revision"] + "/flow/platforms/nangate45/" + item["path"]
        # Curl uses the OS certificate store on both supported platforms.
        with tempfile.TemporaryDirectory(prefix=".download-", dir=str(destination)) as temp:
            candidate = Path(temp) / target.name
            subprocess.run(["curl", "--fail", "--location", "--show-error", "--silent",
                            "--retry", "2", "--connect-timeout", "15", "--max-time", "180",
                            url, "--output", str(candidate)], check=True)
            if digest(candidate) != item["sha256"]:
                raise ValueError("Checksum mismatch for " + url)
            candidate.replace(target)
        print("Downloaded and verified " + str(target))


def wrapper(path, command, runtime='"${SCRIPT_DIR}/rtl_flow.py"', project='"${SCRIPT_DIR}/.."'):
    path.write_text('''#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 %s --project %s %s "$@"
''' % (runtime, project, command))
    path.chmod(0o755)


def setup(args):
    name = identifier(args.name)
    top = identifier(args.top or name)
    base = Path(args.directory).resolve()
    target = base / name
    if target.exists() or target.is_symlink():
        raise ValueError("Project already exists; refusing to overwrite: " + str(target))
    liberty = Path(args.liberty).resolve(strict=True) if args.liberty else None
    if liberty and not liberty.is_file():
        raise ValueError("Liberty must be a file")
    if not liberty:
        # Also verifies every bundled file before copying it.
        download(ROOT / "resources/lib")
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rtl-project-", dir=str(base)) as temp:
        project = Path(temp) / name
        for directory in ("rtl", "tb", "lib", "script", "synth", "dump"):
            (project / directory).mkdir(parents=True)
        if liberty:
            shutil.copy2(str(liberty), str(project / "lib" / liberty.name))
            libname = liberty.name
        else:
            for entry in json.loads((ROOT / "resources/library.json").read_text())["files"]:
                filename = Path(entry["path"]).name
                shutil.copy2(str(ROOT / "resources/lib" / filename), str(project / "lib" / filename))
            shutil.copy2(str(ROOT / "resources/NANGATE-LICENSE"), str(project / "lib/NANGATE-LICENSE"))
            libname = "NangateOpenCellLibrary_typical.lib"
        (project / "project.json").write_text(json.dumps({
            "top": top, "tb_top": top + "_tb", "liberty": "lib/" + libname
        }, indent=2) + "\n")
        for kind, suffix in (("rtl", ".v"), ("tb", "_tb.v")):
            template = (ROOT / "assets" / (kind + ".v.template")).read_text()
            (project / kind / (top + suffix)).write_text(template.replace("@TOP@", top))
            (project / "script" / (kind + ".f")).write_text("../" + kind + "/" + top + suffix + "\n")
        shutil.copy2(str(ROOT / "scripts/rtl_flow.py"), str(project / "script/rtl_flow.py"))
        for filename, command in (("run_synth.sh", "synth"), ("run_tb.sh", "tb"), ("clean.sh", "clean")):
            wrapper(project / "script" / filename, command)
        wrapper(project / "clean.sh", "clean", '"${SCRIPT_DIR}/script/rtl_flow.py"', '"${SCRIPT_DIR}"')
        (project / ".gitignore").write_text("synth/\ndump/\n.rtl-flow-outputs.json\n__pycache__/\n")
        project.rename(target)
    print("Created standalone project: " + str(target))


def install(args):
    if args.destination:
        parent = Path(args.destination).expanduser().resolve()
    else:
        home = Path.home()
        parent = {"codex": Path(os.environ.get("CODEX_HOME", str(home / ".codex"))) / "skills",
                  "claude": home / ".claude/skills",
                  "antigravity": home / ".gemini/config/skills"}[args.target]
        parent = parent.resolve()
    target = parent / "nangate45"
    if target == ROOT or ROOT in target.parents or target in ROOT.parents:
        raise ValueError("Install destination must be outside the source skill")
    if target.exists() or target.is_symlink():
        raise ValueError("Destination already exists; refusing to overwrite: " + str(target))
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".nangate45-install-", dir=str(parent)) as temp:
        staging = Path(temp) / "nangate45"
        shutil.copytree(str(ROOT), str(staging), symlinks=False,
                        ignore=shutil.ignore_patterns(".git", ".serena", ".agents", ".codex",
                                                     "__pycache__", "*.pyc", ".DS_Store",
                                                     ".rtl-flow-outputs.json", "synth", "dump"))
        staging.rename(target)
    print("Installed " + str(target))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("setup")
    create.add_argument("name")
    create.add_argument("directory", nargs="?", default=".")
    create.add_argument("--top")
    create.add_argument("--liberty", help="Copy a local Liberty file instead of Nangate45")
    fetch = sub.add_parser("download")
    fetch.add_argument("directory", nargs="?", default=str(ROOT / "resources/lib"))
    add = sub.add_parser("install")
    add.add_argument("--target", choices=("codex", "claude", "antigravity"), default="codex")
    add.add_argument("--destination", help="Custom parent skills directory")
    args = parser.parse_args()
    try:
        if args.command == "setup":
            setup(args)
        elif args.command == "download":
            download(Path(args.directory).resolve())
        else:
            install(args)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
