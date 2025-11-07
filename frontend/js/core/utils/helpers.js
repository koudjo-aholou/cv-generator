/**
 * Generic helper utilities
 */

export const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
};

export const debounce = (func, delay) => {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
};

export const throttle = (func, limit) => {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

export const deepClone = (obj) => {
    return JSON.parse(JSON.stringify(obj));
};

export const randomId = () => {
    return Math.random().toString(36).substring(2, 9);
};

export const sleep = (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms));
};
