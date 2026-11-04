"""Exercise real Git history, worktree evidence, and baseline boundaries."""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('git_changes', Path(__file__).resolve().parents[1] / 'scripts/git_changes.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class GitChangesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'TRM fixture')
        (self.root / 'src').mkdir()
        (self.root / 'src/a.txt').write_text('old contract\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'initial contract')
        self.base = self.git('rev-parse', 'HEAD').strip()

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.STDOUT).decode()

    def test_history_dirty_untracked_and_scope(self):
        self.git('mv', 'src/a.txt', 'src/renamed.txt')
        self.git('commit', '-qm', 'rename contract')
        (self.root / 'src/renamed.txt').write_text('staged contract\n')
        self.git('add', 'src')
        (self.root / 'src/renamed.txt').write_text('unstaged contract\n')
        (self.root / 'src/new.txt').write_text('new interface\n')
        (self.root / 'outside.txt').write_text('unrelated\n')
        meta, data = module.collect(self.root, self.base, scopes=['src'])
        self.assertIn(b'rename contract', data['commits.log'])
        self.assertIn(b'rename from src/a.txt', data['committed.diff'])
        self.assertIn(b'+staged contract', data['staged.diff'])
        self.assertIn(b'+unstaged contract', data['unstaged.diff'])
        self.assertEqual([x['path'] for x in meta['untracked']], ['src/new.txt'])
        self.assertNotIn(b'outside', data['status.txt'])
        self.assertFalse(meta['baseline_initialization_only'])

    def test_initial_baseline_and_empty_changes(self):
        meta, data = module.collect(self.root, scopes=['src'])
        self.assertTrue(meta['baseline_initialization_only'])
        self.assertEqual(meta['base_commit'], self.base)
        self.assertEqual(data['committed.diff'], b'')
        self.assertEqual(meta['tracked_file_count'], 1)

    def test_reject_ambiguous_date_and_outside_scope(self):
        with self.assertRaisesRegex(ValueError, 'timezone'):
            module.collect(self.root, since='2026-11-03')
        with self.assertRaisesRegex(ValueError, 'inside'):
            module.collect(self.root, self.base, scopes=['../outside'])
        with self.assertRaisesRegex(ValueError, 'No first-parent'):
            module.collect(self.root, since='1970-01-01T00:00:00+00:00')

    def test_reject_diverged_baseline(self):
        self.git('checkout', '-qb', 'other')
        (self.root / 'src/a.txt').write_text('branch contract\n')
        self.git('commit', '-qam', 'other branch')
        other = self.git('rev-parse', 'HEAD').strip()
        self.git('checkout', '-q', '--detach', self.base)
        with self.assertRaisesRegex(ValueError, 'ancestor'):
            module.collect(self.root, other)

if __name__ == '__main__':
    unittest.main()
