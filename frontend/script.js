// API Configuration
const API_URL = 'http://localhost:5000';

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
    education_visible: null    // null means all visible
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
    generateBtn.addEventListener('click', generateCV);
    resetBtn.addEventListener('click', resetApp);
    refreshPreviewBtn.addEventListener('click', refreshPreview);
    downloadFinalBtn.addEventListener('click', downloadFinalPDF);

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

// File Handling
function handleFiles(files) {
    if (files.length === 0) {
        showError('Veuillez sélectionner des fichiers CSV');
        return;
    }

    selectedFiles = files;
    displayFileList();
    photoSection.style.display = 'block';
    hideError();

    // Scroll to photo section
    photoSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
        photoSection.style.display = 'none';
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

        // Hide photo section and show preview section
        photoSection.style.display = 'none';
        previewSection.style.display = 'block';
        previewSection.scrollIntoView({ behavior: 'smooth' });

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

    // Populate experience items
    populateExperienceItems();

    // Populate education items
    populateEducationItems();
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
    experienceItemsList.innerHTML = '';

    if (!parsedData.positions || parsedData.positions.length === 0) {
        document.getElementById('experience-items-section').style.display = 'none';
        return;
    }

    document.getElementById('experience-items-section').style.display = 'block';

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
    educationItemsList.innerHTML = '';

    if (!parsedData.education || parsedData.education.length === 0) {
        document.getElementById('education-items-section').style.display = 'none';
        return;
    }

    document.getElementById('education-items-section').style.display = 'block';

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

    // Show success
    previewSection.style.display = 'none';
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
    photoSection.style.display = 'none';
    previewSection.style.display = 'none';
    successSection.style.display = 'none';
    removePhoto();
    hideError();

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
        education_visible: null
    };

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
