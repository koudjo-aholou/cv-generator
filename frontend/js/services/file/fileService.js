/**
 * File management service
 */

import { cvStateService } from '../state/cvStateService.js';
import { notifications } from '../../core/ui/notifications.js';

class FileService {
    handleFiles(files) {
        if (files.length === 0) {
            notifications.showError('Veuillez sélectionner des fichiers CSV');
            return false;
        }

        cvStateService.setFiles(files);
        cvStateService.setParsedData(null); // Reset parsed data when files change
        notifications.hide();
        return true;
    }

    removeFile(index) {
        cvStateService.removeFile(index);
        cvStateService.setParsedData(null); // Reset parsed data when files change
    }

    getFiles() {
        return cvStateService.getFiles();
    }

    hasFiles() {
        const files = this.getFiles();
        return files && files.length > 0;
    }
}

export const fileService = new FileService();
