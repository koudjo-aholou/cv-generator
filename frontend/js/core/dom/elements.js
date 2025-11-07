/**
 * DOM elements cache and selection utilities
 */

class ElementCache {
    constructor() {
        this.cache = new Map();
    }

    get(id) {
        if (!this.cache.has(id)) {
            const element = document.getElementById(id);
            if (element) {
                this.cache.set(id, element);
            }
        }
        return this.cache.get(id);
    }

    getAll(selector) {
        return document.querySelectorAll(selector);
    }

    clear() {
        this.cache.clear();
    }
}

export const elements = new ElementCache();

// Helper functions
export const $ = (id) => elements.get(id);
export const $$ = (selector) => elements.getAll(selector);
