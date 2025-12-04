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
        console.log('SectionOrderEditor: init() called');
        this.container = $('section-order');
        console.log('SectionOrderEditor: container =', this.container);

        if (!this.container) {
            console.error('section-order element not found');
            return;
        }

        // Listen for data parsed event
        eventBus.on('data:parsed', () => {
            console.log('SectionOrderEditor: data:parsed event received');
            this.render();
        });

        // Listen for config changes
        eventBus.on('config:updated', () => {
            console.log('SectionOrderEditor: config:updated event received');
            this.render();
        });

        // Try to render immediately if config already exists
        const config = cvStateService.getConfig();
        if (config && config.section_order && config.section_order.length > 0) {
            console.log('SectionOrderEditor: config exists, rendering immediately');
            this.render();
        }
    }

    render() {
        console.log('SectionOrderEditor: render() called');
        const config = cvStateService.getConfig();
        const sectionOrder = config.section_order || [];
        console.log('SectionOrderEditor: sectionOrder =', sectionOrder);

        if (!this.container) {
            console.error('SectionOrderEditor: container is null, cannot render');
            return;
        }

        this.container.innerHTML = '';

        if (sectionOrder.length === 0) {
            console.warn('SectionOrderEditor: sectionOrder is empty');
            return;
        }

        sectionOrder.forEach((section, index) => {
            console.log(`SectionOrderEditor: creating item for section ${section} at index ${index}`);
            const item = this.createSectionItem(section, index);
            this.container.appendChild(item);
        });

        console.log(`SectionOrderEditor: rendered ${sectionOrder.length} items`);
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
