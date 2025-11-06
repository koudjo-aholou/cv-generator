// API Configuration
const API_URL = 'http://localhost:5000';

// State
let selectedFiles = [];
let parsedData = null;

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const parseBtn = document.getElementById('parseBtn');
const previewSection = document.getElementById('preview-section');
const dataPreview = document.getElementById('dataPreview');
const generateBtn = document.getElementById('generateBtn');
const resetBtn = document.getElementById('resetBtn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // Drop zone events
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFiles(Array.from(e.target.files));
    });

    // Button events
    parseBtn.addEventListener('click', parseLinkedInData);
    generateBtn.addEventListener('click', generatePDF);
    resetBtn.addEventListener('click', resetApp);
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
    parseBtn.style.display = 'block';
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
        parseBtn.style.display = 'none';
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

// Parse LinkedIn Data
async function parseLinkedInData() {
    if (selectedFiles.length === 0) {
        showError('Aucun fichier sélectionné');
        return;
    }

    showLoading();
    hideError();

    try {
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        const response = await fetch(`${API_URL}/api/parse-linkedin`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Erreur lors de l\'analyse des données');
        }

        parsedData = await response.json();
        displayPreview(parsedData);
        previewSection.style.display = 'block';

        // Scroll to preview
        previewSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        showError('Erreur lors de l\'analyse des fichiers: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Display Preview
function displayPreview(data) {
    let html = '';

    // Profile
    if (data.profile && data.profile.first_name) {
        html += `
            <div class="preview-section">
                <h3>👤 Profil</h3>
                <p><strong>Nom:</strong> ${data.profile.first_name} ${data.profile.last_name}</p>
                ${data.profile.headline ? `<p><strong>Titre:</strong> ${data.profile.headline}</p>` : ''}
                ${data.profile.email ? `<p><strong>Email:</strong> ${data.profile.email}</p>` : ''}
                ${data.profile.phone ? `<p><strong>Téléphone:</strong> ${data.profile.phone}</p>` : ''}
            </div>
        `;
    }

    // Positions
    if (data.positions && data.positions.length > 0) {
        html += `
            <div class="preview-section">
                <h3>💼 Expériences (${data.positions.length})</h3>
                ${data.positions.slice(0, 3).map(pos => `
                    <p><strong>${pos.title}</strong> chez ${pos.company}</p>
                `).join('')}
                ${data.positions.length > 3 ? `<p><em>... et ${data.positions.length - 3} autres</em></p>` : ''}
            </div>
        `;
    }

    // Education
    if (data.education && data.education.length > 0) {
        html += `
            <div class="preview-section">
                <h3>🎓 Formation (${data.education.length})</h3>
                ${data.education.slice(0, 2).map(edu => `
                    <p><strong>${edu.degree || 'Diplôme'}</strong> - ${edu.school}</p>
                `).join('')}
                ${data.education.length > 2 ? `<p><em>... et ${data.education.length - 2} autres</em></p>` : ''}
            </div>
        `;
    }

    // Skills
    if (data.skills && data.skills.length > 0) {
        html += `
            <div class="preview-section">
                <h3>🛠️ Compétences (${data.skills.length})</h3>
                <div>
                    ${data.skills.slice(0, 10).map(skill => `
                        <span class="skill-tag">${skill}</span>
                    `).join('')}
                    ${data.skills.length > 10 ? `<span class="skill-tag">+${data.skills.length - 10} autres</span>` : ''}
                </div>
            </div>
        `;
    }

    // Languages
    if (data.languages && data.languages.length > 0) {
        html += `
            <div class="preview-section">
                <h3>🌍 Langues (${data.languages.length})</h3>
                ${data.languages.map(lang => `
                    <p>${lang.name}${lang.proficiency ? ` - ${lang.proficiency}` : ''}</p>
                `).join('')}
            </div>
        `;
    }

    dataPreview.innerHTML = html || '<p>Aucune donnée trouvée dans les fichiers.</p>';
}

// Generate PDF
async function generatePDF() {
    if (!parsedData) {
        showError('Aucune donnée à générer');
        return;
    }

    showLoading();
    hideError();

    try {
        const response = await fetch(`${API_URL}/api/generate-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(parsedData)
        });

        if (!response.ok) {
            throw new Error('Erreur lors de la génération du PDF');
        }

        // Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'cv.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showSuccess('CV généré avec succès !');

    } catch (error) {
        showError('Erreur lors de la génération du PDF: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Reset Application
function resetApp() {
    selectedFiles = [];
    parsedData = null;
    fileList.innerHTML = '';
    fileInput.value = '';
    parseBtn.style.display = 'none';
    previewSection.style.display = 'none';
    hideError();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
