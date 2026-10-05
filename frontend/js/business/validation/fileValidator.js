/**
 * File validation business logic
 */

export const validateCsvFiles = (files) => {
    return files.filter(file => file.name.endsWith('.csv'));
};

export const hasRequiredFiles = (files, requiredFiles) => {
    const fileNames = files.map(f => f.name);
    return requiredFiles.every(required =>
        fileNames.some(name => name === required)
    );
};
