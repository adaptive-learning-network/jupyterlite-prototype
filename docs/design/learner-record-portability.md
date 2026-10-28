# Learner record portability

Implemented: 28 October 2026. Backup format version 1.

## Learner workflow

1. Select **Download learner backup** in the Learning panel. Supply and confirm a
   password of at least 12 characters. Keep the `.albackup` file and password
   separately. There is no password recovery service.
2. In the destination browser, select **Import learner backup**, choose the file,
   and enter its password. The browser decrypts and validates it locally.
3. Review the preview and select **Import record**, or cancel without changing
   anything. Close other course tabs during import. Re-run activity/reflection
   setup cells to restore controls and recorded writing after import.

The backup contains the opaque learner ID, role, submitted observations, help
history, task sessions (including displayed but unsubmitted cases), bounded
classification choices, reflection answers, and earlier wording/answer history.
The engine recomputes progress and recommendations. Notebook files, unsaved
answers, passwords, tokens, and organisation sign-in links are excluded. A local
sign-in link is preserved when merging into that same learner's existing record.
Link sign-in separately through the normal consent flow on a new browser.

**Export evidence** and **Download reflections** remain readable downloads, not
importable backups. Download edited notebooks separately. This feature transfers
a learner record, not a complete JupyterLite workspace.

## One local learner and merge rules

A browser without attempts, guidance, task sessions, reflections, or a sign-in
link can continue the source learner ID. The same learner ID can merge a backup.
A different ID with work or a sign-in link is refused. Back up that record first
and use an empty browser profile. There is no roster, switching, automatic
replacement, server synchronization, or external upload.

- Matching observation IRIs deduplicate identical content. Different content
  for the same IRI rejects the entire merge.
- Guidance retains its highest level. Task identity is immutable; matching
  sessions retain the greatest counters and guidance.
- Every complete submission position must have exactly one observation.
  Divergent branches with different submissions at the same position cannot
  merge. Separate attempts at the same different-case task are also refused.
  Import cannot reset guidance or make a seen case fresh again.
- Reflection ID/version pairs and legacy prompt identities remain separate.
  The most recently dated saved answer becomes current. Ties retain the local
  answer. Other answers/wording remain in deduplicated history. Device clocks
  affect which answer is considered latest; alternatives remain available.
- The current engine admits merged inputs and recomputes progress. Imported
  estimates are never trusted or stored.

## Versioned encrypted format

The envelope `al-encrypted-backup/1` uses browser Web Crypto: PBKDF2-HMAC-SHA-256
with 600,000 iterations and a random 16-byte salt, then AES-256-GCM with a random
12-byte IV and a 128-bit authentication tag. Authenticated additional data binds
the format, algorithms, and KDF settings. Each export has a fresh salt and IV.
An import cannot request weaker settings or arbitrary KDF work.

The encrypted payload `al-portable-record/1` includes framework IRI, catalog
digest, engine/policy versions, creation time, and validated record. The framework
and role must be compatible. Changed catalog/engine/policy versions appear in the
preview. Historical task versions remain history, not evidence for a different
current version. Unsupported schemas and unknown activities are refused.

Envelope size is limited to 10 MiB, clear records to 5 MiB, and arrays to 10,000
items. Field, length, timestamp, IRI, counter, outcome, reflection-history, and
task-consistency checks reject malformed input. Unexpected fields/prototype keys
are refused. No imported content executes or renders as HTML. The password stays
in memory for the operation and is not stored by the application. JavaScript
does not guarantee immediate erasure of strings from process memory.

## Persistence and limits

The importer compares the preview's record with current in-memory and stored
state immediately before writing. Detected edits require a new preview. One
localStorage write saves the complete record before a success signal. Failed
writes preserve the previous stored and in-memory record. localStorage has no
cross-tab compare-and-swap transaction, so simultaneous edits during import are
unsupported. Keep other course tabs closed.

Encryption protects file contents when the password remains private. It does not
certify authorship, protect an already compromised device, or make formative
evidence a secure examination. Nothing transfers automatically to instructors.

## Acceptance checks

Native tests cover encrypted round trips, tampering/password failures, schema and
size rejection, fresh-browser continuation, idempotent merges, reflection
history, sign-in exclusion, course mismatch, divergent submissions, seen cases,
stale previews, and failed writes. Browser tests exercise real download/import
dialogs across isolated browser contexts, restored controls, cancellation,
reload, and failed-save recovery. Record results separately from planned checks;
scripted tests do not establish learner comprehension or cross-browser support.

### Local verification: 28 October 2026

- TypeScript application and test compilation passed; 45 Node tests passed,
  including nine portability tests. All 30 Python checks passed.
- Two Chromium transfer scenarios passed against a fresh local build: actual
  practice plus a different-case submission and reflection restored in an
  isolated browser, including reload, restored controls, the next unseen case,
  and duplicate import. Cancellation, wrong password, and simulated storage
  failure preserved the earlier record; retry succeeded.
- Export and import dialogs were visually checked at a 1050-pixel viewport.
- Seven existing quiz/reflection and record-view Chromium scenarios passed.
  One initially failed because it expected the previous reset-warning text;
  that assertion was updated to require the encrypted-backup guidance and its
  scenario passed on rerun. No application change was needed for that failure.
- Release regression covered all 45 non-sign-in Chromium scenarios, passing
  across the full run and a targeted transfer-test rerun. The transfer test now
  waits for the requested notebook tab before running cells; workspace
  restoration could otherwise run the previously open notebook. Both transfer
  scenarios passed after this test synchronization fix. The two sign-in tests
  require the hosted mock provider and were unavailable in the local run.
- The first hosted release exposed a second test-layout assumption: at the
  destination viewport, toolbar overflow hid the idle kernel indicator. The
  transfer test now reads that state within the active notebook without
  requiring the indicator itself to be visible. Both local transfer scenarios
  passed again after this test-only correction.
- The local review preview was updated. These results cover local checks;
  deployment verification is a separate release step. Firefox, WebKit, and
  transfer between physical devices remain unverified for this change.

## References

- [Web Crypto encryption](https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/encrypt)
  and [key derivation](https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/deriveKey).
- [OWASP password storage guidance](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
  supplies the PBKDF2-HMAC-SHA-256 iteration reference. This informs the engineering
  choice, not a certification of this backup format.
- [Browser storage](browser-storage.md) and [different-case pilot](classification-reassessment-pilot.md).
