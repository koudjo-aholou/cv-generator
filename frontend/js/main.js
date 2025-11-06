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

// UI Components
import { FileUploader } from './ui/components/fileUploader.js';
import { PhotoUploader } from './ui/components/photoUploader.js';
import { StepperNav } from './ui/components/stepperNav.js';

// UI Editors
import { ExperienceEditor } from './ui/editors/experienceEditor.js';
import { EducationEditor } from './ui/editors/educationEditor.js';
import { SkillsEditor } from './ui/editors/skillsEditor.js';
import { LanguagesEditor } from './ui/editors/languagesEditor.js';
import { CertificationsEditor } from './ui/editors/certificationsEditor.js';

// UI Views
import { ConfigView } from './ui/views/configView.js';
import { PreviewView } from './ui/views/previewView.js';

class Application {
    constructor() {
        this.components = {
            fileUploader: new FileUploader(),
            photoUploader: new PhotoUploader(),
            stepperNav: new StepperNav(),
            experienceEditor: new ExperienceEditor(),
            educationEditor: new EducationEditor(),
            skillsEditor: new SkillsEditor(),
            languagesEditor: new LanguagesEditor(),
            certificationsEditor: new CertificationsEditor(),
            configView: new ConfigView(),
            previewView: new PreviewView()
        };
    }

    async init() {
        // Initialize core UI managers
        loading.init();
        notifications.init();

        // Initialize all components
        Object.values(this.components).forEach(component => {
            if (component.init) {
                component.init();
            }
        });

        // Setup stepper navigation buttons
        this.setupStepperButtons();

        // Setup application-level event listeners
        this.setupEventListeners();

        // Setup global buttons
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
            await this.components.previewView.generatePreview();
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

        // Reset photo uploader
        this.components.photoUploader.removePhoto();

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

        // Re-render components
        this.components.fileUploader.render();

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new Application();
    app.init();
});
