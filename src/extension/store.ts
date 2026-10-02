// Browser-local learner record: an opaque learner IRI, observations, and the
// facilitation level used per activity. The derived state (estimates, gaps,
// recommendations) is never stored; the engine recomputes it.
//
// Browser storage can be cleared or evicted; Export is the durable copy.

import { ISignal, Signal } from '@lumino/signaling';

import { LearnerRecord, Observation } from '../engine';

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

  reset(): void {
    this.update(newRecord(this.defaultAudience));
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
