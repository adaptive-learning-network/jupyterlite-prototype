// Local reviewer mode replaces stale supplied copies. Production never opts in.
import { Notification } from '@jupyterlab/apputils';
import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

import { loadNotebookVersions } from './assets';

function sources(document: unknown): string {
  const notebook = document as { cells: { cell_type: string; source: string | string[]; attachments?: unknown; metadata?: { al?: unknown } }[] };
  return JSON.stringify(notebook.cells.map(cell => [
    cell.cell_type, Array.isArray(cell.source) ? cell.source.join('') : cell.source,
    cell.attachments ?? null, cell.metadata?.al ?? null
  ]));
}

export async function enableCourseReviewUpdates(tracker: INotebookTracker, manager: IDocumentManager): Promise<void> {
  if (PageConfig.getOption('alCourseReviewMode') !== 'true') return;
  const versions = await loadNotebookVersions();
  const pending = new Set<string>();

  async function update(panel: NotebookPanel): Promise<void> {
    await panel.context.ready;
    const path = panel.context.path.replace(/\\/g, '/');
    const version = versions[path];
    if (!version || pending.has(path)) return;
    const key = `al-engine:course-copy:${path}`;
    // A saved/restored tab can contain old attachments even after its version
    // marker was updated. In disposable review mode compare the actual source
    // on every open; a marker alone does not prove that the copy is current.
    pending.add(path);
    try {
      const url = URLExt.join(PageConfig.getBaseUrl(), 'files', ...path.split('/').map(encodeURIComponent));
      const response = await fetch(url, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Could not load the latest ${path} (HTTP ${response.status}).`);
      const supplied = await response.json();
      if (supplied.nbformat !== 4 || !Array.isArray(supplied.cells)) throw new Error('Invalid supplied course notebook.');
      if (panel.isDisposed) return;
      const current = panel.context.model.toJSON();
      if (sources(current) !== sources(supplied)) {
        const stem = path.split('/').pop()!.replace(/\.ipynb$/, '');
        await manager.services.contents.save(path, { type: 'notebook', format: 'json', content: supplied });
        await panel.context.revert();
        Notification.success(`Loaded the current course version of ${stem}.`, { autoClose: 4000 });
      }
      try { localStorage.setItem(key, version); } catch { /* Session-only tracking. */ }
    } catch (error) {
      Notification.error(`Course notebook update failed: ${String(error)}`, { autoClose: false });
    } finally {
      pending.delete(path);
    }
  }

  tracker.widgetAdded.connect((_, panel) => { void update(panel); });
  tracker.forEach(panel => { void update(panel); });
}
