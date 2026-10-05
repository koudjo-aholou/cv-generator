/**
 * Generic validation utilities
 */

export const isValidEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

export const isValidUrl = (url) => {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
};

export const isEmpty = (value) => {
    if (value === null || value === undefined) return true;
    if (typeof value === 'string') return value.trim().length === 0;
    if (Array.isArray(value)) return value.length === 0;
    if (typeof value === 'object') return Object.keys(value).length === 0;
    return false;
};

export const isValidFileSize = (file, maxSize) => {
    return file.size <= maxSize;
};

export const isValidFileType = (file, allowedTypes) => {
    return allowedTypes.includes(file.type);
};

export const isArrayOfStrings = (value) => {
    return Array.isArray(value) && value.every(item => typeof item === 'string');
};
