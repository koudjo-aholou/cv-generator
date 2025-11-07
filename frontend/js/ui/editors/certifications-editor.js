/**
 * Certifications Editor Web Component
 * Usage: <certifications-editor></certifications-editor>
 */

import { cvStateService } from '../../services/state/cvStateService.js';
import * as certificationsBusiness from '../../business/cv/certifications.js';

export class CertificationsEditor extends HTMLElement {
    constructor() {
        super();
        this.certifications = [];
    }

    connectedCallback() {
        // Subscribe to data changes
        this.unsubscribeData = this.subscribeToData();
        this.render();
    }

    disconnectedCallback() {
        if (this.unsubscribeData) this.unsubscribeData();
    }

    subscribeToData() {
        const callback = () => {
            const parsedData = cvStateService.getParsedData();

            if (parsedData && parsedData.certifications) {
                this.certifications = parsedData.certifications;
                this.render();
            }
        };

        // Initial call
        callback();

        // Listen to custom events
        document.addEventListener('data-parsed', callback);
        return () => document.removeEventListener('data-parsed', callback);
    }

    render() {
        if (!this.certifications || this.certifications.length === 0) {
            this.style.display = 'none';
            return;
        }

        this.style.display = 'block';

        this.innerHTML = `
            <div class="editor-section">
                <h3>🏆 Certifications</h3>
                <button class="add-item-btn">➕ Ajouter une certification</button>
                <div class="editor-list" id="certifications-list"></div>
            </div>
        `;

        this.renderCertificationsList();
        this.attachEventListeners();
    }

    renderCertificationsList() {
        const list = this.querySelector('#certifications-list');
        if (!list) return;

        list.innerHTML = '';

        this.certifications.forEach((cert, index) => {
            const item = document.createElement('div');
            item.className = 'editor-item';
            item.innerHTML = `
                <div class="editor-item-header">
                    <span class="editor-item-title">
                        ${cert.name || 'Certification'}
                    </span>
                    <div class="editor-header-actions">
                        <button class="editor-toggle-btn" data-index="${index}">Modifier</button>
                        <button class="editor-delete-btn" data-index="${index}">🗑️ Supprimer</button>
                    </div>
                </div>
                <div class="editor-fields" data-index="${index}" style="display: none;">
                    <div class="form-group">
                        <label>Nom de la certification</label>
                        <input type="text" data-field="name" value="${cert.name || ''}">
                    </div>
                    <div class="form-group">
                        <label>Organisme</label>
                        <input type="text" data-field="authority" value="${cert.authority || ''}">
                    </div>
                    <div class="editor-row">
                        <div class="form-group">
                            <label>Date d'obtention</label>
                            <input type="text" data-field="start_date" value="${cert.start_date || ''}" placeholder="Ex: Jan 2021">
                        </div>
                        <div class="form-group">
                            <label>Date d'expiration</label>
                            <input type="text" data-field="end_date" value="${cert.end_date || ''}" placeholder="Ex: Jan 2024 (optionnel)">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>URL (optionnel)</label>
                        <input type="url" data-field="url" value="${cert.url || ''}" placeholder="https://...">
                    </div>
                </div>
            `;
            list.appendChild(item);
        });
    }

    attachEventListeners() {
        // Add button
        const addBtn = this.querySelector('.add-item-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addCertification());
        }

        // Toggle buttons
        this.querySelectorAll('.editor-toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = e.target.dataset.index;
                const fields = this.querySelector(`.editor-fields[data-index="${index}"]`);
                if (fields) {
                    const isHidden = fields.style.display === 'none';
                    fields.style.display = isHidden ? 'block' : 'none';
                    e.target.textContent = isHidden ? 'Masquer' : 'Modifier';
                }
            });
        });

        // Delete buttons
        this.querySelectorAll('.editor-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                const cert = this.certifications[index];
                if (confirm(`Voulez-vous vraiment supprimer la certification "${cert.name || 'cette certification'}" ?`)) {
                    this.deleteCertification(index);
                }
            });
        });

        // Input changes
        this.querySelectorAll('.editor-fields input').forEach(input => {
            input.addEventListener('input', (e) => {
                const fields = e.target.closest('.editor-fields');
                const index = parseInt(fields.dataset.index);
                const field = e.target.dataset.field;
                this.updateCertification(index, field, e.target.value);
            });
        });
    }

    addCertification() {
        const parsedData = cvStateService.getParsedData();

        const newCertification = certificationsBusiness.createCertification();
        parsedData.certifications.push(newCertification);

        cvStateService.setParsedData(parsedData);

        this.certifications = parsedData.certifications;
        this.render();

        // Auto-expand the new item
        setTimeout(() => {
            const toggleBtns = this.querySelectorAll('.editor-toggle-btn');
            if (toggleBtns.length > 0) {
                toggleBtns[toggleBtns.length - 1].click();
            }
        }, 100);
    }

    deleteCertification(index) {
        const parsedData = cvStateService.getParsedData();

        certificationsBusiness.deleteCertification(parsedData.certifications, index);

        cvStateService.setParsedData(parsedData);

        this.certifications = parsedData.certifications;
        this.render();
    }

    updateCertification(index, field, value) {
        const parsedData = cvStateService.getParsedData();
        certificationsBusiness.updateCertification(parsedData.certifications, index, field, value);
        cvStateService.setParsedData(parsedData);

        // Update title in UI if name field
        if (field === 'name') {
            const title = this.querySelector(`.editor-item:nth-child(${index + 2}) .editor-item-title`);
            if (title) {
                title.textContent = value || 'Certification';
            }
        }
    }
}

customElements.define('certifications-editor', CertificationsEditor);
