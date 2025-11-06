/**
 * Sections management business logic
 */

export const moveSectionUp = (sectionOrder, index) => {
    if (index > 0) {
        const temp = sectionOrder[index];
        sectionOrder[index] = sectionOrder[index - 1];
        sectionOrder[index - 1] = temp;
    }
    return sectionOrder;
};

export const moveSectionDown = (sectionOrder, index) => {
    if (index < sectionOrder.length - 1) {
        const temp = sectionOrder[index];
        sectionOrder[index] = sectionOrder[index + 1];
        sectionOrder[index + 1] = temp;
    }
    return sectionOrder;
};

export const reorderSection = (sectionOrder, fromIndex, toIndex) => {
    const [removed] = sectionOrder.splice(fromIndex, 1);
    sectionOrder.splice(toIndex, 0, removed);
    return sectionOrder;
};

export const checkSectionHasData = (section, parsedData) => {
    switch (section) {
        case 'summary':
            return !!(parsedData.profile && parsedData.profile.summary);
        case 'experience':
            return !!(parsedData.positions && parsedData.positions.length > 0);
        case 'education':
            return !!(parsedData.education && parsedData.education.length > 0);
        case 'skills':
            return !!(parsedData.skills && parsedData.skills.length > 0);
        case 'languages':
            return !!(parsedData.languages && parsedData.languages.length > 0);
        case 'certifications':
            return !!(parsedData.certifications && parsedData.certifications.length > 0);
        default:
            return false;
    }
};
