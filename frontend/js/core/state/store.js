/**
 * Centralized state management store
 */

import { eventBus } from '../dom/events.js';

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

        // Emit global state change event
        eventBus.emit('state:change', {
            oldState,
            newState: this.state,
            updates
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

    reset(initialState = {}) {
        this.state = { ...initialState };
        this.observers.clear();
        eventBus.emit('state:reset', this.state);
    }
}

export const store = new Store();
