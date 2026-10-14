from pathlib import Path
import tempfile
import subprocess
import shutil
import unittest
from repomap.core import inventory, tree, bundle, fenced
from repomap.__main__ import main


class RepoMapTests(unittest.TestCase):
    def test_filters(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ['app.py', 'README.md', '.env', '.env.example', 'secret.key']:
                (root / name).write_text('test')
            (root / 'node_modules').mkdir()
            (root / 'node_modules' / 'x.py').write_text('test')
            self.assertEqual(inventory(root)[1], ['README.md', 'app.py'])
            self.assertEqual(inventory(root, ['*.py'])[1], ['app.py'])
            self.assertEqual(inventory(root, excludes=['*.py'])[1], ['README.md'])

    def test_limits_and_binary(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'a.txt').write_text('hello')
            (root / 'b.txt').write_text('world')
            (root / 'c.bin').write_bytes(b'\0x')
            (root / 'd.txt').write_text('x' * 30)
            result, included, skipped = bundle(root, inventory(root)[1], max_file=10, max_total=5)
            self.assertEqual(included, 1)
            self.assertEqual([s[1] for s in skipped], ['total content limit', 'binary content', 'file size limit'])
            self.assertIn('hello', result)
            self.assertNotIn('world', result)

    def test_fences_and_depth(self):
        self.assertTrue(fenced('```nested```').startswith('````\n'))
        result = tree(['src/deep/app.py', 'README.md'], 'demo', depth=1)
        self.assertIn('src/', result)
        self.assertIn('…', result)
        self.assertNotIn('app.py', result)

    def test_no_overwrite_and_no_self_inclusion(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output = root / 'context.md'
            (root / 'app.py').write_text('print(1)')
            self.assertEqual(main([folder, '--bundle', '-o', str(output)]), 0)
            original = output.read_bytes()
            self.assertNotIn('context.md', original.decode())
            self.assertEqual(main([folder, '--bundle', '-o', str(output)]), 2)
            self.assertEqual(output.read_bytes(), original)

    @unittest.skipUnless(shutil.which('git'), 'Git unavailable')
    def test_gitignore(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            root = Path(folder)
            subprocess.run(['git', 'init', folder], check=True, capture_output=True)
            (root / '.gitignore').write_text('ignored.txt\n')
            (root / 'ignored.txt').write_text('hidden')
            _, files, enabled = inventory(root)
            self.assertTrue(enabled)
            self.assertNotIn('ignored.txt', files)


if __name__ == '__main__':
    unittest.main()
