# Reflection question identity and retained writing

The authored registry is `scripts/reflection_questions.json`. Each section owns stable question IDs and meaning versions. The browser retains explicit Record saves; it does not save unrecorded edits.

## Updating a question

- Wording-only change: retain `id` and `version`, update `prompt` in the registry and the authored prompt. Keep the original legacy text in `legacyPrompts`. Existing identified answers restore by ID/version.
- Changed meaning: increment `version`, or use a new ID for a different question. Earlier-version answers remain in My learning record and Download reflections. The new field starts blank and tells the learner where earlier responses can be reviewed.
- New question: allocate an unused ID. Never renumber or reuse an existing ID because a question moved or was removed.
- Legacy entries without IDs migrate only by an exact approved legacy prompt, and only into version 1. Unmatched legacy entries remain available; they are never discarded on Record.

Recording changed text retains the earlier answer, original prompt, and timestamp in history. Recording an empty field intentionally clears the current answer while preserving earlier writing. Removed questions and earlier meaning versions remain in the browser record and readable download. Storage failures leave the current record unchanged and show an error. Browser eviction and Reset can still remove the local record; the text download is readable, not an automatic restoration format.

The registry covers authoring readings as well as canonical notebooks; only the assembled course is published. A deterministic prompt-derived fallback supports unmapped legacy authoring inputs. New canonical questions should be registered explicitly so subsequent wording edits retain their identity.
