/**
 * Certifications editor component
 */

import { $ } from '../../core/dom/elements.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import { eventBus } from '../../core/dom/events.js';

export class CertificationsEditor {
    constructor() {
        this.container = null;
    }

    init() {
        this.container = $('certifications-editor');
        eventBus.on('data:parsed', () => this.render());
    }

    render() {
        // Manages certifications list with add/edit/delete
    }
}
