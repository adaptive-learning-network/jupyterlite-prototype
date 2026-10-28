import assert from 'node:assert/strict';
import {test} from 'node:test';
import {readFileSync} from 'node:fs';
import {ACTION,assess,beginTask,Catalog,LearnerRecord,OUTCOME,TaskAttempt} from '../src/engine';
import {decryptBackup,encryptBackup} from '../src/portability/crypto';
import {portableRecord,previewImport,readPortable,validateRecord} from '../src/portability/record';
import {LearnerStore} from '../src/extension/store';

const catalog=JSON.parse(readFileSync('app-assets/adaptive-learning/catalog.json','utf8')) as Catalog;
const activity=catalog.activities.find(a=>a.assessment)!;
const date='2026-10-28T12:00:00.000Z';
const password='A long test-only backup password';
const uuid=(n:number)=>`urn:uuid:00000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const fresh=(id=1):LearnerRecord=>({schema:'al-learner-record/0.1',learner:uuid(id),audience:catalog.audiences[0].iri,observations:[],guidance:{}});
function fixture(): LearnerRecord {
 const r=fresh();
 const a:TaskAttempt={id:uuid(2),activity:activity.iri,taskId:'practice',version:activity.assessment!.version,mode:'practice',guidanceLevel:3,submissions:1,startedAt:date};
 r.taskAttempts=[a];r.guidance[activity.iri]=3;
 r.observations=[{iri:uuid(3),activity:activity.iri,object:activity.iri+'/practice',action:ACTION.outputValidated,outcome:OUTCOME.correct,guidanceLevel:3,at:date,language:'python',attempt:{...a},
  criteria:activity.assessment!.tasks[0].tables.map(t=>({id:t.id,outcome:'correct',selection:t.rowUnit==='case'?'case':'aggregate'}))}];
 r.reflections={'exercise:example':[{id:'q1',version:1,prompt:'What does one row represent?',answer:'One individual case.',savedAt:date,history:[{prompt:'Earlier wording',answer:'My earlier answer.',savedAt:'2026-10-27T12:00:00Z'}]}]};
 return r;
}
test('encrypted backup round-trips all record fields, authenticates bytes and excludes sign-in',async()=>{
 const r=fixture();r.identity={iri:uuid(9),issuer:'https://login.example.org',subject:'opaque-subject',boundAt:date,verifiedAt:date,consent:{iri:uuid(10),purpose:'link',revision:'1',consentedAt:date}};
 const p=portableRecord(catalog,r,date),file=await encryptBackup(p,password);
 assert.ok(!file.includes('One individual case.'));assert.ok(!file.includes(r.learner));assert.ok(!JSON.stringify(p).includes('opaque-subject'));
 assert.deepEqual(readPortable(await decryptBackup(file,password),catalog),p);
 const restored=previewImport(catalog,fresh(5),p);
 assert.equal(restored.mode,'continue');assert.equal(restored.record.learner,r.learner);
 assert.deepEqual(assess(catalog,restored.record),assess(catalog,r));assert.equal(restored.record.identity,undefined);
 await assert.rejects(decryptBackup(file,'This is the wrong password'),/incorrect or.*damaged/);
 const e=JSON.parse(file);e.ciphertext=(e.ciphertext[0]==='A'?'B':'A')+e.ciphertext.slice(1);
 await assert.rejects(decryptBackup(JSON.stringify(e),password),/incorrect or.*damaged/);
 assert.notEqual(file,await encryptBackup(p,password));
});
test('unsupported encryption, plaintext, oversized input and short passwords fail before import',async()=>{
 await assert.rejects(encryptBackup(portableRecord(catalog,fresh(),date),'short'),/12 to 1024/);
 await assert.rejects(decryptBackup('<urn:learner> <predicate> <object> .',password),/not an encrypted/);
 await assert.rejects(decryptBackup(JSON.stringify({format:'al-encrypted-backup/2'}),password),/not supported/);
 const e=JSON.parse(await encryptBackup(portableRecord(catalog,fresh(),date),password));e.iterations=1;
 await assert.rejects(decryptBackup(JSON.stringify(e),password),/not supported/);
 await assert.rejects(decryptBackup('a'.repeat(10*1024*1024+1),password),/too large/);
});
test('same-record merge is idempotent and preserves guidance and reflection history',()=>{
 const r=fixture(),incoming=structuredClone(r);
 incoming.reflections!['exercise:example'][0]={id:'q1',version:1,prompt:'What is one row?',answer:'A case, even with a household-size number.',savedAt:'2026-10-28T13:00:00Z'};
 incoming.guidance[activity.iri]=2;
 const before=JSON.stringify(r),p=portableRecord(catalog,incoming,date);
 const one=previewImport(catalog,r,p),two=previewImport(catalog,one.record,p);
 assert.equal(one.mode,'merge');assert.equal(one.newObservations,0);assert.equal(one.record.guidance[activity.iri],3);
 assert.equal(one.record.reflections!['exercise:example'][0].answer,incoming.reflections!['exercise:example'][0].answer);
 assert.equal(one.record.reflections!['exercise:example'][0].history!.length,2);
 assert.deepEqual(two.record,one.record);assert.equal(JSON.stringify(r),before);
});
test('same timestamp reflection conflict retains both answers and keeps local current',()=>{
 const r=fixture(),other=fixture();other.reflections!['exercise:example'][0].answer='Another saved explanation';
 const merged=previewImport(catalog,r,portableRecord(catalog,other,date)).record;
 const entry=merged.reflections!['exercise:example'][0];assert.equal(entry.answer,'One individual case.');
 assert.ok(entry.history!.some(h=>h.answer==='Another saved explanation'));
});
test('different learner with work or sign-in cannot be overwritten; course and audience are checked',()=>{
 const p=portableRecord(catalog,fixture(),date),local=fixture();local.learner=uuid(6);
 assert.throws(()=>previewImport(catalog,local,p),/different learner/);
 const linked=fresh(7);linked.identity={iri:uuid(9),issuer:'https://login.example.org',subject:'opaque',boundAt:date,verifiedAt:date,consent:{iri:uuid(10),purpose:'link',revision:'1',consentedAt:date}};
 assert.throws(()=>previewImport(catalog,linked,p),/different learner/);
 assert.throws(()=>readPortable({...p,framework:'https://other.example/course'},catalog),/different course/);
 assert.throws(()=>readPortable({...p,record:{...p.record,audience:'https://unknown.example/audience'}},catalog));
 assert.ok(previewImport(catalog,fresh(3),{...p,catalogDigest:'older-version'}).courseChanged);
});
test('malformed records, prototype keys, unknown fields and conflicting IDs are rejected',()=>{
 const r=fixture();
 assert.throws(()=>validateRecord({...r,unexpected:true},catalog));
 assert.throws(()=>validateRecord({...r,identity:{}},catalog));
 assert.throws(()=>validateRecord({...r,reflections:JSON.parse('{"__proto__":[]}')},catalog));
 assert.throws(()=>validateRecord({...r,observations:[{...r.observations[0],guidanceLevel:-1}]},catalog));
 assert.throws(()=>validateRecord({...r,observations:[...r.observations,...r.observations]},catalog));
 const other=fixture();other.observations[0].object+='-changed';
 assert.throws(()=>previewImport(catalog,r,portableRecord(catalog,other,date)),/same attempt identifier/);
});
test('seen unsubmitted cases survive restore and cannot be presented as fresh again',()=>{
 const r=fixture();
 const next=beginTask(r,activity,'reassessment',uuid(4),'2026-10-28T12:01:00Z');
 r.taskAttempts!.push(next);
 const restored=previewImport(catalog,fresh(8),portableRecord(catalog,r,date)).record;
 assert.equal(beginTask(restored,activity,'reassessment',uuid(5),'2026-10-28T12:02:00Z').taskId,'new-case-2');
 assert.equal(restored.taskAttempts!.find(a=>a.id===uuid(2))!.guidanceLevel,3);
});
test('conflicting complete submissions and duplicate different-case attempts cannot manufacture independent success',()=>{
 const a=fixture(),b=fixture();
 b.observations[0].iri=uuid(11);
 assert.throws(()=>previewImport(catalog,a,portableRecord(catalog,b,date)),/conflicting submission/);
 a.taskAttempts!.push(beginTask(a,activity,'reassessment',uuid(4),date));
 b.taskAttempts!.push(beginTask(b,activity,'reassessment',uuid(5),date));
 b.observations[0].iri=uuid(3);
 assert.throws(()=>previewImport(catalog,a,portableRecord(catalog,b,date)),/divergent attempts/);
});
test('storage failure and edits after preview leave memory and durable record unchanged',()=>{
 const values=new Map<string,string>();let blocked=false;
 const previous=Object.getOwnPropertyDescriptor(globalThis,'localStorage');
 Object.defineProperty(globalThis,'localStorage',{configurable:true,value:{getItem:(k:string)=>values.get(k)??null,setItem:(k:string,v:string)=>{if(blocked)throw new Error('quota');values.set(k,v);}}});
 try {
  const store=new LearnerStore(catalog.audiences[0].iri),before=JSON.stringify(store.record),expected=store.portabilitySnapshot();
  const p=previewImport(catalog,store.record,portableRecord(catalog,fixture(),date));
  blocked=true;assert.throws(()=>store.importPortable(p.record,expected),/could not save/);
  assert.equal(JSON.stringify(store.record),before);assert.equal(values.get('al-engine:learner-record:v0.1'),before);
  blocked=false;values.set('al-engine:learner-record:v0.1',JSON.stringify(fresh(12)));
  assert.throws(()=>store.importPortable(p.record,expected),/Another tab changed/);assert.equal(JSON.stringify(store.record),before);
 }finally{if(previous)Object.defineProperty(globalThis,'localStorage',previous);else Reflect.deleteProperty(globalThis,'localStorage');}
});
