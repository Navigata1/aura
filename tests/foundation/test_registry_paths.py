"""Registry provenance has one portable representation on every host."""
import importlib.util
import json
from pathlib import Path, PureWindowsPath
import unittest


ROOT = Path(__file__).resolve().parents[2]


class WindowsInput(PureWindowsPath):
    """Filesystem-boundary stand-in: Windows names with the real input bytes."""

    def read_bytes(self):
        return (ROOT / self.relative_to(PureWindowsPath('C:/studio')).as_posix()).read_bytes()


class RegistryPathsTest(unittest.TestCase):
    def test_windows_generation_keeps_portable_provenance(self):
        spec = importlib.util.spec_from_file_location('registry_windows_test', ROOT / 'scripts/registry/sync.py')
        registry = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(registry)
        registry.ROOT = PureWindowsPath('C:/studio')
        output = json.loads(registry.generate(
            WindowsInput('C:/studio/docs/research/evidence-register.json'),
            WindowsInput('C:/studio/scripts/registry/register_overlay.json'),
        ))
        self.assertEqual([source['path'] for source in output['generated_from']], [
            'docs/research/evidence-register.json',
            'scripts/registry/register_overlay.json',
        ])
