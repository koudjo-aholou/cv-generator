// API Configuration
const API_URL = 'http://localhost:5000';

// State
let selectedFiles = [];
let parsedData = null;
let photoFile = null;

// DOM Elements
const dropZone = document.getElementById('dropZone');
const browseBtn = document.getElementById('browseBtn');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const photoSection = document.getElementById('photo-section');
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

    // Photo upload events
    uploadPhotoBtn.addEventListener('click', () => photoInput.click());
    photoInput.addEventListener('change', handlePhotoUpload);
    removePhotoBtn.addEventListener('click', removePhoto);
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

// Generate CV (Parse and Create PDF in one step)
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

        // Step 2: Prepare data with photo if available
        const dataToSend = { ...parsedData };

        if (photoFile) {
            const photoBase64 = await fileToBase64(photoFile);
            dataToSend.photo = photoBase64;
        }

        // Step 3: Generate PDF
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

        // Download the PDF
        const blob = await pdfResponse.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'cv.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        // Show success
        photoSection.style.display = 'none';
        successSection.style.display = 'block';
        successSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        showError('Erreur: ' + error.message);
    } finally {
        hideLoading();
    }
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
    fileList.innerHTML = '';
    fileInput.value = '';
    photoSection.style.display = 'none';
    successSection.style.display = 'none';
    removePhoto();
    hideError();

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
