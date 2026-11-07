"""Planted violations at the repository-lint CLI boundary."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / 'scripts/ci/check.py'
CONTACT = json.loads((ROOT/'contracts/product.json').read_text())['publicContactText']

class PolicyTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        (self.root/'contracts').mkdir()
        (self.root/'contracts/product.json').write_text(json.dumps({'productName':'TestProduct','publicContactText':CONTACT}))

    def tearDown(self): self.temp.cleanup()

    def scan(self,path,content):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
        subprocess.run(['git','-C',str(self.root),'add','-A'],check=True)
        return subprocess.run([sys.executable,str(CHECK),'--root',str(self.root),'--files-only'],text=True,capture_output=True)

    def rejected(self,path,content,rule):
        result=self.scan(path,content)
        self.assertNotEqual(result.returncode,0,result.stdout)
        self.assertIn(rule,result.stdout+result.stderr)

    def test_mail_link_rejected(self): self.rejected('README.md','mail'+'to:'+CONTACT,'contact')
    def test_personal_address_rejected(self): self.rejected('notes.txt','person'+'@'+'example.invalid','contact')
    def test_bare_markdown_contact_rejected(self): self.rejected('README.md',CONTACT,'contact')
    def test_contact_code_span_allowed(self): self.assertEqual(self.scan('README.md','`'+CONTACT+'`').returncode,0)
    def test_manifest_author_rejected(self): self.rejected('package.json',json.dumps({'author':{'email':CONTACT}}),'manifest')
    def test_weight_file_rejected(self): self.rejected('model.safetensors','synthetic','weights')
    def test_large_file_rejected(self):
        p=self.root/'large.dat'
        with p.open('wb') as f:f.truncate(50*1024**2)
        result=self.scan('readme.txt','probe')
        self.assertNotEqual(result.returncode,0);self.assertIn('weights',result.stdout)
    def test_audio_file_rejected(self): self.rejected('sample.wav','synthetic','audio')
    def test_secret_in_source_rejected(self): self.rejected('source.py','token = "'+('ghp_'+'A'*36)+'"','secret')
    def test_secret_in_bundle_rejected(self):
        result=self.scan('readme.txt','probe')
        p=self.root/'apps/web/dist/main.js';p.parent.mkdir(parents=True);p.write_text('const token="'+('ghp_'+'B'*36)+'"')
        result=subprocess.run([sys.executable,str(CHECK),'--root',str(self.root),'--files-only','--bundle'],text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('secret',result.stdout)
    def test_product_in_package_name_rejected(self): self.rejected('pyproject.toml','[project]\nname="testproduct-control"\n','product-name')
    def test_unknown_license_rejected(self):
        self.rejected('license-inventory.json',json.dumps([{'name':'bad','license':'UNKNOWN'}]),'license')
    def test_lgpl_license_rejected(self):
        self.rejected('license-inventory.json',json.dumps([{'name':'bad','license':'LGPL-3.0-only'}]),'license')

    def test_lowercase_code_identifier_rejected(self): self.rejected('source.py','testproduct_cache = 1','product-name')
    def test_lowercase_store_format_rejected(self): self.rejected('source.py','format = "testproduct-store"','product-name')


class InstalledLicenseTest(unittest.TestCase):
    def assert_rejected(self, license):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name,body in [('studio_control-0.1.0.dist-info','Name: studio-control\nVersion: 0.1.0\nRequires-Dist: planted-library\n'),('planted_library-1.0.dist-info','Name: planted-library\nVersion: 1.0\nLicense-Expression: '+license+'\n')]:
                p=root/name;p.mkdir();(p/'METADATA').write_text('Metadata-Version: 2.4\n'+body)
            env={**os.environ,'PYTHONPATH':tmp}
            result=subprocess.run([sys.executable,str(ROOT/'scripts/ci/licenses.py'),'--python-only'],env=env,text=True,capture_output=True)
            self.assertNotEqual(result.returncode,0,result.stdout)
            self.assertIn('planted-library',result.stdout)

    def test_unknown_installed_runtime_dependency_fails(self): self.assert_rejected('UNKNOWN')
    def test_lgpl_installed_runtime_dependency_fails(self): self.assert_rejected('LGPL-3.0-only')

class CommitIdentityTest(unittest.TestCase):
    def check_identity(self,email,message):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);subprocess.run(['git','init','-q',tmp],check=True)
            (root/'contracts').mkdir();(root/'contracts/product.json').write_text(json.dumps({'productName':'TestProduct','publicContactText':CONTACT}))
            subprocess.run(['git','-C',tmp,'add','-A'],check=True)
            env={**os.environ,'GIT_AUTHOR_NAME':'Synthetic','GIT_COMMITTER_NAME':'Synthetic','GIT_AUTHOR_EMAIL':email,'GIT_COMMITTER_EMAIL':email}
            subprocess.run(['git','-C',tmp,'commit','-qm',message],env=env,check=True)
            return subprocess.run([sys.executable,str(CHECK),'--root',tmp],text=True,capture_output=True)

    def test_non_noreply_commit_is_rejected(self):
        result=self.check_identity('person'+'@'+'example.invalid','Synthetic test')
        self.assertNotEqual(result.returncode,0);self.assertIn('commit identity',result.stdout)

    def test_approved_coauthor_trailer_is_allowed(self):
        result=self.check_identity('1+Navigata1'+'@'+'users.noreply.github.com','Synthetic test\n\nCo-Authored-By: Assistant <'+'noreply'+'@'+'anthropic.com>')
        self.assertEqual(result.returncode,0,result.stdout)

class TransitiveExtrasLicenseTest(unittest.TestCase):
    def test_selected_extra_cannot_hide_a_forbidden_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            for directory,body in [
                ('studio_control-0.1.0.dist-info','Name: studio-control\nVersion: 0.1.0\nRequires-Dist: planted-extra[gpl]\n'),
                ('planted_extra-1.0.dist-info','Name: planted-extra\nVersion: 1.0\nLicense-Expression: MIT\nProvides-Extra: gpl\nRequires-Dist: planted-denied; extra == "gpl"\n'),
                ('planted_denied-1.0.dist-info','Name: planted-denied\nVersion: 1.0\nLicense-Expression: LGPL-3.0-only\n')]:
                p=Path(tmp)/directory;p.mkdir();(p/'METADATA').write_text('Metadata-Version: 2.4\n'+body)
            result=subprocess.run([sys.executable,str(ROOT/'scripts/ci/licenses.py'),'--python-only'],env={**os.environ,'PYTHONPATH':tmp},text=True,capture_output=True)
            self.assertNotEqual(result.returncode,0,result.stdout)
            self.assertIn('planted-denied',result.stdout)


if __name__=='__main__':unittest.main()
