import {HTML, JS} from './ui.js';

// Sites supplies trusted identity headers at its private dispatch boundary.
// This code still authorizes every data request; it does not implement OAuth.
export const LIMITS = Object.freeze({body:262144, content:50000, projects:50, documents:500, export:2097152});
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const encoder = new TextEncoder();
function fail(status, message) { throw Object.assign(new Error(message), {status}); }
export async function digest(text) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', encoder.encode(text)))]
    .map(n=>n.toString(16).padStart(2,'0')).join('');
}
function json(data, status=200) {return new Response(JSON.stringify(data), {status, headers:{'Content-Type':'application/json; charset=utf-8'}});}
function owned(request, env) {
  const user=request.headers.get('oai-authenticated-user-id');
  if (!user) fail(401,'Sign in to open your workspace.');
  if (!env.OWNER_USER_ID) fail(503,'Workspace setup is incomplete.');
  if (user!==env.OWNER_USER_ID) fail(403,'This workspace belongs to another account.');
  if (!env.DB) fail(503,'Workspace storage is not connected yet.');
  return user;
}
function origin(request) {
  if (request.headers.get('origin')!==new URL(request.url).origin) fail(403,'Use a same-origin workspace action.');
}
async function readBody(request) {
  if (request.headers.get('content-type')?.split(';')[0]!=='application/json') fail(415,'JSON is required.');
  const length=request.headers.get('content-length');
  if (length && (!/^\d+$/.test(length) || Number(length)>LIMITS.body)) fail(413,'This request is too large.');
  const reader=request.body?.getReader(); if (!reader) fail(400,'A JSON object is required.');
  const chunks=[];let size=0;
  try {
    for (;;) {
      const {done,value}=await reader.read();if(done)break;
      size+=value.length;
      if(size>LIMITS.body){await reader.cancel();fail(413,'This request is too large.');}
      chunks.push(value);
    }
  } finally {reader.releaseLock();}
  const bytes=new Uint8Array(size);let offset=0;
  for(const value of chunks){bytes.set(value,offset);offset+=value.length;}
  let value;
  try {value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}
  catch {fail(400,'A valid JSON object is required.');}
  if(!value || typeof value!=='object' || Array.isArray(value))fail(400,'A JSON object is required.');
  return value;
}
function text(value, name, max, empty=false) {
  if(typeof value!=='string' || value.length>max || (!empty && !value.trim()) || !value.isWellFormed())
    fail(400,name+' is missing, invalid or too long.');
  return value;
}
function requestKey(data) {
  if(typeof data.request_id!=='string' || !UUID.test(data.request_id))fail(400,'A valid request ID is required.');
  return data.request_id;
}
function version(data) {
  if(!Number.isSafeInteger(data.expected_version) || data.expected_version<1)fail(400,'A saved version is required.');
  return data.expected_version;
}
function project(row) {
  return {id:row.id,title:row.title,description:row.description,version:row.version,
    created_at:row.created_at,updated_at:row.updated_at,archived_at:row.archived_at};
}
function document(row) {
  return {id:row.id,project_id:row.project_id,title:row.title,content:row.content,
    version:row.version,created_at:row.created_at,updated_at:row.updated_at,archived_at:row.archived_at};
}
function revision(row) {
  return {id:row.id,document_id:row.document_id,version:row.version,title:row.title,
    content:row.content,archived_at:row.archived_at,created_at:row.created_at};
}
async function getProject(env,user,id) {
  const row=await env.DB.prepare('SELECT * FROM projects WHERE id=? AND owner=?').bind(id,user).first();
  if(!row)fail(404,'Project not found.');return row;
}
async function getDocument(env,user,id) {
  const row=await env.DB.prepare(`SELECT d.*,p.archived_at AS project_archived_at
    FROM documents d JOIN projects p ON p.id=d.project_id AND p.owner=d.owner
    WHERE d.id=? AND d.owner=?`).bind(id,user).first();
  if(!row)fail(404,'Document not found.');return row;
}
function revisionInsert(env,user,id,key,now) {
  return env.DB.prepare(`INSERT INTO document_revisions
    (id,owner,document_id,version,title,content,archived_at,created_at,operation_id)
    SELECT ?,owner,id,version,title,content,archived_at,?,? FROM documents
    WHERE id=? AND owner=? AND last_op=?`)
    .bind(crypto.randomUUID(),now,key,id,user,key);
}

