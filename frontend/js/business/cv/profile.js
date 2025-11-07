/**
 * Profile business logic
 */

export const updateProfile = (profile, field, value) => {
    if (profile) {
        profile[field] = value;
    }
};

export const getProfileField = (profile, field, defaultValue = '') => {
    return profile && profile[field] ? profile[field] : defaultValue;
};
