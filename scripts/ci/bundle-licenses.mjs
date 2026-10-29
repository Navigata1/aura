import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
const workspace = path.resolve(fileURLToPath(new URL('../../', import.meta.url)));

// Inventory the modules actually emitted, regardless of dependencies/devDependencies.
export function bundleLicenses() {
  return {
    name: 'studio-bundle-license-inventory',
    generateBundle(_options, bundle) {
      const packages = new Map();
      const generated = new Set();
      for (const entry of Object.values(bundle)) {
        if (entry.type !== 'chunk') continue;
        for (const id of Object.keys(entry.modules)) {
          let clean = id.replaceAll('\0', '').split('?')[0];
          const appRequire = createRequire(path.join(workspace, 'apps/web/package.json'));
          if (id === '\0vite/modulepreload-polyfill.js') clean = appRequire.resolve('vite');
          if (id === '\0rolldown/runtime.js') clean = createRequire(appRequire.resolve('vite')).resolve('rolldown');
          if (!path.isAbsolute(clean) || !fs.existsSync(clean)) {
            generated.add(id);
            continue;
          }
          let directory = path.dirname(clean);
          while (!fs.existsSync(path.join(directory, 'package.json'))) {
            const parent = path.dirname(directory);
            if (parent === directory) throw new Error('Bundled module has no package provenance');
            directory = parent;
          }
          const metadata = JSON.parse(fs.readFileSync(path.join(directory, 'package.json'), 'utf8'));
          if ([workspace, path.join(workspace, 'apps/web')].includes(directory)) continue;
          packages.set(`${metadata.name}@${metadata.version}`, { name: metadata.name, version: metadata.version, license: metadata.license ?? 'UNKNOWN' });
        }
      }
      this.emitFile({ type: 'asset', fileName: 'license-inventory.json', source: JSON.stringify({ packages: [...packages.values()], generatedModules: [...generated], chunks: Object.fromEntries(Object.values(bundle).filter(entry => entry.type === 'chunk').map(entry => [entry.fileName, createHash('sha256').update(entry.code).digest('hex')])) }, null, 2) });
    },
  };
}
