// Sidebar panel: recommendations with reasons, progress per capability, the
// current exercise's facilitation ladder, and learner-record controls.
// Rendering is a pure function of (catalog, record, assessment, exercise).

import { Dialog, showDialog } from '@jupyterlab/apputils';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { Widget } from '@lumino/widgets';

import { assess, Assessment, Catalog, exportNQuads, GAP, REASON, STATUS } from '../engine';
import { CONSENT_TEXT, IdentityBindingError, newBinding, reverify } from '../identity/binding';
import { OidcConfig, OidcError, signIn } from './oidc';
import { ExerciseContext, INotebookGuide } from './guide';
import { exerciseMetadata, ExerciseObserver, kernelLanguage, ObserverEvent } from './observer';
import { LearnerStore } from './store';

const REASON_TEXT: Readonly<Record<string, string>> = {
  [REASON.notAssessed]: 'not assessed yet',
  [REASON.belowTarget]: 'below target',
  [REASON.insufficientIndependentEvidence]: 'not yet demonstrated',
  [REASON.confirmSelfReport]: 'confirm your self-assessment',
  [REASON.prerequisitesMet]: 'prerequisites done',
  [REASON.criticalGate]: 'critical'
};

const STATE_TEXT: Readonly<Record<string, string>> = {
  [STATUS.demonstrated]: 'Demonstrated',
  [STATUS.reportedNeedsConfirmation]: 'Reported, needs confirmation',
  [STATUS.developmentOpportunity]: 'Keep practising',
  [STATUS.notAssessed]: 'Not assessed'
};

const LANGUAGE_TEXT: Readonly<Record<string, string>> = { python: 'Python', r: 'R' };

function el<K extends keyof HTMLElementTagNameMap>(tag: K, props: Record<string, unknown> = {}, ...children: (Node | string)[]): HTMLElementTagNameMap[K] {
  const node: HTMLElementTagNameMap[K] = document.createElement(tag);
  Object.assign(node, props);
  node.append(...children);
  return node;
}

export class LearningPanel extends Widget {
  private assessment: Assessment;
  private exercise: ExerciseContext | null = null;
  private revealed: { level: number; text: string }[] = [];
  private lastEvent: ObserverEvent | null = null;
  private signInAbort: AbortController | null = null;
  private identityMessage: { text: string; ok: boolean } | null = null;

  constructor(
    private readonly catalog: Catalog,
    private readonly store: LearnerStore,
    tracker: INotebookTracker,
    private readonly docManager: IDocumentManager,
    private readonly guide: INotebookGuide,
    observer: ExerciseObserver,
    private readonly oidc: OidcConfig | null
  ) {
    super();
    this.id = 'al-engine-learning';
    this.title.caption = 'Learning';
    this.addClass('al-LearningPanel');
    this.assessment = assess(catalog, store.record);

    store.changed.connect(() => {
      this.assessment = assess(this.catalog, this.store.record);
      this.render();
    });
    observer.observed.connect((_, event) => {
      this.lastEvent = event;
      this.render();
    });
    tracker.currentChanged.connect((_, panel) => void this.trackExercise(panel));
    void this.trackExercise(tracker.currentWidget);
    this.render();
  }

  private label(iri: string): string {
    return (
      this.catalog.capabilities.find(c => c.iri === iri)?.label ??
      this.catalog.activities.find(a => a.iri === iri)?.title ??
      this.catalog.levels.find(l => l.iri === iri)?.label ??
      iri
    );
  }

  private async trackExercise(panel: NotebookPanel | null): Promise<void> {
    this.exercise = null;
    this.revealed = [];
    if (panel) {
      await panel.context.ready;
      const cell = panel.content.widgets.find(c => exerciseMetadata(c.model.getMetadata('al')));
      const meta = cell ? exerciseMetadata(cell.model.getMetadata('al')) : null;
      if (meta) {
        await panel.sessionContext.ready;
        const kernel = panel.sessionContext.session?.kernel;
        const language = kernel ? await kernelLanguage(kernel) : '';
        this.exercise = { activity: meta.activity, title: this.label(meta.activity), hints: meta.hints, language };
        const used = this.store.guidanceFor(meta.activity);
        for (let level = 1; level <= used; level++) this.revealed.push(await this.guide.help(this.exercise, level));
      }
    }
    this.render();
  }

  private async nextHint(): Promise<void> {
    if (!this.exercise) return;
    const level = this.revealed.length + 1;
    if (level > this.guide.maxLevel(this.exercise)) return;
    const rule = this.catalog.rules.find(r => r.activity === this.exercise!.activity);
    if (rule && level > rule.maximumGuidance) {
      const result = await showDialog({
        title: 'This hint is close to the answer',
        body: `Attempts after more than ${rule.maximumGuidance} hints still give feedback, but they won't count as evidence for this capability.`,
        buttons: [Dialog.cancelButton(), Dialog.okButton({ label: 'Show hint' })]
      });
      if (!result.button.accept) return;
    }
    const reply = await this.guide.help(this.exercise, level);
    this.revealed.push(reply);
    this.store.recordGuidance(this.exercise.activity, reply.level);
  }

