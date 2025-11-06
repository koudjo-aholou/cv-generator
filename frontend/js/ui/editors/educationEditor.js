/**
 * Education editor component
 */

import { $ } from '../../core/dom/elements.js';
import { createElement } from '../../core/dom/builder.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import * as educationBusiness from '../../business/cv/education.js';
import { eventBus } from '../../core/dom/events.js';

export class EducationEditor {
    constructor() {
        this.container = null;
        this.itemsList = null;
    }

    init() {
        this.container = $('education-editor');
        this.itemsList = $('education-items');
        eventBus.on('data:parsed', () => this.render());
    }

    render() {
        if (!this.container) return;

        const parsedData = cvStateService.getParsedData();
        if (!parsedData || !parsedData.education || parsedData.education.length === 0) {
            const section = $('education-editor-section');
            if (section) section.style.display = 'none';
            return;
        }

        const section = $('education-editor-section');
        if (section) section.style.display = 'block';

        this.container.innerHTML = '';
        this.renderAddButton();
        this.renderEducationItems();
        this.renderVisibilityToggles();
    }

    renderAddButton() {
        const addBtn = createElement('button', {
            className: 'add-item-btn',
            innerHTML: '➕ Ajouter une formation',
            events: {
                click: () => this.addEducation()
            }
        });
        this.container.appendChild(addBtn);
    }

    renderEducationItems() {
        const parsedData = cvStateService.getParsedData();

        parsedData.education.forEach((edu, index) => {
            const item = this.createEducationItem(edu, index);
            this.container.appendChild(item);
        });
    }

    createEducationItem(edu, index) {
        const title = createElement('span', {
            className: 'editor-item-title',
            textContent: `${edu.degree || 'Diplôme'} - ${edu.school || 'École'}`
        });

        const fields = this.createEducationFields(edu, index, title);

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
                    if (confirm(`Voulez-vous vraiment supprimer cette formation : "${edu.degree || 'Diplôme'}" ?`)) {
                        this.deleteEducation(index);
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

    createEducationFields(edu, index, title) {
        const parsedData = cvStateService.getParsedData();

        const fields = createElement('div', {
            className: 'editor-fields',
            children: [
                this.createFormRow([
                    this.createFormGroup('Diplôme', 'text', edu.degree, (value) => {
                        educationBusiness.updateEducation(parsedData.education, index, 'degree', value);
                        title.textContent = `${value} - ${parsedData.education[index].school || 'École'}`;
                    }),
                    this.createFormGroup('École / Université', 'text', edu.school, (value) => {
                        educationBusiness.updateEducation(parsedData.education, index, 'school', value);
                        title.textContent = `${parsedData.education[index].degree || 'Diplôme'} - ${value}`;
                    })
                ]),
                this.createFormGroup('Domaine d\'études', 'text', edu.field_of_study, (value) => {
                    educationBusiness.updateEducation(parsedData.education, index, 'field_of_study', value);
                }),
                this.createFormRow([
                    this.createFormGroup('Date de début', 'text', edu.start_date, (value) => {
                        educationBusiness.updateEducation(parsedData.education, index, 'start_date', value);
                    }, 'Ex: 2015'),
                    this.createFormGroup('Date de fin', 'text', edu.end_date, (value) => {
                        educationBusiness.updateEducation(parsedData.education, index, 'end_date', value);
                    }, 'Ex: 2019')
                ])
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

    renderVisibilityToggles() {
        if (!this.itemsList) return;

        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        this.itemsList.innerHTML = '';

        if (!parsedData.education || parsedData.education.length === 0) {
            const section = $('education-items-section');
            if (section) section.style.display = 'none';
            return;
        }

        const section = $('education-items-section');
        if (section) section.style.display = 'block';

        parsedData.education.forEach((edu, index) => {
            const item = createElement('label', {
                className: 'item-toggle',
                children: [
                    this.createVisibilityCheckbox(index, config),
                    createElement('span', {
                        textContent: `${edu.degree || 'Diplôme'} - ${edu.school || 'École inconnue'}`
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
        checkbox.checked = config.education_visible.includes(index);
        checkbox.addEventListener('change', (e) => {
            const newVisible = educationBusiness.toggleEducationVisibility(
                index,
                e.target.checked,
                config.education_visible
            );
            config.education_visible = newVisible;
            cvStateService.setConfig(config);
        });
        return checkbox;
    }

    addEducation() {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        const newEducation = educationBusiness.createEducation();
        parsedData.education.push(newEducation);

        if (config.education_visible) {
            config.education_visible.push(parsedData.education.length - 1);
        }

        cvStateService.setParsedData(parsedData);
        cvStateService.setConfig(config);
        this.render();

        // Auto-expand the new item
        setTimeout(() => {
            const items = document.querySelectorAll('#education-editor .editor-item');
            const lastItem = items[items.length - 1];
            if (lastItem) {
                const toggleBtn = lastItem.querySelector('.editor-toggle-btn');
                if (toggleBtn) {
                    toggleBtn.click();
                }
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
        this.render();
    }
}
