#!/usr/bin/env python3
"""Select processed Serena symbol caches and export human-readable CSV files.

python document_symbols_load.py
python document_symbols_load.py cpp/document_symbols.pkl --match abs3_dispatcher --full
python document_symbols_load.py python/document_symbols.pkl --output /tmp/symbols.csv
"""
import argparse
import curses
import csv
import json
import os
from pathlib import Path
import pickle
import shutil
import sys


def load_cache(path):
    try:
        with path.open("rb") as stream:
            return pickle.load(stream)
    except ModuleNotFoundError as error:
        # Serena pickles may contain solidlsp classes. Use the installed CLI's
        # interpreter without installing packages or substituting fake classes.
        if error.name and error.name.split(".")[0] in {"solidlsp", "serena"}:
            command = shutil.which("serena")
            if command and not os.environ.get("SERENA_CACHE_LOAD_REEXEC"):
                first_line = Path(command).resolve().read_text().splitlines()[0]
                interpreter = first_line[2:].strip() if first_line.startswith("#!") else ""
                if interpreter and Path(interpreter).is_file():
                    environment = dict(os.environ, SERENA_CACHE_LOAD_REEXEC="1",
                                       SERENA_CACHE_LOAD_SELECTED=str(path))
                    os.execve(interpreter, [interpreter, str(Path(__file__).resolve()), *sys.argv[1:]], environment)
        raise RuntimeError(
            f"{error}. Run this loader with the Python environment that provides Serena."
        ) from error


