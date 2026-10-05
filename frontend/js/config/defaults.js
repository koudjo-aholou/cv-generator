/**
 * Default configurations
 */

import { CV_SECTIONS } from './constants.js';

export const TEMPLATE_PRESETS = {
    modern: {
        primary: '#3498db',
        text: '#2c3e50',
        secondary_text: '#7f8c8d'
    },
    classic: {
        primary: '#2c3e50',
        text: '#1a1a1a',
        secondary_text: '#666666'
    },
    creative: {
        primary: '#e74c3c',
        text: '#2c3e50',
        secondary_text: '#95a5a6'
    }
};

export const DEFAULT_CONFIG = {
    language: 'fr',
    cv_type: 'standard',
    sections: Object.fromEntries(CV_SECTIONS.map((section) => [section, true])),
    section_order: [...CV_SECTIONS],
    experience_visible: null,
    education_visible: null,
    skills_selected: null,
    template: 'modern',
    colors: {
        primary: '#3498db',
        text: '#2c3e50',
        secondary_text: '#7f8c8d'
    }
};