  private async open(activityIri: string, language: string): Promise<void> {
    const path = this.catalog.activities.find(a => a.iri === activityIri)?.notebooks[language];
    if (path) this.docManager.openOrReveal(path);
  }

  private async exportRecord(): Promise<void> {
    const nq = await exportNQuads(this.catalog, this.store.record, this.assessment, { generatedAt: new Date().toISOString() });
    const url = URL.createObjectURL(new Blob([nq], { type: 'application/n-quads' }));
    const a = el('a', { href: url, download: 'learner-record.nq' });
    document.body.append(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  private async linkOrVerify(): Promise<void> {
    if (!this.oidc || this.signInAbort) return;
    const existing = this.store.record.identity;
    if (!existing) {
      const consent = await showDialog({
        title: 'Link your sign-in to this learning record?',
        body: CONSENT_TEXT,
        buttons: [Dialog.cancelButton(), Dialog.okButton({ label: 'I agree, sign in' })]
      });
      if (!consent.button.accept) return;
    }
    this.signInAbort = new AbortController();
    this.identityMessage = { text: 'Waiting for sign-in in the pop-up window…', ok: true };
    this.render();
    try {
      const verified = await signIn(this.oidc, this.signInAbort.signal);
      const now = new Date().toISOString();
      const binding = existing
        ? reverify(existing, verified.issuer, verified.subject, now)
        : newBinding(verified.issuer, verified.subject, now, {
            binding: `urn:uuid:${globalThis.crypto.randomUUID()}`,
            consent: `urn:uuid:${globalThis.crypto.randomUUID()}`
          });
      this.identityMessage = { text: existing ? 'Sign-in verified again.' : 'Sign-in linked to this record.', ok: true };
      this.signInAbort = null;
      this.store.setIdentity(binding);
    } catch (error) {
      const known = error instanceof OidcError || error instanceof IdentityBindingError;
      this.identityMessage = { text: known ? (error as Error).message.replace(/^[A-Z_]+: /, '') : 'Sign-in failed.', ok: false };
      if (!known) console.error('al-engine: sign-in failed', error);
      this.signInAbort = null;
      this.render();
    }
  }

  private async unlink(): Promise<void> {
    const result = await showDialog({
      title: 'Unlink sign-in?',
      body: 'The link to your organisation sign-in is removed from this record. Your learning progress is kept.',
      buttons: [Dialog.cancelButton(), Dialog.warnButton({ label: 'Unlink' })]
    });
    if (!result.button.accept) return;
    this.identityMessage = { text: 'Sign-in unlinked.', ok: true };
    this.store.setIdentity(undefined);
  }

  private renderIdentity(): HTMLElement | '' {
    if (!this.oidc) return '';
    const identity = this.store.record.identity;
    const section = el('section', { className: 'al-section al-identity' }, el('h3', {}, 'Identity'));
    if (identity) {
      const host = new URL(identity.issuer).host;
      section.append(
        el('div', { className: 'al-identity-status' }, `Linked to ${host}`),
        el('div', { className: 'al-meta' }, `Previously verified ${new Date(identity.verifiedAt).toLocaleString()}`)
      );
    } else {
      section.append(el('div', { className: 'al-identity-status' }, 'Not linked. Your record is anonymous.'));
    }
    if (this.identityMessage) {
      section.append(el('div', { className: `al-identity-message ${this.identityMessage.ok ? '' : 'al-warning'}` }, this.identityMessage.text));
    }
    if (this.signInAbort) {
      const cancel = el('button', { className: 'jp-Button' }, 'Cancel sign-in');
      cancel.onclick = () => this.signInAbort?.abort();
      section.append(cancel);
    } else {
      const label = identity ? 'Verify again' : this.oidc.label ?? 'Link organisation sign-in';
      const link = el('button', { className: 'jp-Button al-identity-link' }, label);
      link.onclick = () => void this.linkOrVerify();
      section.append(link);
      if (identity) {
        const unlink = el('button', { className: 'jp-Button' }, 'Unlink');
        unlink.onclick = () => void this.unlink();
        section.append(unlink);
      }
    }
    return section;
  }

  private async reset(): Promise<void> {
    const result = await showDialog({
      title: 'Reset learning record?',
      body: 'This deletes your observations and hint history in this browser. Export first if you want to keep them.',
      buttons: [Dialog.cancelButton(), Dialog.warnButton({ label: 'Reset' })]
    });
    if (result.button.accept) this.store.reset();
  }

  private render(): void {
    const { catalog, assessment, store } = this;
    const preferred = store.preferredLanguage;
    const node = this.node;
    node.replaceChildren();

    node.append(el('h2', { className: 'al-title' }, catalog.framework.title));

    // Last observation feedback.
    if (this.lastEvent) {
      const o = this.lastEvent.observation;
      const text = this.lastEvent.problem
        ? this.lastEvent.problem
        : o!.outcome.endsWith('#Correct')
          ? o!.guidanceLevel > (catalog.rules.find(r => r.activity === o!.activity)?.maximumGuidance ?? Infinity)
            ? 'Correct. Recorded, but with this much help it does not count as evidence.'
            : 'Correct. Recorded as evidence.'
          : o!.outcome.endsWith('#Incomplete')
            ? 'Not finished yet: replace the placeholder with your answer and run the cell again.'
            : 'Not yet correct. Try again or use a hint.';
      node.append(el('div', { className: `al-feedback ${o?.outcome.endsWith('#Correct') ? 'al-ok' : ''}` }, text));
    }

    // Recommendations.
    const recs = el('section', { className: 'al-section' }, el('h3', {}, 'Next'));
    const languageSelect = el('select', { className: 'al-language', title: 'Exercise language' });
    for (const [code, name] of Object.entries(LANGUAGE_TEXT)) {
      languageSelect.append(el('option', { value: code, selected: code === preferred }, name));
    }
    languageSelect.onchange = () => (store.preferredLanguage = languageSelect.value);
    recs.append(el('label', { className: 'al-language-label' }, 'Exercises in ', languageSelect));
    if (assessment.recommendations.length === 0) {
      recs.append(el('p', {}, 'All targets in this framework are demonstrated.'));
    }
    for (const rec of assessment.recommendations) {
      const open = el('button', { className: 'jp-Button al-open' }, 'Open');
      open.onclick = () => void this.open(rec.activity, preferred);
      recs.append(
        el(
          'div',
          { className: 'al-rec' },
          el('div', { className: 'al-rec-title' }, `${rec.rank}. ${this.label(rec.activity)}`),
          el('div', { className: 'al-reasons' }, rec.reasons.map(r => REASON_TEXT[r] ?? r).join(' · ')),
          open
        )
      );
    }
    node.append(recs);

    // Current exercise and hints.
    if (this.exercise) {
      const ex = this.exercise;
      const section = el('section', { className: 'al-section' }, el('h3', {}, 'This exercise'), el('p', {}, ex.title));
      for (const hint of this.revealed) section.append(el('div', { className: 'al-hint' }, `Hint ${hint.level}: ${hint.text}`));
      if (this.revealed.length < this.guide.maxLevel(ex)) {
        const button = el('button', { className: 'jp-Button al-hint-button' }, this.revealed.length ? 'Another hint' : 'Show a hint');
        button.onclick = () => void this.nextHint();
        section.append(button);
      }
      node.append(section);
    }

    // Progress.
    const progress = el('section', { className: 'al-section' }, el('h3', {}, 'Progress'));
    const list = el('ul', { className: 'al-progress' });
    for (const gap of assessment.gaps) {
      const estimate = assessment.estimates.find(e => e.iri === gap.estimate);
      list.append(
        el(
          'li',
          { className: `al-gap ${gap.state === GAP.achieved ? 'al-achieved' : ''}` },
          el('span', { className: 'al-cap' }, this.label(gap.capability)),
          el('span', { className: 'al-state' }, STATE_TEXT[gap.status] ?? gap.status, estimate?.level ? ` (${this.label(estimate.level)})` : ''),
          gap.gateBlocked ? el('span', { className: 'al-critical', title: 'Critical target not yet demonstrated' }, 'critical') : ''
        )
      );
    }
    progress.append(list);
    node.append(progress);

    // Knowledge checks (quizzes) declared in the catalog with a URL.
    const quizzes = catalog.activities.filter(a => a.url && a.kind.endsWith('#Assessment'));
    if (quizzes.length) {
      const section = el('section', { className: 'al-section al-quizzes' }, el('h3', {}, 'Knowledge checks'));
      for (const quiz of quizzes) {
        const open = el('button', { className: 'jp-Button al-quiz-open' }, `Open: ${quiz.title}`);
        open.onclick = () => window.open(quiz.url, '_blank', 'noopener');
        section.append(open);
      }
      section.append(el('div', { className: 'al-meta' }, 'Opens in a new tab. Quiz results are not yet recorded in your learning record.'));
      node.append(section);
    }

    node.append(this.renderIdentity());

    // Record controls.
    const exportButton = el('button', { className: 'jp-Button' }, 'Export record');
    exportButton.onclick = () => void this.exportRecord();
    const resetButton = el('button', { className: 'jp-Button' }, 'Reset');
    resetButton.onclick = () => void this.reset();
    node.append(
      el(
        'section',
        { className: 'al-section al-footer' },
        el('div', {}, `Learner ${store.record.learner.slice(9, 17)}… · ${store.record.observations.length} observations`),
        store.persistent ? '' : el('div', { className: 'al-warning' }, 'Browser storage is unavailable: this record lasts only for this page.'),
        el('div', {}, exportButton, resetButton),
        el('div', { className: 'al-meta' }, `${assessment.engineVersion} · policy ${assessment.policyVersion}`)
      )
    );
  }
}
