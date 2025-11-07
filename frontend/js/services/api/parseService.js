/**
 * LinkedIn parsing service
 */

import { ApiClient } from '../../core/api/client.js';
import { ENDPOINTS } from '../../config/endpoints.js';
import { loading } from '../../core/ui/loading.js';
import { notifications } from '../../core/ui/notifications.js';

class ParseService {
    constructor() {
        this.client = new ApiClient();
    }

    async parseLinkedInData(files, photoFile = null) {
        loading.show();

        try {
            const formData = new FormData();
            files.forEach(file => formData.append('files', file));
            if (photoFile) {
                formData.append('photo', photoFile);
            }

            const response = await this.client.post(ENDPOINTS.PARSE_LINKEDIN, formData);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erreur lors du parsing');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            notifications.showError('Erreur lors du parsing des données: ' + error.message);
            throw error;
        } finally {
            loading.hide();
        }
    }
}

export const parseService = new ParseService();
