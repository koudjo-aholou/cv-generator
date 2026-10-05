/**
 * Template presets
 */

import { TEMPLATE_PRESETS } from '../../config/defaults.js';

export const getTemplatePreset = (templateName) => {
    return TEMPLATE_PRESETS[templateName];
};

export const applyTemplateColors = (templateName) => {
    const colors = getTemplatePreset(templateName);
    if (!colors) return null;

    return { ...colors };
};
