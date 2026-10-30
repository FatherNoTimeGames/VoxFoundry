import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createApp, digest, MAX_AUDIO} from '../worker/index.js';

// Real SQLite executes the actual application SQL. This is a D1 API adapter,
// NOT Cloudflare D1 and NOT the Sites dispatch authentication layer.
class LocalD1 {
  constructor() {
    this.db = new DatabaseSync(':memory:');
    this.db.exec(readFileSync(new URL('../schema.sql', import.meta.url), 'utf8'));
  }
  prepare(sql) {
    const native = this.db.prepare(sql); let args=[];
    const bound = {bind(...values) {args=values;return bound;},
      async first() {return native.get(...args) || null;},
      async all() {return {results:native.all(...args)};},
      async run() {return native.run(...args);},
      execute() {return {results:native.all(...args)};}};
    return bound;
  }
  async batch(statements) {
    this.db.exec('BEGIN');
    try {const results=statements.map(s=>s.execute());this.db.exec('COMMIT');return results;}
    catch(e){this.db.exec('ROLLBACK');throw e;}
  }
}
class MemoryR2 {
  data = new Map();
  async put(key, bytes) {this.data.set(key,bytes.slice());await this.afterPut?.();}
  async get(key) {const bytes=this.data.get(key);return bytes ? {arrayBuffer:async()=>bytes.slice().buffer} : null;}
}
function wav() {
  const result = spawnSync('python', ['-c',
    'import sys;sys.path.insert(0,"../../backend");from voxfoundry.poc.audio import test_tone;sys.stdout.buffer.write(test_tone("abcd"*16))'],
    {cwd: new URL('../', import.meta.url)});
  assert.equal(result.status,0,result.stderr.toString());
  return new Uint8Array(result.stdout);
}
const bytes=wav();
async function fixture() {
  let time=1000;
  const env={DB:new LocalD1(),BUCKET:new MemoryR2(),OWNER_USER_ID:'owner'};
  const app=createApp({clock:()=>time});
  const token='x'.repeat(43), auth={'Authorization':'Bearer '+token};
  async function call(path, {method='GET', data, headers={}, identity='owner', raw}={}) {
    const h=new Headers(headers);
    if(identity) h.set('oai-authenticated-user-id',identity);
    if(method==='POST' && !path.startsWith('/worker/')) h.set('Origin','https://poc.example');
    if(data !== undefined) h.set('Content-Type','application/json');
    return app.fetch(new Request('https://poc.example'+path,{method,headers:h,
      body:raw ?? (data === undefined ? undefined : JSON.stringify(data))}),env);
  }
  async function json(path, opts) {const response=await call(path,opts);return {status:response.status,body:await response.json()};}
  const enrolled=await json('/api/devices',{method:'POST',data:{id:'device',token_hash:await digest(token)}});
  assert.equal(enrolled.status,200);
  async function submit(text='An approved non-sensitive test passage.', id=crypto.randomUUID()) {
    const response=await json('/api/jobs',{method:'POST',data:{text,request_id:id,approved:true}});
    assert.equal(response.status,200);return response.body;
  }
  async function claim() {
    const result=await json('/worker/jobs/claim',{method:'POST',identity:null,headers:auth});
    assert.equal(result.status,200);return result.body.job;
  }
  async function upload(job, audio=bytes, extra={}) {
    return json('/worker/jobs/'+job.id+'/result',{method:'POST',identity:null,raw:audio,
      headers:{...auth,'Content-Type':'audio/wav','X-Lease-Token':job.lease_token,'X-Audio-SHA256':await digest(audio),...extra}});
  }
  return {env,app,call,json,submit,claim,upload,auth,advance(n){time+=n;}};
}

