/**
 * CV state management service
 */

import { store } from '../../core/state/store.js';
import { DEFAULT_CONFIG } from '../../config/defaults.js';
import { deepClone } from '../../core/utils/helpers.js';

class CvStateService {
    constructor() {
        this.initializeState();
    }

    initializeState() {
        store.setState({
            selectedFiles: [],
            parsedData: null,
            photoFile: null,
            currentConfig: deepClone(DEFAULT_CONFIG),
            currentPdfBlob: null,
            currentStep: 1,
            isProcessingStep: false
        });
    }

    // Files
    getFiles() {
        return store.get('selectedFiles');
    }

    setFiles(files) {
        store.set('selectedFiles', files);
    }

    observeFiles(callback) {
        store.observe('selectedFiles', callback);
        return () => store.unobserve('selectedFiles', callback);
    }

    addFile(file) {
        const files = this.getFiles();
        store.set('selectedFiles', [...files, file]);
    }

    removeFile(index) {
        const files = this.getFiles();
        files.splice(index, 1);
        store.set('selectedFiles', [...files]);
    }

    // Parsed data
    getParsedData() {
        return store.get('parsedData');
    }

    setParsedData(data) {
        store.set('parsedData', data);
    }

    // Photo
    getPhoto() {
        return store.get('photoFile');
    }

    setPhoto(file) {
        store.set('photoFile', file);
    }

    removePhoto() {
        store.set('photoFile', null);
    }

    // Config
    getConfig() {
        return store.get('currentConfig');
    }

    setConfig(config) {
        store.set('currentConfig', config);
    }

    updateConfig(updates) {
        const currentConfig = this.getConfig();
        store.set('currentConfig', { ...currentConfig, ...updates });
    }

    // PDF Blob
    getPdfBlob() {
        return store.get('currentPdfBlob');
    }

    setPdfBlob(blob) {
        store.set('currentPdfBlob', blob);
    }

    // Step
    getCurrentStep() {
        return store.get('currentStep');
    }

    setCurrentStep(step) {
        store.set('currentStep', step);
    }

    // Processing
    isProcessing() {
        return store.get('isProcessingStep');
    }

    setProcessing(isProcessing) {
        store.set('isProcessingStep', isProcessing);
    }

    // Reset
    reset() {
        this.initializeState();
    }
}

export const cvStateService = new CvStateService();
