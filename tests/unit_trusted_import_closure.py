"""Nonprivileged flattened-layout and no-search dependency regressions."""
import ast
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
from common import Failure
from trusted_install import absolute_dependencies, immutable


class ImportClosure(unittest.TestCase):
    def test_real_flattened_imports_ignore_poisoned_neighbors(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            code = base / 'runtime' / 'code'
            code.mkdir(parents=True)
            for source in (ROOT / 'research').glob('*.py'):
                shutil.copyfile(source, code / source.name)
            for source in ('tests/unit_trusted_observation.py',
                           'tests/integration/trusted_observation.py'):
                shutil.copyfile(ROOT / source, code / Path(source).name)
            # Both old parents[2] and mixin parents[1] escape locations.
            for parent in (base, code.parent):
                for name in ('research', 'tests'):
                    poison = parent / name
                    poison.mkdir()
                    for module in ('common', 'budget', 'trusted_evaluation',
                                   'unit_trusted_observation'):
                        (poison / (module + '.py')).write_text(
                            'raise RuntimeError("POISON LOADED")\n')
            program = (
                'import sys,runpy,pathlib\n'
                'root=pathlib.Path(sys.argv[1])\n'
                'sys.path.insert(0,str(root))\n'
                'before=list(sys.path)\n'
                'runpy.run_path(str(root/"trusted_observation.py"),run_name="layout_review")\n'
                'assert sys.path==before\n'
                'for name in ("common","budget","trusted_evaluation","unit_trusted_observation"):\n'
                ' assert pathlib.Path(sys.modules[name].__file__).parent==root\n'
                'print("verified snapshot imports only")\n')
            result = subprocess.run([sys.executable, '-I', '-S', '-B', '-c',
                                     program, str(code)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('verified snapshot imports only', result.stdout)

    def test_staged_application_modules_do_not_modify_import_path(self):
        sources = list((ROOT / 'research').glob('*.py')) + [
            ROOT / 'tests/unit_trusted_observation.py',
            ROOT / 'tests/integration/trusted_observation.py',
            ROOT / 'tests/integration/trusted_probe.py',
            ROOT / 'tests/launch_lock_probe.py']
        for source in sources:
            if source.name == 'isolated_entry.py':
                continue  # Sole authenticated import-root authority.
            tree = ast.parse(source.read_text())
            self.assertFalse(any(isinstance(node, ast.Attribute) and
                isinstance(node.value, ast.Name) and node.value.id == 'sys' and
                node.attr == 'path' for node in ast.walk(tree)), source)


class AbsoluteClosure(unittest.TestCase):
    def test_absolute_complete_closure(self):
        root = Path('/Library/GRRR/qemu-reviewed')
        absolute_dependencies(root, [str(root / 'lib/libx.dylib'), '/usr/lib/libSystem.B.dylib'],
                              [], {'lib/libx.dylib'})

    def test_shadow_writable_symlink_and_ambiguous_search_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            early, late = root / 'early', root / 'late'
            early.mkdir()
            late.mkdir()
            (early / 'libx.dylib').write_bytes(b'shadow')
            (late / 'libx.dylib').write_bytes(b'reviewed')
            link = root / 'linked'
            link.symlink_to(late, target_is_directory=True)
            for paths in ([str(early), str(late)], [str(early)],
                          [str(link)], [str(late), str(late)]):
                with self.subTest(paths=paths), self.assertRaises(Failure):
                    absolute_dependencies(root, ['@rpath/libx.dylib'], paths,
                                          {'late/libx.dylib'})
            with self.assertRaises(Failure):
                immutable(link / 'libx.dylib')

    def test_tokens_and_noncanonical_absolute_names_rejected(self):
        root = Path('/Library/GRRR/qemu-reviewed')
        for name in ('@rpath/libx', '@loader_path/libx', '@executable_path/libx',
                     str(root) + '/lib/../libx', str(root) + '//libx',
                     '/opt/homebrew/lib/libx'):
            with self.subTest(name=name), self.assertRaises(Failure):
                absolute_dependencies(root, [name], [], {'libx'})
