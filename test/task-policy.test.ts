import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { test } from 'node:test';
import { ACTION, assess, beginTask, Catalog, exportNQuads, GAP, LearnerRecord, Observation, OUTCOME } from '../src/engine';
const catalog: Catalog = JSON.parse(readFileSync('app-assets/adaptive-learning/catalog.json','utf8'));
const activity = catalog.activities.find(a => a.assessment)!;
const record = (): LearnerRecord => ({schema:'al-learner-record/0.1',learner:'urn:uuid:11111111-1111-4111-8111-111111111111',audience:catalog.audiences[0].iri,guidance:{},observations:[]});
function observation(taskId='practice', guidance=0, submission=1, incorrect: string[]=[]): Observation {
 const task=activity.assessment!.tasks.find(t=>t.id===taskId)!;
 return {iri:`urn:uuid:22222222-2222-4222-8222-${String(submission).padStart(12,'0')}`,activity:activity.iri,object:activity.iri+'/'+taskId,action:ACTION.outputValidated,
 outcome:incorrect.length ? OUTCOME.incorrect : OUTCOME.correct,guidanceLevel:guidance,at:`2026-10-22T12:00:${String(submission).padStart(2,'0')}Z`,
 attempt:{id:'urn:task-attempt:'+taskId,activity:activity.iri,taskId,version:activity.assessment!.version,mode:task.mode,guidanceLevel:guidance,submissions:submission,startedAt:'2026-10-22T12:00:00Z'},
 criteria:task.tables.map(t=>({id:t.id,outcome:incorrect.includes(t.id)?'incorrect':'correct',selection:incorrect.includes(t.id) ? (t.rowUnit==='case'?'aggregate':'case') : (t.rowUnit==='case'?'case':'aggregate')}))};
}
function result(observations: Observation[]) {return assess(catalog,{...record(),observations});}

test('practice preserves success but assigns no proficiency level or achieved target',()=>{
 for(const hints of [0,2,3]) {
  const a=result([observation('practice',hints)]);
  assert.equal(a.taskProgress[0].label,hints ? 'Practice completed with assistance':'Practice completed without recorded hints');
  assert.equal(a.gaps.find(g=>g.capability===activity.capabilities[0])!.state,GAP.unknown);
  assert.equal(a.evidence.length,0);
 }
});
test('legacy and obsolete-version successes do not satisfy the new assessment policy',()=>{
 const legacy=observation();delete legacy.attempt;delete legacy.criteria;
 const old=observation('new-case-1');old.attempt!.version='old-version';old.iri+='-old';
 assert.equal(result([legacy,old]).taskProgress[0].demonstrated,false);
});
test('three practice hints do not block a first complete correct response on a different case',()=>{
 const r=record();r.guidance[activity.iri]=3;r.observations=[observation('practice',3)];
 r.taskAttempts=[r.observations[0].attempt!];
 const next=beginTask(r,activity,'reassessment','urn:uuid:44444444-4444-4444-8444-444444444444','2026-10-22T13:00:00Z');
 assert.equal(next.guidanceLevel,0);assert.equal(r.guidance[activity.iri],3);
 const fresh=observation(next.taskId);fresh.iri+='-fresh';fresh.at='2026-10-22T13:01:00Z';
 const a=result([...r.observations,fresh]);
 assert.equal(a.taskProgress[0].label,'Demonstrated on a different case');
 assert.equal(a.gaps.find(g=>g.capability===activity.capabilities[0])!.state,GAP.achieved);
 assert.equal(a.estimates.find(e=>e.capability===activity.capabilities[0])!.level,undefined);
});
test('correcting a case after feedback does not masquerade as a first independent submission',()=>{
 const wrong=observation('new-case-1',0,1,['a']);
 const corrected=observation('new-case-1',0,2);
 const a=result([wrong,corrected]);assert.equal(a.taskProgress[0].demonstrated,false);assert.equal(a.evidence.length,0);
 assert.match(a.taskProgress[0].label,/after feedback/);
});
test('misclassifying individual records and grouped summaries yields different targeted help',()=>{
 const caseMistake=result([observation('practice',0,1,['a'])]).taskProgress[0];
 const groupMistake=result([observation('practice',0,1,['b'])]).taskProgress[0];
 assert.match(caseMistake.suggestions[0],/individual-record/);assert.match(groupMistake.suggestions[0],/grouped summary/);
});
test('a later incorrect result requests a recheck without erasing successful evidence',()=>{
 const pass=observation('new-case-1');
 const miss=observation('new-case-2',0,2,['a']);
 const a=result([pass,miss]);assert.equal(a.taskProgress[0].recheck,true);assert.equal(a.taskProgress[0].demonstrated,false);assert.equal(a.evidence.length,1);
 const recheck=observation('new-case-3',0,3);recheck.attempt!.submissions=1;
 assert.equal(result([pass,miss,recheck]).taskProgress[0].demonstrated,true);
});
test('previously displayed cases and reruns cannot manufacture fresh cases; exhaustion is explicit',()=>{
 const r=record();r.observations=[observation()];r.taskAttempts=[r.observations[0].attempt!];
 for(let i=1;i<=3;i++) {
  const next=beginTask(r,activity,'reassessment','attempt-'+i,'2026-10-22T13:00:00Z');
  assert.equal(next.taskId,'new-case-'+i);r.taskAttempts.push(next);
 }
 assert.throws(()=>beginTask(r,activity,'reassessment','last','2026-10-22T13:00:00Z'),/seen all three/);
});
test('task mode, version, criterion outcomes and progress labels survive the evidence export',async()=>{
 const r=record();r.observations=[observation('practice',3),observation('new-case-1',0,2)];r.observations[1].attempt!.submissions=1;
 r.taskAttempts=r.observations.map(o=>o.attempt!);
 const exported=await exportNQuads(catalog,r,assess(catalog,r),{generatedAt:'2026-10-22T13:00:00Z'});
 assert.match(exported,/assessment#taskVersion/);assert.match(exported,/assessment#TaskAttempt/);assert.match(exported,/assessment#criterionResult/);assert.match(exported,/assessment#classification/);assert.match(exported,/Demonstrated on a different case/);
 writeFileSync('test-results/learner-export-task-pilot.nq',exported);
});
