import { createElement } from 'react';
import product from '../../../contracts/product.json';

export function App() {
  return createElement('main', { 'aria-labelledby': 'product-title' },
    createElement('h1', { id: 'product-title' }, product.productName),
    createElement('p', null, 'Foundation only'),
    createElement('p', null, 'Generation, projects and playback are not connected yet.'),
  );
}
