#!/usr/bin/env python3
"""Portable, project-local Yosys/Icarus runners (Python 3.8+, standard library)."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def identifier(value):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("Expected a simple Verilog identifier: {!r}".format(value))
    return value


def quote(value):
    value = str(value)
    if any(ord(c) < 32 for c in value):
        raise ValueError("Control characters are not supported in paths")
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def filelist(path):
    """One literal filename per line; relative to the filelist, never the cwd."""
    files = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "//")):
            continue
        if line.startswith(('"', "'")) and line[-1:] == line[:1]:
            line = line[1:-1]
        if not line or line.startswith(("-", "+")):
            raise ValueError("Filelists accept paths only, not options: " + line)
        source = (path.parent / line).resolve(strict=True)
        if not source.is_file():
            raise ValueError("Not a source file: " + str(source))
        files.append(source)
    if not files:
        raise ValueError("Empty filelist: " + str(path))
    return files


def tool(name):
    value = os.environ.get(name.upper(), name)
    executable = shutil.which(value)
    if not executable:
        raise ValueError("Missing tool: {}. Install it or set {} to its executable path."
                         .format(value, name.upper()))
    return executable


def reserve(project, paths):
    """Track exact outputs, so clean never sweeps unrelated project files."""
    manifest = project / ".rtl-flow-outputs.json"
    if manifest.is_symlink() or any(p.is_symlink() for p in paths):
        raise ValueError("Refusing to overwrite symlinked output files")
    entries = json.loads(manifest.read_text()) if manifest.exists() else []
    entries = sorted(set(entries + [str(p.relative_to(project)) for p in paths]))
    manifest.write_text(json.dumps(entries, indent=2) + "\n")


def clean(project):
    manifest = project / ".rtl-flow-outputs.json"
    if not manifest.exists():
        return
    for entry in json.loads(manifest.read_text()):
        path = project / entry
        # The manifest is input too; never allow deletion outside output directories.
        if path.parent not in (project / "synth", project / "dump"):
            raise ValueError("Invalid output manifest entry: " + entry)
        if path.parent.is_symlink():
            raise ValueError("Refusing to clean a symlinked output directory")
        if path.is_file() or path.is_symlink():
            path.unlink()
    manifest.unlink()


def run(args):
    project = Path(args.project).resolve(strict=True)
    if args.command == "clean":
        clean(project)
        return
    config = json.loads((project / "project.json").read_text())
    top = identifier(args.top or config["top"])
    script = project / "script"
    rtl = filelist(script / args.rtl_list)
    output = project / ("synth" if args.command == "synth" else "dump")
    if output.is_symlink():
        raise ValueError("Output directory must not be a symlink: " + str(output))
    output.mkdir(exist_ok=True)
    if args.command == "tb":
        tb_top = identifier(args.tb_top or config.get("tb_top", top + "_tb"))
        sources = rtl + filelist(script / args.tb_list)
        compiler, simulator = tool("iverilog"), tool("vvp")
        binary = output / (top + ".vvp")
        wave = output / (top + ".vcd")
        reserve(project, [binary, wave])
        subprocess.run([compiler, "-g2012", "-s", tb_top, "-o", str(binary)] +
                       [str(p) for p in sources], cwd=str(script), check=True)
        subprocess.run([simulator, str(binary)], cwd=str(script), check=True)
        return

    liberty = Path(args.liberty or config["liberty"])
    # CLI and config paths both resolve relative to the project root.
    liberty = (project / liberty).resolve(strict=True)
    executable = tool("yosys")
    netlist = output / (top + "_synth.v")
    report = output / (top + "_synth_report.txt")
    ys = output / ("synth_" + top + ".ys")
    reserve(project, [netlist, report, ys])
    # A failed rerun must not leave a previous successful netlist as its result.
    netlist.unlink(missing_ok=True)
    lines = ["read_verilog {}{}".format("-sv " if p.suffix == ".sv" else "", quote(p))
             for p in rtl]
    lines += ["hierarchy -check -top " + top,
              "synth -top {} -flatten -noabc".format(top),
              # Newer Yosys retains hierarchy metadata as $scopeinfo cells.
              "delete t:$scopeinfo",
              "dfflibmap -liberty " + quote(liberty),
              "abc -liberty " + quote(liberty),
              "clean", "read_liberty -lib " + quote(liberty),
              "hierarchy -check -top " + top, "check -mapped -assert",
              "stat -liberty " + quote(liberty),
              "write_verilog -noattr " + quote(netlist)]
    ys.write_text("\n".join(lines) + "\n")
    subprocess.run([executable, "-l", str(report), str(ys)], cwd=str(script), check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("synth", "tb"):
        command = commands.add_parser(name)
        command.add_argument("top", nargs="?")
        command.add_argument("--rtl-list", default="rtl.f")
        if name == "synth":
            command.add_argument("--liberty", help="Liberty path relative to project root")
        else:
            command.add_argument("--tb-top")
            command.add_argument("--tb-list", default="tb.f")
    commands.add_parser("clean")
    try:
        run(parser.parse_args())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
