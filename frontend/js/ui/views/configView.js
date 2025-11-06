/**
 * Configuration view (Step 2)
 */

import { $, $$ } from '../../core/dom/elements.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import { applyTemplateColors } from '../../business/template/presets.js';
import { eventBus } from '../../core/dom/events.js';
import { checkSectionHasData } from '../../business/cv/sections.js';

export class ConfigView {
    init() {
        this.setupSectionToggles();
        this.setupTemplateSelection();
        this.setupColorPickers();
        this.setupContactFields();

        eventBus.on('data:parsed', () => this.populateFromData());
    }

    setupSectionToggles() {
        ['summary', 'experience', 'education', 'skills', 'languages', 'certifications'].forEach(section => {
            const toggle = $(`toggle-${section}`);
            if (toggle) {
                toggle.addEventListener('change', (e) => {
                    const config = cvStateService.getConfig();
                    config.sections[section] = e.target.checked;
                    cvStateService.setConfig(config);
                });
            }
        });
    }

    setupTemplateSelection() {
        $$('input[name="template"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.checked) {
                    const config = cvStateService.getConfig();
                    config.template = e.target.value;
                    config.colors = applyTemplateColors(e.target.value);
                    cvStateService.setConfig(config);
                    this.updateColorInputs(config.colors);
                }
            });
        });
    }

    setupColorPickers() {
        const colorPrimary = $('color-primary');
        const colorText = $('color-text');
        const colorSecondaryText = $('color-secondary-text');

        if (colorPrimary) {
            colorPrimary.addEventListener('input', (e) => {
                const config = cvStateService.getConfig();
                config.colors.primary = e.target.value;
                cvStateService.setConfig(config);
            });
        }

        if (colorText) {
            colorText.addEventListener('input', (e) => {
                const config = cvStateService.getConfig();
                config.colors.text = e.target.value;
                cvStateService.setConfig(config);
            });
        }

        if (colorSecondaryText) {
            colorSecondaryText.addEventListener('input', (e) => {
                const config = cvStateService.getConfig();
                config.colors.secondary_text = e.target.value;
                cvStateService.setConfig(config);
            });
        }
    }

    setupContactFields() {
        const email = $('contact-email');
        const phone = $('contact-phone');
        const address = $('contact-address');

        // Contact fields are read from inputs when generating PDF
    }

    populateFromData() {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        // Populate contact fields
        if (parsedData.profile) {
            const email = $('contact-email');
            const phone = $('contact-phone');
            const address = $('contact-address');

            if (email && parsedData.profile.email) email.value = parsedData.profile.email;
            if (phone && parsedData.profile.phone) phone.value = parsedData.profile.phone;
            if (address && parsedData.profile.address) address.value = parsedData.profile.address;
        }

        // Update section toggles
        Object.keys(config.sections).forEach(section => {
            const toggle = $(`toggle-${section}`);
            if (toggle) {
                toggle.checked = config.sections[section];
                const hasData = checkSectionHasData(section, parsedData);
                toggle.disabled = !hasData;
                if (!hasData) {
                    toggle.parentElement.style.opacity = '0.5';
                }
            }
        });
    }

    updateColorInputs(colors) {
        const colorPrimary = $('color-primary');
        const colorPrimaryHex = $('color-primary-hex');
        const colorText = $('color-text');
        const colorTextHex = $('color-text-hex');
        const colorSecondaryText = $('color-secondary-text');
        const colorSecondaryTextHex = $('color-secondary-text-hex');

        if (colorPrimary && colors.primary) {
            colorPrimary.value = colors.primary;
            if (colorPrimaryHex) colorPrimaryHex.value = colors.primary;
        }

        if (colorText && colors.text) {
            colorText.value = colors.text;
            if (colorTextHex) colorTextHex.value = colors.text;
        }

        if (colorSecondaryText && colors.secondary_text) {
            colorSecondaryText.value = colors.secondary_text;
            if (colorSecondaryTextHex) colorSecondaryTextHex.value = colors.secondary_text;
        }
    }
}
