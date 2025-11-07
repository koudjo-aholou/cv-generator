/**
 * Education Editor Web Component
 * Usage: <education-editor></education-editor>
 */

import { cvStateService } from '../../services/state/cvStateService.js';
import * as educationBusiness from '../../business/cv/education.js';

export class EducationEditor extends HTMLElement {
    constructor() {
        super();
        this.educations = [];
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

            if (parsedData && parsedData.education) {
                this.educations = parsedData.education;
                this.visibleIndices = config.education_visible || [];
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
        if (!this.educations || this.educations.length === 0) {
            this.style.display = 'none';
            return;
        }

        this.style.display = 'block';

        this.innerHTML = `
            <div class="editor-section">
                <h3>🎓 Formations</h3>
                <button class="add-item-btn">➕ Ajouter une formation</button>
                <div class="editor-list" id="education-list"></div>

                <h4>🎯 Formations à inclure</h4>
                <div class="items-toggle-list" id="education-toggles"></div>
            </div>
        `;

        this.renderEducationList();
        this.renderVisibilityToggles();
        this.attachEventListeners();
    }

    renderEducationList() {
        const list = this.querySelector('#education-list');
        if (!list) return;

        list.innerHTML = '';

        this.educations.forEach((edu, index) => {
            const item = document.createElement('div');
            item.className = 'editor-item';
            item.innerHTML = `
                <div class="editor-item-header">
                    <span class="editor-item-title">
                        ${edu.degree || 'Diplôme'} - ${edu.school || 'École'}
                    </span>
                    <div class="editor-header-actions">
                        <button class="editor-toggle-btn" data-index="${index}">Modifier</button>
                        <button class="editor-delete-btn" data-index="${index}">🗑️ Supprimer</button>
                    </div>
                </div>
                <div class="editor-fields" data-index="${index}" style="display: none;">
                    <div class="editor-row">
                        <div class="form-group">
                            <label>Diplôme</label>
                            <input type="text" data-field="degree" value="${edu.degree || ''}">
                        </div>
                        <div class="form-group">
                            <label>École / Université</label>
                            <input type="text" data-field="school" value="${edu.school || ''}">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Domaine d'études</label>
                        <input type="text" data-field="field_of_study" value="${edu.field_of_study || ''}">
                    </div>
                    <div class="editor-row">
                        <div class="form-group">
                            <label>Date de début</label>
                            <input type="text" data-field="start_date" value="${edu.start_date || ''}" placeholder="Ex: 2015">
                        </div>
                        <div class="form-group">
                            <label>Date de fin</label>
                            <input type="text" data-field="end_date" value="${edu.end_date || ''}" placeholder="Ex: 2019">
                        </div>
                    </div>
                </div>
            `;
            list.appendChild(item);
        });
    }

    renderVisibilityToggles() {
        const toggles = this.querySelector('#education-toggles');
        if (!toggles) return;

        toggles.innerHTML = '';

        this.educations.forEach((edu, index) => {
            const item = document.createElement('label');
            item.className = 'item-toggle';
            item.innerHTML = `
                <input type="checkbox" data-visibility-index="${index}"
                       ${this.visibleIndices.includes(index) ? 'checked' : ''}>
                <span>${edu.degree || 'Diplôme'} - ${edu.school || 'École inconnue'}</span>
            `;
            toggles.appendChild(item);
        });
    }

    attachEventListeners() {
        // Add button
        const addBtn = this.querySelector('.add-item-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addEducation());
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
                if (confirm('Voulez-vous vraiment supprimer cette formation ?')) {
                    this.deleteEducation(index);
                }
            });
        });

        // Input changes
        this.querySelectorAll('.editor-fields input').forEach(input => {
            input.addEventListener('input', (e) => {
                const fields = e.target.closest('.editor-fields');
                const index = parseInt(fields.dataset.index);
                const field = e.target.dataset.field;
                this.updateEducation(index, field, e.target.value);
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

    addEducation() {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        const newEdu = educationBusiness.createEducation();
        parsedData.education.push(newEdu);

        if (config.education_visible) {
            config.education_visible.push(parsedData.education.length - 1);
        }

        cvStateService.setParsedData(parsedData);
        cvStateService.setConfig(config);

        this.educations = parsedData.education;
        this.visibleIndices = config.education_visible;
        this.render();

        // Auto-expand
        setTimeout(() => {
            const lastToggle = this.querySelectorAll('.editor-toggle-btn');
            if (lastToggle.length > 0) {
                lastToggle[lastToggle.length - 1].click();
            }
        }, 100);
    }

    deleteEducation(index) {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        config.education_visible = educationBusiness.deleteEducation(
            parsedData.education,
            index,
            config.education_visible
        );

        cvStateService.setParsedData(parsedData);
        cvStateService.setConfig(config);

        this.educations = parsedData.education;
        this.visibleIndices = config.education_visible;
        this.render();
    }

    updateEducation(index, field, value) {
        const parsedData = cvStateService.getParsedData();
        educationBusiness.updateEducation(parsedData.education, index, field, value);
        cvStateService.setParsedData(parsedData);

        // Update title in UI
        const title = this.querySelector(`.editor-item:nth-child(${index + 2}) .editor-item-title`);
        if (title && (field === 'degree' || field === 'school')) {
            const edu = parsedData.education[index];
            title.textContent = `${edu.degree || 'Diplôme'} - ${edu.school || 'École'}`;
        }
    }

    toggleVisibility(index, checked) {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        const newVisible = educationBusiness.toggleEducationVisibility(
            index,
            checked,
            config.education_visible
        );

        config.education_visible = newVisible;
        cvStateService.setConfig(config);
        this.visibleIndices = newVisible;
    }
}

customElements.define('education-editor', EducationEditor);
