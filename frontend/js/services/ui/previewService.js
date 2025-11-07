/**
 * PDF preview service
 */

import { pdfService } from '../api/pdfService.js';
import { cvStateService } from '../state/cvStateService.js';
import { eventBus } from '../../core/dom/events.js';

class PreviewService {
    async generatePreview(dataToSend) {
        try {
            const blob = await pdfService.generatePdf(dataToSend);
            cvStateService.setPdfBlob(blob);

            // Create URL for preview
            const url = window.URL.createObjectURL(blob);
            eventBus.emit('preview:generated', url);

            return blob;
        } catch (error) {
            eventBus.emit('preview:error', error);
            throw error;
        }
    }

    async refreshPreview(dataToSend) {
        return this.generatePreview(dataToSend);
    }

    downloadPdf() {
        const blob = cvStateService.getPdfBlob();
        if (!blob) {
            throw new Error('Aucun PDF à télécharger');
        }

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'cv.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        eventBus.emit('pdf:downloaded');
    }
}

export const previewService = new PreviewService();
