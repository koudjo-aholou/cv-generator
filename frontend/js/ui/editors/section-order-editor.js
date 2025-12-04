/**
 * Section Order Editor - Drag and drop UI for reordering CV sections
 */

import { $ } from '../../core/dom/elements.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import { moveSectionUp, moveSectionDown, reorderSection } from '../../business/cv/sections.js';
import { eventBus } from '../../core/dom/events.js';

const SECTION_NAMES = {
    summary: 'À Propos',
    experience: 'Expérience Professionnelle',
    education: 'Formation',
    skills: 'Compétences',
    languages: 'Langues',
    certifications: 'Certifications'
};

export class SectionOrderEditor {
    constructor() {
        this.container = null;
        this.draggedItem = null;
        this.draggedIndex = null;
    }

    init() {
        this.container = $('section-order');
        if (!this.container) {
            console.error('section-order element not found');
            return;
        }

        // Listen for data parsed event
        eventBus.on('data:parsed', () => this.render());

        // Listen for config changes
        eventBus.on('config:updated', () => this.render());
    }

    render() {
        const config = cvStateService.getConfig();
        const sectionOrder = config.section_order || [];

        if (!this.container) return;

        this.container.innerHTML = '';

        sectionOrder.forEach((section, index) => {
            const item = this.createSectionItem(section, index);
            this.container.appendChild(item);
        });
    }

    createSectionItem(section, index) {
        const config = cvStateService.getConfig();
        const sectionOrder = config.section_order;

        const item = document.createElement('div');
        item.className = 'section-order-item';
        item.draggable = true;
        item.dataset.section = section;
        item.dataset.index = index;

        // Drag handle
        const dragHandle = document.createElement('span');
        dragHandle.className = 'drag-handle';
        dragHandle.textContent = '☰';

        // Section label
        const label = document.createElement('span');
        label.textContent = SECTION_NAMES[section] || section;

        // Button container
        const buttons = document.createElement('div');
        buttons.className = 'order-buttons';

        // Up button (if not first)
        if (index > 0) {
            const upBtn = document.createElement('button');
            upBtn.textContent = '↑';
            upBtn.className = 'order-btn';
            upBtn.type = 'button';
            upBtn.onclick = (e) => {
                e.stopPropagation();
                this.handleMoveUp(index);
            };
            buttons.appendChild(upBtn);
        }

        // Down button (if not last)
        if (index < sectionOrder.length - 1) {
            const downBtn = document.createElement('button');
            downBtn.textContent = '↓';
            downBtn.className = 'order-btn';
            downBtn.type = 'button';
            downBtn.onclick = (e) => {
                e.stopPropagation();
                this.handleMoveDown(index);
            };
            buttons.appendChild(downBtn);
        }

        // Assemble item
        item.appendChild(dragHandle);
        item.appendChild(label);
        item.appendChild(buttons);

        // Attach drag event listeners
        item.addEventListener('dragstart', (e) => this.handleDragStart(e, index));
        item.addEventListener('dragover', (e) => this.handleDragOver(e));
        item.addEventListener('drop', (e) => this.handleDrop(e, index));
        item.addEventListener('dragend', (e) => this.handleDragEnd(e));

        return item;
    }

    handleMoveUp(index) {
        const config = cvStateService.getConfig();
        const newOrder = moveSectionUp([...config.section_order], index);
        config.section_order = newOrder;
        cvStateService.setConfig(config);
        this.render();
    }

    handleMoveDown(index) {
        const config = cvStateService.getConfig();
        const newOrder = moveSectionDown([...config.section_order], index);
        config.section_order = newOrder;
        cvStateService.setConfig(config);
        this.render();
    }

    handleDragStart(e, index) {
        this.draggedItem = e.target;
        this.draggedIndex = index;
        e.target.style.opacity = '0.5';
        e.dataTransfer.effectAllowed = 'move';
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';

        const targetItem = e.target.closest('.section-order-item');
        if (targetItem && targetItem !== this.draggedItem) {
            // Visual feedback
            targetItem.style.borderTop = '2px solid #3498db';
        }
    }

    handleDrop(e, targetIndex) {
        e.preventDefault();

        const targetItem = e.target.closest('.section-order-item');
        if (!targetItem) return;

        // Remove visual feedback
        targetItem.style.borderTop = '';

        if (this.draggedIndex !== null && this.draggedIndex !== targetIndex) {
            const config = cvStateService.getConfig();
            const newOrder = reorderSection([...config.section_order], this.draggedIndex, targetIndex);
            config.section_order = newOrder;
            cvStateService.setConfig(config);
            this.render();
        }
    }

    handleDragEnd(e) {
        e.target.style.opacity = '';

        // Remove all visual feedback
        const allItems = this.container.querySelectorAll('.section-order-item');
        allItems.forEach(item => {
            item.style.borderTop = '';
        });

        this.draggedItem = null;
        this.draggedIndex = null;
    }
}
