import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from storage_fixture import boundary_environment, managed_python_shell_path, native_bash

ROOT = Path(__file__).resolve().parents[2]

class EnvironmentTest(unittest.TestCase):
    def test_missing_volume_exports_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, 'STUDIO_ROOT': str(Path(tmp) / 'absent'), 'STUDIO_PYTHON': managed_python_shell_path()}
            command = 'before=$(env | sort); source scripts/dev/studio-env.sh; status=$?; after=$(env | sort); [ "$status" -ne 0 ] && [ "$before" = "$after" ]'
            result = subprocess.run([native_bash(), '-c', command], env=env, cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(Path(env['STUDIO_ROOT']).exists())

    def test_missing_volume_worktree_creates_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / 'absent'
            result = subprocess.run([sys.executable, str(ROOT/'scripts/dev/worktree.py'), '99-probe'], env={**os.environ,'STUDIO_ROOT':str(missing)}, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('not mounted',result.stderr)
            self.assertFalse(missing.exists())

    def test_preflight_refuses_impossible_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable,str(ROOT/'scripts/dev/preflight.py'),'--estimate-gib','1000000'],env=boundary_environment(tmp),text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('insufficient',result.stderr)

    def test_every_exported_cache_stays_on_volume(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([native_bash(),'-c','source scripts/dev/studio-env.sh && "$STUDIO_PYTHON" -c "import os,json; print(json.dumps(dict(os.environ)))"'],env=boundary_environment(tmp),cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        values=json.loads(result.stdout)
        root=Path(values['STUDIO_ROOT']).resolve()
        for name in ['HF_HOME','HF_HUB_CACHE','HF_XET_CACHE','UV_CACHE_DIR','UV_PYTHON_INSTALL_DIR','UV_TOOL_DIR','UV_TOOL_BIN_DIR','PIP_CACHE_DIR','TORCH_HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_STATE_HOME','npm_config_cache','COREPACK_HOME','PLAYWRIGHT_BROWSERS_PATH','TMPDIR','PNPM_HOME']:
            self.assertTrue(Path(values[name]).resolve().is_relative_to(root),name)


class StorageRefusalTest(unittest.TestCase):
    @unittest.skipUnless(sys.platform=='darwin','macOS physical backing contract')
    def test_internal_and_nested_image_backing_are_refused(self):
        for host in [{'Internal':True,'BusProtocol':'PCI-Express'},{'Internal':False,'BusProtocol':'Disk Image'}, {'Internal':False}, {'Internal':False,'BusProtocol':'Unverified'}]:
            with self.subTest(host=host),tempfile.TemporaryDirectory() as tmp:
                env=boundary_environment(tmp)
                shim=Path(tmp)/'os-boundary/sitecustomize.py'
                shim.write_text(shim.read_text().replace('{"Internal":False,"BusProtocol":"USB"}',repr(host)))
                result=subprocess.run([sys.executable,str(ROOT/'scripts/dev/environment.py')],env=env,text=True,capture_output=True)
                self.assertNotEqual(result.returncode,0,result.stdout)
                self.assertEqual(result.stdout,'')
                self.assertIn('external physical',result.stderr)
                self.assertFalse((Path(tmp)/'scratch').exists())

    def test_temp_symlink_escape_is_refused_before_mkdir(self):
        if os.name=='nt': self.skipTest('symlink privilege is not assumed on Windows CI')
        with tempfile.TemporaryDirectory() as tmp,tempfile.TemporaryDirectory() as outside:
            env=boundary_environment(tmp)
            (Path(tmp)/'scratch').symlink_to(outside,target_is_directory=True)
            result=subprocess.run([sys.executable,str(ROOT/'scripts/dev/environment.py')],env=env,text=True,capture_output=True)
            self.assertNotEqual(result.returncode,0,result.stdout)
            self.assertIn('escapes',result.stderr)
            self.assertFalse((Path(outside)/'tmp').exists())

class EnvironmentOverrideTest(unittest.TestCase):
    def test_inherited_workspace_environment_override_is_refused_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            env=boundary_environment(tmp);env['UV_PROJECT_ENVIRONMENT']='/must-not-write/internal-env'
            result=subprocess.run([sys.executable,str(ROOT/'scripts/dev/environment.py')],env=env,text=True,capture_output=True)
            self.assertNotEqual(result.returncode,0,result.stdout)
            self.assertEqual(result.stdout,'')
            self.assertIn('UV_PROJECT_ENVIRONMENT',result.stderr)
            self.assertFalse((Path(tmp)/'scratch').exists())

if __name__=='__main__': unittest.main()
