import assert from 'node:assert/strict';
import { test } from 'node:test';
import { reflectionText } from '../src/extension/reflection-export';
import { LearnerRecord } from '../src/engine';

test('reflection download preserves recorded questions, multiline answers and timestamps without mutating the record', () => {
  const record: LearnerRecord = { schema: 'al-learner-record/0.1', learner: 'urn:uuid:11111111-1111-4111-8111-111111111111',
    audience: 'urn:audience:test', observations: [], guidance: {}, reflections: {
      'exercise:test': [{ prompt: 'What needs follow-up?', answer: 'Missing onset date.\nVérifier with the district team.', savedAt: '2026-10-22T12:00:00Z' }]
    } };
  const before = JSON.stringify(record);
  const exported = reflectionText(record);
  assert.ok(exported.includes(record.reflections!['exercise:test'][0].answer));
  assert.ok(exported.includes('What needs follow-up?'));
  assert.ok(exported.includes('2026-10-22T12:00:00Z'));
  assert.ok(exported.includes('Excludes unrecorded changes'));
  assert.equal(JSON.stringify(record), before);
});
