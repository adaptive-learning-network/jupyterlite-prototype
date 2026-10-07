import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { test } from 'node:test';

import { assess, Catalog, EngineInputError, exportNQuads, LearnerRecord } from '../src/engine';
import { checkAssertedIdentity, CONSENT_REVISION, IdentityBindingError, newBinding, reverify } from '../src/identity/binding';
import { codeChallenge, createPkcePair, randomToken } from '../src/identity/pkce';

const ROOT = join(__dirname, '..', '..');
const catalog: Catalog = JSON.parse(readFileSync(join(ROOT, 'content/al/catalog.json'), 'utf8'));
const EX = 'https://adaptive-learning-network.github.io/jupyterlite-prototype/catalog#';
const ISSUER = 'https://login.example.org/realms/fetp';
const NOW = '2026-10-02T12:00:00Z';
const IDS = { binding: 'urn:uuid:1d000000-0000-4000-8000-000000000001', consent: 'urn:uuid:c0000000-0000-4000-8000-000000000001' };

const code = (fn: () => unknown) => {
  try {
    fn();
  } catch (e) {
    return (e as IdentityBindingError | EngineInputError).code;
  }
  return 'none';
};

test('PKCE S256 matches the RFC 7636 Appendix B test vector', async () => {
  assert.equal(await codeChallenge('dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk'), 'E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM');
});

test('PKCE verifiers and state values are URL-safe, long, and unique', async () => {
  const pair = await createPkcePair();
  assert.match(pair.verifier, /^[A-Za-z0-9_-]{43,128}$/);
  assert.equal(pair.challenge, await codeChallenge(pair.verifier));
  const tokens = new Set(Array.from({ length: 50 }, () => randomToken()));
  assert.equal(tokens.size, 50);
});

test('a binding keeps only issuer and opaque subject, under consent', () => {
  const b = newBinding(ISSUER, 'f81d4fae-7dec-11d0-a765-00a0c91e6bf6', NOW, IDS);
  assert.deepEqual(Object.keys(b).sort(), ['boundAt', 'consent', 'iri', 'issuer', 'subject', 'verifiedAt']);
  assert.equal(b.consent.revision, CONSENT_REVISION);
});

test('email-shaped subjects and non-https issuers are refused', () => {
  assert.equal(code(() => checkAssertedIdentity(ISSUER, 'jane.doe@example.org')), 'SUBJECT_IS_EMAIL');
  assert.equal(code(() => checkAssertedIdentity('http://login.example.org', 'abc')), 'ISSUER_NOT_HTTPS');
  assert.equal(code(() => checkAssertedIdentity(ISSUER, '')), 'SUBJECT_INVALID');
  assert.equal(code(() => checkAssertedIdentity(ISSUER, 'x'.repeat(256))), 'SUBJECT_INVALID');
});

test('re-verification must be the same account', () => {
  const b = newBinding(ISSUER, 'subject-1', NOW, IDS);
  assert.equal(reverify(b, ISSUER, 'subject-1', '2026-10-03T08:00:00Z').verifiedAt, '2026-10-03T08:00:00Z');
  assert.equal(code(() => reverify(b, ISSUER, 'subject-2', NOW)), 'DIFFERENT_ACCOUNT');
  assert.equal(code(() => reverify(b, 'https://other.example.org', 'subject-1', NOW)), 'DIFFERENT_ACCOUNT');
});

test('the engine rejects a tampered binding and ignores identity in assessment', () => {
  const base: LearnerRecord = { schema: 'al-learner-record/0.1', learner: 'urn:uuid:22222222-2222-4222-8222-222222222222',
    audience: EX + 'aud-fetp-trainee', observations: [], guidance: {} };
  const linked = { ...base, identity: newBinding(ISSUER, 'subject-1', NOW, IDS) };
  assert.deepEqual(assess(catalog, linked), assess(catalog, base));
  assert.equal(code(() => assess(catalog, { ...linked, identity: { ...linked.identity, subject: 'jane@example.org' } })), 'IDENTITY_BINDING');
});

test('a linked record exports issuer, subject, and consent, and nothing personal', async () => {
  const record: LearnerRecord = { schema: 'al-learner-record/0.1', learner: 'urn:uuid:33333333-3333-4333-8333-333333333333',
    audience: EX + 'aud-fetp-trainee', observations: [], guidance: {}, identity: newBinding(ISSUER, 'f81d4fae-7dec-11d0-a765-00a0c91e6bf6', NOW, IDS) };
  const nq = await exportNQuads(catalog, record, assess(catalog, record), { generatedAt: NOW });
  assert.ok(nq.includes('#IdentityBinding>') && nq.includes('#ConsentDirective>') && nq.includes(ISSUER));
  assert.doesNotMatch(nq, /email|schema\.org\/name|id_token|access_token/i);
  mkdirSync(join(ROOT, 'test-results'), { recursive: true });
  writeFileSync(join(ROOT, 'test-results/learner-export-identity.nq'), nq);
});
