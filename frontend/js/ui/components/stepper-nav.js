/**
 * Stepper Navigation Web Component
 * Usage: <stepper-nav current="1" total="3"></stepper-nav>
 */

import { TOTAL_STEPS } from '../../config/constants.js';

export class StepperNav extends HTMLElement {
    static get observedAttributes() {
        return ['current', 'total'];
    }

    constructor() {
        super();
        this.currentStep = 1;
        this.totalSteps = TOTAL_STEPS;
    }

    connectedCallback() {
        this.currentStep = parseInt(this.getAttribute('current')) || 1;
        this.totalSteps = parseInt(this.getAttribute('total')) || TOTAL_STEPS;
        this.render();
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (oldValue === newValue) return;

        if (name === 'current') {
            this.currentStep = parseInt(newValue) || 1;
            this.updateDisplay();
            this.showStep(this.currentStep);
        } else if (name === 'total') {
            this.totalSteps = parseInt(newValue) || TOTAL_STEPS;
            this.updateDisplay();
        }
    }

    render() {
        this.innerHTML = `
            <div class="stepper">
                <div id="stepperText" class="stepper-text">
                    Étape ${this.currentStep}/${this.totalSteps}
                </div>
            </div>
        `;
    }

    updateDisplay() {
        const stepperText = this.querySelector('#stepperText');
        if (stepperText) {
            stepperText.textContent = `Étape ${this.currentStep}/${this.totalSteps}`;
        }
    }

    showStep(stepNumber) {
        // Hide all steps
        document.querySelectorAll('.step-content').forEach(step => {
            step.classList.remove('active');
        });

        // Show the target step
        const targetStep = document.getElementById(`step-${stepNumber}`);
        if (targetStep) {
            targetStep.classList.add('active');

            // Dispatch event
            this.dispatchEvent(new CustomEvent('step-changed', {
                bubbles: true,
                detail: { step: stepNumber }
            }));
        }
    }

    goToStep(step) {
        if (step < 1 || step > this.totalSteps) return;
        this.setAttribute('current', step);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

customElements.define('stepper-nav', StepperNav);
