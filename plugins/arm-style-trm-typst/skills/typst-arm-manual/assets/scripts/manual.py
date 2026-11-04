#!/usr/bin/env python3
"""Create, build and validate portable Typst technical manuals."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ASSETS = Path(__file__).resolve().parent.parent
PROJECT = ASSETS / 'project'
FONT_VERSION = '1.3.9'
FONT_NAMES = {f'Pretendard-{weight}.otf' for weight in (
    'Thin', 'ExtraLight', 'Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black'
)}


def create_project(destination):
    destination = destination.expanduser().resolve()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError(f'Destination must be a new or empty directory: {destination}')
    if destination == ASSETS or ASSETS in destination.parents:
        raise ValueError('Choose an output directory outside the bundled assets.')
    destination.mkdir(parents=True, exist_ok=True)
    for name in ['template', 'fonts']:
        shutil.copytree(PROJECT / name, destination / name)
    for name in ['main.typ', 'build.sh']:
        shutil.copy2(PROJECT / name, destination / name)
    print(destination)
    return 0


def build_project(project, entry, output):
    project = project.expanduser().resolve()
    if not (project / 'build.sh').is_file():
        raise ValueError(f'Project build.sh not found: {project}')
    return subprocess.run(['bash', str(project / 'build.sh'), entry, output]).returncode


def load_checks():
    # Init/build/font commands work without the optional PDF inspection dependencies.
    sys.dont_write_bytecode = True
    try:
        import _checks
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f'Missing PDF-check dependency: {exc.name}. '
            f'Install with: python3 -m pip install -r "{ASSETS / "scripts/requirements.txt"}"'
        ) from exc
    return _checks


def check_pdfs(paths):
    checks = load_checks()
    failed = False
    for path in paths:
        path = path.expanduser().resolve()
        count, errors = checks.inspect_pdf(path)
        print(f"{'FAIL' if errors else 'PASS'}: {path} ({count} links)")
        for error in errors[:20]:
            print(f'  {error}')
        failed = failed or bool(errors)
    print('GUI clicking and semantic correctness are not covered by these checks.')
    return int(failed)


def install_fonts(archive, target):
    """Validate the complete pinned font set before writing any bundled files."""
    with zipfile.ZipFile(archive) as bundle:
        fonts = [name for name in bundle.namelist()
                 if '/static/' in name and Path(name).name in FONT_NAMES]
        licenses = [name for name in bundle.namelist()
                    if Path(name).name.upper() in ('LICENSE', 'LICENSE.TXT', 'OFL.TXT')]
        if len(fonts) != len(FONT_NAMES) or {Path(name).name for name in fonts} != FONT_NAMES:
            raise ValueError('Archive must contain all nine Pretendard static OTF weights exactly once')
        if not licenses:
            raise ValueError('Font license missing from archive')
        payload = {Path(name).name: bundle.read(name) for name in fonts}
        for name, data in payload.items():
            if data[:4] != b'OTTO':
                raise ValueError(f'Invalid OpenType font: {name}')
        payload['LICENSE'] = bundle.read(licenses[0])
    target.mkdir(parents=True, exist_ok=True)
    for name, data in payload.items():
        (target / name).write_bytes(data)
    checksums = ''.join(f'{hashlib.sha256(payload[name]).hexdigest()}  ./{name}\n'
                        for name in sorted(FONT_NAMES))
    (target / 'SHA256SUMS').write_text(checksums)


def refresh_fonts(archive=None):
    target = PROJECT / 'fonts/Pretendard'
    if archive is not None:
        install_fonts(archive.expanduser().resolve(), target)
    else:
        with tempfile.TemporaryDirectory(prefix='pretendard-') as tmp:
            downloaded = Path(tmp) / 'pretendard.zip'
            url = (f'https://github.com/orioncactus/pretendard/releases/download/'
                   f'v{FONT_VERSION}/Pretendard-{FONT_VERSION}.zip')
            subprocess.run(['curl', '--fail', '--location', '--retry', '2',
                            '--connect-timeout', '15', '--max-time', '180',
                            url, '--output', str(downloaded)], check=True)
            install_fonts(downloaded, target)
    print(f'Font files, license and checksums saved: {target}')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init', help='Create a project in a new or empty directory')
    init.add_argument('destination', type=Path)
    build = commands.add_parser('build', help='Build an existing project from any working directory')
    build.add_argument('project', type=Path)
    build.add_argument('--entry', default='main.typ', help='Project-relative input file')
    build.add_argument('--output', default='build/manual.pdf', help='Project-relative output PDF')
    check = commands.add_parser('check', help='Inspect PDF structure and text bounds')
    check.add_argument('pdf', type=Path, nargs='+')
    commands.add_parser('test', help='Run isolated template regression checks')
    fonts = commands.add_parser('fonts', help=f'Refresh bundled Pretendard v{FONT_VERSION} fonts')
    fonts.add_argument('--archive', type=Path, help='Use a local official release ZIP instead of downloading')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            return create_project(args.destination)
        if args.command == 'build':
            return build_project(args.project, args.entry, args.output)
        if args.command == 'check':
            return check_pdfs(args.pdf)
        if args.command == 'test':
            return load_checks().regression()
        return refresh_fonts(args.archive)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, subprocess.CalledProcessError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
