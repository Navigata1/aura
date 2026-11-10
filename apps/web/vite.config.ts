import { defineConfig } from 'vite';
import { bundleLicenses } from '../../scripts/ci/bundle-licenses.mjs';
export default defineConfig({ plugins: [bundleLicenses()] });
