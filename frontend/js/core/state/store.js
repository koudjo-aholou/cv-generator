/**
 * Centralized state management store
 */

class Store {
    constructor(initialState = {}) {
        this.state = { ...initialState };
        this.observers = new Map();
    }

    getState() {
        return { ...this.state };
    }

    setState(updates) {
        const oldState = { ...this.state };
        this.state = { ...this.state, ...updates };

        // Notify observers
        Object.keys(updates).forEach(key => {
            if (this.observers.has(key)) {
                this.observers.get(key).forEach(callback => {
                    callback(this.state[key], oldState[key]);
                });
            }
        });
    }

    get(key) {
        return this.state[key];
    }

    set(key, value) {
        this.setState({ [key]: value });
    }

    observe(key, callback) {
        if (!this.observers.has(key)) {
            this.observers.set(key, []);
        }
        this.observers.get(key).push(callback);
    }

    unobserve(key, callback) {
        if (!this.observers.has(key)) return;

        const callbacks = this.observers.get(key);
        const index = callbacks.indexOf(callback);
        if (index > -1) {
            callbacks.splice(index, 1);
        }
    }
}

export const store = new Store();
