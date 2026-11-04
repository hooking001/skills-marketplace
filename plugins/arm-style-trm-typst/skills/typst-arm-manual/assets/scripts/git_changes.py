#!/usr/bin/env python3
"""Collect read-only Git evidence for the five-reviewer TRM workflow."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode('utf-8', 'replace').strip())
    return result.stdout


def collect(repo, base=None, since=None, scopes=()):
    root = Path(git(repo, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    paths = []
    for scope in scopes:
        path = (root / scope).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f'Scope must be inside the repository: {scope}')
        paths.append(path.relative_to(root).as_posix())
    # literal pathspecs avoid interpreting file names as Git pathspec magic.
    selected = [f':(literal){p}' for p in paths if p != '.']
    if since:
        stamp = dt.datetime.fromisoformat(since.replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError('--since requires a timezone, for example +09:00')
        base = git(root, 'rev-list', '-1', '--first-parent', f'--before={stamp.isoformat()}', head).decode().strip()
        if not base:
            raise ValueError('No first-parent commit exists at/before the supplied date')
    initial = base is None
    base = git(root, 'rev-parse', '--verify', f'{base or head}^{{commit}}').decode().strip()
    ancestor = subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', base, head], capture_output=True)
    if ancestor.returncode != 0:
        raise ValueError('Baseline must be an ancestor of HEAD; resolve the baseline explicitly')
    common = ['--no-ext-diff', '--no-textconv', '--find-renames']
    files = {
        'commits.log': git(root, 'log', '--format=fuller', '--date=iso-strict', '--name-status', f'{base}..{head}', '--', *selected),
        'committed.diff': git(root, 'diff', *common, base, head, '--', *selected),
        'staged.diff': git(root, 'diff', *common, '--cached', '--', *selected),
        'unstaged.diff': git(root, 'diff', *common, '--', *selected),
        'status.txt': git(root, 'status', '--short', '--untracked-files=all', '--', *selected),
        'ignored.txt': git(root, 'ls-files', '--others', '--ignored', '--exclude-standard', '--', *selected),
    }
    untracked = git(root, 'ls-files', '--others', '--exclude-standard', '-z', '--', *selected)
    inventory = []
    for raw in untracked.split(b'\0'):
        if not raw:
            continue
        name = raw.decode('utf-8', 'surrogateescape')
        path = root / name
        record = {'path': name, 'symlink': path.is_symlink()}
        if path.is_symlink():
            import os
            data = os.readlink(path).encode('utf-8', 'surrogateescape')
        else:
            data = path.read_bytes()
        record.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        inventory.append(record)
    tracked = git(root, 'ls-files', '-z', '--', *selected).count(b'\0')
    metadata = {
        'schema_version': 1, 'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'repo_root': str(root), 'head': head, 'base_commit': base,
        'requested_since': since, 'baseline_initialization_only': initial,
        'scopes': paths or ['.'], 'tracked_file_count': tracked,
        'untracked': inventory,
        'evidence_sha256': {k: hashlib.sha256(v).hexdigest() for k, v in files.items()},
        'limitations': ['Ignored file contents and submodule internal histories are not captured.',
                       'Untracked files are inventoried, not historical additions; inspect their contents separately.'],
    }
    # Detect concurrent HEAD/worktree changes instead of silently mixing evidence.
    if git(root, 'rev-parse', 'HEAD').decode().strip() != head:
        raise ValueError('HEAD changed during collection; run again')
    for name, args in [('staged.diff', ['--cached']), ('unstaged.diff', [])]:
        if git(root, 'diff', *common, *args, '--', *selected) != files[name]:
            raise ValueError('Working tree changed during collection; run again')
    return metadata, files


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    baseline = p.add_mutually_exclusive_group()
    baseline.add_argument('--base')
    baseline.add_argument('--since')
    p.add_argument('--scope', action='append', default=[])
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    try:
        # Preserve previous runs and avoid overwriting evidence used for review.
        if args.output.exists() and any(args.output.iterdir()):
            raise ValueError('Output must be a new or empty directory')
        metadata, files = collect(args.repo, args.base, args.since, args.scope)
        args.output.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            (args.output / name).write_bytes(data)
        (args.output / 'change-set.json').write_text(json.dumps(metadata, ensure_ascii=True, indent=2) + '\n')
        print(json.dumps({'base': metadata['base_commit'], 'head': metadata['head'],
                          'initialization_only': metadata['baseline_initialization_only'],
                          'tracked_files': metadata['tracked_file_count'], 'output': str(args.output)}))
        return 0
    except (ValueError, OSError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
