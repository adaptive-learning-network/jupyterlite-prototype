import { expect, Page, test } from '@playwright/test';

// OpenID Connect linking against the mock provider (ui-tests/mock-oidc.mjs).
// The provider sends COOP (severing window.opener) and extra email/name claims.

// JupyterLite's service worker proxies fetches, and its requests do not inherit
// Playwright's ignoreHTTPSErrors for the mock provider's throwaway certificate.
// Sign-in does not use the service worker, so block it here.
test.use({ serviceWorkers: 'block' });

const ISSUER = 'https://127.0.0.1:8766';
const SUBJECT = 'f81d4fae-7dec-11d0-a765-00a0c91e6bf6';
const RECORD_KEY = 'al-engine:learner-record:v0.1';

async function openWithSignIn(page: Page): Promise<void> {
  await page.route('**/jupyter-lite.json', async route => {
    const response = await route.fetch();
    const config = await response.json();
    config['jupyter-config-data'] = { ...(config['jupyter-config-data'] ?? {}), alOidc: { issuer: ISSUER, clientId: 'test-client' } };
    await route.fulfill({ response, json: config });
  });
  await page.goto('/lab/index.html?path=exercises/python/01-data-or-information.ipynb');
  await expect(page.locator('#al-engine-learning .al-identity')).toBeVisible();
}

async function signInVia(page: Page, button: string, consent: boolean): Promise<void> {
  const panel = page.locator('#al-engine-learning');
  const popup = page.waitForEvent('popup');
  await panel.getByRole('button', { name: button }).click();
  if (consent) await page.locator('.jp-Dialog').getByRole('button', { name: 'I agree, sign in' }).click();
  await popup;
}

async function storageDump(page: Page): Promise<string> {
  return page.evaluate(() => JSON.stringify({ local: { ...localStorage }, session: { ...sessionStorage } }));
}

test('linking stores only issuer and subject, never names, emails, or tokens', async ({ page, request }) => {
  await request.post(`${ISSUER}/__control`, { data: { subject: SUBJECT } });
  await openWithSignIn(page);
  const identity = page.locator('#al-engine-learning .al-identity');
  await expect(identity).toContainText('Not linked');

  await signInVia(page, 'Link organisation sign-in', true);
  await expect(identity).toContainText('Linked to 127.0.0.1:8766');
  await expect(identity).toContainText('Sign-in linked to this record.');
  // The mock login page sends COOP, so the callback had no window.opener and
  // reached this window over BroadcastChannel.

  const record = JSON.parse((await page.evaluate(key => localStorage.getItem(key), RECORD_KEY))!);
  expect(record.identity.issuer).toBe(ISSUER);
  expect(record.identity.subject).toBe(SUBJECT);
  expect(record.identity.consent.revision).toBe('identity-link-consent/1');
  const everything = await storageDump(page);
  expect(everything).not.toMatch(/jane|Jane Doe|eyJ|id_token|access_token/);
});

test('verifying with a different account is refused; unlink returns to anonymous', async ({ page, request }) => {
  await request.post(`${ISSUER}/__control`, { data: { subject: SUBJECT } });
  await openWithSignIn(page);
  const identity = page.locator('#al-engine-learning .al-identity');
  await signInVia(page, 'Link organisation sign-in', true);
  await expect(identity).toContainText('Linked to 127.0.0.1:8766');

  await request.post(`${ISSUER}/__control`, { data: { subject: 'someone-else' } });
  await signInVia(page, 'Verify again', false);
  await expect(identity).toContainText('different account');
  const record = JSON.parse((await page.evaluate(key => localStorage.getItem(key), RECORD_KEY))!);
  expect(record.identity.subject).toBe(SUBJECT);

  await identity.getByRole('button', { name: 'Unlink' }).click();
  await page.locator('.jp-Dialog').getByRole('button', { name: 'Unlink' }).click();
  await expect(identity).toContainText('Not linked');
  const after = JSON.parse((await page.evaluate(key => localStorage.getItem(key), RECORD_KEY))!);
  expect(after.identity).toBeUndefined();
});
