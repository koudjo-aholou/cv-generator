/**
 * Photo Uploader Web Component
 * Usage: <photo-uploader></photo-uploader>
 */

import { photoService } from '../../services/file/photoService.js';
import { cvStateService } from '../../services/state/cvStateService.js';

export class PhotoUploader extends HTMLElement {
    connectedCallback() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        this.innerHTML = `
            <div class="photo-upload-section">
                <h3>📷 Photo de profil (optionnel)</h3>
                <div id="photoPreview" class="photo-preview">
                    <svg width="100" height="100" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="45" fill="#e0e0e0"/>
                        <text x="50" y="60" text-anchor="middle" font-size="40">👤</text>
                    </svg>
                    <img id="photoPreviewImg" style="display: none;" alt="Photo">
                </div>
                <div class="photo-actions">
                    <input type="file" id="photoInput" accept="image/jpeg,image/jpg,image/png" style="display: none;">
                    <button id="uploadPhotoBtn" class="btn-secondary">Choisir une photo</button>
                    <button id="removePhotoBtn" class="btn-danger" style="display: none;">Retirer la photo</button>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const uploadBtn = this.querySelector('#uploadPhotoBtn');
        const removeBtn = this.querySelector('#removePhotoBtn');
        const photoInput = this.querySelector('#photoInput');

        uploadBtn.addEventListener('click', () => {
            photoInput.click();
        });

        photoInput.addEventListener('change', (e) => {
            this.handlePhotoUpload(e.target.files[0]);
        });

        removeBtn.addEventListener('click', () => {
            this.removePhoto();
        });
    }

    handlePhotoUpload(file) {
        if (!file) return;

        if (photoService.handlePhotoUpload(file)) {
            this.showPreview(file);

            this.dispatchEvent(new CustomEvent('photo-uploaded', {
                bubbles: true,
                detail: { file }
            }));
        }
    }

    showPreview(file) {
        const preview = this.querySelector('#photoPreview');
        const previewImg = this.querySelector('#photoPreviewImg');
        const removeBtn = this.querySelector('#removePhotoBtn');
        const svg = preview ? preview.querySelector('svg') : null;

        const reader = new FileReader();
        reader.onload = (e) => {
            if (previewImg) {
                previewImg.src = e.target.result;
                previewImg.style.display = 'block';
            }
            if (svg) {
                svg.style.display = 'none';
            }
            if (removeBtn) {
                removeBtn.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    }

    removePhoto() {
        photoService.removePhoto();

        const photoInput = this.querySelector('#photoInput');
        const previewImg = this.querySelector('#photoPreviewImg');
        const removeBtn = this.querySelector('#removePhotoBtn');
        const preview = this.querySelector('#photoPreview');
        const svg = preview ? preview.querySelector('svg') : null;

        if (photoInput) {
            photoInput.value = '';
        }
        if (previewImg) {
            previewImg.style.display = 'none';
            previewImg.src = '';
        }
        if (svg) {
            svg.style.display = 'block';
        }
        if (removeBtn) {
            removeBtn.style.display = 'none';
        }

        this.dispatchEvent(new CustomEvent('photo-removed', {
            bubbles: true
        }));
    }
}

customElements.define('photo-uploader', PhotoUploader);
