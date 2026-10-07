# Learner identity (OpenID Connect)

Status: implemented in the prototype; off unless a provider is configured.

## Principle

The learner record is identified by an opaque, browser-generated `urn:uuid:`.
OpenID Connect (OIDC) sign-in **links** an external identity to that record. It
never replaces the local identifier, and learning works without signing in.

A link (`al:IdentityBinding`) stores only:

| Field | Example |
| --- | --- |
| Issuer | `https://login.example.org/realms/fetp` |
| Subject | issuer-scoped opaque identifier (`sub` claim) |
| Bound at / last verified at | timestamps |
| Consent | purpose `identity-link`, consent-text revision, time |

Names, email addresses, other claims, and all tokens are discarded after
verification. The `al:` ontology enforces this. `IdentityBindingShape` requires
an `https` issuer and recorded consent, forbids name and email properties, and
rejects email-shaped subjects. Learner exports pass these shapes in CI.

## Flow

JupyterLite is a static site, so it is an OAuth **public client**: Authorization
Code with PKCE (S256), in a popup.

```text
panel: "Link organisation sign-in" → consent dialog
  → discovery  <issuer>/.well-known/openid-configuration (issuer must match)
  → popup      authorization endpoint (client_id, redirect_uri, scope=openid, state, nonce, code_challenge)
  → callback   <site>/oidc-callback.html posts the response URL over BroadcastChannel
               (and postMessage); works even when the provider's COOP severs window.opener
  → exchange   token endpoint (code + code_verifier; no client secret exists)
  → verify     ID token via provider JWKS: signature, iss, aud, exp, nonce (and azp)
  → keep       issuer + sub only; discard tokens and other claims
```

- **Verify again** must return the same issuer and subject. A different account
  is refused; the learner must unlink first.
- **Unlink** removes the binding and keeps learning progress.
- **Offline:** the panel shows "previously verified" with the last verification
  time. Tokens are never kept, so nothing is refreshed or extended offline.

## Configuring a provider

Create `lite/oidc.json` with public values only:

```json
{ "issuer": "https://login.example.org/realms/fetp", "clientId": "jupyterlite-al-engine", "label": "Organisation sign-in" }
```

`scripts/configure_site.py` (run by `jlpm build:site`) adds it to the site
configuration. It rejects secrets, non-`https` issuers, and `email` or `profile`
scopes.

With the provider:

1. Register a **single-page application / public client** with PKCE required.
2. Add the redirect URI `<site URL>/oidc-callback.html`. For GitHub Pages:
   `https://adaptive-learning-network.github.io/jupyterlite-prototype/oidc-callback.html`.
3. Allow the site origin for **CORS on the token endpoint**. SPA platforms in
   Microsoft Entra ID, Keycloak, Auth0, and Okta support this.
4. Request scope `openid` only. Use an opaque, pairwise subject if the provider
   offers it.

Not suitable: Google's OAuth web clients, because their token endpoint requires a
client secret, which a static site cannot keep.

## Tests

- **Unit tests** (`test/identity.test.ts`): PKCE against the RFC 7636 Appendix B
  vector, binding rules, same-account re-verification, and that exports contain
  no personal data. Exports validate against the `al:` SHACL shapes.
- **End to end** (`ui-tests/identity.spec.ts`), with the mock provider
  `ui-tests/mock-oidc.mjs`: HTTPS, PKCE/state/nonce enforcement, RS256 ID tokens,
  a login page that sends COOP, and extra email/name claims. The tests check that
  the record holds only issuer and subject, that browser storage holds no tokens
  or personal data, that a different account is refused, and that unlink works.

## Not yet

- Unlink receipts (an audit trail of unlinking) and a re-consent flow when the
  consent text changes.
- Local re-authentication on shared devices (for example WebAuthn).
- Using the identity for server-side synchronisation. That needs a governed
  service and is out of scope for the static site.
