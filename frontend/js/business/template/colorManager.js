/**
 * Color management business logic
 */

export const updateColor = (colors, colorKey, value) => {
    if (colors) {
        colors[colorKey] = value;
    }
    return colors;
};

export const validateHexColor = (color) => {
    const regex = /^#[0-9A-F]{6}$/i;
    return regex.test(color);
};
