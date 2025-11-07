/**
 * Skills Editor Web Component
 * Usage: <skills-editor></skills-editor>
 */

import { cvStateService } from '../../services/state/cvStateService.js';
import * as skillsBusiness from '../../business/cv/skills.js';

export class SkillsEditor extends HTMLElement {
    constructor() {
        super();
        this.skills = [];
        this.selectedSkills = [];
        this.searchFilter = '';
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

            if (parsedData && parsedData.skills) {
                this.skills = parsedData.skills;

                // Initialize skills_selected with all skills if not set
                if (!config.skills_selected) {
                    config.skills_selected = [...parsedData.skills];
                    cvStateService.setConfig(config);
                }

                this.selectedSkills = config.skills_selected || [];
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
        if (!this.skills || this.skills.length === 0) {
            this.style.display = 'none';
            return;
        }

        this.style.display = 'block';

        this.innerHTML = `
            <div class="editor-section">
                <h3>💡 Compétences</h3>

                <div class="search-box">
                    <input type="text" id="skills-search" placeholder="🔍 Rechercher une compétence..." value="${this.searchFilter}">
                </div>

                <button class="add-item-btn">➕ Ajouter une compétence</button>

                <div class="skills-list" id="skills-list"></div>
            </div>
        `;

        this.renderSkillsList();
        this.attachEventListeners();
    }

    renderSkillsList() {
        const list = this.querySelector('#skills-list');
        if (!list) return;

        list.innerHTML = '';

        // Filter skills based on search
        const filteredSkills = this.skills.filter(skill =>
            skill.toLowerCase().includes(this.searchFilter.toLowerCase())
        );

        if (filteredSkills.length === 0) {
            list.innerHTML = '<p class="no-results">Aucune compétence trouvée</p>';
            return;
        }

        filteredSkills.forEach((skill) => {
            const wrapper = document.createElement('div');
            wrapper.className = 'skill-item-wrapper';
            wrapper.draggable = true;

            const isSelected = this.selectedSkills.includes(skill);

            wrapper.innerHTML = `
                <span class="drag-handle">☰</span>
                <label class="item-toggle">
                    <input type="checkbox" data-skill="${skill}" ${isSelected ? 'checked' : ''}>
                    <span>${skill}</span>
                    <button class="skill-delete-btn" data-skill="${skill}" title="Supprimer cette compétence">🗑️</button>
                </label>
            `;

            list.appendChild(wrapper);
        });
    }

    attachEventListeners() {
        // Search input
        const searchInput = this.querySelector('#skills-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchFilter = e.target.value;
                this.renderSkillsList();
                this.attachSkillEventListeners();
            });
        }

        // Add button
        const addBtn = this.querySelector('.add-item-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addSkill());
        }

        this.attachSkillEventListeners();
    }

    attachSkillEventListeners() {
        // Checkboxes
        this.querySelectorAll('input[type="checkbox"][data-skill]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const skill = e.target.dataset.skill;
                this.toggleSkill(skill, e.target.checked);
            });
        });

        // Delete buttons
        this.querySelectorAll('.skill-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const skill = e.target.dataset.skill;
                if (confirm(`Voulez-vous vraiment supprimer la compétence "${skill}" ?`)) {
                    this.deleteSkill(skill);
                }
            });
        });
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
        this.selectedSkills = newSelected;
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

        this.skills = parsedData.skills;
        this.selectedSkills = config.skills_selected;

        // Re-render
        this.renderSkillsList();
        this.attachSkillEventListeners();
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

        this.skills = parsedData.skills;
        this.selectedSkills = config.skills_selected;

        // Re-render
        this.renderSkillsList();
        this.attachSkillEventListeners();
    }
}

customElements.define('skills-editor', SkillsEditor);
