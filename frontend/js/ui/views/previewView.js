/**
 * Preview view (Step 3)
 */

import { $ } from '../../core/dom/elements.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import { previewService } from '../../services/ui/previewService.js';
import { prepareDataForPdf } from '../../business/workflow/dataMapper.js';
import { eventBus } from '../../core/dom/events.js';
import { notifications } from '../../core/ui/notifications.js';

export class PreviewView {
    constructor() {
        this.previewFrame = null;
        this.previewLoading = null;
        this.refreshBtn = null;
        this.downloadBtn = null;
    }

    init() {
        this.previewFrame = $('pdfPreviewFrame');
        this.previewLoading = $('previewLoading');
        this.refreshBtn = $('refreshPreviewBtn');
        this.downloadBtn = $('downloadFinalBtn');

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