def json_data(value, seen=None, location="$"):
    """Keep shared/cyclic symbol objects readable using $ref path markers."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if seen is None:
        seen = {}
    identity = id(value)
    if identity in seen:
        return {"$ref": seen[identity]}
    seen[identity] = location
    if isinstance(value, dict):
        return {str(k): json_data(v, seen, f"{location}[{k!r}]") for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_data(v, seen, f"{location}[{i}]") for i, v in enumerate(value)]
    if hasattr(value, "__dict__"):
        return {
            "__type__": f"{type(value).__module__}.{type(value).__qualname__}",
            **{k: json_data(v, seen, f"{location}[{k!r}]") for k, v in vars(value).items()},
        }
    raise TypeError(f"Unsupported cache value: {type(value).__name__}")


CSV_FIELDS = ("source_file", "symbol_path", "name", "kind",
              "parent", "depth", "start_line", "start_column", "end_line", "end_column", "detail")
SYMBOL_KINDS = dict(enumerate(("File", "Module", "Namespace", "Package", "Class", "Method",
    "Property", "Field", "Constructor", "Enum", "Interface", "Function", "Variable", "Constant",
    "String", "Number", "Boolean", "Array", "Object", "Key", "Null", "EnumMember", "Struct",
    "Event", "Operator", "TypeParameter"), 1))


def csv_rows(obj):
    """Flatten only child edges; parent/back references never enter the CSV."""
    if not isinstance(obj, dict) or not isinstance(obj.get("obj"), dict):
        raise ValueError("CSV export requires Serena's obj mapping")
    for source, entry in sorted(obj["obj"].items()):
        _, document = entry
        roots = document.root_symbols if hasattr(document, "root_symbols") else document
        if not isinstance(roots, (list, tuple)):
            raise ValueError(f"Unsupported symbol list for {source}")
        common = {"source_file": source}
        seen = set()

        def walk(symbols, parent="", depth=0):
            for symbol in symbols:
                if id(symbol) in seen:
                    continue
                seen.add(id(symbol))
                name = symbol.get("name", "")
                symbol_path = f"{parent}/{name}" if parent else name
                span = symbol.get("range") or symbol.get("location", {}).get("range", {})
                start, end = span.get("start", {}), span.get("end", {})
                def position(point, key):
                    return point[key] + 1 if key in point else ""
                kind = symbol.get("kind", "")
                yield {**common, "symbol_path": symbol_path, "name": name,
                       "kind": SYMBOL_KINDS.get(kind, kind), "parent": parent, "depth": depth,
                       "start_line": position(start, "line"), "start_column": position(start, "character"),
                       "end_line": position(end, "line"), "end_column": position(end, "character"),
                       "detail": " ".join(str(symbol.get("detail", "")).split())}
                yield from walk(symbol.get("children") or [], symbol_path, depth + 1)
        if roots:
            yield from walk(roots)
        else:
            # Retain files whose backend returned no symbols.
            yield common


def save_export(obj, cache_path, output):
    output = output.resolve()
    if output == cache_path or output == Path(__file__).resolve():
        raise ValueError("Output must differ from the cache and loader")
    if output.suffix.lower() == ".csv":
        with output.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
            writer.writeheader()
            count = 0
            for row in csv_rows(obj):
                writer.writerow(row)
                count += 1
        print(f"Saved CSV: {output} ({count} rows; line/column positions are 1-based, end exclusive)")
    elif output.suffix.lower() == ".json":
        with output.open("w", encoding="utf-8") as stream:
            json.dump(json_data(obj), stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(f"Saved JSON: {output}")
    else:
        raise ValueError("Output filename must end in .csv or .json")


def select_cache(directory):
    paths = sorted(directory.rglob("document_symbols.pkl"))
    if not paths:
        raise ValueError(f"No processed document_symbols.pkl caches below {directory}")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise ValueError("Interactive selection needs a terminal; pass a .pkl path explicitly")

    def menu(screen):
        screen.keypad(True)
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        selected = 0
        while True:
            screen.erase()
            height, width = screen.getmaxyx()
            rows = max(1, height - 4)
            start = max(0, min(selected - rows + 1, len(paths) - rows))
            lines = ["Select cache: Up/Down wraps | Enter saves CSV | q cancels", str(directory), ""]
            for index in range(start, min(len(paths), start + rows)):
                marker = "> " if index == selected else "  "
                lines.append(marker + str(paths[index].relative_to(directory)))
            for row, line in enumerate(lines[:max(0, height - 1)]):
                try:
                    screen.addnstr(row, 0, line, max(0, width - 1),
                                   curses.A_REVERSE if row >= 3 and start + row - 3 == selected else 0)
                except curses.error:
                    pass
            screen.refresh()
            key = screen.getch()
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(paths)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(paths)
            elif key in (10, 13, curses.KEY_ENTER):
                return paths[selected]
            elif key in (ord("q"), 27):
                return None
    return curses.wrapper(menu)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", type=Path, help="Open a processed document_symbols.pkl without the selection menu")
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parent,
                        help="Search below this directory (default: loader directory)")
    parser.add_argument("--summary", action="store_true", help="Show only the cache summary")
    parser.add_argument("--match", default="", help="Keep cached file paths containing this text")
    parser.add_argument("--full", action="store_true", help="Print full data as readable JSON")
    parser.add_argument("--output", type=Path, help="Save CSV (.csv) or full JSON (.json); default: CSV beside this loader")
    args = parser.parse_args()
    path = None
    try:
        saved = os.environ.get("SERENA_CACHE_LOAD_SELECTED")
        path = args.file or (Path(saved) if saved else select_cache(args.directory.resolve()))
        if path is None:
            return
        path = path.resolve()
        if path.name != "document_symbols.pkl":
            raise ValueError("Select document_symbols.pkl; raw/internal caches are not for CSV inspection")
        obj = load_cache(path)
        if args.match:
            if not isinstance(obj, dict) or not isinstance(obj.get("obj"), dict):
                raise ValueError("--match requires Serena's obj mapping")
            obj = {**obj, "obj": {k: v for k, v in obj["obj"].items() if args.match in k}}
        if args.output or (not args.summary and not args.full):
            output = args.output or Path(__file__).resolve().parent / f"{path.parent.name}_{path.stem}.csv"
            save_export(obj, path, output)
        elif args.full:
            print(json.dumps(json_data(obj), ensure_ascii=False, indent=2))
        else:
            print(f"Cache: {path}")
            print(f"Type: {type(obj).__name__}")
            if isinstance(obj, dict):
                print(f"Version: {obj.get('__cache_version')}")
                entries = obj.get("obj", {})
                if isinstance(entries, dict):
                    print(f"Files: {len(entries)}")
                    for name in list(entries)[:10]:
                        print(f"  {name}")
                    if len(entries) > 10:
                        print(f"  ... {len(entries) - 10} more")
                else:
                    print(f"Keys: {list(obj)[:10]}")
            print("Use --match TEXT, --output FILE.csv, or --full for JSON.")
    except KeyboardInterrupt:
        return
    except (OSError, ValueError, TypeError, RuntimeError, curses.error, pickle.UnpicklingError, EOFError) as error:
        parser.exit(1, f"Cannot inspect {path}: {error}\n")


if __name__ == "__main__":
    main()
