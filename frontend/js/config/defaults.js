/**
 * Default configurations
 */

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
    sections: {
        summary: true,
        experience: true,
        education: true,
        skills: true,
        languages: true,
        certifications: true
    },
    section_order: ['summary', 'experience', 'education', 'skills', 'languages', 'certifications'],
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
