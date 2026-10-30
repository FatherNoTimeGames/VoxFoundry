import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {Script} from 'node:vm';
import {createApp,LIMITS} from '../worker/index.js';
import {HTML,JS} from '../worker/ui.js';

// Executes actual SQLite SQL behind a local D1-shaped adapter. Does not implement
// or test Sites dispatch, D1 replication/session semantics or browser authentication.
class LocalD1 {
  constructor(filename=':memory:',init=true) {
    this.db=new DatabaseSync(filename);this.db.exec('PRAGMA foreign_keys=ON');
    if(init)this.db.exec(readFileSync(new URL('../schema.sql',import.meta.url),'utf8'));
  }
  prepare(sql) {
    const db=this.db,native=db.prepare(sql);let args=[];
    const statement={bind(...values){args=values;return statement;},
      async first(){return native.get(...args)||null;},
      async all(){return {results:native.all(...args)};},
      async run(){return {meta:{changes:native.run(...args).changes}};},
      execute(){const results=native.all(...args);return {results,meta:{changes:db.prepare('SELECT changes() AS n').get().n}};}};
    return statement;
  }
  async batch(statements) {
    this.db.exec('BEGIN');let result;
    try {result=statements.map((s,i)=>{if(this.failAt===i){this.failAt=null;throw Error('Injected SQL failure');}return s.execute();});this.db.exec('COMMIT');}
    catch(error){this.db.exec('ROLLBACK');throw error;}
    if(this.loseCommitAck){this.loseCommitAck=false;throw Error('Injected lost commit acknowledgment');}
    return result;
  }
}
function fixture(DB=new LocalD1()) {
  const env={DB,OWNER_USER_ID:'owner-a'}, app=createApp({clock:()=>1000});
  async function call(path,{method='GET',data,headers={},user='owner-a',environment=env,raw}={}) {
    const h=new Headers(headers);
    if(user)h.set('oai-authenticated-user-id',user);
    if(method!=='GET'&&!h.has('origin'))h.set('origin','https://studio.example');
    if(data!==undefined)h.set('content-type','application/json');
    return app.fetch(new Request('https://studio.example'+path,{method,headers:h,
      body:raw??(data===undefined?undefined:JSON.stringify(data))}),environment);
  }
  async function api(path,options){const response=await call(path,options);return {status:response.status,body:await response.json(),headers:response.headers};}
  async function project(title='A world in progress',key=crypto.randomUUID(),options={}) {
    const r=await api('/api/projects',{method:'POST',data:{title,description:'Research and stories.',request_id:key},...options});
    assert.equal(r.status,200,JSON.stringify(r.body));return r.body.project;
  }
  async function document(projectId,content='A first page.',options={}) {
    const r=await api('/api/projects/'+projectId+'/documents',{method:'POST',data:{title:'First page',content,request_id:crypto.randomUUID()},...options});
    assert.equal(r.status,200,JSON.stringify(r.body));return r.body.document;
  }
  async function save(doc,content,request_id=crypto.randomUUID(),options={}) {
    return api('/api/documents/'+doc.id,{method:'PUT',data:{title:doc.title,content,expected_version:doc.version,request_id},...options});
  }
  return {env,app,call,api,project,document,save};
}

