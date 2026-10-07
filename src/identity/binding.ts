// Rules for linking a learner record to an external OpenID Connect identity.
//
// Only the issuer and the issuer-scoped subject are kept, under recorded consent.
// Names, email addresses, and tokens never enter the learner record.

import { IdentityBinding } from '../engine/types';

export const CONSENT_REVISION = 'identity-link-consent/1';
export const CONSENT_PURPOSE = 'identity-link';
export const CONSENT_TEXT =
  'Link this learning record to your organisation sign-in. Only the identity provider address and an opaque account ' +
  'identifier are stored with your record in this browser, and in exports you make. Your name, email address, and sign-in ' +
  'tokens are not stored. You can unlink at any time.';

const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export class IdentityBindingError extends Error {
  constructor(readonly code: string, message: string) {
    super(`${code}: ${message}`);
    this.name = 'IdentityBindingError';
  }
}

/** Validate what an ID token asserted before it is stored. */
export function checkAssertedIdentity(issuer: string, subject: unknown): string {
  if (!/^https:\/\//.test(issuer)) throw new IdentityBindingError('ISSUER_NOT_HTTPS', issuer);
  if (typeof subject !== 'string' || subject.length === 0 || subject.length > 255) {
    throw new IdentityBindingError('SUBJECT_INVALID', 'subject must be 1 to 255 characters');
  }
  if (EMAIL.test(subject)) {
    throw new IdentityBindingError('SUBJECT_IS_EMAIL', 'the provider uses an email address as the subject; configure an opaque subject');
  }
  return subject;
}

export function newBinding(issuer: string, subject: string, now: string, ids: { binding: string; consent: string }): IdentityBinding {
  return {
    iri: ids.binding,
    issuer,
    subject: checkAssertedIdentity(issuer, subject),
    boundAt: now,
    verifiedAt: now,
    consent: { iri: ids.consent, purpose: CONSENT_PURPOSE, revision: CONSENT_REVISION, consentedAt: now }
  };
}

/** Re-verification must assert the same account that was linked. */
export function reverify(binding: IdentityBinding, issuer: string, subject: string, now: string): IdentityBinding {
  if (issuer !== binding.issuer || subject !== binding.subject) {
    throw new IdentityBindingError('DIFFERENT_ACCOUNT', 'signed in with a different account than the one linked; unlink first');
  }
  return { ...binding, verifiedAt: now };
}
