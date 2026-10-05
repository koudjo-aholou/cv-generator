/**
 * Step flow business logic
 */

export const initializeConfigFromData = (parsedData, currentConfig) => {
    // Initialize experience_visible with all indices
    if (parsedData.positions && parsedData.positions.length > 0) {
        currentConfig.experience_visible = parsedData.positions.map((_, i) => i);
    }

    // Initialize education_visible with all indices
    if (parsedData.education && parsedData.education.length > 0) {
        currentConfig.education_visible = parsedData.education.map((_, i) => i);
    }

    // Update section toggles based on available data
    currentConfig.sections.summary = !!(parsedData.profile && parsedData.profile.summary);
    currentConfig.sections.experience = !!(parsedData.positions && parsedData.positions.length > 0);
    currentConfig.sections.education = !!(parsedData.education && parsedData.education.length > 0);
    currentConfig.sections.skills = !!(parsedData.skills && parsedData.skills.length > 0);
    currentConfig.sections.languages = !!(parsedData.languages && parsedData.languages.length > 0);
    currentConfig.sections.certifications = !!(parsedData.certifications && parsedData.certifications.length > 0);

    return currentConfig;
};
