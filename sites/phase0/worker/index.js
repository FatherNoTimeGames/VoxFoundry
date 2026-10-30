// Dependency-free Sites Worker ESM. Dispatch, not this code, authenticates the
// private Site boundary. Tests exercise application authorization separately.
export const MAX_AUDIO = 64044;
const LEASE_SECONDS = 60;
const encoder = new TextEncoder();
export async function digest(value) {
  const bytes = typeof value === 'string' ? encoder.encode(value) : value;
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))]
    .map(x => x.toString(16).padStart(2, '0')).join('');
}
function fail(status, message) { throw Object.assign(new Error(message), {status}); }
function json(value, status = 200) {
  return new Response(JSON.stringify(value), {status, headers: {'Content-Type': 'application/json'}});
}
export function validWav(bytes) {
  if (bytes.length !== MAX_AUDIO) fail(400, 'Expected exactly 64044 bytes of test-tone WAV');
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const tag = offset => new TextDecoder().decode(bytes.subarray(offset, offset + 4));
  if (tag(0) !== 'RIFF' || view.getUint32(4, true) !== 64036 || tag(8) !== 'WAVE' ||
      tag(12) !== 'fmt ' || view.getUint32(16, true) !== 16 ||
      view.getUint16(20, true) !== 1 || view.getUint16(22, true) !== 1 ||
      view.getUint32(24, true) !== 16000 || view.getUint32(28, true) !== 32000 ||
      view.getUint16(32, true) !== 2 || view.getUint16(34, true) !== 16 ||
      tag(36) !== 'data' || view.getUint32(40, true) !== 64000)
    fail(400, 'Expected canonical 2-second mono 16 kHz 16-bit PCM WAV');
}
async function bounded(request, limit) {
  const length = request.headers.get('content-length');
  if (length && (!/^\d+$/.test(length) || Number(length) > limit)) fail(413, 'Body too large');
  const chunks = []; let size = 0;
  const reader = request.body?.getReader();
  if (!reader) return new Uint8Array();
  try {
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      size += value.length;
      if (size > limit) { await reader.cancel(); fail(413, 'Body too large'); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const result = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { result.set(chunk, offset); offset += chunk.length; }
  return result;
}
async function body(request) {
  if (request.headers.get('content-type')?.split(';')[0] !== 'application/json') fail(415, 'JSON required');
  try {
    const result = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(await bounded(request, 8192)));
    if (!result || typeof result !== 'object' || Array.isArray(result)) fail(400, 'JSON object required');
    return result;
  }
  catch (error) { if (error.status) throw error; fail(400, 'Invalid JSON'); }
}
function publicJob(row, now) {
  const exhausted = row.state === 'running' && row.lease_until <= now && row.attempts >= row.max_attempts;
  return {id: row.id, state: exhausted ? 'failed' : row.state, progress: row.progress,
    attempts: row.attempts, text_digest: row.text_digest, audio_digest: row.audio_digest,
    lease_expired: row.state === 'running' && row.lease_until <= now};
}
function sameOrigin(request) {
  // Reject missing Origin too: owner writes are browser-only, not service-token APIs.
  if (request.headers.get('origin') !== new URL(request.url).origin) fail(403, 'Same-origin action required');
}
function owner(request, env) {
  const id = request.headers.get('oai-authenticated-user-id');
  if (!id) fail(401, 'Sign in with ChatGPT');
  if (!env.OWNER_USER_ID) fail(503, 'Owner setup required');
  if (id !== env.OWNER_USER_ID) fail(403, 'Owner access required');
  return id;
}
async function device(request, env) {
  if (!env.OWNER_USER_ID) fail(401, 'Worker not authorized');
  const auth = request.headers.get('authorization') || '';
  if (!/^Bearer [A-Za-z0-9_-]{43}$/.test(auth)) fail(401, 'Worker credential required');
  const tokenHash = await digest(auth.slice(7));
  const row = await env.DB.prepare('SELECT * FROM devices WHERE token_hash=? AND revoked=0 AND owner=?')
    .bind(tokenHash, env.OWNER_USER_ID).first();
  if (!row) fail(401, 'Worker not authorized');
  return row;
}
async function currentJob(env, id, deviceId) {
  const row = await env.DB.prepare('SELECT * FROM jobs WHERE id=? AND owner=? AND device_id=?')
    .bind(id, env.OWNER_USER_ID, deviceId).first();
  if (!row) fail(404, 'Job not found');
  return row;
}
async function lease(request, row) {
  const token = request.headers.get('x-lease-token') || '';
  if (token.length !== 36 || await digest(token) !== row.lease_hash) fail(409, 'Lease lost');
}
export function createApp({clock = () => Math.floor(Date.now() / 1000)} = {}) {
  async function route(request, env) {
    const url = new URL(request.url), path = url.pathname, method = request.method, now = clock();
    // This only exposes the authenticated caller's own Site-scoped ID for setup.
    if (path === '/api/identity' && method === 'GET') {
      const id = request.headers.get('oai-authenticated-user-id');
      if (!id) fail(401, 'Sign in with ChatGPT');
      return json({id});
    }
    if (path === '/' && method === 'GET') {
      owner(request, env);
      return new Response(HTML, {headers: {'Content-Type': 'text/html; charset=utf-8'}});
    }
    if (path === '/app.js' && method === 'GET') {
      owner(request, env);
      return new Response(JS, {headers: {'Content-Type': 'text/javascript; charset=utf-8'}});
    }
    if (!env.DB || !env.BUCKET) fail(503, 'Disposable D1/R2 bindings required');
    if (path.startsWith('/api/')) {
      const user = owner(request, env);
      if (method === 'POST') sameOrigin(request);
      if (path === '/api/devices' && method === 'POST') {
        // Only a public verifier enters this owner request, never the worker secret.
        const data = await body(request);
        if (typeof data.id !== 'string' || typeof data.token_hash !== 'string' ||
            !/^[a-zA-Z0-9_-]{1,48}$/.test(data.id) || !/^[a-f0-9]{64}$/.test(data.token_hash))
          fail(400, 'Device id and SHA-256 verifier required');
        await env.DB.prepare('INSERT INTO devices(id,owner,token_hash) VALUES(?,?,?) ON CONFLICT(id) DO NOTHING')
          .bind(data.id, user, data.token_hash).run();
        const row = await env.DB.prepare('SELECT * FROM devices WHERE id=? AND owner=?').bind(data.id, user).first();
        if (!row || row.token_hash !== data.token_hash || row.revoked) fail(409, 'Choose a new device id');
        return json({id: row.id, enrolled: true});
      }
      const revoke = path.match(/^\/api\/devices\/([a-zA-Z0-9_-]+)\/revoke$/);
      if (revoke && method === 'POST') {
        await env.DB.prepare('UPDATE devices SET revoked=1 WHERE id=? AND owner=?').bind(revoke[1], user).run();
        return json({revoked: true});
      }
      if (path === '/api/jobs' && method === 'GET') {
        const rows = await env.DB.prepare('SELECT * FROM jobs WHERE owner=? ORDER BY created_at DESC,id DESC LIMIT 20')
          .bind(user).all();
        return json({jobs: rows.results.map(row => publicJob(row, now))});
      }
      if (path === '/api/jobs' && method === 'POST') {
        const data = await body(request);
        if (data.approved !== true || typeof data.text !== 'string' || !data.text.trim() ||
            data.text.length > 1000 || typeof data.request_id !== 'string' ||
            !/^[a-zA-Z0-9_-]{16,64}$/.test(data.request_id))
          fail(400, 'Explicit approval, 1–1000 characters, and a request id required');
        const textHash = await digest(data.text);
        const id = crypto.randomUUID();
        await env.DB.prepare(`INSERT INTO jobs(id,owner,request_id,text,text_digest,created_at)
          SELECT ?,?,?,?,?,? WHERE (SELECT COUNT(*) FROM jobs WHERE owner=?) < 20
          ON CONFLICT(owner,request_id) DO NOTHING`)
          .bind(id, user, data.request_id, data.text, textHash, now, user).run();
        const row = await env.DB.prepare('SELECT * FROM jobs WHERE owner=? AND request_id=?')
          .bind(user, data.request_id).first();
        if (!row) fail(429, 'Disposable proof is capped at 20 jobs');
        if (row.text_digest !== textHash) fail(409, 'Request id already binds different text');
        return json(publicJob(row, now));
      }
      const retry = path.match(/^\/api\/jobs\/([a-f0-9-]{36})\/retry$/);
      if (retry && method === 'POST') {
        const row = await env.DB.prepare(`UPDATE jobs SET max_attempts=max_attempts+3
          WHERE id=? AND owner=? AND state='running' AND lease_until<=? AND attempts>=max_attempts
          AND max_attempts=3 RETURNING *`).bind(retry[1], user, now).first();
        if (!row) fail(409, 'Only one retry budget of three attempts is allowed');
        return json(publicJob(row, now));
      }
      const audio = path.match(/^\/api\/jobs\/([a-f0-9-]{36})\/audio$/);
      if (audio && method === 'GET') {
        const row = await env.DB.prepare("SELECT * FROM jobs WHERE id=? AND owner=? AND state='succeeded'")
          .bind(audio[1], user).first();
        if (!row) fail(404, 'Completed audio not found');
        const object = await env.BUCKET.get(row.object_key);
        if (!object) fail(503, 'Stored audio unavailable');
        // Tiny fixed-format proof only: bounded full-object read, then exact range.
        const bytes = new Uint8Array(await object.arrayBuffer());
        validWav(bytes);
        if (await digest(bytes) !== row.audio_digest) fail(503, 'Stored audio integrity failure');
        let start = 0, end = bytes.length - 1, status = 200;
        const range = request.headers.get('range');
        const headers = new Headers({'Content-Type': 'audio/wav', 'Accept-Ranges': 'bytes',
          'Content-Disposition': (url.searchParams.has('download') ? 'attachment' : 'inline') + '; filename="voxfoundry-test-tone.wav"'});
        if (range) {
          const match = /^bytes=(\d*)-(\d*)$/.exec(range);
          if (!match || (!match[1] && !match[2])) return new Response(null, {status: 416, headers: {'Content-Range': 'bytes */' + bytes.length}});
          if (!match[1]) start = Math.max(0, bytes.length - Number(match[2]));
          else { start = Number(match[1]); if (match[2]) end = Math.min(end, Number(match[2])); }
          if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start > end || start >= bytes.length)
            return new Response(null, {status: 416, headers: {'Content-Range': 'bytes */' + bytes.length}});
          status = 206; headers.set('Content-Range', `bytes ${start}-${end}/${bytes.length}`);
        }
        headers.set('Content-Length', String(end - start + 1));
        return new Response(bytes.slice(start, end + 1), {status, headers});
      }
    }
    if (path.startsWith('/worker/')) {
      const worker = await device(request, env);
      if (path === '/worker/ping' && method === 'GET') return json({authenticated: true, device_id: worker.id});
      if (path === '/worker/jobs/claim' && method === 'POST') {
        const token = crypto.randomUUID(), hash = await digest(token);
        const result = await env.DB.batch([
          env.DB.prepare(`UPDATE jobs SET state='running', device_id=?, lease_hash=?, lease_until=?,
            attempts=attempts+1, progress=0 WHERE id=(SELECT id FROM jobs WHERE owner=? AND attempts<max_attempts
            AND (state='queued' OR (state='running' AND lease_until<=?)) ORDER BY created_at,id LIMIT 1)
            AND EXISTS(SELECT 1 FROM devices WHERE id=? AND revoked=0) RETURNING *`)
            .bind(worker.id, hash, now + LEASE_SECONDS, worker.owner, now, worker.id),
          env.DB.prepare(`INSERT INTO attempts(job_id,number,device_id,lease_hash,started_at)
            SELECT id,attempts,device_id,lease_hash,? FROM jobs WHERE lease_hash=?`).bind(now, hash)
        ]);
        const row = result[0].results[0];
        return json({job: row ? {id: row.id, text: row.text, text_digest: row.text_digest, lease_token: token,
          lease_until: row.lease_until, format: 'tone-v1'} : null});
      }
      const match = path.match(/^\/worker\/jobs\/([a-f0-9-]{36})(?:\/(heartbeat|result))?$/);
      if (match) {
        const row = await currentJob(env, match[1], worker.id);
        if (!match[2] && method === 'GET') return json(publicJob(row, now));
        if (method !== 'POST') fail(405, 'Method not allowed');
        await lease(request, row);
        if (match[2] === 'heartbeat') {
          const data = await body(request);
          if (!Number.isInteger(data.progress) || data.progress < 0 || data.progress > 99) fail(400, 'Invalid progress');
          const heartbeatTime = clock();
          const updated = await env.DB.prepare(`UPDATE jobs SET progress=MAX(progress,?), lease_until=?
            WHERE id=? AND lease_hash=? AND state='running' AND lease_until>?
            AND EXISTS(SELECT 1 FROM devices WHERE id=? AND revoked=0) RETURNING *`)
            .bind(data.progress, heartbeatTime + LEASE_SECONDS, row.id, row.lease_hash, heartbeatTime, worker.id).first();
          if (!updated) fail(409, 'Lease lost');
          return json(publicJob(updated, now));
        }
        if (match[2] === 'result') {
          if (request.headers.get('content-type') !== 'audio/wav') fail(415, 'audio/wav required');
          if (row.state !== 'succeeded' && row.lease_until <= now) fail(409, 'Lease expired');
          const bytes = await bounded(request, MAX_AUDIO); validWav(bytes);
          const audioHash = await digest(bytes);
          if (request.headers.get('x-audio-sha256') !== audioHash) fail(400, 'Upload digest mismatch');
          if (row.state === 'succeeded') {
            if (row.audio_digest !== audioHash) fail(409, 'Immutable completed audio differs');
            return json(publicJob(row, now)); // lost-ack retry, same device and lease
          }
          // Attempt- and content-addressed keys cannot overwrite a newer result.
          const key = `phase0/${row.id}/${row.lease_hash}/${audioHash}.wav`;
          await env.BUCKET.put(key, bytes, {httpMetadata: {contentType: 'audio/wav'}});
          const updated = await env.DB.prepare(`UPDATE jobs SET state='succeeded',progress=100,audio_digest=?,object_key=?
            WHERE id=? AND lease_hash=? AND state='running' AND lease_until>?
            AND EXISTS(SELECT 1 FROM devices WHERE id=? AND revoked=0) RETURNING *`)
            .bind(audioHash, key, row.id, row.lease_hash, clock(), worker.id).first();
          if (!updated) {
            // Another identical upload might already have committed this key. Never delete it.
            const current = await currentJob(env, row.id, worker.id);
            if (current.object_key === key && current.state === 'succeeded') return json(publicJob(current, clock()));
            fail(409, 'Upload stored but lease lost; orphan retained for cleanup');
          }
          return json(publicJob(updated, clock()));
        }
      }
    }
    fail(404, 'Not found');
  }
  return {async fetch(request, env) {
    let response;
    try { response = await route(request, env); }
    catch (error) { response = json({error: error.status ? error.message : 'Operation failed; preserve request id and retry'}, error.status || 500); }
    const headers = new Headers(response.headers);
    headers.set('Cache-Control', 'private, no-store');
    headers.set('X-Content-Type-Options', 'nosniff');
    headers.set('Referrer-Policy', 'no-referrer');
    // No CORS grant. Sites embedding policy is left to the platform.
    headers.set('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; media-src 'self'; base-uri 'none'; form-action 'self'");
    return new Response(response.body, {status: response.status, headers});
  }};
}
export default createApp();

const HTML = `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VoxFoundry · Audio transport proof</title>
<style>body{margin:0;background:#111820;color:#e9e8df;font:17px/1.5 system-ui}main{max-width:700px;margin:auto;padding:24px 18px}h1{font:2.3rem Georgia;margin:16px 0}small{color:#b8c9c6}section,article{background:#1c2931;padding:18px;border-radius:14px;margin:18px 0}textarea,input,button,a{font:inherit}textarea{box-sizing:border-box;width:100%;min-height:140px;padding:12px;background:#111820;color:inherit;border:1px solid #758c91;border-radius:8px}button,.download{min-height:44px;padding:10px 16px;border:0;border-radius:8px;background:#c5ddae;color:#15201a;display:inline-block;margin:8px 8px 8px 0}button:disabled{opacity:.55}input[type=checkbox]{width:24px;height:24px;vertical-align:middle}label{display:block;padding:12px 0;min-height:44px;box-sizing:border-box}audio,progress{width:100%}a{color:#c5ddae}#message{min-height:2em;overflow-wrap:anywhere}summary{min-height:44px;cursor:pointer}input[type=text]{box-sizing:border-box;width:100%;min-height:44px}code{overflow-wrap:anywhere}button:focus-visible,a:focus-visible,textarea:focus-visible{outline:3px solid #f2c879;outline-offset:3px}</style>
<main><small>VOXFOUNDRY / PHASE 0</small><h1>A small signal.<br>A complete round trip.</h1><p>Approve a short passage, then follow its test audio from the outbound worker to private storage.</p>
<section><strong>Test tone only — no speech synthesis.</strong><p>The result is a two-second tone. Your passage stays in this disposable proof. Maximum 1,000 characters and 20 jobs.</p>
<form id="submit"><label for="text">Test passage</label><textarea id="text" maxlength="1000" required placeholder="A short, non-sensitive passage you approve for this test."></textarea><label><input id="approved" type="checkbox" required> I approve this exact passage for the test-tone job.</label><button id="send">Approve &amp; queue</button></form></section>
<p id="message" role="status" aria-live="polite"></p><button id="refresh" type="button">Refresh jobs</button><div id="jobs"></div>
<details><summary>Worker setup &amp; revocation</summary><p>Generate a device verifier with the local setup script. Paste only its public ID and SHA-256 verifier here. Never paste a service credential or worker token.</p><label for="device">Public device ID</label><input id="device" type="text" maxlength="48"><label for="verifier">Public SHA-256 verifier</label><input id="verifier" type="text" maxlength="64"><button id="enroll" type="button">Enroll device verifier</button><button id="revoke" type="button">Revoke device</button></details>
<p><small>No worker? Jobs remain queued. Completed audio is served from central storage after the worker exits. This is a transport experiment, not a production studio.</small></p></main><script src="/app.js" defer></script></html>`;
const JS = String.raw`
const $ = id => document.getElementById(id);
let pending = null, submitting = false;
async function api(path, data) {
  const response = await fetch(path, data === undefined ? {cache:'no-store'} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw Error(result.error || 'Request failed');
  return result;
}
function message(value) { $('message').textContent = value; }
async function refresh() {
  try {
    const {jobs} = await api('/api/jobs');
    const fragment = document.createDocumentFragment();
    for (const job of jobs) {
      const card = document.createElement('article');
      const title = document.createElement('h2'); title.textContent = job.state + ' · ' + job.progress + '%'; card.append(title);
      const text = document.createElement('p'); text.textContent = 'Job ' + job.id + ' · attempts ' + job.attempts; card.append(text);
      const progress = document.createElement('progress'); progress.max = 100; progress.value = job.progress; progress.setAttribute('aria-label','Job progress'); card.append(progress);
      if (job.lease_expired && job.state !== 'failed') { const p=document.createElement('p'); p.textContent='Worker lease expired; waiting for a new claim.'; card.append(p); }
      if (job.state === 'failed' && job.attempts === 3) {
        const retry=document.createElement('button'); retry.textContent='Approve three more attempts'; retry.onclick=async()=>{try{await api('/api/jobs/'+job.id+'/retry',{});await refresh();}catch(e){message(e.message);}};card.append(retry);
      }
      if (job.state === 'succeeded') {
        const audio = document.createElement('audio'); audio.controls = true; audio.preload = 'none'; audio.src = '/api/jobs/'+job.id+'/audio'; card.append(audio);
        const link = document.createElement('a'); link.className='download'; link.href=audio.src+'?download=1';link.textContent='Download test tone';link.download='voxfoundry-test-tone.wav';card.append(link);
      }
      fragment.append(card);
    }
    $('jobs').replaceChildren(fragment);
  } catch(e) { message('Refresh failed; previous results retained. ' + e.message); }
}
$('text').addEventListener('input',()=>{$('approved').checked=false; pending=null;});
$('submit').addEventListener('submit',async event=>{
  event.preventDefault(); if(submitting || !$('approved').checked) return;
  submitting=true; $('send').disabled=true; $('text').disabled=true; $('approved').disabled=true;
  const text=$('text').value;
  if(!pending || pending.text!==text) pending={text, request_id:crypto.randomUUID()};
  try { const job=await api('/api/jobs',{...pending,approved:true});message('Job queued: '+job.id); pending=null; $('approved').checked=false;await refresh(); }
  catch(e){message(e.message+' Retry without editing to reuse the request id.');}
  finally{submitting=false;$('send').disabled=false;$('text').disabled=false;$('approved').disabled=false;}
});
$('refresh').onclick=refresh;
$('enroll').onclick=async()=>{try{await api('/api/devices',{id:$('device').value,token_hash:$('verifier').value});message('Device enrolled.');}catch(e){message(e.message);}};
$('revoke').onclick=async()=>{try{await api('/api/devices/'+encodeURIComponent($('device').value)+'/revoke',{});message('Device revoked. Active leases can no longer commit.');}catch(e){message(e.message);}};
refresh();
// Manual refresh avoids continuous database reads while this disposable page is idle.
`;
