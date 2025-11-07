/**
 * Preview view (Step 3)
 */

import { $ } from '../../core/dom/elements.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import { previewService } from '../../services/ui/previewService.js';
import { prepareDataForPdf } from '../../business/workflow/dataMapper.js';
import { eventBus } from '../../core/dom/events.js';
import { notifications } from '../../core/ui/notifications.js';
import { emailService } from '../../services/api/emailService.js';

export class PreviewView {
    constructor() {
        this.previewFrame = null;
        this.previewLoading = null;
        this.refreshBtn = null;
        this.downloadBtn = null;
        this.sendEmailBtn = null;
        this.recipientEmailInput = null;
        this.emailSubjectInput = null;
        this.emailMessageInput = null;
    }

    init() {
        this.previewFrame = $('pdfPreviewFrame');
        this.previewLoading = $('previewLoading');
        this.refreshBtn = $('refreshPreviewBtn');
        this.downloadBtn = $('downloadFinalBtn');
        this.sendEmailBtn = $('sendEmailBtn');
        this.recipientEmailInput = $('recipient-email');
        this.emailSubjectInput = $('email-subject');
        this.emailMessageInput = $('email-message');

        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', async () => {
                await this.refreshPreview();
            });
        }

        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => {
                this.downloadPdf();
            });
        }

        if (this.sendEmailBtn) {
            this.sendEmailBtn.addEventListener('click', async () => {
                await this.sendEmail();
            });
        }

        eventBus.on('preview:generated', (url) => {
            if (this.previewFrame) {
                this.previewFrame.src = url;
            }
            this.hideLoading();
        });

        eventBus.on('preview:error', (error) => {
            this.hideLoading();
        });

        eventBus.on('pdf:downloaded', () => {
            const successSection = $('success-section');
            if (successSection) {
                successSection.style.display = 'block';
                successSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    async generatePreview() {
        this.showLoading();

        try {
            const dataToSend = await this.prepareData();
            await previewService.generatePreview(dataToSend);
        } catch (error) {
            notifications.showError('Erreur lors de la génération de l\'aperçu: ' + error.message);
            this.hideLoading();
        }
    }

    async refreshPreview() {
        await this.generatePreview();
    }

    async prepareData() {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();
        const photoFile = cvStateService.getPhoto();

        const contactInfo = {
            email: $('contact-email')?.value || '',
            phone: $('contact-phone')?.value || '',
            address: $('contact-address')?.value || ''
        };

        return prepareDataForPdf(parsedData, config, contactInfo, photoFile);
    }

    downloadPdf() {
        try {
            previewService.downloadPdf();
        } catch (error) {
            notifications.showError(error.message);
        }
    }

    async sendEmail() {
        try {
            // Validate recipient email
            const recipient = this.recipientEmailInput?.value.trim();
            if (!recipient) {
                notifications.showError('Veuillez saisir une adresse email');
                return;
            }

            // Basic email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(recipient)) {
                notifications.showError('Veuillez saisir une adresse email valide');
                return;
            }

            // Get optional fields
            const subject = this.emailSubjectInput?.value.trim() || 'Mon CV';
            const message = this.emailMessageInput?.value.trim() || 'Veuillez trouver ci-joint mon CV.';

            // Get PDF blob
            const blob = cvStateService.getPdfBlob();
            if (!blob) {
                notifications.showError('Aucun CV à envoyer. Veuillez générer le CV d\'abord.');
                return;
            }

            // Send email
            await emailService.sendCvByEmail(recipient, subject, message, blob);

            // Clear form after successful send
            if (this.recipientEmailInput) this.recipientEmailInput.value = '';
            if (this.emailMessageInput) this.emailMessageInput.value = '';
        } catch (error) {
            // Error is already shown by emailService
            console.error('Error sending email:', error);
        }
    }

    showLoading() {
        if (this.previewLoading) {
            this.previewLoading.style.display = 'flex';
        }
    }

    hideLoading() {
        if (this.previewLoading) {
            this.previewLoading.style.display = 'none';
        }
    }
}
