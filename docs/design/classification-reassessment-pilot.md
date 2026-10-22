# U03 N06: practice and different-case reassessment pilot

Status: local implementation for course-owner review; educational effectiveness is unvalidated. This policy applies only to U03 N06. Other activities retain their existing policy.

## Learner workflow

1. Classify the five course-aligned practice tables. Submit gives a result for each table. Incorrect classifications trigger authored help about individual records, grouped summaries, or both.
2. Use up to three practice hints. Guidance and submissions remain in the local learner record.
3. Select **Try another case**. The host selects a table set that this browser learner has not previously opened. This attempt starts without recorded hints; hints are disabled for the check.
4. Submit all classifications. Incomplete submissions receive no correctness feedback and do not consume the first complete submission. A correct first complete submission demonstrates performance on this different case. Once correctness feedback has been shown, corrections to that same case are practice, not a new independent demonstration.
5. Return to practice, or try the next different case. Re-running controls or reloading resumes the current attempt; it does not reset hint history or turn a displayed case into an unseen case.
6. Record an unscored explanation of what one row represents. It appears with the learner's reflections.

Practice completion does not assign Competent or any other proficiency level. The pilot reports **Practice completed with assistance**, **Practice completed without recorded hints**, or **Demonstrated on a different case**. Later incorrect performance requests a recheck while preserving the earlier successful observation and evidence. A further correct first submission on an unseen case resolves the recheck.

## Data and policy

`catalog/case-aggregate-v1.json` is the shared, versioned assessment definition referenced by the TriG activity. It holds invented example rows, their row meanings, three different-case sets, and authored remediation. The catalog projection validates the bounded definition and includes it in the source digest. The notebook generator and check use the same definition. New meanings or changed task cases require a new version.

The pure engine applies the declared `practice-transfer/1` policy. It interprets criterion outcomes and versioned attempt snapshots, and bounded case/aggregate selections, without free-text answers. Host code supplies attempt IDs, timestamps, hint levels, and submission counts. A version handshake rejects stale pilot controls. Existing observations remain in the record but cannot silently satisfy the new assessment policy.

No new upper-ontology terms are asserted. Optional pilot provenance uses the application's `assessment#` namespace in the evidence export. The export includes task version, mode, attempt ID, submission count, criterion outcomes, and task progress wording. Only the selected case/aggregate codes are retained, so submitted choices can be restored on reopening. Incomplete submissions store those choices with unscored criterion outcomes and reveal no correctness feedback. Unsubmitted choices are not saved. Free-text reflection answers stay in the browser record and its separate reflection download. No learner records leave the browser automatically.

Pilot saves write the updated attempt and observation together before acknowledging success. If browser storage refuses the write, the UI reports failure and keeps the previous record. Other activities keep their existing storage behavior.

## Deliberate limits

- The pool contains three different-case sets. A displayed case is counted as seen even if abandoned. Exhaustion is explicit; returning to practice remains available, but another independent check requires an additional authored case. The pilot does not invent fresh evidence by cycling old cases.
- No recorded hints does not prove absence of outside help, guessing, or answer inspection. This is formative browser-local evidence, not a secure examination.
- One different-case result supports the bounded classification task, not workplace proficiency, retention, or broad transfer.
- Authored remediation is determined by missed row classifications; no AI diagnosis is performed.
- Earlier observations and reflections remain intact. An old course task's success alone does not meet this new task version.
- Learner testing should review whether participants can explain one row, handle numeric values in individual records and identifiers in summaries, use the suggested help, and classify unfamiliar examples. Scripted tests establish software behavior only.

## Review checks

- Three practice hints followed by a new-case success can advance task progress without deleting the earlier guided history.
- Correcting a wrong answer after feedback on the same case does not advance independent demonstration.
- Incomplete submissions reveal no correctness feedback; retries remain recorded.
- Reruns, reloads, returning to practice, and previously displayed cases preserve their history.
- Per-table outcomes and progress remain readable in My learning record and the evidence export.
- The existing notebook count and Python-only course route remain unchanged.

## Local validation - 2026-10-22

36 Node tests and 30 Python tests passed. Both standard and extended pilot evidence exports conform to the al-core shapes. All 22 published Python notebook sources compile; all 42 authoring notebooks pass reference checks. Six distinct Chromium scenarios passed: U03 N01 and N05 regressions; the complete N06 practice/reassessment/reload/record-view journey; N06 storage-write failure and recovery; downstream Unit 4 and Unit 9 workflows with qualifying prerequisite evidence. The narrow rendered radio/feedback layout was inspected. The final local VS Code preview matches the assembled notebook bytes and compiled extension. These results do not establish learner effectiveness or Firefox/WebKit behavior. Publication is gated by the full hosted build and browser suite.
