/**
 * Photo management service
 */

import { cvStateService } from '../state/cvStateService.js';
import { notifications } from '../../core/ui/notifications.js';
import { PHOTO_CONSTRAINTS } from '../../config/constants.js';
import { isValidFileSize, isValidFileType } from '../../core/utils/validators.js';

class PhotoService {
    handlePhotoUpload(file) {
        if (!file) return false;

        // Validate file type
        if (!isValidFileType(file, PHOTO_CONSTRAINTS.ALLOWED_TYPES)) {
            notifications.showError('Format non supporté. Utilisez JPG ou PNG.');
            return false;
        }

        // Validate file size
        if (!isValidFileSize(file, PHOTO_CONSTRAINTS.MAX_SIZE)) {
            notifications.showError('La photo est trop grande. Maximum 5MB.');
            return false;
        }

        cvStateService.setPhoto(file);
        notifications.hide();
        return true;
    }

    removePhoto() {
        cvStateService.removePhoto();
    }

    getPhoto() {
        return cvStateService.getPhoto();
    }

    hasPhoto() {
        return this.getPhoto() !== null;
    }
}

export const photoService = new PhotoService();
