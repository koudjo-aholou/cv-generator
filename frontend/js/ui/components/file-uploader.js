/**
 * File Uploader Web Component
 * Usage: <file-uploader></file-uploader>
 */

import { cvStateService } from '../../services/state/cvStateService.js';
import { fileService } from '../../services/file/fileService.js';
import { formatFileSize } from '../../core/utils/formatters.js';
import { validateCsvFiles } from '../../business/validation/fileValidator.js';

export class FileUploader extends HTMLElement {
    constructor() {
        super();
        this.files = [];
    }

    connectedCallback() {
        this.render();
        this.attachEventListeners();

        // Subscribe to state changes
        this.unsubscribe = cvStateService.observeFiles(() => {
            this.files = cvStateService.getFiles();
            this.renderFileList();
        });
    }

    disconnectedCallback() {
        if (this.unsubscribe) this.unsubscribe();
    }

    render() {
        this.innerHTML = `
            <div id="dropZone" class="drop-zone">
                <div class="upload-icon">📁</div>
                <h3>Glissez vos fichiers CSV ici</h3>
                <p>ou</p>
                <button id="browseBtn" class="btn-primary">Parcourir les fichiers</button>
                <input type="file" id="fileInput" accept=".csv" multiple style="display: none;">
                <p class="file-info">Fichiers requis : Profile.csv, Positions.csv, Education.csv</p>
            </div>
            <div id="fileList" class="file-list"></div>
        `;
    }

    attachEventListeners() {
        const dropZone = this.querySelector('#dropZone');
        const browseBtn = this.querySelector('#browseBtn');
        const fileInput = this.querySelector('#fileInput');

        // Browse button
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });

        // Drop zone
        dropZone.addEventListener('click', (e) => {
            if (e.target !== browseBtn && !browseBtn.contains(e.target)) {
                fileInput.click();
            }
        });

        dropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        dropZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        dropZone.addEventListener('drop', (e) => this.handleDrop(e));

        // File input
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(Array.from(e.target.files));
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        this.querySelector('#dropZone').classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.querySelector('#dropZone').classList.remove('drag-over');
    }

    handleDrop(e) {
        e.preventDefault();
        this.querySelector('#dropZone').classList.remove('drag-over');

        const files = validateCsvFiles(Array.from(e.dataTransfer.files));
        this.handleFiles(files);
    }

    handleFiles(files) {
        if (fileService.handleFiles(files)) {
            this.files = cvStateService.getFiles();
            this.renderFileList();

            // Dispatch custom event
            this.dispatchEvent(new CustomEvent('files-changed', {
                bubbles: true,
                detail: { files: this.files }
            }));
        }
    }

    renderFileList() {
        const fileList = this.querySelector('#fileList');
        if (!fileList) return;

        fileList.innerHTML = '';

        this.files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-item-info">
                    <span class="file-icon">📄</span>
                    <div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${formatFileSize(file.size)}</div>
                    </div>
                </div>
                <button class="remove-file" data-index="${index}">Retirer</button>
            `;

            const removeBtn = fileItem.querySelector('.remove-file');
            removeBtn.addEventListener('click', () => this.removeFile(index));

            fileList.appendChild(fileItem);
        });
    }

    removeFile(index) {
        fileService.removeFile(index);
        this.files = cvStateService.getFiles();
        this.renderFileList();

        this.dispatchEvent(new CustomEvent('files-changed', {
            bubbles: true,
            detail: { files: this.files }
        }));
    }
}

// Register the custom element
customElements.define('file-uploader', FileUploader);
