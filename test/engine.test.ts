import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { test } from 'node:test';

import {
  ACTION,
  assess,
  canonicalJson,
  Catalog,
  EngineInputError,
  EXCLUSION,
  exportNQuads,
  GAP,
  LearnerRecord,
  Observation,
  OUTCOME,
  REASON,
  STATUS
} from '../src/engine';

const ROOT = join(__dirname, '..', '..');
const catalog: Catalog = JSON.parse(readFileSync(join(ROOT, 'content/al/catalog.json'), 'utf8'));
const EX = 'https://adaptive-learning-network.github.io/jupyterlite-prototype/catalog#';
const LEARNER = 'urn:uuid:11111111-1111-4111-8111-111111111111';

let counter = 0;
function obs(activity: string, outcome: string, guidanceLevel = 0, language = 'python'): Observation {
  counter += 1;
  const n = String(counter).padStart(12, '0');
  return {
    iri: `urn:uuid:00000000-0000-4000-8000-${n}`,
    activity: EX + activity,
    object: `${EX}${activity}-exercise`,
    action: ACTION.outputValidated,
    outcome,
    guidanceLevel,
    at: `2026-10-02T10:${String(counter % 60).padStart(2, '0')}:00Z`,
    language
  };
}

function record(observations: Observation[]): LearnerRecord {
  return { schema: 'al-learner-record/0.1', learner: LEARNER, audience: EX + 'aud-fetp-trainee', observations, guidance: {} };
}

const gapOf = (a: ReturnType<typeof assess>, cap: string) => a.gaps.find(g => g.capability === EX + cap)!;

test('a new learner is offered only capabilities without prerequisites', () => {
  const a = assess(catalog, record([]));
  assert.equal(a.evidence.length, 0);
  assert.ok(a.gaps.every(g => g.state === GAP.unknown && g.status === STATUS.notAssessed));
  assert.deepEqual(a.recommendations.map(r => r.capability), [EX + 'cap-data-vs-information', EX + 'cap-explore-dataset']);
  assert.ok(a.recommendations.every(r => r.reasons.join() === REASON.notAssessed));
  assert.equal(gapOf(a, 'cap-combine-variables').gateBlocked, true, 'critical target not achieved blocks the gate');
});

test('recommendations prefer notebook exercises over the external quiz', () => {
  const a = assess(catalog, record([]));
  assert.ok(a.recommendations.every(r => !r.activity.endsWith('act-unit-03-quiz')));
});

test('a correct exercise is simulation evidence and unlocks dependent capabilities', () => {
  const a = assess(catalog, record([obs('act-explore-dataset', OUTCOME.correct)]));
  const gap = gapOf(a, 'cap-explore-dataset');
  assert.equal(gap.state, GAP.achieved);
  assert.equal(gap.status, STATUS.demonstrated);
  assert.deepEqual(a.recommendations.map(r => r.capability),
    [EX + 'cap-data-vs-information', EX + 'cap-filter-records', EX + 'cap-machine-readable']);
  assert.ok(a.recommendations[1].reasons.includes(REASON.prerequisitesMet));
});

test('the critical capability is recommended first once its prerequisites are met', () => {
  const a = assess(catalog, record(['act-data-or-information', 'act-explore-dataset', 'act-filter-records'].map(x => obs(x, OUTCOME.correct))));
  assert.equal(a.recommendations[0].capability, EX + 'cap-combine-variables');
  assert.ok(a.recommendations[0].reasons.includes(REASON.criticalGate));
});

test('incorrect attempts are not negative evidence', () => {
  const a = assess(catalog, record([obs('act-explore-dataset', OUTCOME.incorrect), obs('act-explore-dataset', OUTCOME.incomplete)]));
  assert.equal(a.evidence.length, 0);
  assert.equal(gapOf(a, 'cap-explore-dataset').state, GAP.unknown);
  const rec = a.recommendations.find(r => r.capability === EX + 'cap-explore-dataset')!;
  assert.ok(rec.reasons.includes(REASON.insufficientIndependentEvidence));
});

test('guidance above the rule ceiling excludes the evidence', () => {
  const a = assess(catalog, record([obs('act-explore-dataset', OUTCOME.correct), obs('act-filter-records', OUTCOME.correct, 3)]));
  const estimate = a.estimates.find(e => e.capability === EX + 'cap-filter-records')!;
  assert.equal(estimate.level, undefined);
  assert.equal(estimate.excluded[0].reason, EXCLUSION.guidanceExceeded);
  assert.equal(gapOf(a, 'cap-filter-records').state, GAP.unknown);
  assert.ok(a.recommendations.some(r => r.capability === EX + 'cap-filter-records'));
});

