// Validated, local-only portable records. No browser storage or UI here.
import { ACTION, assess, canonicalJson, Catalog, CriterionResult, ENGINE_VERSION, LearnerRecord, Observation, OUTCOME, ReflectionEntry, TaskAttempt, validTaskObservation } from '../engine';

export const MAX_BACKUP_BYTES = 10 * 1024 * 1024;
const MAX_ITEMS = 10000;
export interface PortableRecord {
  format: 'al-portable-record/1';
  framework: string;
  catalogDigest: string;
  engineVersion: string;
  policyVersion: string;
  createdAt: string;
  record: LearnerRecord;
}
export interface ImportPreview {
  record: LearnerRecord;
  mode: 'continue' | 'merge';
  newObservations: number;
  newAttempts: number;
  reflections: number;
  courseChanged: boolean;
}
function fail(message = 'The backup contains an invalid or unsupported learner record.'): never { throw new Error(message); }
function object(value: unknown, keys?: string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return fail();
  const result = value as Record<string, unknown>;
  if (Object.keys(result).some(k => ['__proto__', 'prototype', 'constructor'].includes(k) || (keys && !keys.includes(k)))) fail();
  return result;
}
function string(value: unknown, max = 2048): string {
  if (typeof value !== 'string' || value.length > max) return fail();
  return value;
}
function iri(value: unknown): string {
  const s = string(value);
  if (!/^(urn:|https?:\/\/)[^\s<>"\\]+$/.test(s)) fail();
  return s;
}
function integer(value: unknown, max = 100000): number {
  if (!Number.isInteger(value) || (value as number) < 0 || (value as number) > max) return fail();
  return value as number;
}
function time(value: unknown): string {
  const s = string(value, 32);
  if (!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{3})?Z$/.test(s) || !Number.isFinite(Date.parse(s)) || new Date(s).toISOString().replace('.000Z', 'Z') !== s.replace('.000Z', 'Z')) fail();
  return s;
}
function array(value: unknown): unknown[] {
  if (!Array.isArray(value) || value.length > MAX_ITEMS) return fail();
  return value;
}
function attempt(value: unknown): TaskAttempt {
  const a = object(value, ['id','activity','taskId','version','mode','guidanceLevel','submissions','startedAt']);
  if (!['practice', 'reassessment'].includes(String(a.mode))) fail();
  const taskId = string(a.taskId,128), version = string(a.version,128);
  if (!taskId || !version) fail();
  return {id:iri(a.id),activity:iri(a.activity),taskId,version,mode:a.mode as TaskAttempt['mode'],guidanceLevel:integer(a.guidanceLevel,1000),submissions:integer(a.submissions),startedAt:time(a.startedAt)};
}
function criterion(value: unknown): CriterionResult {
  const r = object(value, ['id','outcome','selection']);
  if (!['correct','incorrect','incomplete'].includes(String(r.outcome)) || ![undefined,null,'case','aggregate'].includes(r.selection as string)) fail();
  const id = string(r.id,128); if (!id) fail();
  return {id,outcome:r.outcome as CriterionResult['outcome'],...(r.selection !== undefined ? {selection:r.selection as CriterionResult['selection']} : {})};
}
function observation(value: unknown): Observation {
  const o = object(value,['iri','activity','object','action','outcome','guidanceLevel','at','language','attempt','criteria']);
  if (o.action !== ACTION.outputValidated || !Object.values(OUTCOME).includes(o.outcome as typeof OUTCOME.correct)) fail();
  return {iri:iri(o.iri),activity:iri(o.activity),object:iri(o.object),action:iri(o.action),outcome:iri(o.outcome),guidanceLevel:integer(o.guidanceLevel,1000),at:time(o.at),
    ...(o.language !== undefined ? {language:string(o.language,32)} : {}),
    ...(o.attempt !== undefined ? {attempt:attempt(o.attempt)} : {}),
    ...(o.criteria !== undefined ? {criteria:array(o.criteria).map(criterion)} : {})};
}
function reflection(value: unknown): ReflectionEntry {
  const r = object(value,['id','version','prompt','answer','savedAt','history']);
  if ((r.id === undefined) !== (r.version === undefined)) fail();
  if (r.version !== undefined && integer(r.version) === 0) fail();
  return { ...(r.id !== undefined ? {id:string(r.id,512),version:integer(r.version)} : {}),prompt:string(r.prompt,16000),answer:string(r.answer,64000),savedAt:time(r.savedAt),
    ...(r.history !== undefined ? {history:array(r.history).map(item => {
      const h=object(item,['prompt','answer','savedAt']);return {prompt:string(h.prompt,16000),answer:string(h.answer,64000),savedAt:time(h.savedAt)};
    })} : {})};
}
function immutable(a: TaskAttempt): string { return canonicalJson({id:a.id,activity:a.activity,taskId:a.taskId,version:a.version,mode:a.mode,startedAt:a.startedAt}); }

export function validateRecord(value: unknown, catalog: Catalog): LearnerRecord {
  const r = object(value,['schema','learner','audience','observations','guidance','taskAttempts','reflections']);
  if (r.schema !== 'al-learner-record/0.1') fail();
  const learner=string(r.learner);
  if (!/^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(learner)) fail();
  const guidance: Record<string,number> = {};
  for (const [key,val] of Object.entries(object(r.guidance))) guidance[iri(key)]=integer(val,1000);
  const reflections: Record<string,ReflectionEntry[]> = {};
  if (r.reflections !== undefined) for (const [key,val] of Object.entries(object(r.reflections))) {
    if (!key || key.length>512) fail();
    const entries=array(val).map(reflection);
    const identities=entries.map(reflectionKey);
    if (new Set(identities).size !== identities.length) fail('The backup contains duplicate reflection questions.');
    reflections[key]=entries;
  }
  const record: LearnerRecord = {schema:'al-learner-record/0.1',learner,audience:iri(r.audience),observations:array(r.observations).map(observation),guidance,
    ...(r.taskAttempts !== undefined ? {taskAttempts:array(r.taskAttempts).map(attempt)} : {}),
    ...(r.reflections !== undefined ? {reflections} : {})};
  const activities=new Map(catalog.activities.map(a=>[a.iri,a]));
  for (const key of Object.keys(guidance)) if (!activities.has(key)) fail('This course no longer recognizes an activity in the backup.');
  const attempts=new Map<string,TaskAttempt>(), seenCases=new Set<string>();
  for (const a of record.taskAttempts ?? []) {
    if (attempts.has(a.id) || !activities.has(a.activity)) fail();
    attempts.set(a.id,a);
    if (a.mode === 'reassessment') {
      const key=canonicalJson([a.activity,a.version,a.taskId]);
      if (seenCases.has(key)) fail('These records contain divergent attempts on the same different-case check. Keep both backups; they cannot be safely merged.');
      seenCases.add(key);
    }
    const policy=activities.get(a.activity)!.assessment;
    if (policy?.version === a.version && !policy.tasks.some(t=>t.id===a.taskId && t.mode===a.mode)) fail();
    if (a.mode === 'reassessment' && a.guidanceLevel !== 0) fail();
  }
  const counters=new Map<string,Set<number>>();
  for (const o of record.observations) {
    if (!activities.has(o.activity)) fail('This course no longer recognizes an activity in the backup.');
    if (o.criteria && !o.attempt) fail();
    if (!o.attempt) continue;
    const a=attempts.get(o.attempt.id);
    if (!a || immutable(a)!==immutable(o.attempt) || a.submissions<o.attempt.submissions || a.guidanceLevel<o.attempt.guidanceLevel || o.activity!==a.activity || o.guidanceLevel!==o.attempt.guidanceLevel) fail();
    if (o.outcome!==OUTCOME.incomplete) {
      const numbers=counters.get(a.id) ?? new Set<number>();
      if (!o.attempt.submissions || numbers.has(o.attempt.submissions)) fail('These records have conflicting submission histories. Keep both backups; they cannot be safely merged.');
      numbers.add(o.attempt.submissions);counters.set(a.id,numbers);
    }
    const activity=activities.get(o.activity)!;
    if (activity.assessment?.version === o.attempt.version) {
      if (!validTaskObservation(activity,o)) fail();
      const task=activity.assessment.tasks.find(t=>t.id===o.attempt!.taskId)!;
      for (const result of o.criteria!) {
        const unit=task.tables.find(t=>t.id===result.id)!.rowUnit;
        const expected=result.selection==null ? 'incomplete' : result.selection===(unit==='case'?'case':'aggregate') ? 'correct' : 'incorrect';
        if (result.outcome!==expected) fail('Classification choices and feedback disagree in this backup.');
      }
      const expected=o.criteria!.some(r=>r.outcome==='incomplete') ? OUTCOME.incomplete : o.criteria!.some(r=>r.outcome==='incorrect') ? OUTCOME.incorrect : OUTCOME.correct;
      if (o.outcome!==expected) fail();
    }
  }
  for (const a of attempts.values()) {
    const numbers=counters.get(a.id) ?? new Set<number>();
    if (numbers.size!==a.submissions || [...numbers].some(n=>n>a.submissions)) fail('The backup is missing part of a task submission history.');
  }
  // The same input admission used by the current adaptive-learning engine.
  assess(catalog,record);
  return record;
}
function reflectionKey(r: ReflectionEntry): string { return r.id ? canonicalJson([r.id,r.version]) : canonicalJson(['legacy',r.prompt]); }
function mergeWriting(local: ReflectionEntry[], incoming: ReflectionEntry[]): ReflectionEntry[] {
  const result=new Map(local.map(r=>[reflectionKey(r),r]));
  for (const r of incoming) {
    const key=reflectionKey(r), old=result.get(key);
    if (!old) {result.set(key,r);continue;}
    const winner=Date.parse(r.savedAt)>Date.parse(old.savedAt) ? r : old;
    const history=new Map<string,{prompt:string;answer:string;savedAt:string}>();
    for (const h of [...(old.history??[]),...(r.history??[]),old,r]) {
      const item={prompt:h.prompt,answer:h.answer,savedAt:h.savedAt};
      if (canonicalJson(item)!==canonicalJson({prompt:winner.prompt,answer:winner.answer,savedAt:winner.savedAt})) history.set(canonicalJson(item),item);
    }
    result.set(key,{...winner,...(history.size ? {history:[...history.values()].sort((a,b)=>a.savedAt.localeCompare(b.savedAt)||canonicalJson(a).localeCompare(canonicalJson(b)))} : {})});
  }
  return [...result.values()];
}
export function portableRecord(catalog: Catalog, record: LearnerRecord, createdAt: string): PortableRecord {
  const {identity: _identity,...data}=record;
  return {format:'al-portable-record/1',framework:catalog.framework.iri,catalogDigest:catalog.sourceDigest,engineVersion:ENGINE_VERSION,policyVersion:catalog.policy.version,createdAt:time(createdAt),record:validateRecord(data,catalog)};
}
export function readPortable(value: unknown, catalog: Catalog): PortableRecord {
  const p=object(value,['format','framework','catalogDigest','engineVersion','policyVersion','createdAt','record']);
  if (p.format!=='al-portable-record/1') fail('This backup version is not supported.');
  if (p.framework!==catalog.framework.iri) fail('This backup belongs to a different course.');
  return {format:'al-portable-record/1',framework:iri(p.framework),catalogDigest:string(p.catalogDigest,256),engineVersion:string(p.engineVersion,128),policyVersion:string(p.policyVersion,128),createdAt:time(p.createdAt),record:validateRecord(p.record,catalog)};
}
export function previewImport(catalog: Catalog, local: LearnerRecord, backup: PortableRecord): ImportPreview {
  const incoming=readPortable(backup,catalog).record;
  const {identity,...localData}=local;
  const current=validateRecord(localData,catalog);
  const empty=!current.observations.length && !Object.keys(current.guidance).length && !(current.taskAttempts?.length) && !Object.values(current.reflections??{}).some(a=>a.length) && !identity;
  if (current.learner!==incoming.learner && !empty) fail('This browser already contains a different learner record. Download its backup first, then import into an empty browser profile. Existing work has not changed.');
  if (!empty && current.audience!==incoming.audience) fail('The learner roles in these records differ. Existing work has not changed.');
  let merged=incoming;
  if (!empty) {
    const observations=new Map(current.observations.map(o=>[o.iri,o]));
    for (const o of incoming.observations) {
      const old=observations.get(o.iri);
      if (old && canonicalJson(old)!==canonicalJson(o)) fail('The same attempt identifier has different content in these records. Existing work has not changed.');
      observations.set(o.iri,o);
    }
    const attempts=new Map((current.taskAttempts??[]).map(a=>[a.id,a]));
    for (const a of incoming.taskAttempts??[]) {
      const old=attempts.get(a.id);
      if (old && immutable(old)!==immutable(a)) fail('A task identifier has conflicting history. Existing work has not changed.');
      attempts.set(a.id,old ? {...a,submissions:Math.max(a.submissions,old.submissions),guidanceLevel:Math.max(a.guidanceLevel,old.guidanceLevel)} : a);
    }
    const guidance={...current.guidance};
    for (const [key,level] of Object.entries(incoming.guidance)) guidance[key]=Math.max(level,guidance[key]??0);
    const reflections={...current.reflections};
    for (const [key,entries] of Object.entries(incoming.reflections??{})) reflections[key]=mergeWriting(reflections[key]??[],entries);
    merged={...current,guidance,observations:[...observations.values()].sort((a,b)=>a.at.localeCompare(b.at)||a.iri.localeCompare(b.iri)),
      taskAttempts:[...attempts.values()].sort((a,b)=>a.startedAt.localeCompare(b.startedAt)||a.id.localeCompare(b.id)),reflections};
  }
  merged=validateRecord(merged,catalog);
  if (identity) merged.identity=identity; // A local sign-in remains local; none is trusted from a backup.
  return {record:merged,mode:empty?'continue':'merge',newObservations:merged.observations.length-current.observations.length,
    newAttempts:(merged.taskAttempts?.length??0)-(current.taskAttempts?.length??0),reflections:Object.values(merged.reflections??{}).reduce((n,r)=>n+r.length,0),courseChanged:backup.catalogDigest!==catalog.sourceDigest || backup.engineVersion!==ENGINE_VERSION || backup.policyVersion!==catalog.policy.version};
}