// A successful write, immutable document revision and replay receipt are committed
// in one D1 batch. A duplicate key rolls the whole competing batch back, preventing
// a second object or revision. No exactly-once network delivery is assumed.
async function mutate(env,user,key,kind,payload,statements,table,id,result,now) {
  const hash=await digest(JSON.stringify([kind,payload]));
  async function replay() {
    const receipt=await env.DB.prepare('SELECT * FROM commands WHERE owner=? AND request_id=?').bind(user,key).first();
    if(!receipt)return null;
    if(receipt.request_hash!==hash)fail(409,'This request ID already belongs to a different change.');
    return json(JSON.parse(receipt.result_json));
  }
  const existing=await replay();if(existing)return existing;
  // table is an internal constant chosen by the route, never a request parameter.
  const receipt=env.DB.prepare(`INSERT INTO commands(owner,request_id,request_hash,result_json,created_at)
    SELECT ?,?,?,?,? FROM ${table} WHERE id=? AND owner=? AND last_op=?`)
    .bind(user,key,hash,JSON.stringify(result),now,id,user,key);
  let applied;
  try {applied=await env.DB.batch([...statements,receipt]);}
  catch(error) {const recovered=await replay();if(recovered)return recovered;throw error;}
  if(applied.at(-1).meta?.changes!==1) {
    const recovered=await replay();if(recovered)return recovered;
    fail(409,'The saved version changed, the item was archived, or the workspace limit was reached. Your edits have not been applied.');
  }
  return json(result);
}

