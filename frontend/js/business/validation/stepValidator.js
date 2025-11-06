/**
 * Step validation business logic
 */

import { REQUIRED_FILES } from '../../config/constants.js';
import { notifications } from '../../core/ui/notifications.js';

export const validateStep1 = (selectedFiles) => {
    // Check if at least one file is uploaded
    if (!selectedFiles || selectedFiles.length === 0) {
        notifications.showError('Veuillez télécharger au moins les fichiers CSV requis');
        return false;
    }

    const uploadedFileNames = selectedFiles.map(f => f.name);

    const missingFiles = REQUIRED_FILES.filter(req =>
        !uploadedFileNames.some(uploaded => uploaded === req)
    );

    if (missingFiles.length > 0) {
        notifications.showError(`Fichiers requis manquants : ${missingFiles.join(', ')}`);
        return false;
    }

    return true;
};

export const validateStep2 = () => {
    // Step 2 validation - always passes for now
    return true;
};
