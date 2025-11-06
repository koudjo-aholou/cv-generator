// API Configuration
const API_URL = 'http://localhost:5000';

// Template presets
const TEMPLATE_PRESETS = {
    modern: {
        primary: '#3498db',
        text: '#2c3e50',
        secondary_text: '#7f8c8d'
    },
    classic: {
        primary: '#2c3e50',
        text: '#1a1a1a',
        secondary_text: '#666666'
    },
    creative: {
        primary: '#e74c3c',
        text: '#2c3e50',
        secondary_text: '#95a5a6'
    }
};

// Stepper State
let currentStep = 1;
const totalSteps = 3;

// State
let selectedFiles = [];
let parsedData = null;
let photoFile = null;
let currentConfig = {
    sections: {
        summary: true,
        experience: true,
        education: true,
        skills: true,
        languages: true,
        certifications: true
    },
    section_order: ['summary', 'experience', 'education', 'skills', 'languages', 'certifications'],
    experience_visible: null, // null means all visible
    education_visible: null,   // null means all visible
    skills_selected: null,     // null means all visible, array means specific skills
    template: 'modern',
    colors: {
        primary: '#3498db',
        text: '#2c3e50',
        secondary_text: '#7f8c8d'
    }
};
let currentPdfBlob = null;

// DOM Elements
const dropZone = document.getElementById('dropZone');
const browseBtn = document.getElementById('browseBtn');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const photoSection = document.getElementById('photo-section');
const previewSection = document.getElementById('preview-section');
const successSection = document.getElementById('success-section');
const generateBtn = document.getElementById('generateBtn');
const resetBtn = document.getElementById('resetBtn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');
const photoInput = document.getElementById('photoInput');
const uploadPhotoBtn = document.getElementById('uploadPhotoBtn');
const removePhotoBtn = document.getElementById('removePhotoBtn');
const photoPreview = document.getElementById('photoPreview');
const photoPreviewImg = document.getElementById('photoPreviewImg');

// Preview Elements
const pdfPreviewFrame = document.getElementById('pdfPreviewFrame');
const previewLoading = document.getElementById('previewLoading');
const refreshPreviewBtn = document.getElementById('refreshPreviewBtn');
const downloadFinalBtn = document.getElementById('downloadFinalBtn');
const sectionOrderList = document.getElementById('section-order');
const experienceItemsList = document.getElementById('experience-items');
const educationItemsList = document.getElementById('education-items');

// Contact Fields
const contactEmailInput = document.getElementById('contact-email');
const contactPhoneInput = document.getElementById('contact-phone');
const contactAddressInput = document.getElementById('contact-address');

// Color and Template Elements
const colorPrimaryInput = document.getElementById('color-primary');
const colorPrimaryHex = document.getElementById('color-primary-hex');
const colorTextInput = document.getElementById('color-text');
const colorTextHex = document.getElementById('color-text-hex');
const colorSecondaryTextInput = document.getElementById('color-secondary-text');
const colorSecondaryTextHex = document.getElementById('color-secondary-text-hex');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // Browse button - prevent event propagation to dropZone
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    // Drop zone events - only trigger if not clicking on button
    dropZone.addEventListener('click', (e) => {
        // Don't trigger if clicking on the browse button
        if (e.target !== browseBtn && !browseBtn.contains(e.target)) {
            fileInput.click();
        }
    });
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFiles(Array.from(e.target.files));
    });

    // Button events
    if (generateBtn) generateBtn.addEventListener('click', generateCV);
    if (resetBtn) resetBtn.addEventListener('click', resetApp);
    if (refreshPreviewBtn) refreshPreviewBtn.addEventListener('click', async () => await refreshPreview());
    if (downloadFinalBtn) downloadFinalBtn.addEventListener('click', downloadFinalPDF);

    // Stepper navigation
    const nextStep1Btn = document.getElementById('nextStep1');
    const nextStep2Btn = document.getElementById('nextStep2');
    const prevStep2Btn = document.getElementById('prevStep2');
    const prevStep3Btn = document.getElementById('prevStep3');
    const newCvBtn = document.getElementById('newCvBtn');

    if (nextStep1Btn) nextStep1Btn.addEventListener('click', async () => await goToNextStep(1));
    if (nextStep2Btn) nextStep2Btn.addEventListener('click', async () => await goToNextStep(2));
    if (prevStep2Btn) prevStep2Btn.addEventListener('click', () => goToStep(1));
    if (prevStep3Btn) prevStep3Btn.addEventListener('click', () => goToStep(2));
    if (newCvBtn) newCvBtn.addEventListener('click', resetApp);

    // Photo upload events
    uploadPhotoBtn.addEventListener('click', () => photoInput.click());
    photoInput.addEventListener('change', handlePhotoUpload);
    removePhotoBtn.addEventListener('click', removePhoto);

    // Section toggles
    ['summary', 'experience', 'education', 'skills', 'languages', 'certifications'].forEach(section => {
        const toggle = document.getElementById(`toggle-${section}`);
        if (toggle) {
            toggle.addEventListener('change', (e) => {
                currentConfig.sections[section] = e.target.checked;
            });
        }
    });

    // Template selection
    document.querySelectorAll('input[name="template"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.checked) {
                currentConfig.template = e.target.value;
                applyTemplateColors(e.target.value);
            }
        });
    });

    // Color pickers
    if (colorPrimaryInput) {
        colorPrimaryInput.addEventListener('input', (e) => {
            currentConfig.colors.primary = e.target.value;
            colorPrimaryHex.value = e.target.value;
        });
    }

    if (colorTextInput) {
        colorTextInput.addEventListener('input', (e) => {
            currentConfig.colors.text = e.target.value;
            colorTextHex.value = e.target.value;
        });
    }

    if (colorSecondaryTextInput) {
        colorSecondaryTextInput.addEventListener('input', (e) => {
            currentConfig.colors.secondary_text = e.target.value;
            colorSecondaryTextHex.value = e.target.value;
        });
    }
}

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = Array.from(e.dataTransfer.files).filter(file =>
        file.name.endsWith('.csv')
    );

    handleFiles(files);
}

