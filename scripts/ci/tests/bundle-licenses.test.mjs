import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { bundleLicenses } from '../bundle-licenses.mjs';

test('emitted module inventory includes a forbidden package even when declared dev-only', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'bundle-license-'));
  try {
    fs.writeFileSync(path.join(root, 'package.json'), JSON.stringify({ name: 'test-app', devDependencies: { 'planted-web': '1.0.0' } }));
    const dep = path.join(root, 'node_modules/planted-web'); fs.mkdirSync(dep, { recursive: true });
    fs.writeFileSync(path.join(dep, 'package.json'), JSON.stringify({ name: 'planted-web', version: '1.0.0', license: 'LGPL-3.0-only' }));
    const module = path.join(dep, 'index.js'); fs.writeFileSync(module, 'export const sentinel=1;');
    let output;
    bundleLicenses().generateBundle.call({ emitFile(asset) { output=JSON.parse(asset.source); } }, {}, { 'main.js': { type: 'chunk', fileName: 'main.js', code: 'console.log(1)', modules: { [module]: {} } } });
    assert.deepEqual(output.packages, [{ name: 'planted-web', version: '1.0.0', license: 'LGPL-3.0-only' }]);
    assert.equal(output.chunks['main.js'].length, 64);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
