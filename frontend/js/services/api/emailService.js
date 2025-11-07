/**
 * Email service for opening mail client
 */

import { notifications } from '../../core/ui/notifications.js';

class EmailService {
    /**
     * Open default mail client with pre-filled data
     * Note: Due to security restrictions, attachments cannot be added automatically via mailto
     */
    openMailClient(recipient, subject, message) {
        try {
            // Build mailto URL
            const params = [];

            if (recipient) {
                // Recipient is part of the mailto URL, not a parameter
            }

            if (subject) {
                params.push(`subject=${encodeURIComponent(subject)}`);
            }

            if (message) {
                params.push(`body=${encodeURIComponent(message)}`);
            }

            // Construct the mailto URL
            const mailtoUrl = `mailto:${recipient || ''}${params.length > 0 ? '?' + params.join('&') : ''}`;

            // Open mail client
            window.location.href = mailtoUrl;

            notifications.showSuccess('Client mail ouvert ! N\'oubliez pas d\'attacher le CV téléchargé.');
            return true;
        } catch (error) {
            notifications.showError('Erreur lors de l\'ouverture du client mail: ' + error.message);
            throw error;
        }
    }
}

export const emailService = new EmailService();
