import { expect, test } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { createElement } from 'react';
import { App } from './app';
import product from '../../../contracts/product.json';

test('foundation names the product and exposes its implementation status', () => {
  const html = renderToStaticMarkup(createElement(App));
  expect(html).toContain(product.productName);
  expect(html).toContain('Foundation only');
  expect(html).toContain('Generation, projects and playback are not connected yet.');
});
