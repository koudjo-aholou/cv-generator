/**
 * Certifications editor component
 */

import { $ } from '../../core/dom/elements.js';
import { createElement } from '../../core/dom/builder.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import * as certificationsBusiness from '../../business/cv/certifications.js';
import { eventBus } from '../../core/dom/events.js';

export class CertificationsEditor {
    constructor() {
        this.container = null;
    }

    init() {
        this.container = $('certifications-editor');
        eventBus.on('data:parsed', () => this.render());
    }

    render() {
        if (!this.container) return;

        const parsedData = cvStateService.getParsedData();

        const section = $('certifications-editor-section');
        if (!parsedData || !parsedData.certifications || parsedData.certifications.length === 0) {
            if (section) section.style.display = 'none';
            return;
        }

        if (section) section.style.display = 'block';

        this.container.innerHTML = '';
        this.renderAddButton();
        this.renderCertificationItems();
    }

    renderAddButton() {
        const addBtn = createElement('button', {
            className: 'add-item-btn',
            innerHTML: '➕ Ajouter une certification',
            events: {
                click: () => this.addCertification()
            }
        });
        this.container.appendChild(addBtn);
    }

    renderCertificationItems() {
        const parsedData = cvStateService.getParsedData();

        parsedData.certifications.forEach((cert, index) => {
            const item = this.createCertificationItem(cert, index);
            this.container.appendChild(item);
        });
    }

    createCertificationItem(cert, index) {
        const title = createElement('span', {
            className: 'editor-item-title',
            textContent: cert.name || 'Certification'
        });

        const fields = this.createCertificationFields(cert, index, title);

        const toggleBtn = createElement('button', {
            className: 'editor-toggle-btn',
            textContent: 'Modifier',
            events: {
                click: () => {
                    const isHidden = fields.style.display === 'none';
                    fields.style.display = isHidden ? 'flex' : 'none';
                    toggleBtn.textContent = isHidden ? 'Masquer' : 'Modifier';
                }
            }
        });

        const deleteBtn = createElement('button', {
            className: 'editor-delete-btn',
            textContent: '🗑️ Supprimer',
            events: {
                click: (e) => {
                    e.stopPropagation();
                    if (confirm(`Voulez-vous vraiment supprimer la certification "${cert.name || 'cette certification'}" ?`)) {
                        this.deleteCertification(index);
                    }
                }
            }
        });

        const header = createElement('div', {
            className: 'editor-item-header',
            children: [
                title,
                createElement('div', {
                    className: 'editor-header-actions',
                    children: [toggleBtn, deleteBtn]
                })
            ]
        });

        return createElement('div', {
            className: 'editor-item',
            children: [header, fields]
        });
    }

    createCertificationFields(cert, index, title) {
        const parsedData = cvStateService.getParsedData();

        const nameInput = createElement('input', {
            attributes: {
                type: 'text',
                value: cert.name || ''
            }
        });
        nameInput.addEventListener('input', (e) => {
            certificationsBusiness.updateCertification(parsedData.certifications, index, 'name', e.target.value);
            title.textContent = e.target.value || 'Certification';
        });

        const nameGroup = createElement('div', {
            className: 'form-group',
            children: [
                createElement('label', { textContent: 'Nom de la certification' }),
                nameInput
            ]
        });

        const authorityInput = createElement('input', {
            attributes: {
                type: 'text',
                value: cert.authority || ''
            }
        });
        authorityInput.addEventListener('input', (e) => {
            certificationsBusiness.updateCertification(parsedData.certifications, index, 'authority', e.target.value);
        });

        const authorityGroup = createElement('div', {
            className: 'form-group',
            children: [
                createElement('label', { textContent: 'Organisme' }),
                authorityInput
            ]
        });

        const startInput = createElement('input', {
            attributes: {
                type: 'text',
                value: cert.start_date || '',
                placeholder: 'Ex: Jan 2021'
            }
        });
        startInput.addEventListener('input', (e) => {
            certificationsBusiness.updateCertification(parsedData.certifications, index, 'start_date', e.target.value);
        });

        const startGroup = createElement('div', {
            className: 'form-group',
            children: [
                createElement('label', { textContent: 'Date d\'obtention' }),
                startInput
            ]
        });

        const endInput = createElement('input', {
            attributes: {
                type: 'text',
                value: cert.end_date || '',
                placeholder: 'Ex: Jan 2024 (optionnel)'
            }
        });
        endInput.addEventListener('input', (e) => {
            certificationsBusiness.updateCertification(parsedData.certifications, index, 'end_date', e.target.value);
        });

        const endGroup = createElement('div', {
            className: 'form-group',
            children: [
                createElement('label', { textContent: 'Date d\'expiration' }),
                endInput
            ]
        });

        const row = createElement('div', {
            className: 'editor-row',
            children: [startGroup, endGroup]
        });

        const urlInput = createElement('input', {
            attributes: {
                type: 'url',
                value: cert.url || '',
                placeholder: 'https://...'
            }
        });
        urlInput.addEventListener('input', (e) => {
            certificationsBusiness.updateCertification(parsedData.certifications, index, 'url', e.target.value);
        });

        const urlGroup = createElement('div', {
            className: 'form-group',
            children: [
                createElement('label', { textContent: 'URL (optionnel)' }),
                urlInput
            ]
        });

        const fields = createElement('div', {
            className: 'editor-fields',
            children: [nameGroup, authorityGroup, row, urlGroup]
        });

        fields.style.display = 'none';
        return fields;
    }

    addCertification() {
        const parsedData = cvStateService.getParsedData();

        const newCertification = certificationsBusiness.createCertification();
        parsedData.certifications.push(newCertification);

        cvStateService.setParsedData(parsedData);
        this.render();

        // Auto-expand the new item
        setTimeout(() => {
            const items = document.querySelectorAll('#certifications-editor .editor-item');
            const lastItem = items[items.length - 1];
            if (lastItem) {
                const toggleBtn = lastItem.querySelector('.editor-toggle-btn');
                if (toggleBtn) {
                    toggleBtn.click();
                }
            }
        }, 100);
    }

    deleteCertification(index) {
        const parsedData = cvStateService.getParsedData();

        certificationsBusiness.deleteCertification(parsedData.certifications, index);

        cvStateService.setParsedData(parsedData);
        this.render();
    }
}
