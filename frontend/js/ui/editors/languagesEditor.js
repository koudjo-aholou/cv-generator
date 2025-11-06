/**
 * Languages editor component
 */

import { $ } from '../../core/dom/elements.js';
import { createElement } from '../../core/dom/builder.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import * as languagesBusiness from '../../business/cv/languages.js';
import { eventBus } from '../../core/dom/events.js';

export class LanguagesEditor {
    constructor() {
        this.container = null;
    }

    init() {
        this.container = $('languages-editor');
        eventBus.on('data:parsed', () => this.render());
    }

    render() {
        if (!this.container) return;

        const parsedData = cvStateService.getParsedData();

        const section = $('languages-editor-section');
        if (!parsedData || !parsedData.languages || parsedData.languages.length === 0) {
            if (section) section.style.display = 'none';
            return;
        }

        if (section) section.style.display = 'block';

        this.container.innerHTML = '';
        this.renderAddButton();
        this.renderLanguageItems();
    }

    renderAddButton() {
        const addBtn = createElement('button', {
            className: 'add-item-btn',
            innerHTML: '➕ Ajouter une langue',
            events: {
                click: () => this.addLanguage()
            }
        });
        this.container.appendChild(addBtn);
    }

    renderLanguageItems() {
        const parsedData = cvStateService.getParsedData();

        parsedData.languages.forEach((lang, index) => {
            const item = this.createLanguageItem(lang, index);
            this.container.appendChild(item);
        });
    }

    createLanguageItem(lang, index) {
        const parsedData = cvStateService.getParsedData();

        const deleteBtn = createElement('button', {
            className: 'editor-delete-btn-small',
            textContent: '🗑️',
            attributes: { title: 'Supprimer cette langue' },
            events: {
                click: (e) => {
                    e.stopPropagation();
                    if (confirm(`Voulez-vous vraiment supprimer la langue "${lang.name || 'cette langue'}" ?`)) {
                        this.deleteLanguage(index);
                    }
                }
            }
        });

        const itemHeader = createElement('div', {
            className: 'editor-item-header-simple',
            children: [deleteBtn]
        });

        const nameInput = createElement('input', {
            attributes: {
                type: 'text',
                value: lang.name || ''
            }
        });
        nameInput.addEventListener('input', (e) => {
            languagesBusiness.updateLanguage(parsedData.languages, index, 'name', e.target.value);
        });

        const nameGroup = createElement('div', {
            className: 'form-group',
            children: [
                createElement('label', { textContent: 'Langue' }),
                nameInput
            ]
        });

        const proficiencyInput = createElement('input', {
            attributes: {
                type: 'text',
                value: lang.proficiency || '',
                placeholder: 'Ex: Courant, Natif, B2...'
            }
        });
        proficiencyInput.addEventListener('input', (e) => {
            languagesBusiness.updateLanguage(parsedData.languages, index, 'proficiency', e.target.value);
        });

        const proficiencyGroup = createElement('div', {
            className: 'form-group',
            children: [
                createElement('label', { textContent: 'Niveau' }),
                proficiencyInput
            ]
        });

        const row = createElement('div', {
            className: 'editor-row',
            children: [nameGroup, proficiencyGroup]
        });

        const item = createElement('div', {
            className: 'editor-item',
            children: [itemHeader, row]
        });

        return item;
    }

    addLanguage() {
        const parsedData = cvStateService.getParsedData();

        const newLanguage = languagesBusiness.createLanguage();
        parsedData.languages.push(newLanguage);

        cvStateService.setParsedData(parsedData);
        this.render();

        // Focus on the first input of the new language
        setTimeout(() => {
            const items = document.querySelectorAll('#languages-editor .editor-item');
            const lastItem = items[items.length - 1];
            if (lastItem) {
                const firstInput = lastItem.querySelector('input');
                if (firstInput) {
                    firstInput.focus();
                }
            }
        }, 100);
    }

    deleteLanguage(index) {
        const parsedData = cvStateService.getParsedData();

        languagesBusiness.deleteLanguage(parsedData.languages, index);

        cvStateService.setParsedData(parsedData);
        this.render();
    }
}
