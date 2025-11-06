/**
 * Skills editor component
 */

import { $ } from '../../core/dom/elements.js';
import { createElement } from '../../core/dom/builder.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import * as skillsBusiness from '../../business/cv/skills.js';
import { eventBus } from '../../core/dom/events.js';

export class SkillsEditor {
    constructor() {
        this.container = null;
        this.searchInput = null;
    }

    init() {
        this.container = $('skills-selector');
        this.searchInput = $('skills-search');
        eventBus.on('data:parsed', () => this.render());
    }

    render() {
        // Manages skills with checkboxes and search
        // Add/delete/toggle selection functionality
    }
}
