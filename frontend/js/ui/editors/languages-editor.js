/**
 * Languages Editor Web Component
 * Usage: <languages-editor></languages-editor>
 */

import { cvStateService } from '../../services/state/cvStateService.js';
import * as languagesBusiness from '../../business/cv/languages.js';

export class LanguagesEditor extends HTMLElement {
    constructor() {
        super();
        this.languages = [];
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

            if (parsedData && parsedData.languages) {
                this.languages = parsedData.languages;
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
        if (!this.languages || this.languages.length === 0) {
            this.style.display = 'none';
            return;
        }

        this.style.display = 'block';

        this.innerHTML = `
            <div class="editor-section">
                <h3>🌍 Langues</h3>
                <button class="add-item-btn">➕ Ajouter une langue</button>
                <div class="editor-list" id="languages-list"></div>
            </div>
        `;

        this.renderLanguagesList();
        this.attachEventListeners();
    }

    renderLanguagesList() {
        const list = this.querySelector('#languages-list');
        if (!list) return;

        list.innerHTML = '';

        this.languages.forEach((lang, index) => {
            const item = document.createElement('div');
            item.className = 'editor-item';
            item.innerHTML = `
                <div class="editor-item-header-simple">
                    <button class="editor-delete-btn-small" data-index="${index}" title="Supprimer cette langue">🗑️</button>
                </div>
                <div class="editor-row">
                    <div class="form-group">
                        <label>Langue</label>
                        <input type="text" data-index="${index}" data-field="name" value="${lang.name || ''}">
                    </div>
                    <div class="form-group">
                        <label>Niveau</label>
                        <input type="text" data-index="${index}" data-field="proficiency" value="${lang.proficiency || ''}" placeholder="Ex: Courant, Natif, B2...">
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
            addBtn.addEventListener('click', () => this.addLanguage());
        }

        // Delete buttons
        this.querySelectorAll('.editor-delete-btn-small').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                const lang = this.languages[index];
                if (confirm(`Voulez-vous vraiment supprimer la langue "${lang.name || 'cette langue'}" ?`)) {
                    this.deleteLanguage(index);
                }
            });
        });

        // Input changes
        this.querySelectorAll('.editor-list input').forEach(input => {
            input.addEventListener('input', (e) => {
                const index = parseInt(e.target.dataset.index);
                const field = e.target.dataset.field;
                this.updateLanguage(index, field, e.target.value);
            });
        });
    }

    addLanguage() {
        const parsedData = cvStateService.getParsedData();

        const newLanguage = languagesBusiness.createLanguage();
        parsedData.languages.push(newLanguage);

        cvStateService.setParsedData(parsedData);

        this.languages = parsedData.languages;
        this.render();

        // Focus on the first input of the new language
        setTimeout(() => {
            const items = this.querySelectorAll('.editor-item');
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

        this.languages = parsedData.languages;
        this.render();
    }

    updateLanguage(index, field, value) {
        const parsedData = cvStateService.getParsedData();
        languagesBusiness.updateLanguage(parsedData.languages, index, field, value);
        cvStateService.setParsedData(parsedData);
    }
}

customElements.define('languages-editor', LanguagesEditor);
