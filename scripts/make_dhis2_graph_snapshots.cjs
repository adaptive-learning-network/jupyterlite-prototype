// Generate private, synthetic N-Quads snapshots for the final notebook demo.
// They use the same catalog, assessment, and export functions as the app.
const { spawnSync } = require('node:child_process');
const { mkdirSync, readFileSync, writeFileSync } = require('node:fs');
const { join } = require('node:path');

const root = join(__dirname, '..');
const compile = spawnSync(process.execPath, [require.resolve('typescript/bin/tsc'), '-p', 'tsconfig.test.json'], {
  cwd: root, stdio: 'inherit'
});
if (compile.error) throw compile.error;
if (compile.status !== 0) process.exit(compile.status ?? 1);

const { ACTION, OUTCOME, assess, exportNQuads } = require(join(root, 'lib-test/src/engine'));
const catalog = JSON.parse(readFileSync(join(root, 'content/al/catalog.json'), 'utf8'));
const ex = 'https://adaptive-learning-network.github.io/jupyterlite-prototype/catalog#';
const learner = 'urn:uuid:11111111-1111-4111-8111-111111111111';
const record = {
  schema: 'al-learner-record/0.1', learner, audience: ex + 'aud-fetp-trainee',
  observations: [], guidance: {}
};
const dir = join(root, '.tools/dhis2-graph-demo');
mkdirSync(dir, { recursive: true });

(async () => {
  const outcomes = [OUTCOME.incomplete, OUTCOME.incorrect, OUTCOME.incorrect, OUTCOME.correct];
  for (let index = 0; index < outcomes.length; index++) {
    const number = index + 1;
    record.observations.push({
      iri: `urn:uuid:22222222-2222-4222-8222-${String(number).padStart(12, '0')}`,
      activity: ex + 'act-dhis2-query', object: ex + 'act-dhis2-query-exercise',
      action: ACTION.outputValidated, outcome: outcomes[index], guidanceLevel: 0,
      at: `2026-10-07T12:0${number}:00Z`, language: 'python'
    });
    const assessment = assess(catalog, record);
    const data = await exportNQuads(catalog, record, assessment, { generatedAt: `2026-10-07T12:1${number}:00Z` });
    const filename = `learner-record-${String(number).padStart(2, '0')}.nq`;
    writeFileSync(join(dir, filename), data);
    const recommendations = assessment.recommendations.map(r => catalog.activities.find(a => a.iri === r.activity)?.title ?? r.activity);
    process.stdout.write(`${filename}: ${record.observations.length} attempts, ${assessment.evidence.length} evidence assertions; next: ${recommendations.join('; ')}\n`);
  }
  process.stdout.write(`Upload the four files from ${dir} beside 08-my-learning-record.ipynb. These are synthetic demonstration records.\n`);
})().catch(error => { console.error(error); process.exitCode = 1; });
