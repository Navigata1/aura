import { expect, test } from 'vitest';
import * as contracts from './index';
test('foundation package loads without claiming generated record types', () => { expect(Object.keys(contracts)).toEqual([]); });
