/**
 * Photo uploader component
 */

import { $ } from '../../core/dom/elements.js';
import { photoService } from '../../services/file/photoService.js';
import { eventBus } from '../../core/dom/events.js';

export class PhotoUploader {
    constructor() {
        this.photoInput = null;
        this.uploadBtn = null;
        this.removeBtn = null;
        this.preview = null;
        this.previewImg = null;
    }

    init() {
        this.photoInput = $('photoInput');
        this.uploadBtn = $('uploadPhotoBtn');
        this.removeBtn = $('removePhotoBtn');
        this.preview = $('photoPreview');
        this.previewImg = $('photoPreviewImg');

        this.setupEventListeners();
    }

    setupEventListeners() {
        if (!this.photoInput || !this.uploadBtn) return;

        this.uploadBtn.addEventListener('click', () => {
            this.photoInput.click();
        });

        this.photoInput.addEventListener('change', (e) => {
            this.handlePhotoUpload(e.target.files[0]);
        });

        if (this.removeBtn) {
            this.removeBtn.addEventListener('click', () => {
                this.removePhoto();
            });
        }
    }

    handlePhotoUpload(file) {
        if (!file) return;

        if (photoService.handlePhotoUpload(file)) {
            this.showPreview(file);
            eventBus.emit('photo:uploaded');
        }
    }

    showPreview(file) {
        if (!this.preview || !this.previewImg) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImg.src = e.target.result;
            this.previewImg.style.display = 'block';
            const svg = this.preview.querySelector('svg');
            if (svg) svg.style.display = 'none';
            if (this.removeBtn) this.removeBtn.style.display = 'inline-block';
        };
        reader.readAsDataURL(file);
    }

    removePhoto() {
        photoService.removePhoto();

        if (this.photoInput) this.photoInput.value = '';
        if (this.previewImg) {
            this.previewImg.style.display = 'none';
            this.previewImg.src = '';
        }
        const svg = this.preview?.querySelector('svg');
        if (svg) svg.style.display = 'block';
        if (this.removeBtn) this.removeBtn.style.display = 'none';

        eventBus.emit('photo:removed');
    }
}
