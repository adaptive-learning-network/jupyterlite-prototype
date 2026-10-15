// Application resources live outside the learner's JupyterLite contents drive.
// configure_site.py pins the catalog and checks to one build-specific asset URL.
import { PageConfig, URLExt } from '@jupyterlab/coreutils';

import { Catalog } from '../engine';

async function readAsset(path: string): Promise<Response> {
  const base = PageConfig.getOption('alAssetsBaseUrl');
  if (!base) throw new Error('Adaptive-learning application assets are not configured.');
  const response = await fetch(URLExt.join(PageConfig.getBaseUrl(), base, path));
  if (!response.ok) {
    throw new Error(`Could not load adaptive-learning resource ${path} (HTTP ${response.status}). Reload the course and try again.`);
  }
  return response;
}

export async function loadCatalog(): Promise<Catalog> {
  const response = await readAsset('catalog.json');
  const catalog = await response.json() as Catalog;
  if (catalog?.schema !== 'al-catalog-projection/0.1') {
    throw new Error('Unsupported adaptive-learning catalog projection.');
  }
  return catalog;
}

export async function loadCheck(path: string): Promise<string> {
  // Keep existing notebook metadata (checks/<name>) working, but never resolve
  // arbitrary metadata paths or browser-saved copies as executable checks.
  if (!/^checks\/[a-z0-9-]+\.(py|R)$/.test(path)) {
    throw new Error(`Unsupported exercise check: ${path}`);
  }
  return (await readAsset(path)).text();
}

export async function loadNotebookVersions(): Promise<Record<string, string>> {
  return (await readAsset('notebooks.json')).json();
}
