/**
 * File uploader component
 */

import { $, $$ } from '../../core/dom/elements.js';
import { createElement } from '../../core/dom/builder.js';
import { fileService } from '../../services/file/fileService.js';
import { formatFileSize } from '../../core/utils/formatters.js';
import { validateCsvFiles } from '../../business/validation/fileValidator.js';
import { eventBus } from '../../core/dom/events.js';

export class FileUploader {
    constructor() {
        this.dropZone = null;
        this.fileInput = null;
        this.fileList = null;
        this.browseBtn = null;
    }

    init() {
        this.dropZone = $('dropZone');
        this.fileInput = $('fileInput');
        this.fileList = $('fileList');
        this.browseBtn = $('browseBtn');

        this.setupEventListeners();
    }

    setupEventListeners() {
        if (!this.dropZone || !this.fileInput || !this.browseBtn) return;

        // Browse button
        this.browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.fileInput.click();
        });

        // Drop zone
        this.dropZone.addEventListener('click', (e) => {
            if (e.target !== this.browseBtn && !this.browseBtn.contains(e.target)) {
                this.fileInput.click();
            }
        });

        this.dropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.dropZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.dropZone.addEventListener('drop', (e) => this.handleDrop(e));

        // File input
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(Array.from(e.target.files));
        });

        // Listen to state changes
        eventBus.on('files:changed', () => this.render());
    }

    handleDragOver(e) {
        e.preventDefault();
        this.dropZone.classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.dropZone.classList.remove('drag-over');
    }

    handleDrop(e) {
        e.preventDefault();
        this.dropZone.classList.remove('drag-over');

        const files = validateCsvFiles(Array.from(e.dataTransfer.files));
        this.handleFiles(files);
    }

    handleFiles(files) {
        if (fileService.handleFiles(files)) {
            this.render();
            eventBus.emit('files:changed');
        }
    }

    removeFile(index) {
        fileService.removeFile(index);
        this.render();
        eventBus.emit('files:changed');
    }

    render() {
        if (!this.fileList) return;

        const files = fileService.getFiles();
        this.fileList.innerHTML = '';

        files.forEach((file, index) => {
            const fileItem = createElement('div', {
                className: 'file-item',
                children: [
                    createElement('div', {
                        className: 'file-item-info',
                        children: [
                            createElement('span', {
                                className: 'file-icon',
                                textContent: '📄'
                            }),
                            createElement('div', {
                                children: [
                                    createElement('div', {
                                        className: 'file-name',
                                        textContent: file.name
                                    }),
                                    createElement('div', {
                                        className: 'file-size',
                                        textContent: formatFileSize(file.size)
                                    })
                                ]
                            })
                        ]
                    }),
                    createElement('button', {
                        className: 'remove-file',
                        textContent: 'Retirer',
                        events: {
                            click: () => this.removeFile(index)
                        }
                    })
                ]
            });

            this.fileList.appendChild(fileItem);
        });
    }
}
