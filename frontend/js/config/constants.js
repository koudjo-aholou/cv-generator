/**
 * Application constants
 */

export const API_URL = 'http://localhost:5000';

export const STEPS = {
    UPLOAD: 1,
    CONFIGURE: 2,
    PREVIEW: 3
};

export const TOTAL_STEPS = 3;

export const REQUIRED_FILES = ['Profile.csv', 'Positions.csv', 'Education.csv'];

export const PHOTO_CONSTRAINTS = {
    MAX_SIZE: 5 * 1024 * 1024, // 5MB
    ALLOWED_TYPES: ['image/jpeg', 'image/jpg', 'image/png']
};

export const SECTION_NAMES_BY_LANG = {
    fr: {
        about: 'À Propos',
        experience: 'Expériences Professionnelles',
        education: 'Formations',
        skills: 'Compétences',
        languages: 'Langues',
        certifications: 'Certifications'
    },
    en: {
        about: 'About',
        experience: 'Professional Experience',
        education: 'Education',
        skills: 'Skills',
        languages: 'Languages',
        certifications: 'Certifications'
    }
};
