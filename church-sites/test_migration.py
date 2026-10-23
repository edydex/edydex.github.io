"""Offline checks for the independent Libre landing-page artifacts."""
from html.parser import HTMLParser
from pathlib import Path
import json
import subprocess
import unittest
import tempfile
from hashlib import sha256
from package_libre_show import package_site, PREPARE_FILES

ROOT = Path(__file__).parent
DOMAINS = ('libre.church', 'libre.faith', 'libre.show')


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = []
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.anchors.append(attrs.get('href'))
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))


class MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faith_before = {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in (ROOT / 'libre-faith').rglob('*') if p.is_file()}
        cls.build = subprocess.run(['python3', str(ROOT / 'build.py')], check=True, capture_output=True, text=True)

    def test_only_three_independent_static_worker_artifacts(self):
        for domain in DOMAINS:
            folder = ROOT / domain.replace('.', '-')
            config = json.loads((folder / 'wrangler.jsonc').read_text())
            self.assertEqual(set(config), {'name', 'compatibility_date', 'assets'})
            self.assertEqual(config['name'], domain.replace('.', '-'))
            self.assertEqual(config['assets'], {'directory': './package' if domain == 'libre.show' else './dist', 'not_found_handling': '404-page'})
            # No route, binding, runtime proxy, redirect or PWA can capture the
            # protected church. Cloudflare account routing still needs inspection.
            self.assertFalse((folder / 'dist' / '_redirects').exists())
            for file in (folder / 'dist').iterdir():
                self.assertNotEqual(file.suffix, '.js')
                self.assertNotIn('wotbc.heritage.faith', file.read_text())

    def test_canonicals_navigation_and_reader_continuity(self):
        for domain in DOMAINS:
            html = (ROOT / domain.replace('.', '-') / 'dist' / 'index.html').read_text()
            parsed = Links()
            parsed.feed(html)
            self.assertEqual(parsed.canonicals, [f'https://{domain}/'])
            for destination in DOMAINS:
                self.assertIn(f'https://{destination}/', parsed.anchors)
            if domain != 'libre.faith':
                self.assertIn('LibreChurch Stack', html)
            if domain == 'libre.faith':
                self.assertIn('https://heritage.faith/', parsed.anchors)
            if domain == 'libre.church':
                self.assertIn('https://github.com/edydex/heritage-community', parsed.anchors)
            if domain == 'libre.show':
                self.assertIn('/prepare/', parsed.anchors)
                self.assertIn('https://github.com/edydex/SyncShow/releases/latest', parsed.anchors)
                self.assertIn('preview', html.lower())

    def test_build_leaves_paused_faith_artifacts_unchanged(self):
        after = {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in (ROOT / 'libre-faith').rglob('*') if p.is_file()}
        self.assertEqual(after, self.faith_before)
        self.assertNotIn('libre.faith', self.build.stdout)
        self.assertIn('libre.church', self.build.stdout)
        self.assertIn('libre.show', self.build.stdout)
        refused = subprocess.run(['python3', str(ROOT / 'build.py'), '--site', 'libre-faith'], capture_output=True)
        self.assertNotEqual(refused.returncode, 0)

    def test_package_includes_editor_and_one_local_only_policy(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'editor'
            source.mkdir()
            for name in PREPARE_FILES:
                (source / name).write_text('synthetic packaging fixture')
            (source / 'source.json').write_text(json.dumps({'kind': 'local-browser-preparation', 'sources': {'packages/service-core/index.js': 'a' * 64}}))
            (source / '_headers').write_text("/*\n  Content-Security-Policy: connect-src 'none'; img-src 'self' blob:; form-action 'none'\n")
            output = package_site(source, root / 'package')
            self.assertTrue((output / 'prepare' / 'index.html').is_file())
            self.assertFalse((output / 'prepare' / '_headers').exists())
            self.assertIn("connect-src 'none'", (output / '_headers').read_text())
            receipt = json.loads((output / 'build-receipt.json').read_text())
            self.assertEqual(receipt['hostname'], 'libre.show')
            package_site(source, output)
            (output / 'user-file.libreshow').write_text('preserve')
            with self.assertRaisesRegex(ValueError, 'unknown files'):
                package_site(source, output)
            self.assertEqual((output / 'user-file.libreshow').read_text(), 'preserve')

    def test_package_refuses_unrecognized_source_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'editor'
            source.mkdir()
            (source / '.env').write_text('must never be packaged')
            with self.assertRaisesRegex(ValueError, 'Unexpected or missing'):
                package_site(source, Path(temporary) / 'package')


if __name__ == '__main__':
    unittest.main()
