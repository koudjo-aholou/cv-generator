/**
 * Data formatting utilities
 */

export const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

export const formatDate = (dateString) => {
    if (!dateString) return '';

    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR');
    } catch {
        return dateString;
    }
};

export const truncateString = (str, maxLength) => {
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength - 3) + '...';
};

export const capitalize = (str) => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
};

export const slugify = (str) => {
    return str
        .toLowerCase()
        .trim()
        .replace(/[^\w\s-]/g, '')
        .replace(/[\s_-]+/g, '-')
        .replace(/^-+|-+$/g, '');
};
