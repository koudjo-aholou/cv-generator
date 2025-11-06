/**
 * Languages editor component
 */

import { $ } from '../../core/dom/elements.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import { eventBus } from '../../core/dom/events.js';

export class LanguagesEditor {
    constructor() {
        this.container = null;
    }

    init() {
        this.container = $('languages-editor');
        eventBus.on('data:parsed', () => this.render());
    }

    render() {
        // Manages languages list with add/edit/delete
    }
}
