import { ILabShell, JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { INotebookTracker } from '@jupyterlab/notebook';
import { LabIcon } from '@jupyterlab/ui-components';

import { Catalog } from '../engine';
import { StaticHintGuide } from './guide';
import { ExerciseObserver } from './observer';
import { LearningPanel } from './panel';
import { LearnerStore } from './store';

const CATALOG_PATH = 'al/catalog.json';

const learningIcon = new LabIcon({
  name: 'al-engine:learning',
  svgstr:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path class="jp-icon3" fill="#616161" d="M12 3 1 9l11 6 9-4.91V17h2V9L12 3zm-6.82 9.5v4L12 21l6.82-4.5v-4L12 16l-6.82-3.5z"/></svg>'
});

async function loadCatalog(app: JupyterFrontEnd): Promise<Catalog> {
  const model = await app.serviceManager.contents.get(CATALOG_PATH, { content: true });
  const catalog = (typeof model.content === 'string' ? JSON.parse(model.content) : model.content) as Catalog;
  if (catalog?.schema !== 'al-catalog-projection/0.1') throw new Error(`${CATALOG_PATH}: unsupported catalog projection`);
  return catalog;
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlite-al-engine:plugin',
  description: 'Ontology-driven adaptive-learning engine for notebook exercises.',
  autoStart: true,
  requires: [ILabShell, INotebookTracker, IDocumentManager],
  activate: async (app: JupyterFrontEnd, shell: ILabShell, tracker: INotebookTracker, docManager: IDocumentManager) => {
    let catalog: Catalog;
    try {
      catalog = await loadCatalog(app);
    } catch (error) {
      console.warn('al-engine: no catalog, learning panel disabled.', error);
      return;
    }
    const store = new LearnerStore(catalog.audiences[0].iri);
    const observer = new ExerciseObserver(catalog, store, tracker, app.serviceManager.contents);
    const panel = new LearningPanel(catalog, store, tracker, docManager, new StaticHintGuide(), observer);
    panel.title.icon = learningIcon;
    shell.add(panel, 'right', { rank: 50 });
    app.restored.then(() => shell.activateById(panel.id));
  }
};

export default plugin;
