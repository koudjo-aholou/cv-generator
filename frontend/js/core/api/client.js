/**
 * Generic HTTP client
 */

export class ApiClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    async request(url, options = {}) {
        const fullUrl = url.startsWith('http') ? url : `${this.baseURL}${url}`;

        try {
            const response = await fetch(fullUrl, options);
            return response;
        } catch (error) {
            throw new Error(`Network error: ${error.message}`);
        }
    }

    async get(url, options = {}) {
        return this.request(url, {
            ...options,
            method: 'GET'
        });
    }

    async post(url, data, options = {}) {
        const isFormData = data instanceof FormData;

        return this.request(url, {
            ...options,
            method: 'POST',
            body: data,
            headers: {
                ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
                ...options.headers
            }
        });
    }

    async put(url, data, options = {}) {
        return this.request(url, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
    }

    async delete(url, options = {}) {
        return this.request(url, {
            ...options,
            method: 'DELETE'
        });
    }
}
