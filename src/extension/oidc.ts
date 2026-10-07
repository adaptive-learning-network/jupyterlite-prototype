// OpenID Connect sign-in for a static JupyterLite site (public client).
//
// Authorization Code flow with PKCE in a popup:
//   1. discovery: <issuer>/.well-known/openid-configuration
//   2. popup to the authorization endpoint with S256 code challenge, state, nonce
//   3. oidc-callback.html (same origin) posts its URL back to this window
//   4. code exchange at the token endpoint (the provider must allow CORS for
//      browser clients; no client secret exists or is used)
//   5. ID token verified with the issuer's JWKS: signature, iss, aud, exp, nonce
// Only the issuer and the subject are returned. Tokens are discarded.

import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { createRemoteJWKSet, jwtVerify } from 'jose';

import { createPkcePair, randomToken } from '../identity/pkce';

export interface OidcConfig {
  issuer: string;
  clientId: string;
  /** Defaults to "openid". Request nothing more: no profile, no email. */
  scope?: string;
  /** Defaults to <site>/oidc-callback.html. Must be registered with the provider. */
  redirectUri?: string;
  /** Label for the sign-in button, e.g. "Organisation sign-in". */
  label?: string;
}

export interface VerifiedIdentity {
  issuer: string;
  subject: string;
}

interface Discovery {
  issuer: string;
  authorization_endpoint: string;
  token_endpoint: string;
  jwks_uri: string;
}

export const CALLBACK_CHANNEL = 'al-oidc-callback';

export class OidcError extends Error {
  constructor(readonly code: string, message: string) {
    super(message);
    this.name = 'OidcError';
  }
}

/** Read `alOidc` from the JupyterLite page config (jupyter-lite.json). */
export function readOidcConfig(): OidcConfig | null {
  const raw = PageConfig.getOption('alOidc');
  if (!raw) return null;
  try {
    const parsed = (typeof raw === 'string' ? JSON.parse(raw) : raw) as OidcConfig;
    if (!parsed.issuer?.startsWith('https://')) return null;
    return parsed.clientId ? parsed : null;
  } catch {
    return null;
  }
}

export function redirectUri(config: OidcConfig): string {
  return config.redirectUri ?? URLExt.join(PageConfig.getBaseUrl(), 'oidc-callback.html');
}

async function discover(issuer: string): Promise<Discovery> {
  const url = issuer.replace(/\/$/, '') + '/.well-known/openid-configuration';
  let response: Response;
  try {
    response = await fetch(url);
  } catch {
    throw new OidcError('UNREACHABLE', 'The sign-in provider cannot be reached. Check your connection; your record is unchanged.');
  }
  if (!response.ok) throw new OidcError('DISCOVERY', `Provider discovery failed (HTTP ${response.status}).`);
  const doc = (await response.json()) as Discovery;
  if (doc.issuer !== issuer) throw new OidcError('ISSUER_MISMATCH', 'Provider issuer does not match the configured issuer.');
  return doc;
}

/**
 * Wait for oidc-callback.html to report the authorization response. It posts on a
 * same-origin BroadcastChannel, which works even when the provider's
 * Cross-Origin-Opener-Policy severs window.opener, and also via postMessage.
 * Responses are accepted only for this request's state.
 */
function waitForCallback(expectedState: string, signal: AbortSignal, timeoutMs = 300_000): Promise<URL> {
  return new Promise((resolve, reject) => {
    const channel = new BroadcastChannel(CALLBACK_CHANNEL);
    const cleanup = () => {
      channel.close();
      window.removeEventListener('message', onWindowMessage);
      clearTimeout(timer);
      signal.removeEventListener('abort', onAbort);
    };
    const handle = (data: unknown) => {
      const message = data as { type?: string; url?: string };
      if (message?.type !== 'al-oidc-callback' || typeof message.url !== 'string') return;
      const url = new URL(message.url);
      if (url.origin !== window.location.origin) return;
      if (url.searchParams.get('state') !== expectedState) return; // another request's response
      cleanup();
      const error = url.searchParams.get('error');
      if (error) reject(new OidcError('PROVIDER_ERROR', `The provider returned "${error}".`));
      else resolve(url);
    };
    const onWindowMessage = (event: MessageEvent) => {
      if (event.origin === window.location.origin) handle(event.data);
    };
    const onAbort = () => {
      cleanup();
      reject(new OidcError('CANCELLED', 'Sign-in was cancelled.'));
    };
    const timer = setTimeout(() => {
      cleanup();
      reject(new OidcError('TIMEOUT', 'Sign-in timed out.'));
    }, timeoutMs);
    channel.onmessage = event => handle(event.data);
    window.addEventListener('message', onWindowMessage);
    signal.addEventListener('abort', onAbort);
  });
}

/** Run a full sign-in and return the verified issuer and subject. */
export async function signIn(config: OidcConfig, signal: AbortSignal): Promise<VerifiedIdentity> {
  // Open the popup synchronously with the user gesture, then navigate it.
  const popup = window.open('', 'al-oidc', 'popup,width=520,height=680');
  if (!popup) throw new OidcError('POPUP_BLOCKED', 'Allow pop-ups for this site to sign in.');
  try {
    const discovery = await discover(config.issuer);
    const pkce = await createPkcePair();
    const state = randomToken();
    const nonce = randomToken();
    const redirect = redirectUri(config);

    const authorize = new URL(discovery.authorization_endpoint);
    authorize.search = new URLSearchParams({
      response_type: 'code',
      client_id: config.clientId,
      redirect_uri: redirect,
      scope: config.scope ?? 'openid',
      state,
      nonce,
      code_challenge: pkce.challenge,
      code_challenge_method: 'S256'
    }).toString();
    popup.location.href = authorize.toString();

    const callback = await waitForCallback(state, signal);
    const code = callback.searchParams.get('code');
    if (!code) throw new OidcError('NO_CODE', 'The provider did not return an authorization code.');

    const tokenResponse = await fetch(discovery.token_endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: redirect,
        client_id: config.clientId,
        code_verifier: pkce.verifier
      })
    }).catch(() => {
      throw new OidcError('TOKEN_UNREACHABLE', 'Token endpoint unreachable. The provider must allow browser (CORS) token requests.');
    });
    if (!tokenResponse.ok) throw new OidcError('TOKEN', `Token request failed (HTTP ${tokenResponse.status}).`);
    const tokens = (await tokenResponse.json()) as { id_token?: string };
    if (!tokens.id_token) throw new OidcError('NO_ID_TOKEN', 'The provider did not return an ID token.');

    const { payload } = await jwtVerify(tokens.id_token, createRemoteJWKSet(new URL(discovery.jwks_uri)), {
      issuer: discovery.issuer,
      audience: config.clientId
    }).catch(error => {
      throw new OidcError('ID_TOKEN_INVALID', `ID token rejected: ${(error as Error).message}`);
    });
    if (payload.nonce !== nonce) throw new OidcError('NONCE', 'ID token nonce does not match this request.');
    if (Array.isArray(payload.aud) && payload.aud.length > 1 && payload.azp !== config.clientId) {
      throw new OidcError('AZP', 'ID token was issued to a different client.');
    }
    // Only these two claims leave this function; everything else, including tokens, is dropped.
    return { issuer: discovery.issuer, subject: String(payload.sub ?? '') };
  } finally {
    try {
      popup.close();
    } catch {
      // The provider may have severed the opener; the callback page closes itself.
    }
  }
}
