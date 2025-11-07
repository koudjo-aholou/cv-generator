/**
 * Notification system for errors, success, and info messages
 */

import { $ } from '../dom/elements.js';

class NotificationManager {
    constructor() {
        this.errorElement = null;
        this.timeout = null;
    }

    init(elementId = 'errorMessage') {
        this.errorElement = $(elementId);
    }

    showError(message) {
        if (!this.errorElement) return;

        this.errorElement.textContent = '❌ ' + message;
        this.errorElement.style.display = 'block';
        this.errorElement.style.background = '';
        this.errorElement.style.color = '';
        this.errorElement.style.borderLeftColor = '';

        this.clearAutoHide();
    }

    showSuccess(message, autoHide = true) {
        if (!this.errorElement) return;

        this.errorElement.textContent = '✅ ' + message;
        this.errorElement.style.display = 'block';
        this.errorElement.style.background = '#d4edda';
        this.errorElement.style.color = '#155724';
        this.errorElement.style.borderLeftColor = '#28a745';

        if (autoHide) {
            this.autoHide(5000);
        }
    }

    showInfo(message, autoHide = false) {
        if (!this.errorElement) return;

        this.errorElement.textContent = 'ℹ️ ' + message;
        this.errorElement.style.display = 'block';
        this.errorElement.style.background = '#d1ecf1';
        this.errorElement.style.color = '#0c5460';
        this.errorElement.style.borderLeftColor = '#17a2b8';

        if (autoHide) {
            this.autoHide(3000);
        }
    }

    hide() {
        if (!this.errorElement) return;

        this.errorElement.style.display = 'none';
        this.clearAutoHide();
    }

    autoHide(delay = 5000) {
        this.clearAutoHide();
        this.timeout = setTimeout(() => {
            this.hide();
        }, delay);
    }

    clearAutoHide() {
        if (this.timeout) {
            clearTimeout(this.timeout);
            this.timeout = null;
        }
    }
}

export const notifications = new NotificationManager();