export function createApp({clock=()=>Math.floor(Date.now()/1000)}={}) {
  async function route(request,env) {
    const url=new URL(request.url), path=url.pathname, method=request.method;
    if(method==='GET' && path==='/')return new Response(HTML,{headers:{'Content-Type':'text/html; charset=utf-8'}});
    if(method==='GET' && path==='/app.js')return new Response(JS,{headers:{'Content-Type':'text/javascript; charset=utf-8'}});
    if(path==='/api/identity' && method==='GET') {
      const id=request.headers.get('oai-authenticated-user-id');
      if(!id)fail(401,'Sign in to open your workspace.');
      return json({id}); // caller's own Site-scoped ID for owner setup only
    }
    if(path==='/api/session' && method==='GET') {
      const user=owned(request,env);
      return json({authenticated:true,workspace:'VoxFoundry',user_id:user});
    }
    if(!path.startsWith('/api/'))fail(404,'Not found.');
    const user=owned(request,env), now=clock();
    if(!['GET','POST','PUT','PATCH'].includes(method))fail(405,'Method not supported.');
    if(method!=='GET')origin(request);
    if(path==='/api/projects' && method==='GET') {
      const rows=await env.DB.prepare(`SELECT * FROM projects WHERE owner=?
        AND (?=1 OR archived_at IS NULL) ORDER BY updated_at DESC,id LIMIT 50`)
        .bind(user,url.searchParams.get('archived')==='1'?1:0).all();
      return json({projects:rows.results.map(project)});
    }
    if(path==='/api/projects' && method==='POST') {
      const data=await readBody(request), key=requestKey(data);
      const title=text(data.title,'Project title',120).trim();
      const description=text(data.description??'','Description',1000,true);
      const id=crypto.randomUUID();
      const result={project:{id,title,description,version:1,created_at:now,updated_at:now,archived_at:null}};
      return mutate(env,user,key,'create-project',{title,description},[
        env.DB.prepare(`INSERT INTO projects(id,owner,title,description,created_at,updated_at,last_op)
          SELECT ?,?,?,?,?,?,? WHERE (SELECT COUNT(*) FROM projects WHERE owner=?) < ?`)
          .bind(id,user,title,description,now,now,key,user,LIMITS.projects)
      ],'projects',id,result,now);
    }
    const pm=path.match(/^\/api\/projects\/([a-f0-9-]{36})(?:\/(documents|archive|export))?$/);
    if(pm) {
      const id=pm[1], action=pm[2], row=await getProject(env,user,id);
      if(!action && method==='GET')return json({project:project(row)});
      if((!action && method==='PATCH') || (action==='archive' && method==='POST')) {
        const data=await readBody(request), key=requestKey(data), expected=version(data);
        const archive=action==='archive';
        const title=archive?row.title:text(data.title,'Project title',120).trim();
        const description=archive?row.description:text(data.description??'','Description',1000,true);
        const result={project:{...project(row),title,description,version:expected+1,updated_at:now,
          archived_at:archive?now:null}};
        return mutate(env,user,key,archive?'archive-project':'edit-project',
          archive?{id,expected}:{id,expected,title,description},[
            env.DB.prepare(`UPDATE projects SET title=?,description=?,version=version+1,
              updated_at=?,archived_at=?,last_op=? WHERE id=? AND owner=? AND version=? AND archived_at IS NULL`)
              .bind(title,description,now,archive?now:null,key,id,user,expected)
          ],'projects',id,result,now);
      }
      if(action==='documents' && method==='GET') {
        const rows=await env.DB.prepare(`SELECT * FROM documents WHERE project_id=? AND owner=?
          AND (?=1 OR archived_at IS NULL) ORDER BY updated_at DESC,id LIMIT 500`)
          .bind(id,user,url.searchParams.get('archived')==='1'?1:0).all();
        return json({project:project(row),documents:rows.results.map(r=>{
          const value=document(r);delete value.content;return value;
        })});
      }
      if(action==='documents' && method==='POST') {
        const data=await readBody(request), key=requestKey(data);
        const title=text(data.title,'Document title',180).trim();
        const content=text(data.content??'','Document',LIMITS.content,true), docId=crypto.randomUUID();
        const result={document:{id:docId,project_id:id,title,content,version:1,created_at:now,updated_at:now,archived_at:null}};
        return mutate(env,user,key,'create-document',{project_id:id,title,content},[
          env.DB.prepare(`INSERT INTO documents(id,project_id,owner,title,content,created_at,updated_at,last_op)
            SELECT ?,?,?,?,?,?,?,? FROM projects WHERE id=? AND owner=? AND archived_at IS NULL
            AND (SELECT COUNT(*) FROM documents WHERE owner=?) < ?`)
            .bind(docId,id,user,title,content,now,now,key,id,user,user,LIMITS.documents),
          revisionInsert(env,user,docId,key,now)
        ],'documents',docId,result,now);
      }
      if(action==='export' && method==='GET') {
        // All reads in a single batch give an internally consistent project snapshot.
        // The SQL gate bounds raw text/row overhead before large rows enter the Worker.
        const sizeSQL=`(COALESCE((SELECT SUM(length(CAST(title AS BLOB))+length(CAST(content AS BLOB))+512)
          FROM documents WHERE project_id=? AND owner=?),0)+COALESCE((SELECT
          SUM(length(CAST(r.title AS BLOB))+length(CAST(r.content AS BLOB))+512)
          FROM document_revisions r JOIN documents d ON d.id=r.document_id AND d.owner=r.owner
          WHERE d.project_id=? AND d.owner=?),0))`;
        const sizeArgs=[id,user,id,user];
        const rows=await env.DB.batch([
          env.DB.prepare(`SELECT *,${sizeSQL} AS export_bytes FROM projects WHERE id=? AND owner=?`).bind(...sizeArgs,id,user),
          env.DB.prepare(`SELECT * FROM documents WHERE project_id=? AND owner=? AND ${sizeSQL}<=? ORDER BY id`)
            .bind(id,user,...sizeArgs,LIMITS.export),
          env.DB.prepare(`SELECT r.* FROM document_revisions r JOIN documents d ON d.id=r.document_id AND d.owner=r.owner
            WHERE d.project_id=? AND d.owner=? AND ${sizeSQL}<=? ORDER BY r.document_id,r.version`)
            .bind(id,user,...sizeArgs,LIMITS.export)
        ]);
        if(rows[0].results[0].export_bytes>LIMITS.export)
          fail(413,'This project exceeds the foundation export size limit. Its saved data has not been changed.');
        const value={format:'voxfoundry-project/v1',exported_at:now,project:project(rows[0].results[0]),
          documents:rows[1].results.map(document),revisions:rows[2].results.map(revision)};
        const response=json(value);
        response.headers.set('Content-Disposition','attachment; filename="voxfoundry-project-'+id+'.json"');
        return response;
      }
    }
    const dm=path.match(/^\/api\/documents\/([a-f0-9-]{36})(?:\/(revisions|archive))?$/);
    if(dm) {
      const id=dm[1], action=dm[2], row=await getDocument(env,user,id);
      if(!action && method==='GET')return json({document:document(row),project_archived:row.project_archived_at!==null});
      if(action==='revisions' && method==='GET') {
        const rows=await env.DB.prepare(`SELECT * FROM document_revisions WHERE document_id=? AND owner=?
          ORDER BY version DESC LIMIT 20`).bind(id,user).all();
        return json({revisions:rows.results.map(revision)});
      }
      if((!action && method==='PUT') || (action==='archive' && method==='POST')) {
        const data=await readBody(request), key=requestKey(data), expected=version(data), archive=action==='archive';
        const title=archive?row.title:text(data.title,'Document title',180).trim();
        const content=archive?row.content:text(data.content,'Document',LIMITS.content,true);
        const result={document:{...document(row),title,content,version:expected+1,updated_at:now,archived_at:archive?now:null}};
        return mutate(env,user,key,archive?'archive-document':'save-document',
          archive?{id,expected}:{id,expected,title,content},[
            env.DB.prepare(`UPDATE documents SET title=?,content=?,version=version+1,updated_at=?,archived_at=?,last_op=?
              WHERE id=? AND owner=? AND version=? AND archived_at IS NULL
              AND EXISTS(SELECT 1 FROM projects p WHERE p.id=documents.project_id AND p.owner=? AND p.archived_at IS NULL)`)
              .bind(title,content,now,archive?now:null,key,id,user,expected,user),
            revisionInsert(env,user,id,key,now)
          ],'documents',id,result,now);
      }
    }
    fail(404,'Not found.');
  }
  return {async fetch(request,env) {
    let response;
    try {response=await route(request,env);}
    catch(error){response=json({error:error.status?error.message:'The change could not be confirmed. Keep your edits and retry the same request.'},error.status||500);}
    const headers=new Headers(response.headers);
    headers.set('Cache-Control','private, no-store');headers.set('X-Content-Type-Options','nosniff');
    headers.set('Referrer-Policy','no-referrer');
    headers.set('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'self'");
    return new Response(response.body,{status:response.status,headers});
  }};
}
export default createApp();
