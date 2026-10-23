"""Package the LibreShow landing and an already-built local editor; never deploy."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).parent
LANDING_FILES = {'index.html', '404.html', 'style.css', '_headers', 'robots.txt', 'sitemap.xml',
                 'libre-show.svg', 'libre-faith.svg', 'libre-church.svg'}
PREPARE_FILES = {'index.html', 'style.css', 'app.js', 'editor-model.js', 'recovery.js',
                 'workspace-controls.js', 'workspace-recovery.js', '_headers',
                 'service-core.js', 'portable.js', 'LICENSE.txt', 'source.json'}
RECEIPT = 'build-receipt.json'


def checked_files(directory, expected):
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('Use a real static artifact directory, not a symlink.')
    actual = set()
    for item in directory.iterdir():
        if item.is_symlink() or not item.is_file():
            raise ValueError('Static artifacts must contain only ordinary files.')
        actual.add(item.name)
    if actual != expected:
        raise ValueError(f'Unexpected or missing artifact files: {sorted(actual ^ expected)}')
    if sum((directory / name).stat().st_size for name in expected) > 5 * 1024 * 1024:
        raise ValueError('Static artifact exceeds the packaging size bound.')


def package_site(prepare_dir, output=None):
    prepare_dir = Path(prepare_dir)
    landing = ROOT / 'libre-show' / 'dist'
    checked_files(prepare_dir, PREPARE_FILES)
    checked_files(landing, LANDING_FILES)
    source = json.loads((prepare_dir / 'source.json').read_text())
    if source.get('kind') != 'local-browser-preparation' or not source.get('sources'):
        raise ValueError('Expected the verified SyncShow browser build receipt.')
    for name, digest in source['sources'].items():
        if not isinstance(name, str) or name.startswith('/') or '..' in name.split('/') or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('Browser source receipt contains an invalid path or checksum.')
    headers = (prepare_dir / '_headers').read_text()
    if "connect-src 'none'" not in headers or "img-src 'self' blob:" not in headers or "form-action 'none'" not in headers:
        raise ValueError('The local-only browser policy is required.')
    if "'unsafe-eval'" in headers or "'unsafe-inline'" in headers:
        raise ValueError('Executable inline/eval permissions are not part of this package.')
    target = Path(output) if output else ROOT / 'libre-show' / 'package'
    if target.is_symlink():
        raise ValueError('Package output must not be a symlink.')
    target = target.resolve()
    for source_dir in [prepare_dir.resolve(), landing.resolve()]:
        if target == source_dir or target in source_dir.parents or source_dir in target.parents:
            raise ValueError('Package output must be separate from its source artifacts.')
    expected = LANDING_FILES | {f'prepare/{name}' for name in PREPARE_FILES - {'_headers'}} | {RECEIPT}
    if target.exists():
        if not (target / RECEIPT).is_file():
            raise ValueError('Existing output has no package marker; it was left untouched.')
        marker = json.loads((target / RECEIPT).read_text())
        if marker.get('kind') != 'libre-show-static-package':
            raise ValueError('Existing output is not a LibreShow package; it was left untouched.')
        for file in target.rglob('*'):
            if file.is_symlink() or (file.is_file() and file.relative_to(target).as_posix() not in expected):
                raise ValueError('Existing output contains unknown files; it was left untouched.')
    target.mkdir(parents=True, exist_ok=True)
    (target / 'prepare').mkdir(exist_ok=True)
    for name in LANDING_FILES:
        shutil.copyfile(landing / name, target / name)
    for name in PREPARE_FILES - {'_headers'}:
        shutil.copyfile(prepare_dir / name, target / 'prepare' / name)
    # Cloudflare reads the root _headers file. One policy covers landing and
    # editor, avoiding intersecting policies that accidentally deny Blob images.
    (target / '_headers').write_text(headers)
    files = {name: sha256((target / name).read_bytes()).hexdigest() for name in sorted(expected - {RECEIPT})}
    receipt = {'schemaVersion': 1, 'kind': 'libre-show-static-package', 'hostname': 'libre.show',
               'preparePath': '/prepare/', 'downloadUrl': 'https://github.com/edydex/SyncShow/releases/latest',
               'files': files, 'editorSources': source['sources']}
    (target / RECEIPT).write_text(json.dumps(receipt, indent=2) + '\n')
    return target


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-dir', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        print(package_site(args.prepare_dir, args.output))
    except (ValueError, OSError) as error:
        parser.exit(1, f'Package stopped: {error}\n')
