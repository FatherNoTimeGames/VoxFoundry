// Packaging only. Bindings, migration integration and Site ID must be verified
// before publication. Do not invent a hosting manifest or create resources here.
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
const source = await readFile(root + 'worker/index.js', 'utf8');
const mod = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
if (typeof mod.default?.fetch !== 'function') throw Error('Missing Worker fetch export');
await mkdir(root + 'dist/server', {recursive:true});
await writeFile(root + 'dist/server/index.js', source);
console.log('Worker ESM validated and copied; NOT a deployable archive (hosting configuration pending).');