test('guidance within the ceiling still counts', () => {
  const a = assess(catalog, record([obs('act-explore-dataset', OUTCOME.correct, 2)]));
  assert.equal(gapOf(a, 'cap-explore-dataset').state, GAP.achieved);
});

test('repeated success in one activity is one dependence group', () => {
  const a = assess(catalog, record([obs('act-explore-dataset', OUTCOME.correct), obs('act-explore-dataset', OUTCOME.correct)]));
  const estimate = a.estimates.find(e => e.capability === EX + 'cap-explore-dataset')!;
  assert.equal(estimate.derivedFrom.length, 1);
  assert.deepEqual(estimate.excluded.map(x => x.reason), [EXCLUSION.dependent]);
});

test('the Jupyter kernel language does not change the assessment', () => {
  counter = 100;
  const py = assess(catalog, record([obs('act-explore-dataset', OUTCOME.correct, 0, 'python')]));
  counter = 100;
  const r = assess(catalog, record([obs('act-explore-dataset', OUTCOME.correct, 0, 'r')]));
  assert.equal(canonicalJson(py), canonicalJson(r));
});

test('the assessment does not depend on observation order', () => {
  const observations = [obs('act-explore-dataset', OUTCOME.correct), obs('act-filter-records', OUTCOME.incorrect), obs('act-filter-records', OUTCOME.correct)];
  const forward = assess(catalog, record(observations));
  const backward = assess(catalog, record([...observations].reverse()));
  assert.equal(canonicalJson(forward), canonicalJson(backward));
});

test('a learner who completes every exercise has no open gates', () => {
  const all = ['act-data-or-information', 'act-explore-dataset', 'act-filter-records', 'act-coverage', 'act-machine-readable', 'act-case-or-aggregate'];
  const a = assess(catalog, record(all.map(x => obs(x, OUTCOME.correct))));
  assert.ok(a.gaps.every(g => g.state === GAP.achieved && !g.gateBlocked));
  assert.equal(a.recommendations.length, 0);
});

test('invalid input fails closed with a stable code', () => {
  const code = (fn: () => unknown) => {
    try {
      fn();
    } catch (e) {
      return (e as EngineInputError).code;
    }
    return 'none';
  };
  assert.equal(code(() => assess(catalog, { ...record([]), learner: 'Jane Doe' })), 'LEARNER_IRI');
  assert.equal(code(() => assess(catalog, record([{ ...obs('act-explore-dataset', OUTCOME.correct), activity: EX + 'nope' }]))), 'UNKNOWN_ACTIVITY');
  const dup = obs('act-explore-dataset', OUTCOME.correct);
  assert.equal(code(() => assess(catalog, record([dup, dup]))), 'DUPLICATE_OBSERVATION');
  const cyclic: Catalog = JSON.parse(JSON.stringify(catalog));
  cyclic.capabilities.find(c => c.notation === 'explore-dataset')!.prerequisites = [EX + 'cap-case-vs-aggregate'];
  assert.equal(code(() => assess(cyclic, record([]))), 'PREREQUISITE_CYCLE');
});

test('export writes an al: learner graph for SHACL validation', async () => {
  const r = record([
    obs('act-explore-dataset', OUTCOME.incorrect, 1, 'r'),
    obs('act-explore-dataset', OUTCOME.correct, 1, 'r'),
    obs('act-filter-records', OUTCOME.correct, 3, 'python'),
    obs('act-filter-records', OUTCOME.correct, 0, 'python'),
    obs('act-filter-records', OUTCOME.correct, 0, 'python')
  ]);
  const a = assess(catalog, r);
  const nq = await exportNQuads(catalog, r, a, { generatedAt: '2026-10-02T12:00:00Z' });
  assert.ok(nq.includes('LearningGraph'));
  assert.equal(nq, await exportNQuads(catalog, r, assess(catalog, r), { generatedAt: '2026-10-02T12:00:00Z' }), 'export is deterministic');
  mkdirSync(join(ROOT, 'test-results'), { recursive: true });
  writeFileSync(join(ROOT, 'test-results/learner-export.nq'), nq);
});