// Stepper Navigation Functions
function goToStep(stepNumber) {
    if (stepNumber < 1 || stepNumber > totalSteps) return;

    // Hide all steps
    document.querySelectorAll('.step-content').forEach(step => {
        step.classList.remove('active');
    });

    // Show the target step
    const targetStep = document.getElementById(`step-${stepNumber}`);
    if (targetStep) {
        targetStep.classList.add('active');
        currentStep = stepNumber;
        updateStepperIndicator();

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

async function goToNextStep(fromStep) {
    // Validate current step
    const isValid = await validateStep(fromStep);
    if (!isValid) {
        return;
    }

    // Special handling for step 2 -> 3: generate preview
    if (fromStep === 2) {
        await generatePreviewForStep3();
    }

    goToStep(fromStep + 1);
}

async function validateStep(stepNumber) {
    if (stepNumber === 1) {
        // Check if required CSV files are uploaded
        const requiredFiles = ['Profile.csv', 'Positions.csv', 'Education.csv'];
        const uploadedFileNames = selectedFiles.map(f => f.name);

        const missingFiles = requiredFiles.filter(req =>
            !uploadedFileNames.some(uploaded => uploaded === req)
        );

        if (missingFiles.length > 0) {
            showError(`Fichiers requis manquants : ${missingFiles.join(', ')}`);
            return false;
        }

        // Parse data if not already done
        if (!parsedData) {
            try {
                await parseDataForStep2();
                return true;
            } catch (error) {
                // Error already displayed by parseDataForStep2
                return false;
            }
        }

        return true;
    }

    if (stepNumber === 2) {
        // Step 2 validation (optional, always pass for now)
        return true;
    }

    return true;
}

function updateStepperIndicator() {
    const stepperText = document.getElementById('stepperText');
    if (stepperText) {
        stepperText.textContent = `Étape ${currentStep}/${totalSteps}`;
    }
}

async function parseDataForStep2() {
    try {
        showLoading();

        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('files', file));
        if (photoFile) {
            formData.append('photo', photoFile);
        }

        const response = await fetch(`${API_URL}/api/parse-linkedin`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erreur lors du parsing');
        }

        parsedData = await response.json();

        // Initialize config based on parsed data
        initializeConfig();

        // Populate configuration UI
        populateConfigUI();

        hideLoading();
    } catch (error) {
        hideLoading();
        showError('Erreur lors du parsing des données: ' + error.message);
        throw error;
    }
}

async function generatePreviewForStep3() {
    try {
        showLoading();
        await refreshPreview();
        hideLoading();
    } catch (error) {
        hideLoading();
        showError('Erreur lors de la génération de l\'aperçu: ' + error.message);
    }
}

// File Handling
function handleFiles(files) {
    if (files.length === 0) {
        showError('Veuillez sélectionner des fichiers CSV');
        return;
    }

    selectedFiles = files;
    displayFileList();
    hideError();
}

function displayFileList() {
    fileList.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const fileInfo = document.createElement('div');
        fileInfo.className = 'file-item-info';

        const fileIcon = document.createElement('span');
        fileIcon.className = 'file-icon';
        fileIcon.textContent = '📄';

        const fileDetails = document.createElement('div');

        const fileName = document.createElement('div');
        fileName.className = 'file-name';
        fileName.textContent = file.name;

        const fileSize = document.createElement('div');
        fileSize.className = 'file-size';
        fileSize.textContent = formatFileSize(file.size);

        fileDetails.appendChild(fileName);
        fileDetails.appendChild(fileSize);

        fileInfo.appendChild(fileIcon);
        fileInfo.appendChild(fileDetails);

        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-file';
        removeBtn.textContent = 'Retirer';
        removeBtn.onclick = () => removeFile(index);

        fileItem.appendChild(fileInfo);
        fileItem.appendChild(removeBtn);

        fileList.appendChild(fileItem);
    });
}

