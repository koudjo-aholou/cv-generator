/**
 * Stepper navigation service
 */

import { cvStateService } from '../state/cvStateService.js';
import { eventBus } from '../../core/dom/events.js';
import { TOTAL_STEPS } from '../../config/constants.js';

class StepperService {
    goToStep(stepNumber) {
        if (stepNumber < 1 || stepNumber > TOTAL_STEPS) return;

        cvStateService.setCurrentStep(stepNumber);
        eventBus.emit('stepper:change', stepNumber);

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async goToNextStep(fromStep, validator) {
        // Prevent concurrent processing
        if (cvStateService.isProcessing()) {
            return false;
        }

        cvStateService.setProcessing(true);

        try {
            // Validate current step
            const isValid = await validator(fromStep);
            if (!isValid) {
                return false;
            }

            // Emit event for pre-navigation actions
            eventBus.emit('stepper:beforeNext', fromStep);

            this.goToStep(fromStep + 1);
            return true;
        } finally {
            cvStateService.setProcessing(false);
        }
    }

    goToPreviousStep() {
        const currentStep = cvStateService.getCurrentStep();
        if (currentStep > 1) {
            this.goToStep(currentStep - 1);
        }
    }

    getCurrentStep() {
        return cvStateService.getCurrentStep();
    }
}

export const stepperService = new StepperService();
