import {cp,mkdir,readFile,rm,stat,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {Script} from 'node:vm';
const root=fileURLToPath(new URL('../',import.meta.url));
const source=await readFile(root+'worker/index.js','utf8');
const ui=await readFile(root+'worker/ui.js','utf8');
// Minimal pre-registration manifest documented by OpenAI's Manage a site page.
// Copy only the declared bindings/real identity; never synthesize a project ID.
const manifestText=await readFile(root+'.openai/hosting.json','utf8');
const manifest=JSON.parse(manifestText);
if(!manifest || Array.isArray(manifest) || manifest.d1!=='DB' || manifest.r2!==null ||
   Object.keys(manifest).some(key=>!['project_id','d1','r2'].includes(key)))
  throw Error('Expected the text-only Studio binding manifest; runtime values do not belong here.');
if('project_id' in manifest && (typeof manifest.project_id!=='string' || !manifest.project_id.trim() || /[<>]/.test(manifest.project_id)))
  throw Error('Use only the real project ID returned by Sites, or omit it before registration.');
const {JS}=await import(new URL('../worker/ui.js',import.meta.url));
new Script(JS,{filename:'browser-app.js'});
const marker="import {HTML, JS} from './ui.js';";
if(!source.includes(marker))throw Error('Unexpected Worker import layout');
const bundled=source.replace(marker,()=>ui.replaceAll('export const ','const '));
const result=await import('data:text/javascript;base64,'+Buffer.from(bundled).toString('base64'));
if(typeof result.default?.fetch!=='function')throw Error('Worker fetch export is missing');
await mkdir(root+'dist/server',{recursive:true});
// Match the production packaging contract in @openai/sites-vite-plugin 0.2.0
// (openai/sites@7eb9d4b9): replace metadata, then copy optional Drizzle sidecars.
// This copies reviewed generated files; it never invents SQL, snapshots or journals.
await rm(root+'dist/.openai',{recursive:true,force:true});
await mkdir(root+'dist/.openai',{recursive:true});
await writeFile(root+'dist/server/index.js',bundled);
await writeFile(root+'dist/.openai/hosting.json',manifestText);
let hasDrizzle=false;
try {
  await stat(root+'drizzle');
  hasDrizzle=true;
} catch(error) {
  if(error.code!=='ENOENT')throw error;
}
if(hasDrizzle)await cp(root+'drizzle',root+'dist/.openai/drizzle',{recursive:true});
console.log('Studio ESM and binding manifest prepared; '+(hasDrizzle?'Drizzle sidecars copied (not validated or applied).':'no generated Drizzle migrations present.')+' Migration generation/review, Site registration and private deployment remain pending; this is not a deployable archive.');
