/**
 * Main application entry point
 * Initializes all modules and orchestrates the application
 */

// Core
import { loading } from './core/ui/loading.js';
import { notifications } from './core/ui/notifications.js';
import { eventBus } from './core/dom/events.js';
import { $ } from './core/dom/elements.js';

// Services
import { parseService } from './services/api/parseService.js';
import { cvStateService } from './services/state/cvStateService.js';
import { stepperService } from './services/ui/stepperService.js';
import { fileService } from './services/file/fileService.js';

// Business
import { validateStep1, validateStep2 } from './business/validation/stepValidator.js';
import { initializeConfigFromData } from './business/workflow/stepFlow.js';

// Web Components (just import to register them)
import './ui/components/file-uploader.js';
import './ui/components/photo-uploader.js';
import './ui/components/stepper-nav.js';
import './ui/editors/experience-editor.js';
import './ui/editors/education-editor.js';
import './ui/editors/skills-editor.js';
import './ui/editors/languages-editor.js';
import './ui/editors/certifications-editor.js';

// UI Views (remain as coordinator classes)
import { ConfigView } from './ui/views/configView.js';
import { PreviewView } from './ui/views/previewView.js';

class Application {
    constructor() {
        console.log('🔵 Application: constructor called');
        // Only instantiate coordinator views, not Web Components
        try {
            console.log('🔵 Application: Creating ConfigView...');
            this.configView = new ConfigView();
            console.log('🔵 Application: ConfigView created');
        } catch (error) {
            console.error('🔴 Application: Error creating ConfigView:', error);
        }

        try {
            console.log('🔵 Application: Creating PreviewView...');
            this.previewView = new PreviewView();
            console.log('🔵 Application: PreviewView created');
        } catch (error) {
            console.error('🔴 Application: Error creating PreviewView:', error);
        }
    }

    async init() {
        console.log('🔵 Application: init() called');

        // Initialize core UI managers
        console.log('🔵 Application: Initializing loading...');
        loading.init();
        console.log('🔵 Application: Initializing notifications...');
        notifications.init();

        // Initialize coordinator views
        console.log('🔵 Application: Initializing configView...');
        this.configView.init();
        console.log('🔵 Application: configView initialized');

        console.log('🔵 Application: Initializing previewView...');
        this.previewView.init();
        console.log('🔵 Application: previewView initialized');

        // Setup stepper navigation buttons
        console.log('🔵 Application: Setting up stepper buttons...');
        this.setupStepperButtons();

        // Setup application-level event listeners
        console.log('🔵 Application: Setting up event listeners...');
        this.setupEventListeners();

        // Setup global buttons
        console.log('🔵 Application: Setting up global buttons...');
        this.setupGlobalButtons();

        console.log('✅ Application initialized');
    }

    setupStepperButtons() {
        const nextStep1Btn = $('nextStep1');
        const nextStep2Btn = $('nextStep2');
        const prevStep2Btn = $('prevStep2');
        const prevStep3Btn = $('prevStep3');

        if (nextStep1Btn) {
            nextStep1Btn.addEventListener('click', async () => {
                await this.goToNextStep(1);
            });
        }

        if (nextStep2Btn) {
            nextStep2Btn.addEventListener('click', async () => {
                await this.goToNextStep(2);
            });
        }

        if (prevStep2Btn) {
            prevStep2Btn.addEventListener('click', () => {
                stepperService.goToStep(1);
            });
        }

        if (prevStep3Btn) {
            prevStep3Btn.addEventListener('click', () => {
                stepperService.goToStep(2);
            });
        }
    }

    async goToNextStep(fromStep) {
        const validator = async (step) => {
            if (step === 1) {
                const files = fileService.getFiles();
                if (!validateStep1(files)) {
                    return false;
                }

                // Parse data if not already done
                if (!cvStateService.getParsedData()) {
                    try {
                        await this.parseDataForStep2();
                        return true;
                    } catch (error) {
                        return false;
                    }
                }
                return true;
            }

            if (step === 2) {
                return validateStep2();
            }

            return true;
        };

        const success = await stepperService.goToNextStep(fromStep, validator);

        // If moving from step 2 to 3, generate preview
        if (success && fromStep === 2) {
            await this.previewView.generatePreview();
        }
    }

    async parseDataForStep2() {
        const files = cvStateService.getFiles();
        const photoFile = cvStateService.getPhoto();

        const parsedData = await parseService.parseLinkedInData(files, photoFile);
        cvStateService.setParsedData(parsedData);

        // Initialize configuration based on parsed data
        const config = cvStateService.getConfig();
        const updatedConfig = initializeConfigFromData(parsedData, config);
        cvStateService.setConfig(updatedConfig);

        // Notify components that data is parsed
        eventBus.emit('data:parsed');
        document.dispatchEvent(new CustomEvent('data-parsed'));
    }

    setupEventListeners() {
        // Listen to before next step events
        eventBus.on('stepper:beforeNext', async (fromStep) => {
            // Additional actions before moving to next step can be added here
        });
    }

    setupGlobalButtons() {
        const resetBtn = $('resetBtn');
        const newCvBtn = $('newCvBtn');

        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetApp());
        }

        if (newCvBtn) {
            newCvBtn.addEventListener('click', () => this.resetApp());
        }
    }

    resetApp() {
        // Reset state
        cvStateService.reset();

        // Clear file input
        const fileInput = $('fileInput');
        if (fileInput) fileInput.value = '';

        // Reset photo uploader via custom event
        const photoUploader = document.querySelector('photo-uploader');
        if (photoUploader && photoUploader.removePhoto) {
            photoUploader.removePhoto();
        }

        // Hide success section
        const successSection = $('success-section');
        if (successSection) successSection.style.display = 'none';

        // Go back to step 1
        stepperService.goToStep(1);

        // Reset template selection
        const modernRadio = document.querySelector('input[name="template"][value="modern"]');
        if (modernRadio) modernRadio.checked = true;

        // Clear notifications
        notifications.hide();

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new Application();
    app.init();
});
