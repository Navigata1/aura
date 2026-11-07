"""The CLI is the public seam; copied packages emulate adding a command."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]

class CliTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        source = ROOT / 'services/control/studio_control'
        if source.exists():
            shutil.copytree(source, self.root / 'studio_control')
        (self.root / 'contracts').mkdir()
        (self.root / 'contracts/product.json').write_text(json.dumps({'productName': 'Renamed Studio'}))
        self.env = {**os.environ, 'PYTHONPATH': str(self.root)}

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'studio_control.cli', *args], env=self.env, cwd=self.root, text=True, capture_output=True)

    def test_version_reads_single_product_constant(self):
        result = self.cli('--version')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'Renamed Studio 0.1.0')

    def test_command_is_discovered_by_file(self):
        p = self.root / 'studio_control/cli/commands/probe.py'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('def register(parser):\n    parser.set_defaults(run=lambda args: print("command discovered"))\n')
        result = self.cli('probe')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'command discovered')

    def test_doctor_section_is_discovered_by_file(self):
        p = self.root / 'studio_control/cli/doctor/probe.py'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('def inspect():\n    return {"status": "unverified", "detail": "probe discovered"}\n')
        result = self.cli('doctor')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['probe']['detail'], 'probe discovered')

if __name__ == '__main__':
    unittest.main()
