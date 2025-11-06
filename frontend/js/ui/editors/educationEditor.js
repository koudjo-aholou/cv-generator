/**
 * Education editor component (similar structure to experienceEditor)
 */

import { $} from '../../core/dom/elements.js';
import { createElement } from '../../core/dom/builder.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import * as educationBusiness from '../../business/cv/education.js';
import { eventBus } from '../../core/dom/events.js';

export class EducationEditor {
    constructor() {
        this.container = null;
        this.itemsList = null;
    }

    init() {
        this.container = $('education-editor');
        this.itemsList = $('education-items');
        eventBus.on('data:parsed', () => this.render());
    }

    render() {
        // Similar implementation as ExperienceEditor
        // Manages education list with add/edit/delete/visibility
    }
}
