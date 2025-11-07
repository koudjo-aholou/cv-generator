/**
 * DOM element builder utilities
 */

export const createElement = (tag, options = {}) => {
    const element = document.createElement(tag);

    if (options.className) {
        element.className = options.className;
    }

    if (options.id) {
        element.id = options.id;
    }

    if (options.textContent) {
        element.textContent = options.textContent;
    }

    if (options.innerHTML) {
        element.innerHTML = options.innerHTML;
    }

    if (options.attributes) {
        Object.entries(options.attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
    }

    if (options.dataset) {
        Object.entries(options.dataset).forEach(([key, value]) => {
            element.dataset[key] = value;
        });
    }

    if (options.events) {
        Object.entries(options.events).forEach(([event, handler]) => {
            element.addEventListener(event, handler);
        });
    }

    if (options.children) {
        options.children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else if (child instanceof Node) {
                element.appendChild(child);
            }
        });
    }

    return element;
};

export const createButton = (text, className = '', onClick = null) => {
    return createElement('button', {
        className,
        textContent: text,
        events: onClick ? { click: onClick } : {}
    });
};

export const createInput = (type, value = '', placeholder = '') => {
    return createElement('input', {
        attributes: {
            type,
            value,
            placeholder
        }
    });
};

export const createLabel = (text, forId = null) => {
    const options = { textContent: text };
    if (forId) {
        options.attributes = { for: forId };
    }
    return createElement('label', options);
};

export const createDiv = (className = '', children = []) => {
    return createElement('div', {
        className,
        children
    });
};
