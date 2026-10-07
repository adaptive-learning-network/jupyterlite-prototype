// Minimal OpenID Connect provider for end-to-end tests only.
//
// HTTPS on 127.0.0.1:8766 with a throwaway self-signed certificate. Enforces
// PKCE (S256), state round-trip, nonce, client_id, and redirect_uri; signs ID
// tokens with RS256 and serves the JWKS. It also:
//   - sends Cross-Origin-Opener-Policy: same-origin on the authorize page, which
//     severs window.opener (as some real providers do);
//   - adds email and name claims, so tests can prove they are never stored.
// POST /__control {"subject": "..."} sets the subject for the next sign-in.

import { execFileSync } from 'node:child_process';
import { createHash, randomBytes } from 'node:crypto';
import { mkdtempSync, readFileSync } from 'node:fs';
import { createServer } from 'node:https';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { exportJWK, generateKeyPair, SignJWT } from 'jose';

const PORT = 8766;
const ISSUER = `https://127.0.0.1:${PORT}`;
const CLIENT_ID = 'test-client';

const dir = mkdtempSync(join(tmpdir(), 'mock-oidc-'));
execFileSync('openssl', ['req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1', '-subj', '/CN=127.0.0.1',
  '-addext', 'subjectAltName=IP:127.0.0.1', '-keyout', join(dir, 'key.pem'), '-out', join(dir, 'cert.pem')], { stdio: 'ignore' });

const { privateKey, publicKey } = await generateKeyPair('RS256');
const jwk = { ...(await exportJWK(publicKey)), kid: 'test-key', alg: 'RS256', use: 'sig' };
const codes = new Map();
let nextSubject = 'f81d4fae-7dec-11d0-a765-00a0c91e6bf6';

const s256 = verifier => createHash('sha256').update(verifier).digest('base64url');

function send(res, status, body, headers = {}) {
  res.writeHead(status, { 'Content-Type': 'application/json', ...headers });
  res.end(typeof body === 'string' ? body : JSON.stringify(body));
}

function readBody(req) {
  return new Promise(resolve => {
    let data = '';
    req.on('data', chunk => (data += chunk));
    req.on('end', () => resolve(data));
  });
}

const server = createServer({ key: readFileSync(join(dir, 'key.pem')), cert: readFileSync(join(dir, 'cert.pem')) }, async (req, res) => {
  const url = new URL(req.url, ISSUER);
  const cors = { 'Access-Control-Allow-Origin': req.headers.origin ?? '*', 'Access-Control-Allow-Headers': 'Content-Type' };

  if (req.method === 'OPTIONS') return send(res, 204, '', cors);

  if (url.pathname === '/.well-known/openid-configuration') {
    return send(res, 200, {
      issuer: ISSUER,
      authorization_endpoint: `${ISSUER}/authorize`,
      token_endpoint: `${ISSUER}/token`,
      jwks_uri: `${ISSUER}/jwks`,
      response_types_supported: ['code'],
      subject_types_supported: ['public'],
      id_token_signing_alg_values_supported: ['RS256'],
      code_challenge_methods_supported: ['S256']
    }, cors);
  }

  if (url.pathname === '/jwks') return send(res, 200, { keys: [jwk] }, cors);

  if (url.pathname === '/authorize') {
    const p = url.searchParams;
    const problems = [];
    if (p.get('response_type') !== 'code') problems.push('response_type');
    if (p.get('client_id') !== CLIENT_ID) problems.push('client_id');
    if (p.get('code_challenge_method') !== 'S256' || !p.get('code_challenge')) problems.push('pkce');
    if (!p.get('state') || !p.get('nonce')) problems.push('state/nonce');
    if (!(p.get('scope') ?? '').split(' ').includes('openid')) problems.push('scope');
    if (problems.length) return send(res, 400, { error: 'invalid_request', problems });
    const code = randomBytes(16).toString('hex');
    codes.set(code, { challenge: p.get('code_challenge'), nonce: p.get('nonce'), redirect: p.get('redirect_uri'), subject: nextSubject });
    const back = new URL(p.get('redirect_uri'));
    back.searchParams.set('code', code);
    back.searchParams.set('state', p.get('state'));
    // A real login page loads as a document; COOP on it severs window.opener.
    res.writeHead(200, { 'Content-Type': 'text/html', 'Cross-Origin-Opener-Policy': 'same-origin' });
    return res.end(`<!doctype html><title>Mock sign-in</title><p>Signing in…</p>
<script>setTimeout(function () { location.replace(${JSON.stringify(back.toString())}); }, 200);</script>`);
  }

  if (url.pathname === '/token' && req.method === 'POST') {
    const form = new URLSearchParams(await readBody(req));
    const grant = codes.get(form.get('code'));
    codes.delete(form.get('code'));
    if (!grant || form.get('grant_type') !== 'authorization_code' || form.get('client_id') !== CLIENT_ID
        || form.get('redirect_uri') !== grant.redirect || s256(form.get('code_verifier') ?? '') !== grant.challenge) {
      return send(res, 400, { error: 'invalid_grant' }, cors);
    }
    const idToken = await new SignJWT({ nonce: grant.nonce, email: 'jane.doe@example.org', name: 'Jane Doe' })
      .setProtectedHeader({ alg: 'RS256', kid: 'test-key' })
      .setIssuer(ISSUER).setAudience(CLIENT_ID).setSubject(grant.subject)
      .setIssuedAt().setExpirationTime('5m').sign(privateKey);
    return send(res, 200, { id_token: idToken, access_token: 'eyJ.mock.access', token_type: 'Bearer', expires_in: 300 }, cors);
  }

  if (url.pathname === '/__control' && req.method === 'POST') {
    nextSubject = JSON.parse(await readBody(req)).subject;
    return send(res, 200, { subject: nextSubject });
  }

  return send(res, 404, { error: 'not_found' });
});

server.listen(PORT, '127.0.0.1', () => console.log(`mock OIDC provider at ${ISSUER}`));