test('explicit approval, bounded passage, and immutable idempotency body',async()=>{
  const f=await fixture(), request_id=crypto.randomUUID();
  assert.equal((await f.json('/api/jobs',{method:'POST',data:{text:'test',request_id,approved:false}})).status,400);
  const a=await f.submit('test',request_id), b=await f.submit('test',request_id);assert.equal(a.id,b.id);
  assert.equal((await f.json('/api/jobs',{method:'POST',data:{text:'changed',request_id,approved:true}})).status,409);
  assert.equal((await f.json('/api/jobs',{method:'POST',data:{text:'a'.repeat(1001),request_id,approved:true}})).status,400);
});
test('owner identity and Origin are required; service credential alone grants no owner access',async()=>{
  const f=await fixture();
  assert.equal((await f.call('/api/jobs',{identity:null,headers:{'OAI-Sites-Authorization':'Bearer dummy'}})).status,401);
  assert.equal((await f.call('/api/jobs',{identity:'other-user'})).status,403);
  const response=await f.app.fetch(new Request('https://poc.example/api/jobs',{method:'POST',headers:{'oai-authenticated-user-id':'owner','origin':'https://evil.example','content-type':'application/json'},body:'{}'}),f.env);
  assert.equal(response.status,403);
  assert.equal((await f.call('/api/jobs',{method:'OPTIONS',identity:null})).headers.has('access-control-allow-origin'),false);
});
test('request id must be a string, without regex coercion or database errors',async()=>{
  const f=await fixture(), id=crypto.randomUUID();
  for (const request_id of [[id], {[id]:true}, 1234567890123456, null]) {
    const result=await f.json('/api/jobs',{method:'POST',data:{text:'Approved.',approved:true,request_id}});
    assert.equal(result.status,400);
  }
  assert.equal(f.env.DB.db.prepare('SELECT count(*) AS n FROM jobs').get().n,0);
});
test('another enrolled device cannot read or complete a job with a copied lease',async()=>{
  const f=await fixture(), otherToken='y'.repeat(43);
  assert.equal((await f.json('/api/devices',{method:'POST',data:{id:'second-device',token_hash:await digest(otherToken)}})).status,200);
  const headers={Authorization:'Bearer '+otherToken};
  await f.submit();const first=await f.claim();
  assert.equal((await f.call('/worker/jobs/'+first.id,{identity:null,headers})).status,404);
  assert.equal((await f.json('/worker/jobs/'+first.id+'/heartbeat',{method:'POST',identity:null,
    headers:{...headers,'X-Lease-Token':first.lease_token},data:{progress:80}})).status,404);
  assert.equal((await f.upload(first,bytes,headers)).status,404);
  f.advance(61);
  const reclaimed=(await f.json('/worker/jobs/claim',{method:'POST',identity:null,headers})).body.job;
  assert.equal(reclaimed.id,first.id);assert.notEqual(reclaimed.lease_token,first.lease_token);
  assert.equal((await f.upload(first)).status,404);
  assert.equal((await f.upload(reclaimed,bytes,headers)).status,200);
});
test('concurrent differing uploads produce one committed result and retain the orphan',async()=>{
  const f=await fixture();await f.submit();const job=await f.claim();
  const alternative=bytes.slice();alternative[100]^=1;
  const results=await Promise.all([f.upload(job,bytes),f.upload(job,alternative)]);
  assert.deepEqual(results.map(result=>result.status).sort(),[200,409]);
  const committed=f.env.DB.db.prepare('SELECT * FROM jobs WHERE id=?').get(job.id);
  assert.equal(committed.state,'succeeded');
  assert.equal(f.env.BUCKET.data.size,2); // losing valid upload is a documented orphan
  const response=await f.call('/api/jobs/'+job.id+'/audio');
  assert.equal(response.status,200);
  assert.equal(await digest(new Uint8Array(await response.arrayBuffer())),committed.audio_digest);
  assert.equal(results.find(result=>result.status===200).body.audio_digest,committed.audio_digest);
});
test('wrong or missing worker credentials denied; owner cookie cannot claim',async()=>{
  const f=await fixture();
  assert.equal((await f.call('/worker/jobs/claim',{method:'POST'})).status,401);
  assert.equal((await f.call('/worker/jobs/claim',{method:'POST',headers:{Authorization:'Bearer '+'z'.repeat(43)}})).status,401);
});
test('read-only worker probe authenticates device but never supplies owner identity',async()=>{
  const f=await fixture();
  assert.equal((await f.call('/worker/ping',{identity:null})).status,401);
  const probe=await f.json('/worker/ping',{identity:null,headers:f.auth});
  assert.equal(probe.status,200);assert.equal(probe.body.device_id,'device');
  assert.equal((await f.call('/api/jobs',{identity:null,headers:f.auth})).status,401);
  assert.equal(f.env.DB.db.prepare('SELECT count(*) AS n FROM jobs').get().n,0);
});
test('atomic claim admits one claimant, records attempts, and hides secrets from owner list',async()=>{
  const f=await fixture();await f.submit();
  const claimed=await Promise.all([f.claim(),f.claim()]);assert.equal(claimed.filter(Boolean).length,1);
  assert.equal(f.env.DB.db.prepare('SELECT count(*) AS n FROM attempts').get().n,1);
  const list=await f.json('/api/jobs');assert.equal(JSON.stringify(list).includes('lease_token'),false);
  assert.equal(JSON.stringify(list).includes('lease_hash'),false);
});
test('progress is monotonic and heartbeat renews a live lease',async()=>{
  const f=await fixture();await f.submit();const job=await f.claim();
  for(const progress of [80,20]) {
    const result=await f.json('/worker/jobs/'+job.id+'/heartbeat',{method:'POST',identity:null,
      headers:{...f.auth,'X-Lease-Token':job.lease_token},data:{progress}});
    assert.equal(result.status,200);assert.equal(result.body.progress,80);
  }
  f.advance(61);
  assert.equal((await f.json('/worker/jobs/'+job.id+'/heartbeat',{method:'POST',identity:null,
    headers:{...f.auth,'X-Lease-Token':job.lease_token},data:{progress:90}})).status,409);
});
test('expired lease is fenced after reclaim, even for same worker',async()=>{
  const f=await fixture();await f.submit();const old=await f.claim();f.advance(61);const current=await f.claim();
  assert.equal(old.id,current.id);assert.notEqual(old.lease_token,current.lease_token);
  assert.equal((await f.upload(old)).status,409);assert.equal((await f.upload(current)).status,200);
});
test('revocation blocks claims and uploads including an in-flight upload',async()=>{
  const f=await fixture();await f.submit();const job=await f.claim();
  f.env.BUCKET.afterPut=async()=>{await f.json('/api/devices/device/revoke',{method:'POST',data:{}});};
  assert.equal((await f.upload(job)).status,409);
  assert.equal((await f.call('/worker/jobs/claim',{method:'POST',identity:null,headers:f.auth})).status,401);
  assert.equal((await f.upload(job)).status,401);
  assert.equal((await f.json('/api/jobs')).body.jobs[0].state,'running');
});
test('rejects truncated, oversized, malformed format and wrong-digest WAVs',async()=>{
  const f=await fixture();await f.submit();const job=await f.claim();
  assert.equal(bytes.length,MAX_AUDIO);
  assert.equal((await f.upload(job,bytes.slice(0,-1))).status,400);
  assert.equal((await f.upload(job,new Uint8Array(MAX_AUDIO+1))).status,413);
  const bad=bytes.slice();bad[22]=2;assert.equal((await f.upload(job,bad)).status,400);
  assert.equal((await f.upload(job,bytes,{'X-Audio-SHA256':'0'.repeat(64)})).status,400);
  assert.equal(f.env.BUCKET.data.size,0);
});
test('upload is idempotent after lost acknowledgment; completed bytes are immutable',async()=>{
  const f=await fixture();await f.submit();const job=await f.claim();
  assert.equal((await f.upload(job)).status,200);f.advance(3600);
  assert.equal((await f.upload(job)).status,200);
  const different=bytes.slice();different[100]^=1;
  assert.equal((await f.upload(job,different)).status,409);
  assert.equal(f.env.BUCKET.data.size,1);
});
test('authorized ranged playback and download survive app restart without worker',async()=>{
  const f=await fixture();await f.submit();const job=await f.claim();await f.upload(job);
  const restarted=createApp();
  const request=new Request('https://poc.example/api/jobs/'+job.id+'/audio?download=1',
    {headers:{'oai-authenticated-user-id':'owner',Range:'bytes=44-99'}});
  const response=await restarted.fetch(request,f.env);
  assert.equal(response.status,206);assert.equal(response.headers.get('content-range'),'bytes 44-99/64044');
  assert.match(response.headers.get('content-disposition'),/^attachment/);
  assert.deepEqual(new Uint8Array(await response.arrayBuffer()),bytes.slice(44,100));
  assert.equal(response.headers.get('cache-control'),'private, no-store');
  assert.equal((await f.call('/api/jobs/'+job.id+'/audio',{identity:'other'})).status,403);
  const suffix=await f.call('/api/jobs/'+job.id+'/audio',{headers:{Range:'bytes=-10'}});
  assert.equal((await suffix.arrayBuffer()).byteLength,10);
  assert.equal((await f.call('/api/jobs/'+job.id+'/audio',{headers:{Range:'bytes=0-2,8-10'}})).status,416);
});
test('lease expiry during R2 put cannot mark success; orphan remains explicitly',async()=>{
  const f=await fixture();await f.submit();const job=await f.claim();
  f.env.BUCKET.afterPut=async()=>f.advance(61);
  assert.equal((await f.upload(job)).status,409);
  assert.equal((await f.json('/api/jobs')).body.jobs[0].state,'running');
  assert.equal(f.env.BUCKET.data.size,1);
});
test('R2 or database failure does not fabricate completion; upload retry recovers',async()=>{
  const f=await fixture();await f.submit();const job=await f.claim();
  const put=f.env.BUCKET.put.bind(f.env.BUCKET);f.env.BUCKET.put=async()=>{throw Error('storage failure');};
  assert.equal((await f.upload(job)).status,500);
  assert.equal((await f.json('/api/jobs')).body.jobs[0].state,'running');
  f.env.BUCKET.put=put;assert.equal((await f.upload(job)).status,200);
});
test('bounded attempts, explicit one-time retry budget, and job quota',async()=>{
  const f=await fixture();await f.submit();let job;
  for(let i=0;i<3;i++){job=await f.claim();assert.ok(job);f.advance(61);}
  assert.equal(await f.claim(),null);assert.equal((await f.json('/api/jobs')).body.jobs[0].state,'failed');
  assert.equal((await f.json('/api/jobs/'+job.id+'/retry',{method:'POST',data:{}})).status,200);
  for(let i=0;i<3;i++){assert.ok(await f.claim());f.advance(61);}
  assert.equal((await f.json('/api/jobs/'+job.id+'/retry',{method:'POST',data:{}})).status,409);
  for(let i=1;i<20;i++) await f.submit();
  assert.equal((await f.json('/api/jobs',{method:'POST',data:{text:'extra',approved:true,request_id:crypto.randomUUID()}})).status,429);
});
test('missing owner or storage configuration fails closed',async()=>{
  const f=await fixture();delete f.env.OWNER_USER_ID;
  assert.equal((await f.call('/api/jobs')).status,503);
  assert.equal((await f.call('/worker/jobs/claim',{method:'POST',headers:f.auth})).status,401);
  assert.equal((await f.call('/api/identity')).status,200);
});
test('mobile UI, CSP and script parse checks (not browser QA)',async()=>{
  const f=await fixture();const response=await f.call('/');const html=await response.text();
  assert.match(html,/width=device-width/);assert.match(html,/aria-live="polite"/);
  assert.match(html,/min-height:44px/);assert.match(html,/Test tone only/);
  assert.match(response.headers.get('content-security-policy'),/script-src 'self'/);
  const script=await (await f.call('/app.js')).text();assert.doesNotThrow(()=>new Function(script));
  assert.equal(script.includes('OAI-Sites-Authorization'),false);assert.equal(script.includes('lease_token'),false);
});
