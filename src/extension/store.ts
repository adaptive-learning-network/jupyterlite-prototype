// Browser-local learner record: an opaque learner IRI, observations, and the
// facilitation level used per activity. The derived state (estimates, gaps,
// recommendations) is never stored; the engine recomputes it.
//
// Browser storage can be cleared or evicted; Export is the durable copy.

import { ISignal, Signal } from '@lumino/signaling';

import { beginTask, canonicalJson, CatalogActivity, CriterionResult, IdentityBinding, LearnerRecord, Observation, TaskAttempt } from '../engine';
import { mergeReflections, ReflectionAnswer } from './reflection-history';

const KEY = 'al-engine:learner-record:v0.1';
const LANGUAGE_KEY = 'al-engine:preferred-language';

function newRecord(audience: string): LearnerRecord {
  return {
    schema: 'al-learner-record/0.1',
    learner: `urn:uuid:${globalThis.crypto.randomUUID()}`,
    audience,
    observations: [],
    guidance: {}
  };
}

export class LearnerStore {
  private _record: LearnerRecord;
  private readonly _changed = new Signal<this, LearnerRecord>(this);
  /** False when the browser refused storage; the record then lasts for this page only. */
  readonly persistent: boolean;

  constructor(private readonly defaultAudience: string) {
    let stored: LearnerRecord | null = null;
    let persistent = true;
    try {
      const raw = globalThis.localStorage.getItem(KEY);
      stored = raw ? (JSON.parse(raw) as LearnerRecord) : null;
    } catch {
      persistent = false;
    }
    this.persistent = persistent;
    this._record = stored?.schema === 'al-learner-record/0.1' ? stored : newRecord(defaultAudience);
    this.save();
  }

  get record(): LearnerRecord {
    return this._record;
  }

  get changed(): ISignal<this, LearnerRecord> {
    return this._changed;
  }

  get preferredLanguage(): string {
    try {
      return globalThis.localStorage.getItem(LANGUAGE_KEY) ?? 'python';
    } catch {
      return 'python';
    }
  }

  set preferredLanguage(language: string) {
    try {
      globalThis.localStorage.setItem(LANGUAGE_KEY, language);
    } catch {
      // Preference is a convenience only.
    }
    this._changed.emit(this._record);
  }

  guidanceFor(activity: string): number {
    return this._record.guidance[activity] ?? 0;
  }

  addObservation(observation: Omit<Observation, 'iri' | 'guidanceLevel'>): Observation {
    const full: Observation = {
      ...observation,
      iri: `urn:uuid:${globalThis.crypto.randomUUID()}`,
      guidanceLevel: this.guidanceFor(observation.activity)
    };
    this.update({ ...this._record, observations: [...this._record.observations, full] });
    return full;
  }

  recordGuidance(activity: string, level: number): void {
    if (level <= this.guidanceFor(activity)) return;
    this.update({ ...this._record, guidance: { ...this._record.guidance, [activity]: level } });
  }

  activeTask(activity: CatalogActivity): TaskAttempt | undefined {
    return this._record.taskAttempts?.filter(a => a.activity === activity.iri && a.version === activity.assessment?.version).at(-1);
  }

  beginTask(activity: CatalogActivity, mode: TaskAttempt['mode']): TaskAttempt {
    const attempt = beginTask(this._record, activity, mode, `urn:uuid:${globalThis.crypto.randomUUID()}`, new Date().toISOString());
    this.commitTask({ ...this._record, taskAttempts: [...(this._record.taskAttempts ?? []), attempt] });
    return attempt;
  }

  taskHint(activity: CatalogActivity, attemptId: string): TaskAttempt {
    const active = this.activeTask(activity);
    if (!active || active.id !== attemptId || active.mode !== 'practice') throw new Error('Hints are available in the current practice attempt.');
    const next = { ...active, guidanceLevel: Math.min(3, active.guidanceLevel + 1) };
    this.commitTask({ ...this._record, taskAttempts: this._record.taskAttempts!.map(a => a.id === active.id ? next : a) });
    return next;
  }

  submitTask(activity: CatalogActivity, attemptId: string, outcome: string, criteria: CriterionResult[], language: string): Observation {
    const active = this.activeTask(activity);
    if (!active || active.id !== attemptId) throw new Error('This task changed in another session. Run the controls cell again.');
    const next = { ...active, submissions: active.submissions + (outcome.endsWith('#Incomplete') ? 0 : 1) };
    const observation: Observation = { iri: `urn:uuid:${globalThis.crypto.randomUUID()}`, activity: activity.iri,
      object: `${activity.iri}/${next.version}/${next.taskId}`, action: 'https://adaptive-learning-network.github.io/adaptive-learning-ontology/al#OutputValidated',
      outcome, guidanceLevel: next.guidanceLevel, at: new Date().toISOString(), language, attempt: { ...next }, criteria };
    this.commitTask({ ...this._record, taskAttempts: this._record.taskAttempts!.map(a => a.id === active.id ? next : a),
      observations: [...this._record.observations, observation] });
    return observation;
  }

  /** A pilot acknowledgement means the attempt and observation were saved together. */
  private commitTask(record: LearnerRecord): void {
    try {
      globalThis.localStorage.setItem(KEY, JSON.stringify(record));
    } catch {
      throw new Error('Browser storage could not save this attempt. Your earlier record is unchanged. Try again when storage is available.');
    }
    this._record = record;
    this._changed.emit(record);
  }

  /** Link, re-verify, or (with undefined) unlink an external identity. */
  setIdentity(identity: IdentityBinding | undefined): void {
    const next = { ...this._record };
    if (identity) next.identity = identity;
    else delete next.identity;
    this.update(next);
  }

  reset(): void {
    this.update(newRecord(this.defaultAudience));
  }

  /** Capture the exact record being previewed; detect changes from another tab. */
  portabilitySnapshot(): string {
    const expected=canonicalJson(this._record);
    const stored=globalThis.localStorage.getItem(KEY);
    if (!stored || canonicalJson(JSON.parse(stored))!==expected) throw new Error('Another tab changed this learning record. Reload before previewing the backup again.');
    return expected;
  }

  /** The caller supplies a validated merge, confirmed by the learner. Write first. */
  importPortable(record: LearnerRecord, expected: string): void {
    if (this.portabilitySnapshot()!==expected) throw new Error('Your record changed after the import preview. Preview the backup again before importing.');
    try { globalThis.localStorage.setItem(KEY,JSON.stringify(record)); }
    catch { throw new Error('Browser storage could not save the imported record. Your earlier record is unchanged. Keep your backup and try again when storage is available.'); }
    this._record=record;
    this._changed.emit(record);
  }

  recordReflections(section: string, entries: ReflectionAnswer[]): void {
    const savedAt = new Date().toISOString();
    const next = { ...this._record, reflections: { ...this._record.reflections,
      [section]: mergeReflections(this._record.reflections?.[section] ?? [], entries, savedAt) } };
    // Acknowledge only after storage succeeds; never silently claim a durable save.
    globalThis.localStorage.setItem(KEY, JSON.stringify(next));
    this._record = next;
    this._changed.emit(next);
  }

  private update(record: LearnerRecord): void {
    this._record = record;
    this.save();
    this._changed.emit(record);
  }

  private save(): void {
    try {
      globalThis.localStorage.setItem(KEY, JSON.stringify(this._record));
    } catch {
      // Storage unavailable (private window, quota); keep the in-memory record.
    }
  }
}
