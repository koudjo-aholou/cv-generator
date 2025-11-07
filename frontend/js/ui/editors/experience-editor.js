/**
 * Experience Editor Web Component
 * Usage: <experience-editor></experience-editor>
 */

import { cvStateService } from '../../services/state/cvStateService.js';
import * as experienceBusiness from '../../business/cv/experience.js';

export class ExperienceEditor extends HTMLElement {
    constructor() {
        super();
        this.experiences = [];
        this.visibleIndices = [];
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
            const config = cvStateService.getConfig();

            if (parsedData && parsedData.positions) {
                this.experiences = parsedData.positions;
                this.visibleIndices = config.experience_visible || [];
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
        if (!this.experiences || this.experiences.length === 0) {
            this.style.display = 'none';
            return;
        }

        this.style.display = 'block';

        this.innerHTML = `
            <div class="editor-section">
                <h3>💼 Expériences Professionnelles</h3>
                <button class="add-item-btn">➕ Ajouter une expérience</button>
                <div class="editor-list" id="experience-list"></div>

                <h4>🎯 Expériences à inclure</h4>
                <div class="items-toggle-list" id="experience-toggles"></div>
            </div>
        `;

        this.renderExperienceList();
        this.renderVisibilityToggles();
        this.attachEventListeners();
    }

    renderExperienceList() {
        const list = this.querySelector('#experience-list');
        if (!list) return;

        list.innerHTML = '';

        this.experiences.forEach((exp, index) => {
            const item = document.createElement('div');
            item.className = 'editor-item';
            item.innerHTML = `
                <div class="editor-item-header">
                    <span class="editor-item-title">
                        ${exp.title || 'Sans titre'} - ${exp.company || 'Entreprise'}
                    </span>
                    <div class="editor-header-actions">
                        <button class="editor-toggle-btn" data-index="${index}">Modifier</button>
                        <button class="editor-delete-btn" data-index="${index}">🗑️ Supprimer</button>
                    </div>
                </div>
                <div class="editor-fields" data-index="${index}" style="display: none;">
                    <div class="editor-row">
                        <div class="form-group">
                            <label>Titre du poste</label>
                            <input type="text" data-field="title" value="${exp.title || ''}">
                        </div>
                        <div class="form-group">
                            <label>Entreprise</label>
                            <input type="text" data-field="company" value="${exp.company || ''}">
                        </div>
                    </div>
                    <div class="editor-row">
                        <div class="form-group">
                            <label>Date de début</label>
                            <input type="text" data-field="started_on" value="${exp.started_on || ''}" placeholder="Ex: Jan 2020">
                        </div>
                        <div class="form-group">
                            <label>Date de fin</label>
                            <input type="text" data-field="finished_on" value="${exp.finished_on || ''}" placeholder="Ex: Déc 2022">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea data-field="description" rows="4">${exp.description || ''}</textarea>
                    </div>
                </div>
            `;
            list.appendChild(item);
        });
    }

    renderVisibilityToggles() {
        const toggles = this.querySelector('#experience-toggles');
        if (!toggles) return;

        toggles.innerHTML = '';

        this.experiences.forEach((exp, index) => {
            const item = document.createElement('label');
            item.className = 'item-toggle';
            item.innerHTML = `
                <input type="checkbox" data-visibility-index="${index}"
                       ${this.visibleIndices.includes(index) ? 'checked' : ''}>
                <span>${exp.title || 'Sans titre'} - ${exp.company || 'Entreprise inconnue'}</span>
            `;
            toggles.appendChild(item);
        });
    }

    attachEventListeners() {
        // Add button
        const addBtn = this.querySelector('.add-item-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addExperience());
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
                if (confirm('Voulez-vous vraiment supprimer cette expérience ?')) {
                    this.deleteExperience(index);
                }
            });
        });

        // Input changes
        this.querySelectorAll('.editor-fields input, .editor-fields textarea').forEach(input => {
            input.addEventListener('input', (e) => {
                const fields = e.target.closest('.editor-fields');
                const index = parseInt(fields.dataset.index);
                const field = e.target.dataset.field;
                this.updateExperience(index, field, e.target.value);
            });
        });

        // Visibility toggles
        this.querySelectorAll('[data-visibility-index]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const index = parseInt(e.target.dataset.visibilityIndex);
                this.toggleVisibility(index, e.target.checked);
            });
        });
    }

    addExperience() {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        const newExp = experienceBusiness.createExperience();
        parsedData.positions.push(newExp);

        if (config.experience_visible) {
            config.experience_visible.push(parsedData.positions.length - 1);
        }

        cvStateService.setParsedData(parsedData);
        cvStateService.setConfig(config);

        this.experiences = parsedData.positions;
        this.visibleIndices = config.experience_visible;
        this.render();

        // Auto-expand
        setTimeout(() => {
            const lastToggle = this.querySelectorAll('.editor-toggle-btn');
            if (lastToggle.length > 0) {
                lastToggle[lastToggle.length - 1].click();
            }
        }, 100);
    }

    deleteExperience(index) {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        config.experience_visible = experienceBusiness.deleteExperience(
            parsedData.positions,
            index,
            config.experience_visible
        );

        cvStateService.setParsedData(parsedData);
        cvStateService.setConfig(config);

        this.experiences = parsedData.positions;
        this.visibleIndices = config.experience_visible;
        this.render();
    }

    updateExperience(index, field, value) {
        const parsedData = cvStateService.getParsedData();
        experienceBusiness.updateExperience(parsedData.positions, index, field, value);
        cvStateService.setParsedData(parsedData);

        // Update title in UI
        const title = this.querySelector(`.editor-item:nth-child(${index + 2}) .editor-item-title`);
        if (title && (field === 'title' || field === 'company')) {
            const exp = parsedData.positions[index];
            title.textContent = `${exp.title || 'Sans titre'} - ${exp.company || 'Entreprise'}`;
        }
    }

    toggleVisibility(index, checked) {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        const newVisible = experienceBusiness.toggleExperienceVisibility(
            index,
            checked,
            config.experience_visible
        );

        config.experience_visible = newVisible;
        cvStateService.setConfig(config);
        this.visibleIndices = newVisible;
    }
}

customElements.define('experience-editor', ExperienceEditor);
