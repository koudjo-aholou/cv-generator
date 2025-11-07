/**
 * Data mapping for PDF generation
 */

import { fileToBase64 } from '../../core/utils/helpers.js';

export const prepareDataForPdf = async (parsedData, config, contactInfo, photoFile) => {
    const dataToSend = { ...parsedData };

    // Update contact information
    if (!dataToSend.profile) {
        dataToSend.profile = {};
    }
    if (contactInfo.email) {
        dataToSend.profile.email = contactInfo.email;
    }
    if (contactInfo.phone) {
        dataToSend.profile.phone = contactInfo.phone;
    }
    if (contactInfo.address) {
        dataToSend.profile.address = contactInfo.address;
    }

    // Update skills if specific skills are selected
    if (config.skills_selected && config.skills_selected.length > 0) {
        dataToSend.skills = config.skills_selected;
    }

    // Add photo if available
    if (photoFile) {
        const photoBase64 = await fileToBase64(photoFile);
        dataToSend.photo = photoBase64;
    }

    // Add configuration
    dataToSend.config = config;

    return dataToSend;
};
