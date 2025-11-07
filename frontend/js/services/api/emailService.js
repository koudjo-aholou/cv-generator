/**
 * Email service for sending CV
 */

import { ApiClient } from '../../core/api/client.js';
import { ENDPOINTS } from '../../config/endpoints.js';
import { loading } from '../../core/ui/loading.js';
import { notifications } from '../../core/ui/notifications.js';

class EmailService {
    constructor() {
        this.client = new ApiClient();
    }

    async sendCvByEmail(recipient, subject, message, pdfBlob) {
        loading.show();

        try {
            // Convert blob to base64
            const base64Pdf = await this.blobToBase64(pdfBlob);

            const response = await this.client.post(
                ENDPOINTS.SEND_EMAIL,
                JSON.stringify({
                    recipient: recipient,
                    subject: subject,
                    message: message,
                    pdf: base64Pdf
                }),
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erreur lors de l\'envoi de l\'email');
            }

            const result = await response.json();
            notifications.showSuccess('Email envoyé avec succès !');
            return result;
        } catch (error) {
            notifications.showError('Erreur lors de l\'envoi de l\'email: ' + error.message);
            throw error;
        } finally {
            loading.hide();
        }
    }

    blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                // Remove the data URL prefix (e.g., "data:application/pdf;base64,")
                const base64String = reader.result.split(',')[1];
                resolve(base64String);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }
}

export const emailService = new EmailService();
