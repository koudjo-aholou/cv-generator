/**
 * PDF generation service
 */

import { ApiClient } from '../../core/api/client.js';
import { ENDPOINTS } from '../../config/endpoints.js';
import { loading } from '../../core/ui/loading.js';
import { notifications } from '../../core/ui/notifications.js';

class PdfService {
    constructor() {
        this.client = new ApiClient();
    }

    async generatePdf(data) {
        loading.show();

        try {
            const response = await this.client.post(
                ENDPOINTS.GENERATE_PDF,
                JSON.stringify(data),
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                throw new Error('Erreur lors de la génération du PDF');
            }

            const blob = await response.blob();
            return blob;
        } catch (error) {
            notifications.showError('Erreur lors de la génération du PDF: ' + error.message);
            throw error;
        } finally {
            loading.hide();
        }
    }
}

export const pdfService = new PdfService();
