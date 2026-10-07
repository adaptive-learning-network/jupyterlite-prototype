// Run the DHIS2 scenarios without starting the unrelated mock OIDC provider.
const { spawnSync } = require('node:child_process');

const result = spawnSync(process.execPath, [require.resolve('@playwright/test/cli'), 'test', 'ui-tests/dhis2-scenarios.spec.ts', ...process.argv.slice(2)], {
  stdio: 'inherit',
  env: { ...process.env, JUPYTERLITE_SKIP_MOCK_OIDC: '1' }
});
if (result.error) throw result.error;
process.exit(result.status ?? 1);
