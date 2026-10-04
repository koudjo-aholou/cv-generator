/**
 * Shared jsdom harness for the frontend tests.
 *
 * Loads the REAL frontend/index.html and frontend/style.css so the tests
 * catch any drift in ids or markup, and so visibility can be asserted
 * through getComputedStyle rather than through implementation details.
 */
import { JSDOM } from 'jsdom';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const HTML = fs.readFileSync(path.join(ROOT, 'frontend', 'index.html'), 'utf8');
const CSS = fs.readFileSync(path.join(ROOT, 'frontend', 'style.css'), 'utf8');

/**
 * Build a fresh DOM and publish the globals the application modules expect.
 *
 * The modules are singletons that read `document` at call time, so a new DOM
 * per test is enough — provided the element cache is cleared, otherwise it
 * would hand back nodes belonging to the previous document.
 */
let generation = 0;

export async function setupDom() {
    generation += 1;
    const dom = new JSDOM(HTML, { runScripts: 'outside-only', url: 'http://localhost:8080' });
    const { window } = dom;

    // The <link> is not fetched (no `resources: usable`): inject the real
    // stylesheet instead, via textContent so jsdom parses it.
    const style = window.document.createElement('style');
    style.textContent = CSS;
    window.document.head.appendChild(style);

    // `navigator` is a getter-only global in Node, so it is left out.
    for (const key of [
        'window', 'document', 'HTMLElement', 'customElements', 'CustomEvent',
        'Event', 'FileReader', 'File', 'Blob', 'getComputedStyle'
    ]) {
        globalThis[key] = window[key];
    }

    const { elements } = await import('../../frontend/js/core/dom/elements.js');
    elements.clear();

    const { cvStateService } = await import('../../frontend/js/services/state/cvStateService.js');
    cvStateService.reset();

    return { dom, window, document: window.document, cvStateService };
}

/** True when the element is hidden, however that is implemented. */
export function isHidden(el) {
    return globalThis.getComputedStyle(el).display === 'none';
}

export const $ = (id) => globalThis.document.getElementById(id);

/**
 * Register a Web Component on the CURRENT document's registry.
 *
 * Two problems are solved here. The editors call customElements.define() at
 * module scope, so with the ES module cache that only runs on the very first
 * import. Worse, the class captures `HTMLElement` from whichever window was
 * current at evaluation time — from the second DOM on, the prototype chain no
 * longer matches and the tags in index.html silently stay inert.
 *
 * Re-importing with a per-DOM cache-busting token re-evaluates the module
 * against the current globals. Only the editor modules are tokenised: their
 * own imports (the state service in particular) resolve untokenised and stay
 * the shared singletons the tests assert against.
 */
export async function defineEditor(tag, moduleFile, className) {
    const mod = await import(`../../frontend/js/ui/editors/${moduleFile}?dom=${generation}`);
    if (!globalThis.customElements.get(tag)) {
        globalThis.customElements.define(tag, mod[className]);
    }
    return mod[className];
}
