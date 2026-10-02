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
  return { schema: 'al-learner-record/0.1', learner: LEARNER, audience: EX + 'aud-intro', observations, guidance: {} };
}

const gapOf = (a: ReturnType<typeof assess>, cap: string) => a.gaps.find(g => g.capability === EX + cap)!;

test('a new learner is offered only the capability without prerequisites', () => {
  const a = assess(catalog, record([]));
  assert.equal(a.evidence.length, 0);
  assert.ok(a.gaps.every(g => g.state === GAP.unknown && g.status === STATUS.notAssessed));
  assert.deepEqual(a.recommendations.map(r => r.capability), [EX + 'cap-frequency']);
  assert.deepEqual(a.recommendations[0].reasons, [REASON.notAssessed]);
  assert.equal(gapOf(a, 'cap-risk-ratio').gateBlocked, true, 'critical target not achieved blocks the gate');
});

test('a correct exercise is simulation evidence and unlocks the next capability', () => {
  const a = assess(catalog, record([obs('act-frequency', OUTCOME.correct)]));
  const gap = gapOf(a, 'cap-frequency');
  assert.equal(gap.state, GAP.achieved);
  assert.equal(gap.status, STATUS.demonstrated);
  assert.deepEqual(a.recommendations.map(r => r.capability), [EX + 'cap-attack-rate']);
  assert.ok(a.recommendations[0].reasons.includes(REASON.prerequisitesMet));
});

test('incorrect attempts are not negative evidence', () => {
  const a = assess(catalog, record([obs('act-frequency', OUTCOME.incorrect), obs('act-frequency', OUTCOME.incomplete)]));
  assert.equal(a.evidence.length, 0);
  assert.equal(gapOf(a, 'cap-frequency').state, GAP.unknown);
  assert.ok(a.recommendations[0].reasons.includes(REASON.insufficientIndependentEvidence));
});

test('guidance above the rule ceiling excludes the evidence', () => {
  const a = assess(catalog, record([obs('act-frequency', OUTCOME.correct), obs('act-attack-rate', OUTCOME.correct, 3)]));
  const estimate = a.estimates.find(e => e.capability === EX + 'cap-attack-rate')!;
  assert.equal(estimate.level, undefined);
  assert.equal(estimate.excluded[0].reason, EXCLUSION.guidanceExceeded);
  assert.equal(gapOf(a, 'cap-attack-rate').state, GAP.unknown);
  assert.equal(a.recommendations[0].capability, EX + 'cap-attack-rate');
});

test('guidance within the ceiling still counts', () => {
  const a = assess(catalog, record([obs('act-frequency', OUTCOME.correct, 2)]));
  assert.equal(gapOf(a, 'cap-frequency').state, GAP.achieved);
});

test('repeated success in one activity is one dependence group', () => {
  const a = assess(catalog, record([obs('act-frequency', OUTCOME.correct), obs('act-frequency', OUTCOME.correct)]));
  const estimate = a.estimates.find(e => e.capability === EX + 'cap-frequency')!;
  assert.equal(estimate.derivedFrom.length, 1);
  assert.deepEqual(estimate.excluded.map(x => x.reason), [EXCLUSION.dependent]);
});

test('the Jupyter kernel language does not change the assessment', () => {
  counter = 100;
  const py = assess(catalog, record([obs('act-frequency', OUTCOME.correct, 0, 'python')]));
  counter = 100;
  const r = assess(catalog, record([obs('act-frequency', OUTCOME.correct, 0, 'r')]));
  assert.equal(canonicalJson(py), canonicalJson(r));
});

test('the assessment does not depend on observation order', () => {
  const observations = [obs('act-frequency', OUTCOME.correct), obs('act-attack-rate', OUTCOME.incorrect), obs('act-attack-rate', OUTCOME.correct)];
  const forward = assess(catalog, record(observations));
  const backward = assess(catalog, record([...observations].reverse()));
  assert.equal(canonicalJson(forward), canonicalJson(backward));
});

test('a learner who completes the pathway has no open gates', () => {
  const a = assess(catalog, record(['act-frequency', 'act-attack-rate', 'act-risk-ratio', 'act-interpret-rr'].map(x => obs(x, OUTCOME.correct))));
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
  assert.equal(code(() => assess(catalog, record([{ ...obs('act-frequency', OUTCOME.correct), activity: EX + 'nope' }]))), 'UNKNOWN_ACTIVITY');
  const dup = obs('act-frequency', OUTCOME.correct);
  assert.equal(code(() => assess(catalog, record([dup, dup]))), 'DUPLICATE_OBSERVATION');
  const cyclic: Catalog = JSON.parse(JSON.stringify(catalog));
  cyclic.capabilities[0].prerequisites = [EX + 'cap-interpret-rr'];
  assert.equal(code(() => assess(cyclic, record([]))), 'PREREQUISITE_CYCLE');
});

test('export writes an al: learner graph for SHACL validation', async () => {
  const r = record([
    obs('act-frequency', OUTCOME.incorrect, 1, 'r'),
    obs('act-frequency', OUTCOME.correct, 1, 'r'),
    obs('act-attack-rate', OUTCOME.correct, 3, 'python'),
    obs('act-attack-rate', OUTCOME.correct, 0, 'python'),
    obs('act-attack-rate', OUTCOME.correct, 0, 'python')
  ]);
  const a = assess(catalog, r);
  const nq = await exportNQuads(catalog, r, a, { generatedAt: '2026-10-02T12:00:00Z' });
  assert.ok(nq.includes('LearningGraph'));
  assert.equal(nq, await exportNQuads(catalog, r, assess(catalog, r), { generatedAt: '2026-10-02T12:00:00Z' }), 'export is deterministic');
  mkdirSync(join(ROOT, 'test-results'), { recursive: true });
  writeFileSync(join(ROOT, 'test-results/learner-export.nq'), nq);
});
