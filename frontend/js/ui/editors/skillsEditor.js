/**
 * Skills editor component
 */

import { $ } from '../../core/dom/elements.js';
import { createElement } from '../../core/dom/builder.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import * as skillsBusiness from '../../business/cv/skills.js';
import { eventBus } from '../../core/dom/events.js';

export class SkillsEditor {
    constructor() {
        this.container = null;
        this.searchInput = null;
    }

    init() {
        this.container = $('skills-selector');
        this.searchInput = $('skills-search');
        eventBus.on('data:parsed', () => this.render());
    }

    render() {
        if (!this.container) return;

        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        const section = $('skills-selector-section');
        if (!parsedData || !parsedData.skills || parsedData.skills.length === 0) {
            if (section) section.style.display = 'none';
            return;
        }

        if (section) section.style.display = 'block';

        // Initialize skills_selected with all skills if not set
        if (!config.skills_selected) {
            config.skills_selected = [...parsedData.skills];
            cvStateService.setConfig(config);
        }

        this.renderSkills();
        this.setupSearch();
    }

    setupSearch() {
        if (!this.searchInput) return;

        this.searchInput.addEventListener('input', (e) => {
            this.renderSkills(e.target.value);
        });
    }

    renderSkills(filter = '') {
        if (!this.container) return;

        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        this.container.innerHTML = '';

        // Add button
        const addBtn = createElement('button', {
            className: 'add-item-btn',
            innerHTML: '➕ Ajouter une compétence',
            events: {
                click: () => this.addSkill()
            }
        });
        this.container.appendChild(addBtn);

        // Filter skills
        const filteredSkills = parsedData.skills.filter(skill =>
            skill.toLowerCase().includes(filter.toLowerCase())
        );

        // Render each skill
        filteredSkills.forEach((skill) => {
            const wrapper = this.createSkillItem(skill, config);
            this.container.appendChild(wrapper);
        });
    }

    createSkillItem(skill, config) {
        const dragHandle = createElement('span', {
            className: 'drag-handle',
            textContent: '☰'
        });

        const checkbox = createElement('input', {
            attributes: { type: 'checkbox' }
        });
        checkbox.checked = config.skills_selected.includes(skill);
        checkbox.addEventListener('change', (e) => {
            this.toggleSkill(skill, e.target.checked);
        });

        const text = createElement('span', {
            textContent: skill
        });

        const deleteBtn = createElement('button', {
            className: 'skill-delete-btn',
            textContent: '🗑️',
            attributes: { title: 'Supprimer cette compétence' },
            events: {
                click: (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (confirm(`Voulez-vous vraiment supprimer la compétence "${skill}" ?`)) {
                        this.deleteSkill(skill);
                    }
                }
            }
        });

        const item = createElement('label', {
            className: 'item-toggle',
            children: [checkbox, text, deleteBtn]
        });

        const wrapper = createElement('div', {
            className: 'skill-item-wrapper',
            attributes: { draggable: 'true' },
            children: [dragHandle, item]
        });

        return wrapper;
    }

    toggleSkill(skill, checked) {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        const newSelected = skillsBusiness.toggleSkillSelection(
            skill,
            checked,
            config.skills_selected
        );
        config.skills_selected = newSelected;
        cvStateService.setConfig(config);
    }

    addSkill() {
        const skillName = prompt('Entrez le nom de la compétence à ajouter :');

        if (!skillName || !skillName.trim()) return;

        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        const result = skillsBusiness.addSkill(
            parsedData.skills,
            skillName,
            config.skills_selected
        );

        if (!result.success) {
            alert(result.message);
            return;
        }

        cvStateService.setParsedData(parsedData);
        cvStateService.setConfig(config);

        // Re-render
        const filter = this.searchInput ? this.searchInput.value : '';
        this.renderSkills(filter);
    }

    deleteSkill(skill) {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        const newSelected = skillsBusiness.deleteSkill(
            parsedData.skills,
            skill,
            config.skills_selected
        );

        if (newSelected !== null) {
            config.skills_selected = newSelected;
        }

        cvStateService.setParsedData(parsedData);
        cvStateService.setConfig(config);

        // Re-render
        const filter = this.searchInput ? this.searchInput.value : '';
        this.renderSkills(filter);
    }
}
