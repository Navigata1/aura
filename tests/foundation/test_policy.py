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

def joined(separator,*parts):
    # Planted paths are assembled at run time, so this file never holds a form it plants.
    return separator.join(parts)

PRIVATE_PATHS = {
    'macOS home': joined('/','','Users','someone','notes.txt'),
    'Linux home': joined('/','','home','someone','notes.txt'),
    'Windows home': joined('\\','C:','Users','someone','notes.txt'),
    'Windows home, JSON-escaped': joined('\\\\','D:','Users','someone','notes.txt'),
    'Windows home, forward slashes': joined('/','c:','users','someone','notes.txt'),
    'Git Bash home': joined('/','','c','Users','someone','notes.txt'),
    'WSL home': joined('/','','mnt','c','Users','someone','notes.txt'),
    'file URL': 'file://'+joined('/','','home','someone','notes.txt'),
    'tilde into a machine folder': joined('/','~','Projects','notes.txt'),
    'canonical checkout shape': joined('/','~','Some Folder','checkout'),
    'home variable into a machine folder': joined('/','$HOME','Some Folder','checkout'),
    'Windows profile into a machine folder': joined('\\','%USERPROFILE%','Some Folder','checkout'),
    'placeholder account into a machine folder': joined('/','','Users','<name>','Some Folder','checkout'),
    'cloud drive under Library': joined('/','~','Library','Mobile Documents','com~apple~CloudDocs','Some Folder'),
}
DOCUMENTED_PATHS = '\n'.join([
    'Studio volume: /Volumes/STUDIO/worktrees/C05-private-path-lint/',
    'Tool folders: `~/.config/studio/env.sh`, `$HOME/.cache/uv`, `~/Library/Caches/pnpm`, `%USERPROFILE%\\AppData\\Local`',
    'Placeholders: /Users/<name>/, /home/<user>/.cache/uv, C:\\Users\\<name>\\AppData\\Local, `~/`, `/Users/`',
    'Not home paths: apps/web/src/home/Home.tsx, ./home/Home, src/Users/List.tsx, https://example.com/home/page, ~400 lines',
    'Web routes: fetch(`/users/${id}`), GET /users/{id}/orders',
])

class PolicyTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        (self.root/'contracts').mkdir()
        (self.root/'contracts/product.json').write_text(json.dumps({'productName':'TestProduct','publicContactText':CONTACT}))

    def tearDown(self): self.temp.cleanup()

    def scan(self,path,content):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True)
        if isinstance(content,bytes):p.write_bytes(content)
        else:p.write_text(content)
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

    def test_each_private_path_form_rejected_without_echo(self):
        for form,text in PRIVATE_PATHS.items():
            with self.subTest(form=form):
                result=self.scan('docs/research/notes.md','See '+text+' for details.\n')
                self.assertNotEqual(result.returncode,0,result.stdout)
                self.assertIn('docs/research/notes.md: private-path: line 1:',result.stdout)
                self.assertNotIn('someone',result.stdout+result.stderr)
    def test_documented_path_forms_allowed(self):
        result=self.scan('docs/research/notes.md',DOCUMENTED_PATHS)
        self.assertEqual(result.returncode,0,result.stdout)
    def test_verbatim_source_archive_is_excluded(self):
        self.assertEqual(self.scan('docs/research/sources/notes.md',PRIVATE_PATHS['macOS home']).returncode,0)
    def test_private_path_in_undecodable_bytes_rejected(self):
        for form,raw in [('invalid UTF-8',b'\xff'+PRIVATE_PATHS['Linux home'].encode()),
                         ('UTF-16 with a byte-order mark',PRIVATE_PATHS['Windows home'].encode('utf-16'))]:
            with self.subTest(form=form): self.rejected('evidence.log',raw,'evidence.log: private-path')
    @unittest.skipIf(os.name=='nt','Windows checkouts store a tracked symlink as a text file, which the text scan reads')
    def test_private_symlink_target_rejected(self):
        (self.root/'models').symlink_to(joined('/','','Users','someone','models'))
        self.rejected('readme.txt','probe','models: private-path')


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
