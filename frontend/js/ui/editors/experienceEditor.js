/**
 * Experience editor component
 */

import { $ } from '../../core/dom/elements.js';
import { createElement } from '../../core/dom/builder.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import * as experienceBusiness from '../../business/cv/experience.js';
import { eventBus } from '../../core/dom/events.js';

export class ExperienceEditor {
    constructor() {
        this.container = null;
        this.itemsList = null;
    }

    init() {
        this.container = $('experience-editor');
        this.itemsList = $('experience-items');
        eventBus.on('data:parsed', () => this.render());
    }

    render() {
        if (!this.container) return;

        const parsedData = cvStateService.getParsedData();
        if (!parsedData || !parsedData.positions || parsedData.positions.length === 0) {
            const section = $('experience-editor-section');
            if (section) section.style.display = 'none';
            return;
        }

        const section = $('experience-editor-section');
        if (section) section.style.display = 'block';

        this.container.innerHTML = '';
        this.renderAddButton();
        this.renderExperienceItems();
        this.renderVisibilityToggles();
    }

    renderAddButton() {
        const addBtn = createElement('button', {
            className: 'add-item-btn',
            innerHTML: '➕ Ajouter une expérience',
            events: {
                click: () => this.addExperience()
            }
        });
        this.container.appendChild(addBtn);
    }

    renderExperienceItems() {
        const parsedData = cvStateService.getParsedData();

        parsedData.positions.forEach((position, index) => {
            const item = this.createExperienceItem(position, index);
            this.container.appendChild(item);
        });
    }

    createExperienceItem(position, index) {
        const title = createElement('span', {
            className: 'editor-item-title',
            textContent: `${position.title || 'Sans titre'} - ${position.company || 'Entreprise'}`
        });

        const fields = this.createExperienceFields(position, index, title);

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
                    if (confirm(`Voulez-vous vraiment supprimer cette expérience ?`)) {
                        this.deleteExperience(index);
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

    createExperienceFields(position, index, title) {
        const parsedData = cvStateService.getParsedData();

        const fields = createElement('div', {
            className: 'editor-fields',
            children: [
                this.createFormRow([
                    this.createFormGroup('Titre du poste', 'text', position.title, (value) => {
                        experienceBusiness.updateExperience(parsedData.positions, index, 'title', value);
                        title.textContent = `${value} - ${parsedData.positions[index].company || 'Entreprise'}`;
                    }),
                    this.createFormGroup('Entreprise', 'text', position.company, (value) => {
                        experienceBusiness.updateExperience(parsedData.positions, index, 'company', value);
                        title.textContent = `${parsedData.positions[index].title || 'Sans titre'} - ${value}`;
                    })
                ]),
                this.createFormRow([
                    this.createFormGroup('Date de début', 'text', position.started_on, (value) => {
                        experienceBusiness.updateExperience(parsedData.positions, index, 'started_on', value);
                    }, 'Ex: Jan 2020'),
                    this.createFormGroup('Date de fin', 'text', position.finished_on, (value) => {
                        experienceBusiness.updateExperience(parsedData.positions, index, 'finished_on', value);
                    }, 'Ex: Déc 2022 ou Présent')
                ]),
                this.createTextareaGroup('Description', position.description, (value) => {
                    experienceBusiness.updateExperience(parsedData.positions, index, 'description', value);
                })
            ]
        });

        fields.style.display = 'none';
        return fields;
    }

    createFormRow(children) {
        return createElement('div', {
            className: 'editor-row',
            children
        });
    }

    createFormGroup(label, type, value, onChange, placeholder = '') {
        const input = createElement('input', {
            attributes: {
                type,
                value: value || '',
                placeholder
            }
        });
        input.addEventListener('input', (e) => onChange(e.target.value));

        return createElement('div', {
            className: 'form-group',
            children: [
                createElement('label', { textContent: label }),
                input
            ]
        });
    }

    createTextareaGroup(label, value, onChange) {
        const textarea = createElement('textarea', {
            attributes: { rows: '4' }
        });
        textarea.value = value || '';
        textarea.addEventListener('input', (e) => onChange(e.target.value));

        return createElement('div', {
            className: 'form-group',
            children: [
                createElement('label', { textContent: label }),
                textarea
            ]
        });
    }

    renderVisibilityToggles() {
        if (!this.itemsList) return;

        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        this.itemsList.innerHTML = '';

        if (!parsedData.positions || parsedData.positions.length === 0) {
            const section = $('experience-items-section');
            if (section) section.style.display = 'none';
            return;
        }

        const section = $('experience-items-section');
        if (section) section.style.display = 'block';

        parsedData.positions.forEach((position, index) => {
            const item = createElement('label', {
                className: 'item-toggle',
                children: [
                    this.createVisibilityCheckbox(index, config),
                    createElement('span', {
                        textContent: `${position.title || 'Sans titre'} - ${position.company || 'Entreprise inconnue'}`
                    })
                ]
            });

            this.itemsList.appendChild(item);
        });
    }

    createVisibilityCheckbox(index, config) {
        const checkbox = createElement('input', {
            attributes: { type: 'checkbox' }
        });
        checkbox.checked = config.experience_visible.includes(index);
        checkbox.addEventListener('change', (e) => {
            const newVisible = experienceBusiness.toggleExperienceVisibility(
                index,
                e.target.checked,
                config.experience_visible
            );
            config.experience_visible = newVisible;
            cvStateService.setConfig(config);
        });
        return checkbox;
    }

    addExperience() {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        const newExperience = experienceBusiness.createExperience();
        parsedData.positions.push(newExperience);

        if (config.experience_visible) {
            config.experience_visible.push(parsedData.positions.length - 1);
        }

        cvStateService.setParsedData(parsedData);
        cvStateService.setConfig(config);
        this.render();
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
        this.render();
    }
}
