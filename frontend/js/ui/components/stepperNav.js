/**
 * Stepper navigation component
 */

import { $, $$ } from '../../core/dom/elements.js';
import { eventBus } from '../../core/dom/events.js';
import { TOTAL_STEPS } from '../../config/constants.js';

export class StepperNav {
    constructor() {
        this.stepperText = null;
    }

    init() {
        this.stepperText = $('stepperText');

        // Listen to stepper changes
        eventBus.on('stepper:change', (step) => {
            this.updateIndicator(step);
            this.showStep(step);
        });
    }

    updateIndicator(step) {
        if (this.stepperText) {
            this.stepperText.textContent = `Étape ${step}/${TOTAL_STEPS}`;
        }
    }

    showStep(stepNumber) {
        // Hide all steps
        $$('.step-content').forEach(step => {
            step.classList.remove('active');
        });

        // Show the target step
        const targetStep = $(`step-${stepNumber}`);
        if (targetStep) {
            targetStep.classList.add('active');
        }
    }
}
