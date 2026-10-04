/**
 * Configuration view (Step 2)
 */

import { $, $$ } from '../../core/dom/elements.js';
import { cvStateService } from '../../services/state/cvStateService.js';
import { applyTemplateColors } from '../../business/template/presets.js';
import { eventBus } from '../../core/dom/events.js';
import { checkSectionHasData } from '../../business/cv/sections.js';
import { SectionOrderEditor } from '../editors/section-order-editor.js';
import {
    SECTION_NAMES_BY_LANG,
    CV_SECTIONS,
    LABEL_KEYS
} from '../../config/constants.js';
import { DEFAULT_CONFIG } from '../../config/defaults.js';

// Free-text inputs of step 2 that hold personal data. They are read straight
// from the DOM when the PDF is generated, so they must be cleared on reset:
// otherwise the previous person's details end up in the next CV.
const PERSONAL_INPUT_IDS = [
    'profile-headline',
    'profile-summary',
    'contact-email',
    'contact-phone',
    'contact-address',
    'contact-birth-date',
    'contact-nationality',
    'contact-civil-status',
    'contact-permit'
];

export class ConfigView {
    constructor() {
        this.sectionOrderEditor = new SectionOrderEditor();
    }

    init() {
        this.setupSectionToggles();
        this.setupTemplateSelection();
        this.setupColorPickers();
        this.setupLabelInputs();
        this.setupLanguageAndCvType();
        this.sectionOrderEditor.init();

        eventBus.on('data:parsed', () => this.populateFromData());
    }

    /**
     * Rewrite every step-2 control from the given config and clear the
     * personal inputs. Called on reset so the form can never disagree with
     * the state it is supposed to represent.
     */
    syncFromConfig(config = cvStateService.getConfig()) {
        // Fill in anything the caller left out: this method must always leave
        // the form in a complete, coherent state. Throwing halfway through
        // would be worse than not resetting, since the personal inputs are
        // cleared first and the selects would keep the previous values.
        const safe = { ...DEFAULT_CONFIG, ...config };
        safe.sections = { ...DEFAULT_CONFIG.sections, ...(config.sections || {}) };
        safe.colors = { ...DEFAULT_CONFIG.colors, ...(config.colors || {}) };
        config = safe;

        PERSONAL_INPUT_IDS.forEach((id) => {
            const input = $(id);
            if (input) input.value = '';
        });

        const languageSelect = $('cv-language');
        if (languageSelect) languageSelect.value = config.language;

        const cvTypeSelect = $('cv-type');
        if (cvTypeSelect) cvTypeSelect.value = config.cv_type;

        this.toggleSwissSection(config.cv_type);

        // Labels fall back to the defaults of the configured language
        const defaults = SECTION_NAMES_BY_LANG[config.language] || SECTION_NAMES_BY_LANG.fr;
        LABEL_KEYS.forEach((key) => {
            const input = $(`label-${key}`);
            if (input) input.value = (config.labels && config.labels[key]) || defaults[key];
        });

        CV_SECTIONS.forEach((section) => {
            const toggle = $(`toggle-${section}`);
            if (toggle) {
                toggle.checked = config.sections[section] !== false;
                toggle.disabled = false;
                if (toggle.parentElement) toggle.parentElement.style.opacity = '';
            }
        });

        const templateRadio = document.querySelector(
            `input[name="template"][value="${config.template}"]`
        );
        if (templateRadio) templateRadio.checked = true;

        // Colours are driven by the template, so they must follow it
        this.updateColorInputs(config.colors);

        this.sectionOrderEditor.render();
    }

    toggleSwissSection(cvType) {
        const swissSection = $('swiss-fields-section');
        if (swissSection) {
            swissSection.style.display = cvType === 'swiss' ? '' : 'none';
        }
    }

    setupLanguageAndCvType() {
        const languageSelect = $('cv-language');
        const cvTypeSelect = $('cv-type');

        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                const language = e.target.value;
                const config = cvStateService.getConfig();
                config.language = language;

                // Switching language resets the section labels to that
                // language's defaults, overwriting any customization —
                // keeping French titles on an English CV is never wanted.
                const defaults = SECTION_NAMES_BY_LANG[language];
                LABEL_KEYS.forEach((key) => {
                    const input = $(`label-${key}`);
                    if (input) input.value = defaults[key];
                });
                config.labels = { ...defaults };
                cvStateService.setConfig(config);

                eventBus.emit('config:language-changed', language);
            });
        }

        if (cvTypeSelect) {
            cvTypeSelect.addEventListener('change', (e) => {
                const cvType = e.target.value;
                const config = cvStateService.getConfig();
                config.cv_type = cvType;
                cvStateService.setConfig(config);

                this.toggleSwissSection(cvType);
            });
        }
    }

    setupLabelInputs() {
        LABEL_KEYS.forEach(key => {
            const input = $(`label-${key}`);
            if (!input) return;
            input.addEventListener('input', () => {
                const config = cvStateService.getConfig();
                if (!config.labels) config.labels = {};
                config.labels[key] = input.value.trim() || undefined;
                cvStateService.setConfig(config);
            });
        });
    }

    setupSectionToggles() {
        CV_SECTIONS.forEach(section => {
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

    populateFromData() {
        const parsedData = cvStateService.getParsedData();
        const config = cvStateService.getConfig();

        // Populate contact fields
        if (parsedData.profile) {
            const headline = $('profile-headline');
            const email = $('contact-email');
            const phone = $('contact-phone');
            const address = $('contact-address');
            const summary = $('profile-summary');

            if (headline && parsedData.profile.headline) headline.value = parsedData.profile.headline;
            if (email && parsedData.profile.email) email.value = parsedData.profile.email;
            if (phone && parsedData.profile.phone) phone.value = parsedData.profile.phone;
            if (address && parsedData.profile.address) address.value = parsedData.profile.address;
            if (summary && parsedData.profile.summary) summary.value = parsedData.profile.summary;
        }

        // Update section toggles
        CV_SECTIONS.forEach(section => {
            const toggle = $(`toggle-${section}`);
            if (!toggle) return;

            toggle.checked = config.sections[section] !== false;
            const hasData = checkSectionHasData(section, parsedData);
            toggle.disabled = !hasData;
            // Reset the dimming too, otherwise a section that was empty on a
            // previous import stays greyed out once it does have data
            if (toggle.parentElement) {
                toggle.parentElement.style.opacity = hasData ? '' : '0.5';
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