test('requires trusted owner identity and fails closed without setup or storage',async()=>{
  const f=fixture();
  assert.equal((await f.call('/api/projects',{user:null})).status,401);
  assert.equal((await f.call('/api/projects',{user:'other'})).status,403);
  assert.equal((await f.call('/api/projects',{user:null,headers:{Authorization:'Bearer fake-device','OAI-Sites-Authorization':'Bearer fake-service'}})).status,401);
  assert.equal((await f.call('/api/projects',{environment:{DB:f.env.DB}})).status,503);
  assert.equal((await f.call('/api/projects',{environment:{OWNER_USER_ID:'owner-a'}})).status,503);
  assert.equal((await f.api('/api/identity')).body.id,'owner-a');
  assert.equal((await f.call('/api/identity',{user:null})).status,401);
});
test('mutations require matching Origin; no CORS grant or unsupported deletes',async()=>{
  const f=fixture(),data={title:'Test',request_id:crypto.randomUUID()};
  assert.equal((await f.api('/api/projects',{method:'POST',data,headers:{origin:'https://evil.example'}})).status,403);
  assert.equal((await f.api('/api/projects',{method:'POST',data,headers:{origin:'null'}})).status,403);
  const response=await f.call('/api/projects',{method:'OPTIONS'});
  assert.equal(response.status,405);assert.equal(response.headers.has('access-control-allow-origin'),false);
  assert.equal((await f.call('/api/projects',{method:'DELETE'})).status,405);
});
test('duplicate project creation is atomic and request IDs bind the full operation',async()=>{
  const f=fixture(),key=crypto.randomUUID();
  const results=await Promise.all([f.project('Test',key),f.project('Test',key),f.project('Test',key)]);
  assert.equal(new Set(results.map(r=>r.id)).size,1);
  assert.equal(f.env.DB.db.prepare('SELECT COUNT(*) AS n FROM projects').get().n,1);
  assert.equal(f.env.DB.db.prepare('SELECT COUNT(*) AS n FROM commands').get().n,1);
  assert.equal((await f.api('/api/projects',{method:'POST',data:{title:'Changed',description:'Research and stories.',request_id:key}})).status,409);
  assert.equal((await f.api('/api/projects/'+results[0].id+'/archive',{method:'POST',data:{expected_version:1,request_id:key}})).status,409);
});
test('project rename is version checked and replayable',async()=>{
  const f=fixture(),p=await f.project(),key=crypto.randomUUID();
  const data={title:'Renamed',description:'Updated',expected_version:1,request_id:key};
  const a=await f.api('/api/projects/'+p.id,{method:'PATCH',data});
  assert.equal(a.status,200);assert.equal(a.body.project.version,2);
  const b=await f.api('/api/projects/'+p.id,{method:'PATCH',data});assert.deepEqual(a.body,b.body);
  assert.equal((await f.api('/api/projects/'+p.id,{method:'PATCH',data:{...data,request_id:crypto.randomUUID()}})).status,409);
});
test('competing duplicate document creations commit one document and one revision',async()=>{
  const f=fixture(),p=await f.project(),key=crypto.randomUUID();
  const data={title:'One document',content:'One first revision.',request_id:key};
  const results=await Promise.all(Array.from({length:3},()=>f.api('/api/projects/'+p.id+'/documents',{method:'POST',data})));
  assert.deepEqual(results.map(r=>r.status),[200,200,200]);
  assert.equal(new Set(results.map(r=>r.body.document.id)).size,1);
  assert.equal(f.env.DB.db.prepare('SELECT COUNT(*) AS n FROM documents').get().n,1);
  assert.equal(f.env.DB.db.prepare('SELECT COUNT(*) AS n FROM document_revisions').get().n,1);
  assert.equal(f.env.DB.db.prepare('SELECT COUNT(*) AS n FROM commands').get().n,2); // project + document
});
test('every project, document, history and export lookup is owner-scoped',async()=>{
  const f=fixture(),foreignEnv={DB:f.env.DB,OWNER_USER_ID:'owner-b'},scope={user:'owner-b',environment:foreignEnv};
  const p=await f.project('Private B',crypto.randomUUID(),scope),d=await f.document(p.id,'B-only text',scope);
  for(const path of ['/api/projects/'+p.id,'/api/projects/'+p.id+'/documents','/api/projects/'+p.id+'/export','/api/documents/'+d.id,'/api/documents/'+d.id+'/revisions'])
    assert.equal((await f.call(path)).status,404,path);
  assert.equal((await f.save(d,'Intrusion')).status,404);
  assert.equal((await f.api('/api/projects')).body.projects.length,0);
  assert.equal((await f.api('/api/projects/'+p.id+'/documents',{method:'POST',data:{title:'Intrusion',content:'',request_id:crypto.randomUUID()}})).status,404);
});
test('create and save retain immutable revisions and original content',async()=>{
  const f=fixture(),p=await f.project(),d=await f.document(p.id);
  const saved=await f.save(d,'A revised page.');assert.equal(saved.status,200);assert.equal(saved.body.document.version,2);
  const history=await f.api('/api/documents/'+d.id+'/revisions');
  assert.deepEqual(history.body.revisions.map(r=>[r.version,r.content]),[[2,'A revised page.'],[1,'A first page.']]);
  assert.equal((await f.api('/api/documents/'+d.id)).body.document.content,'A revised page.');
  const listing=await f.api('/api/projects/'+p.id+'/documents');assert.equal('content' in listing.body.documents[0],false);
});
test('simultaneous saves from one base version commit only one revision',async()=>{
  const f=fixture(),p=await f.project(),d=await f.document(p.id);
  const results=await Promise.all([f.save(d,'Writer one.'),f.save(d,'Writer two.')]);
  assert.deepEqual(results.map(r=>r.status).sort(),[200,409]);
  const history=(await f.api('/api/documents/'+d.id+'/revisions')).body.revisions;
  assert.equal(history.length,2);assert.equal(history[0].content,results.find(r=>r.status===200).body.document.content);
});
test('lost save acknowledgment replays the original outcome even after a later edit',async()=>{
  const f=fixture(),p=await f.project(),d=await f.document(p.id),key=crypto.randomUUID();
  const first=await f.save(d,'Second version.',key),later=await f.save(first.body.document,'Third version.');
  assert.equal(later.status,200);
  const replay=await f.save(d,'Second version.',key);assert.deepEqual(replay.body,first.body);
  assert.equal((await f.api('/api/documents/'+d.id)).body.document.version,3);
  assert.equal((await f.api('/api/documents/'+d.id+'/revisions')).body.revisions.length,3);
  assert.equal((await f.save(d,'Different payload.',key)).status,409);
});
test('SQL failure rolls back the object, revision and receipt together; retry is safe',async()=>{
  const f=fixture(),p=await f.project(),key=crypto.randomUUID(),data={title:'Fail once',content:'Keep this.',request_id:key};
  f.env.DB.failAt=1;
  assert.equal((await f.api('/api/projects/'+p.id+'/documents',{method:'POST',data})).status,500);
  assert.equal(f.env.DB.db.prepare('SELECT COUNT(*) AS n FROM documents').get().n,0);
  assert.equal(f.env.DB.db.prepare('SELECT COUNT(*) AS n FROM document_revisions').get().n,0);
  assert.equal((await f.api('/api/projects/'+p.id+'/documents',{method:'POST',data})).status,200);
  assert.equal(f.env.DB.db.prepare('SELECT COUNT(*) AS n FROM documents').get().n,1);
});
test('unknown batch commit outcome is recovered through the durable receipt',async()=>{
  const f=fixture(),p=await f.project();f.env.DB.loseCommitAck=true;
  const d=await f.document(p.id);assert.equal(d.version,1);
  assert.equal(f.env.DB.db.prepare('SELECT COUNT(*) AS n FROM documents').get().n,1);
  assert.equal(f.env.DB.db.prepare('SELECT COUNT(*) AS n FROM document_revisions').get().n,1);
});
test('archiving keeps originals/history and disables new edits, not prior replay',async()=>{
  const f=fixture(),p=await f.project(),d=await f.document(p.id),key=crypto.randomUUID();
  const saved=await f.save(d,'Keep this version.',key),archiveKey=crypto.randomUUID();
  const archived=await f.api('/api/documents/'+d.id+'/archive',{method:'POST',data:{expected_version:2,request_id:archiveKey}});
  assert.equal(archived.status,200);assert.equal(archived.body.document.version,3);
  assert.equal((await f.save(archived.body.document,'Should fail.')).status,409);
  assert.deepEqual((await f.save(d,'Keep this version.',key)).body,saved.body);
  assert.equal((await f.api('/api/documents/'+d.id+'/revisions')).body.revisions.length,3);
  assert.equal((await f.api('/api/projects/'+p.id+'/documents')).body.documents.length,0);
  assert.equal((await f.api('/api/projects/'+p.id+'/documents?archived=1')).body.documents.length,1);
});
test('project archive preserves documents and prevents creation or editing beneath it',async()=>{
  const f=fixture(),p=await f.project(),d=await f.document(p.id);
  assert.equal((await f.api('/api/projects/'+p.id+'/archive',{method:'POST',data:{expected_version:1,request_id:crypto.randomUUID()}})).status,200);
  assert.equal((await f.api('/api/projects')).body.projects.length,0);
  assert.equal((await f.api('/api/projects?archived=1')).body.projects.length,1);
  assert.equal((await f.api('/api/documents/'+d.id)).body.project_archived,true);
  assert.equal((await f.save(d,'Not applied.')).status,409);
  assert.equal((await f.api('/api/projects/'+p.id+'/documents',{method:'POST',data:{title:'Nope',content:'',request_id:crypto.randomUUID()}})).status,409);
  assert.equal((await f.api('/api/documents/'+d.id)).body.document.content,'A first page.');
});
test('validation rejects coercion, ill-formed Unicode, wrong versions and oversized input',async()=>{
  const f=fixture();
  for(const data of [null,[],{title:'T',request_id:[crypto.randomUUID()]},{title:'\ud800',request_id:crypto.randomUUID()},{title:'T'.repeat(121),request_id:crypto.randomUUID()}])
    assert.equal((await f.api('/api/projects',{method:'POST',data})).status,400);
  const p=await f.project(),d=await f.document(p.id);
  assert.equal((await f.save(d,'x'.repeat(LIMITS.content+1))).status,400);
  assert.equal((await f.api('/api/documents/'+d.id,{method:'PUT',data:{title:'T',content:'C',expected_version:'1',request_id:crypto.randomUUID()}})).status,400);
  assert.equal((await f.call('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},raw:'x'.repeat(LIMITS.body+1)})).status,413);
  assert.equal((await f.call('/api/projects',{method:'POST',raw:'{}'})).status,415);
});
test('export contains archived data and immutable revisions without owner/receipt internals',async()=>{
  const f=fixture(),p=await f.project(),d=await f.document(p.id);await f.save(d,'Export this.');
  const exported=await f.api('/api/projects/'+p.id+'/export');
  assert.equal(exported.status,200);assert.equal(exported.body.format,'voxfoundry-project/v1');
  assert.equal(exported.body.documents[0].content,'Export this.');assert.equal(exported.body.revisions.length,2);
  assert.match(exported.headers.get('content-disposition'),/^attachment/);
  for(const field of ['owner','last_op','request_hash','operation_id'])assert.equal(JSON.stringify(exported.body).includes('"'+field+'"'),false);
  await f.api('/api/documents/'+d.id+'/archive',{method:'POST',data:{expected_version:2,request_id:crypto.randomUUID()}});
  assert.equal((await f.api('/api/projects/'+p.id+'/export')).body.documents[0].archived_at,1000);
});
test('oversized export fails without silently omitting history or changing stored data',async()=>{
  const f=fixture(),p=await f.project(),d=await f.document(p.id);
  f.env.DB.db.prepare('UPDATE document_revisions SET content=? WHERE document_id=?').run('x'.repeat(LIMITS.export+1),d.id);
  assert.equal((await f.call('/api/projects/'+p.id+'/export')).status,413);
  assert.equal(f.env.DB.db.prepare('SELECT length(content) AS n FROM document_revisions WHERE document_id=?').get(d.id).n,LIMITS.export+1);
});
test('project limit is owner-scoped and does not break replay of an earlier creation',async()=>{
  const f=fixture(),key=crypto.randomUUID(),p=await f.project('Saved project',key);
  const insert=f.env.DB.db.prepare('INSERT INTO projects(id,owner,title,created_at,updated_at,last_op) VALUES(?,?,?,?,?,?)');
  for(let i=1;i<LIMITS.projects;i++)insert.run(crypto.randomUUID(),'owner-a','Test '+i,1000,1000,'quota-seed');
  assert.equal((await f.api('/api/projects',{method:'POST',data:{title:'Overflow',request_id:crypto.randomUUID()}})).status,409);
  assert.equal((await f.project('Saved project',key)).id,p.id);
});
test('file-backed SQLite retains documents, revisions and replay receipts after close/reopen',async()=>{
  const directory=mkdtempSync(join(tmpdir(),'voxfoundry-studio-')),filename=join(directory,'site.sqlite3');
  let db=new LocalD1(filename);
  try {
    const f=fixture(db),p=await f.project(),d=await f.document(p.id),key=crypto.randomUUID();
    await f.save(d,'Durable after connection close.',key);db.db.close();db=new LocalD1(filename,false);
    const restarted=fixture(db);
    assert.equal((await restarted.api('/api/documents/'+d.id)).body.document.content,'Durable after connection close.');
    assert.equal((await restarted.api('/api/documents/'+d.id+'/revisions')).body.revisions.length,2);
    assert.equal((await restarted.save(d,'Durable after connection close.',key)).body.document.version,2);
  } finally {db.db.close();rmSync(directory,{recursive:true,force:true});}
});
test('UI uses top-level platform sign-in and safe script/CSP shape (not browser verification)',async()=>{
  const f=fixture();const response=await f.call('/',{user:null});
  assert.equal(response.status,200);assert.match(HTML,/width=device-width/);
  assert.match(HTML,/href="\/signin-with-chatgpt\?return_to=%2F" target="_top"/);
  assert.match(HTML,/aria-live="polite"/);assert.doesNotThrow(()=>new Script(JS));
  assert.equal(JS.includes('innerHTML'),false);assert.equal(JS.includes('OAI-Sites-Authorization'),false);
  assert.equal(response.headers.get('cache-control'),'private, no-store');
  assert.match(response.headers.get('content-security-policy'),/script-src 'self'/);
});