function removeFile(index) {
    selectedFiles.splice(index, 1);

    if (selectedFiles.length === 0) {
        fileList.innerHTML = '';
    } else {
        displayFileList();
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Apply template colors
function applyTemplateColors(template) {
    const colors = TEMPLATE_PRESETS[template];
    if (!colors) return;

    // Update config
    currentConfig.colors = { ...colors };

    // Update UI
    if (colorPrimaryInput) {
        colorPrimaryInput.value = colors.primary;
        colorPrimaryHex.value = colors.primary;
    }
    if (colorTextInput) {
        colorTextInput.value = colors.text;
        colorTextHex.value = colors.text;
    }
    if (colorSecondaryTextInput) {
        colorSecondaryTextInput.value = colors.secondary_text;
        colorSecondaryTextHex.value = colors.secondary_text;
    }
}

// Generate CV - Now shows preview instead of downloading
async function generateCV() {
    if (selectedFiles.length === 0) {
        showError('Aucun fichier sélectionné');
        return;
    }

    showLoading();
    hideError();

    try {
        // Step 1: Parse LinkedIn data
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        const parseResponse = await fetch(`${API_URL}/api/parse-linkedin`, {
            method: 'POST',
            body: formData
        });

        if (!parseResponse.ok) {
            throw new Error('Erreur lors de l\'analyse des données');
        }

        parsedData = await parseResponse.json();

        // Initialize config based on available data
        initializeConfig();

        // Populate configuration UI
        populateConfigUI();

        // Generate initial preview
        await generatePreview();

    } catch (error) {
        showError('Erreur: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Initialize configuration based on available data
function initializeConfig() {
    // Initialize experience_visible with all indices
    if (parsedData.positions && parsedData.positions.length > 0) {
        currentConfig.experience_visible = parsedData.positions.map((_, i) => i);
    }

    // Initialize education_visible with all indices
    if (parsedData.education && parsedData.education.length > 0) {
        currentConfig.education_visible = parsedData.education.map((_, i) => i);
    }

    // Update section toggles based on available data
    currentConfig.sections.summary = !!(parsedData.profile && parsedData.profile.summary);
    currentConfig.sections.experience = !!(parsedData.positions && parsedData.positions.length > 0);
    currentConfig.sections.education = !!(parsedData.education && parsedData.education.length > 0);
    currentConfig.sections.skills = !!(parsedData.skills && parsedData.skills.length > 0);
    currentConfig.sections.languages = !!(parsedData.languages && parsedData.languages.length > 0);
    currentConfig.sections.certifications = !!(parsedData.certifications && parsedData.certifications.length > 0);
}

// Populate configuration UI
function populateConfigUI() {
    // Populate contact fields
    if (parsedData.profile) {
        if (contactEmailInput && parsedData.profile.email) {
            contactEmailInput.value = parsedData.profile.email;
        }
        if (contactPhoneInput && parsedData.profile.phone) {
            contactPhoneInput.value = parsedData.profile.phone;
        }
        if (contactAddressInput && parsedData.profile.address) {
            contactAddressInput.value = parsedData.profile.address;
        }
    }

    // Update section toggles
    Object.keys(currentConfig.sections).forEach(section => {
        const toggle = document.getElementById(`toggle-${section}`);
        if (toggle) {
            toggle.checked = currentConfig.sections[section];

            // Disable toggle if no data
            const hasData = checkSectionHasData(section);
            toggle.disabled = !hasData;
            if (!hasData) {
                toggle.parentElement.style.opacity = '0.5';
            }
        }
    });

    // Populate section order
    populateSectionOrder();

    // Populate profile summary editor
    populateProfileSummaryEditor();

    // Populate experience editor and items
    populateExperienceEditor();
    populateExperienceItems();

    // Populate education editor and items
    populateEducationEditor();
    populateEducationItems();

    // Populate skills selector
    populateSkillsSelector();

    // Populate languages editor
    populateLanguagesEditor();

    // Populate certifications editor
    populateCertificationsEditor();
}

function checkSectionHasData(section) {
    switch (section) {
        case 'summary':
            return !!(parsedData.profile && parsedData.profile.summary);
        case 'experience':
            return !!(parsedData.positions && parsedData.positions.length > 0);
        case 'education':
            return !!(parsedData.education && parsedData.education.length > 0);
        case 'skills':
            return !!(parsedData.skills && parsedData.skills.length > 0);
        case 'languages':
            return !!(parsedData.languages && parsedData.languages.length > 0);
        case 'certifications':
            return !!(parsedData.certifications && parsedData.certifications.length > 0);
        default:
            return false;
    }
}

// Populate section order with drag and drop
function populateSectionOrder() {
    if (!sectionOrderList) return;

    sectionOrderList.innerHTML = '';

    const sectionNames = {
        summary: 'À Propos',
        experience: 'Expérience Professionnelle',
        education: 'Formation',
        skills: 'Compétences',
        languages: 'Langues',
        certifications: 'Certifications'
    };

    currentConfig.section_order.forEach((section, index) => {
        const item = document.createElement('div');
        item.className = 'section-order-item';
        item.draggable = true;
        item.dataset.section = section;

        const dragHandle = document.createElement('span');
        dragHandle.className = 'drag-handle';
        dragHandle.textContent = '☰';

        const label = document.createElement('span');
        label.textContent = sectionNames[section];

        const buttons = document.createElement('div');
        buttons.className = 'order-buttons';

        if (index > 0) {
            const upBtn = document.createElement('button');
            upBtn.textContent = '↑';
            upBtn.className = 'order-btn';
            upBtn.onclick = () => moveSectionUp(index);
            buttons.appendChild(upBtn);
        }

        if (index < currentConfig.section_order.length - 1) {
            const downBtn = document.createElement('button');
            downBtn.textContent = '↓';
            downBtn.className = 'order-btn';
            downBtn.onclick = () => moveSectionDown(index);
            buttons.appendChild(downBtn);
        }

        item.appendChild(dragHandle);
        item.appendChild(label);
        item.appendChild(buttons);

        // Drag events
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragover', handleDragOverOrder);
        item.addEventListener('drop', handleDropOrder);
        item.addEventListener('dragend', handleDragEnd);

        sectionOrderList.appendChild(item);
    });
}

let draggedItem = null;

function handleDragStart(e) {
    draggedItem = e.target;
    e.target.style.opacity = '0.5';
}

function handleDragOverOrder(e) {
    e.preventDefault();
    const target = e.target.closest('.section-order-item');
    if (target && target !== draggedItem) {
        target.style.borderTop = '2px solid #3498db';
    }
}

function handleDropOrder(e) {
    e.preventDefault();
    const target = e.target.closest('.section-order-item');

    if (target && target !== draggedItem) {
        const draggedIndex = Array.from(sectionOrderList.children).indexOf(draggedItem);
        const targetIndex = Array.from(sectionOrderList.children).indexOf(target);

        // Update config
        const [removed] = currentConfig.section_order.splice(draggedIndex, 1);
        currentConfig.section_order.splice(targetIndex, 0, removed);

        // Re-render
        populateSectionOrder();
    }

    target.style.borderTop = '';
}

function handleDragEnd(e) {
    e.target.style.opacity = '1';
    document.querySelectorAll('.section-order-item').forEach(item => {
        item.style.borderTop = '';
    });
}

function moveSectionUp(index) {
    if (index > 0) {
        const temp = currentConfig.section_order[index];
        currentConfig.section_order[index] = currentConfig.section_order[index - 1];
        currentConfig.section_order[index - 1] = temp;
        populateSectionOrder();
    }
}

function moveSectionDown(index) {
    if (index < currentConfig.section_order.length - 1) {
        const temp = currentConfig.section_order[index];
        currentConfig.section_order[index] = currentConfig.section_order[index + 1];
        currentConfig.section_order[index + 1] = temp;
        populateSectionOrder();
    }
}

// Populate experience items with checkboxes
function populateExperienceItems() {
    if (!experienceItemsList) return;

    experienceItemsList.innerHTML = '';

    if (!parsedData.positions || parsedData.positions.length === 0) {
        const section = document.getElementById('experience-items-section');
        if (section) section.style.display = 'none';
        return;
    }

    const section = document.getElementById('experience-items-section');
    if (section) section.style.display = 'block';

    parsedData.positions.forEach((position, index) => {
        const item = document.createElement('label');
        item.className = 'item-toggle';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = currentConfig.experience_visible.includes(index);
        checkbox.onchange = (e) => toggleExperienceItem(index, e.target.checked);

        const text = document.createElement('span');
        text.textContent = `${position.title || 'Sans titre'} - ${position.company || 'Entreprise inconnue'}`;

        item.appendChild(checkbox);
        item.appendChild(text);

        experienceItemsList.appendChild(item);
    });
}

function toggleExperienceItem(index, checked) {
    if (checked) {
        if (!currentConfig.experience_visible.includes(index)) {
            currentConfig.experience_visible.push(index);
            currentConfig.experience_visible.sort((a, b) => a - b);
        }
    } else {
        currentConfig.experience_visible = currentConfig.experience_visible.filter(i => i !== index);
    }
}

// Populate education items with checkboxes
function populateEducationItems() {
    if (!educationItemsList) return;

    educationItemsList.innerHTML = '';

    if (!parsedData.education || parsedData.education.length === 0) {
        const section = document.getElementById('education-items-section');
        if (section) section.style.display = 'none';
        return;
    }

    const section = document.getElementById('education-items-section');
    if (section) section.style.display = 'block';

    parsedData.education.forEach((edu, index) => {
        const item = document.createElement('label');
        item.className = 'item-toggle';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = currentConfig.education_visible.includes(index);
        checkbox.onchange = (e) => toggleEducationItem(index, e.target.checked);

        const text = document.createElement('span');
        const degree = edu.degree || 'Diplôme';
        const school = edu.school || 'École inconnue';
        text.textContent = `${degree} - ${school}`;

        item.appendChild(checkbox);
        item.appendChild(text);

        educationItemsList.appendChild(item);
    });
}

function toggleEducationItem(index, checked) {
    if (checked) {
        if (!currentConfig.education_visible.includes(index)) {
            currentConfig.education_visible.push(index);
            currentConfig.education_visible.sort((a, b) => a - b);
        }
    } else {
        currentConfig.education_visible = currentConfig.education_visible.filter(i => i !== index);
    }
}

// Profile Summary Editor
function populateProfileSummaryEditor() {
    const section = document.getElementById('profile-summary-section');
    const textarea = document.getElementById('profile-summary');

    if (!section || !textarea) return;

    if (!parsedData.profile || !parsedData.profile.summary) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';
    textarea.value = parsedData.profile.summary || '';

    textarea.addEventListener('input', (e) => {
        parsedData.profile.summary = e.target.value;
    });
}

// Delete Experience
function deleteExperience(index) {
    parsedData.positions.splice(index, 1);

    // Update config visibility if needed
    if (currentConfig.experience_visible) {
        currentConfig.experience_visible = currentConfig.experience_visible
            .filter(i => i !== index)
            .map(i => i > index ? i - 1 : i);
    }

    // Re-render
    populateExperienceEditor();
    populateExperienceItems();
}

// Add Experience
function addNewExperience() {
    const newExperience = {
        title: '',
        company: '',
        description: '',
        started_on: '',
        finished_on: ''
    };

    parsedData.positions.push(newExperience);

    // Update config visibility
    if (currentConfig.experience_visible) {
        currentConfig.experience_visible.push(parsedData.positions.length - 1);
    }

    // Re-render
    populateExperienceEditor();
    populateExperienceItems();

    // Auto-expand the new item
    setTimeout(() => {
        const items = document.querySelectorAll('#experience-editor .editor-item');
        const lastItem = items[items.length - 1];
        if (lastItem) {
            const toggleBtn = lastItem.querySelector('.editor-toggle-btn');
            if (toggleBtn) {
                toggleBtn.click();
            }
        }
    }, 100);
}

// Experience Editor
function populateExperienceEditor() {
    const section = document.getElementById('experience-editor-section');
    const editorContainer = document.getElementById('experience-editor');

    if (!section || !editorContainer) return;

    if (!parsedData.positions || parsedData.positions.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';
    editorContainer.innerHTML = '';

    // Add button
    const addBtn = document.createElement('button');
    addBtn.className = 'add-item-btn';
    addBtn.innerHTML = '➕ Ajouter une expérience';
    addBtn.onclick = addNewExperience;
    editorContainer.appendChild(addBtn);

    parsedData.positions.forEach((position, index) => {
        const item = document.createElement('div');
        item.className = 'editor-item';

        const header = document.createElement('div');
        header.className = 'editor-item-header';

        const title = document.createElement('span');
        title.className = 'editor-item-title';
        title.textContent = `${position.title || 'Sans titre'} - ${position.company || 'Entreprise'}`;

        const headerActions = document.createElement('div');
        headerActions.className = 'editor-header-actions';

        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'editor-toggle-btn';
        toggleBtn.textContent = 'Modifier';

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'editor-delete-btn';
        deleteBtn.textContent = '🗑️ Supprimer';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            if (confirm(`Voulez-vous vraiment supprimer cette expérience : "${position.title || 'Sans titre'}" ?`)) {
                deleteExperience(index);
            }
        };

        headerActions.appendChild(toggleBtn);
        headerActions.appendChild(deleteBtn);

        header.appendChild(title);
        header.appendChild(headerActions);

        const fields = document.createElement('div');
        fields.className = 'editor-fields';
        fields.style.display = 'none';

        // Title and Company
        const row1 = document.createElement('div');
        row1.className = 'editor-row';

        const titleGroup = document.createElement('div');
        titleGroup.className = 'form-group';
        const titleLabel = document.createElement('label');
        titleLabel.textContent = 'Titre du poste';
        const titleInput = document.createElement('input');
        titleInput.type = 'text';
        titleInput.value = position.title || '';
        titleInput.addEventListener('input', (e) => {
            parsedData.positions[index].title = e.target.value;
            title.textContent = `${e.target.value} - ${parsedData.positions[index].company || 'Entreprise'}`;
        });
        titleGroup.appendChild(titleLabel);
        titleGroup.appendChild(titleInput);

        const companyGroup = document.createElement('div');
        companyGroup.className = 'form-group';
        const companyLabel = document.createElement('label');
        companyLabel.textContent = 'Entreprise';
        const companyInput = document.createElement('input');
        companyInput.type = 'text';
        companyInput.value = position.company || '';
        companyInput.addEventListener('input', (e) => {
            parsedData.positions[index].company = e.target.value;
            title.textContent = `${parsedData.positions[index].title || 'Sans titre'} - ${e.target.value}`;
        });
        companyGroup.appendChild(companyLabel);
        companyGroup.appendChild(companyInput);

        row1.appendChild(titleGroup);
        row1.appendChild(companyGroup);

        // Dates
        const row2 = document.createElement('div');
        row2.className = 'editor-row';

        const startGroup = document.createElement('div');
        startGroup.className = 'form-group';
        const startLabel = document.createElement('label');
        startLabel.textContent = 'Date de début';
        const startInput = document.createElement('input');
        startInput.type = 'text';
        startInput.value = position.started_on || '';
        startInput.placeholder = 'Ex: Jan 2020';
        startInput.addEventListener('input', (e) => {
            parsedData.positions[index].started_on = e.target.value;
        });
        startGroup.appendChild(startLabel);
        startGroup.appendChild(startInput);

        const endGroup = document.createElement('div');
        endGroup.className = 'form-group';
        const endLabel = document.createElement('label');
        endLabel.textContent = 'Date de fin';
        const endInput = document.createElement('input');
        endInput.type = 'text';
        endInput.value = position.finished_on || '';
        endInput.placeholder = 'Ex: Déc 2022 ou Présent';
        endInput.addEventListener('input', (e) => {
            parsedData.positions[index].finished_on = e.target.value;
        });
        endGroup.appendChild(endLabel);
        endGroup.appendChild(endInput);

        row2.appendChild(startGroup);
        row2.appendChild(endGroup);

        // Description
        const descGroup = document.createElement('div');
        descGroup.className = 'form-group';
        const descLabel = document.createElement('label');
        descLabel.textContent = 'Description';
        const descTextarea = document.createElement('textarea');
        descTextarea.rows = 4;
        descTextarea.value = position.description || '';
        descTextarea.addEventListener('input', (e) => {
            parsedData.positions[index].description = e.target.value;
        });
        descGroup.appendChild(descLabel);
        descGroup.appendChild(descTextarea);

        fields.appendChild(row1);
        fields.appendChild(row2);
        fields.appendChild(descGroup);

        toggleBtn.addEventListener('click', () => {
            const isHidden = fields.style.display === 'none';
            fields.style.display = isHidden ? 'flex' : 'none';
            toggleBtn.textContent = isHidden ? 'Masquer' : 'Modifier';
        });

        item.appendChild(header);
        item.appendChild(fields);
        editorContainer.appendChild(item);
    });
}

// Delete Education
function deleteEducation(index) {
    parsedData.education.splice(index, 1);

    // Update config visibility if needed
    if (currentConfig.education_visible) {
        currentConfig.education_visible = currentConfig.education_visible
            .filter(i => i !== index)
            .map(i => i > index ? i - 1 : i);
    }

    // Re-render
    populateEducationEditor();
    populateEducationItems();
}

// Add Education
function addNewEducation() {
    const newEducation = {
        school: '',
        degree: '',
        field_of_study: '',
        start_date: '',
        end_date: ''
    };

    parsedData.education.push(newEducation);

    // Update config visibility
    if (currentConfig.education_visible) {
        currentConfig.education_visible.push(parsedData.education.length - 1);
    }

    // Re-render
    populateEducationEditor();
    populateEducationItems();

    // Auto-expand the new item
    setTimeout(() => {
        const items = document.querySelectorAll('#education-editor .editor-item');
        const lastItem = items[items.length - 1];
        if (lastItem) {
            const toggleBtn = lastItem.querySelector('.editor-toggle-btn');
            if (toggleBtn) {
                toggleBtn.click();
            }
        }
    }, 100);
}

// Education Editor
function populateEducationEditor() {
    const section = document.getElementById('education-editor-section');
    const editorContainer = document.getElementById('education-editor');

    if (!section || !editorContainer) return;

    if (!parsedData.education || parsedData.education.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';
    editorContainer.innerHTML = '';

    // Add button
    const addBtn = document.createElement('button');
    addBtn.className = 'add-item-btn';
    addBtn.innerHTML = '➕ Ajouter une formation';
    addBtn.onclick = addNewEducation;
    editorContainer.appendChild(addBtn);

    parsedData.education.forEach((edu, index) => {
        const item = document.createElement('div');
        item.className = 'editor-item';

        const header = document.createElement('div');
        header.className = 'editor-item-header';

        const title = document.createElement('span');
        title.className = 'editor-item-title';
        title.textContent = `${edu.degree || 'Diplôme'} - ${edu.school || 'École'}`;

        const headerActions = document.createElement('div');
        headerActions.className = 'editor-header-actions';

        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'editor-toggle-btn';
        toggleBtn.textContent = 'Modifier';

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'editor-delete-btn';
        deleteBtn.textContent = '🗑️ Supprimer';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            if (confirm(`Voulez-vous vraiment supprimer cette formation : "${edu.degree || 'Diplôme'}" ?`)) {
                deleteEducation(index);
            }
        };

        headerActions.appendChild(toggleBtn);
        headerActions.appendChild(deleteBtn);

        header.appendChild(title);
        header.appendChild(headerActions);

        const fields = document.createElement('div');
        fields.className = 'editor-fields';
        fields.style.display = 'none';

        // Degree and School
        const row1 = document.createElement('div');
        row1.className = 'editor-row';

        const degreeGroup = document.createElement('div');
        degreeGroup.className = 'form-group';
        const degreeLabel = document.createElement('label');
        degreeLabel.textContent = 'Diplôme';
        const degreeInput = document.createElement('input');
        degreeInput.type = 'text';
        degreeInput.value = edu.degree || '';
        degreeInput.addEventListener('input', (e) => {
            parsedData.education[index].degree = e.target.value;
            title.textContent = `${e.target.value} - ${parsedData.education[index].school || 'École'}`;
        });
        degreeGroup.appendChild(degreeLabel);
        degreeGroup.appendChild(degreeInput);

        const schoolGroup = document.createElement('div');
        schoolGroup.className = 'form-group';
        const schoolLabel = document.createElement('label');
        schoolLabel.textContent = 'École / Université';
        const schoolInput = document.createElement('input');
        schoolInput.type = 'text';
        schoolInput.value = edu.school || '';
        schoolInput.addEventListener('input', (e) => {
            parsedData.education[index].school = e.target.value;
            title.textContent = `${parsedData.education[index].degree || 'Diplôme'} - ${e.target.value}`;
        });
        schoolGroup.appendChild(schoolLabel);
        schoolGroup.appendChild(schoolInput);

        row1.appendChild(degreeGroup);
        row1.appendChild(schoolGroup);

        // Field of study
        const fieldGroup = document.createElement('div');
        fieldGroup.className = 'form-group';
        const fieldLabel = document.createElement('label');
        fieldLabel.textContent = 'Domaine d\'études';
        const fieldInput = document.createElement('input');
        fieldInput.type = 'text';
        fieldInput.value = edu.field_of_study || '';
        fieldInput.addEventListener('input', (e) => {
            parsedData.education[index].field_of_study = e.target.value;
        });
        fieldGroup.appendChild(fieldLabel);
        fieldGroup.appendChild(fieldInput);

        // Dates
        const row2 = document.createElement('div');
        row2.className = 'editor-row';

        const startGroup = document.createElement('div');
        startGroup.className = 'form-group';
        const startLabel = document.createElement('label');
        startLabel.textContent = 'Date de début';
        const startInput = document.createElement('input');
        startInput.type = 'text';
        startInput.value = edu.start_date || '';
        startInput.placeholder = 'Ex: 2015';
        startInput.addEventListener('input', (e) => {
            parsedData.education[index].start_date = e.target.value;
        });
        startGroup.appendChild(startLabel);
        startGroup.appendChild(startInput);

        const endGroup = document.createElement('div');
        endGroup.className = 'form-group';
        const endLabel = document.createElement('label');
        endLabel.textContent = 'Date de fin';
        const endInput = document.createElement('input');
        endInput.type = 'text';
        endInput.value = edu.end_date || '';
        endInput.placeholder = 'Ex: 2019';
        endInput.addEventListener('input', (e) => {
            parsedData.education[index].end_date = e.target.value;
        });
        endGroup.appendChild(endLabel);
        endGroup.appendChild(endInput);

        row2.appendChild(startGroup);
        row2.appendChild(endGroup);

        fields.appendChild(row1);
        fields.appendChild(fieldGroup);
        fields.appendChild(row2);

        toggleBtn.addEventListener('click', () => {
            const isHidden = fields.style.display === 'none';
            fields.style.display = isHidden ? 'flex' : 'none';
            toggleBtn.textContent = isHidden ? 'Masquer' : 'Modifier';
        });

        item.appendChild(header);
        item.appendChild(fields);
        editorContainer.appendChild(item);
    });
}

// Delete Skill
function deleteSkill(skill) {
    // Remove from main skills list
    const skillIndex = parsedData.skills.indexOf(skill);
    if (skillIndex > -1) {
        parsedData.skills.splice(skillIndex, 1);
    }

    // Remove from selected skills
    if (currentConfig.skills_selected) {
        currentConfig.skills_selected = currentConfig.skills_selected.filter(s => s !== skill);
    }

    // Re-render
    populateSkillsSelector();
}

// Add Skill
function addNewSkill() {
    const skillName = prompt('Entrez le nom de la compétence à ajouter :');

    if (skillName && skillName.trim()) {
        const trimmedSkill = skillName.trim();

        // Check if skill already exists
        if (parsedData.skills.includes(trimmedSkill)) {
            alert('Cette compétence existe déjà !');
            return;
        }

        // Add to skills list
        parsedData.skills.push(trimmedSkill);

        // Add to selected skills
        if (currentConfig.skills_selected) {
            currentConfig.skills_selected.push(trimmedSkill);
        }

        // Re-render
        populateSkillsSelector();
    }
}

// Skills Selector
function populateSkillsSelector() {
    const section = document.getElementById('skills-selector-section');
    const selectorContainer = document.getElementById('skills-selector');
    const searchInput = document.getElementById('skills-search');

    if (!section || !selectorContainer) return;

    if (!parsedData.skills || parsedData.skills.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';

    // Initialize skills_selected with all skills if not set
    if (!currentConfig.skills_selected) {
        currentConfig.skills_selected = [...parsedData.skills];
    }

    function renderSkills(filter = '') {
        selectorContainer.innerHTML = '';

        // Add button
        const addBtn = document.createElement('button');
        addBtn.className = 'add-item-btn';
        addBtn.innerHTML = '➕ Ajouter une compétence';
        addBtn.onclick = addNewSkill;
        selectorContainer.appendChild(addBtn);

        const filteredSkills = parsedData.skills.filter(skill =>
            skill.toLowerCase().includes(filter.toLowerCase())
        );

        filteredSkills.forEach((skill, originalIndex) => {
            const wrapper = document.createElement('div');
            wrapper.className = 'skill-item-wrapper';
            wrapper.draggable = true;

            const dragHandle = document.createElement('span');
            dragHandle.className = 'drag-handle';
            dragHandle.textContent = '☰';

            const item = document.createElement('label');
            item.className = 'item-toggle';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = currentConfig.skills_selected.includes(skill);
            checkbox.onchange = (e) => {
                if (e.target.checked) {
                    if (!currentConfig.skills_selected.includes(skill)) {
                        currentConfig.skills_selected.push(skill);
                    }
                } else {
                    currentConfig.skills_selected = currentConfig.skills_selected.filter(s => s !== skill);
                }
            };

            const text = document.createElement('span');
            text.textContent = skill;

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'skill-delete-btn';
            deleteBtn.textContent = '🗑️';
            deleteBtn.title = 'Supprimer cette compétence';
            deleteBtn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (confirm(`Voulez-vous vraiment supprimer la compétence "${skill}" ?`)) {
                    deleteSkill(skill);
                }
            };

            item.appendChild(checkbox);
            item.appendChild(text);
            item.appendChild(deleteBtn);

            wrapper.appendChild(dragHandle);
            wrapper.appendChild(item);

            selectorContainer.appendChild(wrapper);
        });
    }

    renderSkills();

    searchInput.addEventListener('input', (e) => {
        renderSkills(e.target.value);
    });
}

// Delete Language
function deleteLanguage(index) {
    parsedData.languages.splice(index, 1);

    // Re-render
    populateLanguagesEditor();
}

// Add Language
function addNewLanguage() {
    const newLanguage = {
        name: '',
        proficiency: ''
    };

    parsedData.languages.push(newLanguage);

    // Re-render
    populateLanguagesEditor();

    // Focus on the first input of the new language
    setTimeout(() => {
        const items = document.querySelectorAll('#languages-editor .editor-item');
        const lastItem = items[items.length - 1];
        if (lastItem) {
            const firstInput = lastItem.querySelector('input');
            if (firstInput) {
                firstInput.focus();
            }
        }
    }, 100);
}

// Languages Editor
function populateLanguagesEditor() {
    const section = document.getElementById('languages-editor-section');
    const editorContainer = document.getElementById('languages-editor');

    if (!section || !editorContainer) return;

    if (!parsedData.languages || parsedData.languages.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';
    editorContainer.innerHTML = '';

    // Add button
    const addBtn = document.createElement('button');
    addBtn.className = 'add-item-btn';
    addBtn.innerHTML = '➕ Ajouter une langue';
    addBtn.onclick = addNewLanguage;
    editorContainer.appendChild(addBtn);

    parsedData.languages.forEach((lang, index) => {
        const item = document.createElement('div');
        item.className = 'editor-item';

        const itemHeader = document.createElement('div');
        itemHeader.className = 'editor-item-header-simple';

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'editor-delete-btn-small';
        deleteBtn.textContent = '🗑️';
        deleteBtn.title = 'Supprimer cette langue';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            if (confirm(`Voulez-vous vraiment supprimer la langue "${lang.name || 'cette langue'}" ?`)) {
                deleteLanguage(index);
            }
        };

        itemHeader.appendChild(deleteBtn);
        item.appendChild(itemHeader);

        const row = document.createElement('div');
        row.className = 'editor-row';

        const nameGroup = document.createElement('div');
        nameGroup.className = 'form-group';
        const nameLabel = document.createElement('label');
        nameLabel.textContent = 'Langue';
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.value = lang.name || '';
        nameInput.addEventListener('input', (e) => {
            parsedData.languages[index].name = e.target.value;
        });
        nameGroup.appendChild(nameLabel);
        nameGroup.appendChild(nameInput);

        const proficiencyGroup = document.createElement('div');
        proficiencyGroup.className = 'form-group';
        const proficiencyLabel = document.createElement('label');
        proficiencyLabel.textContent = 'Niveau';
        const proficiencyInput = document.createElement('input');
        proficiencyInput.type = 'text';
        proficiencyInput.value = lang.proficiency || '';
        proficiencyInput.placeholder = 'Ex: Courant, Natif, B2...';
        proficiencyInput.addEventListener('input', (e) => {
            parsedData.languages[index].proficiency = e.target.value;
        });
        proficiencyGroup.appendChild(proficiencyLabel);
        proficiencyGroup.appendChild(proficiencyInput);

        row.appendChild(nameGroup);
        row.appendChild(proficiencyGroup);

        item.appendChild(row);
        editorContainer.appendChild(item);
    });
}

// Delete Certification
function deleteCertification(index) {
    parsedData.certifications.splice(index, 1);

    // Re-render
    populateCertificationsEditor();
}

// Add Certification
function addNewCertification() {
    const newCertification = {
        name: '',
        authority: '',
        start_date: '',
        end_date: '',
        url: ''
    };

    parsedData.certifications.push(newCertification);

    // Re-render
    populateCertificationsEditor();

    // Auto-expand the new item
    setTimeout(() => {
        const items = document.querySelectorAll('#certifications-editor .editor-item');
        const lastItem = items[items.length - 1];
        if (lastItem) {
            const toggleBtn = lastItem.querySelector('.editor-toggle-btn');
            if (toggleBtn) {
                toggleBtn.click();
            }
        }
    }, 100);
}

// Certifications Editor
function populateCertificationsEditor() {
    const section = document.getElementById('certifications-editor-section');
    const editorContainer = document.getElementById('certifications-editor');

    if (!section || !editorContainer) return;

    if (!parsedData.certifications || parsedData.certifications.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';
    editorContainer.innerHTML = '';

    // Add button
    const addBtn = document.createElement('button');
    addBtn.className = 'add-item-btn';
    addBtn.innerHTML = '➕ Ajouter une certification';
    addBtn.onclick = addNewCertification;
    editorContainer.appendChild(addBtn);

    parsedData.certifications.forEach((cert, index) => {
        const item = document.createElement('div');
        item.className = 'editor-item';

        const header = document.createElement('div');
        header.className = 'editor-item-header';

        const title = document.createElement('span');
        title.className = 'editor-item-title';
        title.textContent = cert.name || 'Certification';

        const headerActions = document.createElement('div');
        headerActions.className = 'editor-header-actions';

        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'editor-toggle-btn';
        toggleBtn.textContent = 'Modifier';

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'editor-delete-btn';
        deleteBtn.textContent = '🗑️ Supprimer';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            if (confirm(`Voulez-vous vraiment supprimer la certification "${cert.name || 'cette certification'}" ?`)) {
                deleteCertification(index);
            }
        };

        headerActions.appendChild(toggleBtn);
        headerActions.appendChild(deleteBtn);

        header.appendChild(title);
        header.appendChild(headerActions);

        const fields = document.createElement('div');
        fields.className = 'editor-fields';
        fields.style.display = 'none';

        // Name
        const nameGroup = document.createElement('div');
        nameGroup.className = 'form-group';
        const nameLabel = document.createElement('label');
        nameLabel.textContent = 'Nom de la certification';
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.value = cert.name || '';
        nameInput.addEventListener('input', (e) => {
            parsedData.certifications[index].name = e.target.value;
            title.textContent = e.target.value || 'Certification';
        });
        nameGroup.appendChild(nameLabel);
        nameGroup.appendChild(nameInput);

        // Authority
        const authorityGroup = document.createElement('div');
        authorityGroup.className = 'form-group';
        const authorityLabel = document.createElement('label');
        authorityLabel.textContent = 'Organisme';
        const authorityInput = document.createElement('input');
        authorityInput.type = 'text';
        authorityInput.value = cert.authority || '';
        authorityInput.addEventListener('input', (e) => {
            parsedData.certifications[index].authority = e.target.value;
        });
        authorityGroup.appendChild(authorityLabel);
        authorityGroup.appendChild(authorityInput);

        // Dates
        const row = document.createElement('div');
        row.className = 'editor-row';

        const startGroup = document.createElement('div');
        startGroup.className = 'form-group';
        const startLabel = document.createElement('label');
        startLabel.textContent = 'Date d\'obtention';
        const startInput = document.createElement('input');
        startInput.type = 'text';
        startInput.value = cert.start_date || '';
        startInput.placeholder = 'Ex: Jan 2021';
        startInput.addEventListener('input', (e) => {
            parsedData.certifications[index].start_date = e.target.value;
        });
        startGroup.appendChild(startLabel);
        startGroup.appendChild(startInput);

        const endGroup = document.createElement('div');
        endGroup.className = 'form-group';
        const endLabel = document.createElement('label');
        endLabel.textContent = 'Date d\'expiration';
        const endInput = document.createElement('input');
        endInput.type = 'text';
        endInput.value = cert.end_date || '';
        endInput.placeholder = 'Ex: Jan 2024 (optionnel)';
        endInput.addEventListener('input', (e) => {
            parsedData.certifications[index].end_date = e.target.value;
        });
        endGroup.appendChild(endLabel);
        endGroup.appendChild(endInput);

        row.appendChild(startGroup);
        row.appendChild(endGroup);

        // URL
        const urlGroup = document.createElement('div');
        urlGroup.className = 'form-group';
        const urlLabel = document.createElement('label');
        urlLabel.textContent = 'URL (optionnel)';
        const urlInput = document.createElement('input');
        urlInput.type = 'url';
        urlInput.value = cert.url || '';
        urlInput.placeholder = 'https://...';
        urlInput.addEventListener('input', (e) => {
            parsedData.certifications[index].url = e.target.value;
        });
        urlGroup.appendChild(urlLabel);
        urlGroup.appendChild(urlInput);

        fields.appendChild(nameGroup);
        fields.appendChild(authorityGroup);
        fields.appendChild(row);
        fields.appendChild(urlGroup);

        toggleBtn.addEventListener('click', () => {
            const isHidden = fields.style.display === 'none';
            fields.style.display = isHidden ? 'flex' : 'none';
            toggleBtn.textContent = isHidden ? 'Masquer' : 'Modifier';
        });

        item.appendChild(header);
        item.appendChild(fields);
        editorContainer.appendChild(item);
    });
}

// Generate PDF preview
async function generatePreview() {
    previewLoading.style.display = 'flex';

    try {
        // Prepare data with photo if available
        const dataToSend = { ...parsedData };

        // Update contact information from input fields
        if (!dataToSend.profile) {
            dataToSend.profile = {};
        }
        if (contactEmailInput && contactEmailInput.value) {
            dataToSend.profile.email = contactEmailInput.value;
        }
        if (contactPhoneInput && contactPhoneInput.value) {
            dataToSend.profile.phone = contactPhoneInput.value;
        }
        if (contactAddressInput && contactAddressInput.value) {
            dataToSend.profile.address = contactAddressInput.value;
        }

        // Update skills if specific skills are selected
        if (currentConfig.skills_selected && currentConfig.skills_selected.length > 0) {
            dataToSend.skills = currentConfig.skills_selected;
        }

        if (photoFile) {
            const photoBase64 = await fileToBase64(photoFile);
            dataToSend.photo = photoBase64;
        }

        // Add configuration
        dataToSend.config = currentConfig;

        // Generate PDF
        const pdfResponse = await fetch(`${API_URL}/api/generate-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataToSend)
        });

        if (!pdfResponse.ok) {
            throw new Error('Erreur lors de la génération du PDF');
        }

        // Get the PDF blob
        currentPdfBlob = await pdfResponse.blob();

        // Display in iframe
        const url = window.URL.createObjectURL(currentPdfBlob);
        pdfPreviewFrame.src = url;

    } catch (error) {
        showError('Erreur lors de la génération de l\'aperçu: ' + error.message);
    } finally {
        previewLoading.style.display = 'none';
    }
}

// Refresh preview
async function refreshPreview() {
    await generatePreview();
}

// Download final PDF
function downloadFinalPDF() {
    if (!currentPdfBlob) {
        showError('Aucun PDF à télécharger');
        return;
    }

    const url = window.URL.createObjectURL(currentPdfBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cv.pdf';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    // Show success message
    successSection.style.display = 'block';
    successSection.scrollIntoView({ behavior: 'smooth' });
}

// Photo Upload Handlers
function handlePhotoUpload(e) {
    const file = e.target.files[0];

    if (!file) return;

    // Validate file type
    if (!file.type.match('image/(jpeg|jpg|png)')) {
        showError('Format non supporté. Utilisez JPG ou PNG.');
        return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
        showError('La photo est trop grande. Maximum 5MB.');
        return;
    }

    photoFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        photoPreviewImg.src = e.target.result;
        photoPreviewImg.style.display = 'block';
        photoPreview.querySelector('svg').style.display = 'none';
        removePhotoBtn.style.display = 'inline-block';
    };
    reader.readAsDataURL(file);

    hideError();
}

function removePhoto() {
    photoFile = null;
    photoInput.value = '';
    photoPreviewImg.style.display = 'none';
    photoPreviewImg.src = '';
    photoPreview.querySelector('svg').style.display = 'block';
    removePhotoBtn.style.display = 'none';
}

// Reset Application
function resetApp() {
    selectedFiles = [];
    parsedData = null;
    currentPdfBlob = null;
    fileList.innerHTML = '';
    fileInput.value = '';
    successSection.style.display = 'none';
    removePhoto();
    hideError();

    // Reset stepper to step 1
    goToStep(1);

    // Reset config
    currentConfig = {
        sections: {
            summary: true,
            experience: true,
            education: true,
            skills: true,
            languages: true,
            certifications: true
        },
        section_order: ['summary', 'experience', 'education', 'skills', 'languages', 'certifications'],
        experience_visible: null,
        education_visible: null,
        skills_selected: null,
        template: 'modern',
        colors: {
            primary: '#3498db',
            text: '#2c3e50',
            secondary_text: '#7f8c8d'
        }
    };

    // Reset template and colors UI
    document.querySelector('input[name="template"][value="modern"]').checked = true;
    applyTemplateColors('modern');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Helper function to convert file to base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// UI Helper Functions
function showLoading() {
    loading.style.display = 'block';
}

function hideLoading() {
    loading.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = '❌ ' + message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showSuccess(message) {
    errorMessage.textContent = '✅ ' + message;
    errorMessage.style.display = 'block';
    errorMessage.style.background = '#d4edda';
    errorMessage.style.color = '#155724';
    errorMessage.style.borderLeftColor = '#28a745';

    setTimeout(() => {
        hideError();
        errorMessage.style.background = '';
        errorMessage.style.color = '';
        errorMessage.style.borderLeftColor = '';
    }, 5000);
}
