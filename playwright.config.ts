import { defineConfig } from '@playwright/test';

// End-to-end tests against the built JupyterLite site in _output/.
// Build first: see README ("Build the site"). A mock OpenID Connect provider
// (ui-tests/mock-oidc.mjs, HTTPS with a throwaway certificate) runs alongside.
export default defineConfig({
  testDir: 'ui-tests',
  timeout: 240_000,
  expect: { timeout: 120_000 },
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: 'http://127.0.0.1:8765',
    trace: 'retain-on-failure',
    viewport: { width: 1400, height: 900 },
    ignoreHTTPSErrors: true
  },
  webServer: [
    {
      command: 'python3 -m http.server 8765 --bind 127.0.0.1 --directory _output',
      url: 'http://127.0.0.1:8765/lab/index.html',
      reuseExistingServer: true,
      timeout: 60_000,
      stdout: 'ignore',
      stderr: 'ignore'
    },
    {
      command: 'node ui-tests/mock-oidc.mjs',
      url: 'https://127.0.0.1:8766/.well-known/openid-configuration',
      ignoreHTTPSErrors: true,
      reuseExistingServer: false,
      timeout: 60_000,
      stdout: 'ignore',
      stderr: 'pipe'
    }
  ]
});
