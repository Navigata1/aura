import { createElement } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './app';
import product from '../../../contracts/product.json';

document.title = product.productName;
const root = document.getElementById('root');
if (!root) throw new Error('Missing application root');
createRoot(root).render(createElement(App));
