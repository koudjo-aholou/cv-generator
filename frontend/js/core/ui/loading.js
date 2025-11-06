/**
 * Loading indicator management
 */

import { $ } from '../dom/elements.js';

class LoadingManager {
    constructor() {
        this.loadingElement = null;
        this.count = 0;
    }

    init(elementId = 'loading') {
        this.loadingElement = $(elementId);
    }

    show() {
        this.count++;
        if (this.loadingElement) {
            this.loadingElement.style.display = 'block';
        }
    }

    hide() {
        this.count = Math.max(0, this.count - 1);
        if (this.count === 0 && this.loadingElement) {
            this.loadingElement.style.display = 'none';
        }
    }

    forceHide() {
        this.count = 0;
        if (this.loadingElement) {
            this.loadingElement.style.display = 'none';
        }
    }

    isVisible() {
        return this.count > 0;
    }
}

export const loading = new LoadingManager();
