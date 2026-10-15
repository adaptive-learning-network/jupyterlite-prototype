import { ILabShell, JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { INotebookTracker } from '@jupyterlab/notebook';
import { LabIcon } from '@jupyterlab/ui-components';

import { Catalog } from '../engine';
import { loadCatalog, loadCheck } from './assets';
import { enableCourseReviewUpdates } from './course-updates';
import { StaticHintGuide } from './guide';
import { ExerciseObserver } from './observer';
import { readOidcConfig } from './oidc';
import { LearningPanel } from './panel';
import { LearnerStore } from './store';
import { enableReflections } from './reflections';

// JupyterLite's browser contents store uses POSIX paths. An older Windows
// build put backslashes in notebook models; those paths remain in open tabs
// and browser storage even after the static site is rebuilt. Normalize at the
// contents boundary so saving an existing tab does not lose learner edits.
function normalizeBrowserContentsPaths(app: JupyterFrontEnd): void {
  const contents = app.serviceManager.contents;
  const path = (value: string) => value.replace(/\\/g, '/');
  const get = contents.get.bind(contents);
  const save = contents.save.bind(contents);
  const rename = contents.rename.bind(contents);
  const newUntitled = contents.newUntitled.bind(contents);
  const copy = contents.copy.bind(contents);
  const remove = contents.delete.bind(contents);
  contents.get = (name, options) => get(path(name), options);
  contents.save = (name, options) => save(path(name), options && {
    ...options,
    ...(options.path ? { path: path(options.path) } : {})
  });
  contents.rename = (oldName, newName) => rename(path(oldName), path(newName));
  contents.newUntitled = options => newUntitled(options && {
    ...options,
    ...(options.path ? { path: path(options.path) } : {})
  });
  contents.copy = (name, toDir) => copy(path(name), path(toDir));
  contents.delete = name => remove(path(name));
}

// A browser may retain notebooks from an older site build after the bundled
// readings directory disappears. Recreate only the missing directory entries;
// never replace a learner's notebook or clear browser storage.
async function ensureReadingDirectories(app: JupyterFrontEnd): Promise<void> {
  const contents = app.serviceManager.contents;
  for (const path of ['readings', 'readings/ucsf']) {
    const existing = await contents.get(path, { content: false }).catch(() => null);
    if (existing?.type === 'directory') continue;
    if (existing) throw new Error(`${path} exists but is not a directory`);
    const slash = path.lastIndexOf('/');
    const parent = slash < 0 ? '' : path.slice(0, slash);
    const temporary = await contents.newUntitled({ path: parent, type: 'directory' });
    await contents.rename(temporary.path, path);
  }
}

const learningIcon = new LabIcon({
  name: 'al-engine:learning',
  svgstr:
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path class="jp-icon3" fill="#616161" d="M12 3 1 9l11 6 9-4.91V17h2V9L12 3zm-6.82 9.5v4L12 21l6.82-4.5v-4L12 16l-6.82-3.5z"/></svg>'
});

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlite-al-engine:plugin',
  description: 'Ontology-driven adaptive-learning engine for notebook exercises.',
  autoStart: true,
  requires: [ILabShell, INotebookTracker, IDocumentManager],
  activate: async (app: JupyterFrontEnd, shell: ILabShell, tracker: INotebookTracker, docManager: IDocumentManager) => {
    normalizeBrowserContentsPaths(app);
    try {
      await ensureReadingDirectories(app);
    } catch (error) {
      console.warn('al-engine: could not repair reading directories.', error);
    }
    let catalog: Catalog;
    try {
      catalog = await loadCatalog();
    } catch (error) {
      console.warn('al-engine: no catalog, learning panel disabled.', error);
      return;
    }
    const store = new LearnerStore(catalog.audiences[0].iri);
    enableReflections(tracker, store);
    const observer = new ExerciseObserver(catalog, store, tracker, loadCheck);
    const panel = new LearningPanel(catalog, store, tracker, docManager, new StaticHintGuide(), observer, readOidcConfig());
    void enableCourseReviewUpdates(tracker, docManager).catch(error => {
      console.warn('al-engine: local course-copy updates could not start.', error);
    });
    panel.title.icon = learningIcon;
    shell.add(panel, 'right', { rank: 50 });
    app.restored.then(() => shell.activateById(panel.id));
  }
};

export default plugin;
