import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { LearnerStore } from './store';

/** Bridge widget comms to the same browser-local record used by the engine. */
export function enableReflections(tracker: INotebookTracker, store: LearnerStore): void {
  const attach = (panel: NotebookPanel) => {
    const connect = () => {
      const kernel = panel.sessionContext.session?.kernel;
      if (!kernel) return;
      kernel.registerCommTarget('al.reflections', (comm, message) => {
        const section = message.content.data.section;
        if (typeof section !== 'string' || !/^[a-z0-9:/-]{1,200}$/.test(section)) {
          comm.send({ error: 'Invalid reflection section.' });
          return;
        }
        comm.onMsg = msg => {
          try {
            const entries = msg.content.data.entries;
            if (!Array.isArray(entries) || entries.length > 100 || entries.some(entry =>
              !entry || typeof entry !== 'object' || Array.isArray(entry) ||
              typeof entry.prompt !== 'string' || typeof entry.answer !== 'string' ||
              entry.prompt.length > 10000 || entry.answer.length > 100000)) {
              throw new Error('Invalid or oversized reflection.');
            }
            store.recordReflections(section, entries as { prompt: string; answer: string }[]);
            comm.send({ saved: true });
          } catch {
            comm.send({ error: 'Not recorded. Browser storage is unavailable or the response is too large. Keep your text and try again.' });
          }
        };
        comm.send({ entries: store.record.reflections?.[section] ?? [] });
      });
    };
    panel.sessionContext.kernelChanged.connect(connect);
    void panel.sessionContext.ready.then(connect);
    connect();
  };
  tracker.forEach(attach);
  tracker.widgetAdded.connect((_, panel) => attach(panel));
}
