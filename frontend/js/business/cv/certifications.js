/**
 * Certifications business logic
 */

export const createCertification = () => {
    return {
        name: '',
        authority: '',
        start_date: '',
        end_date: '',
        url: ''
    };
};

export const deleteCertification = (certifications, index) => {
    certifications.splice(index, 1);
};

export const updateCertification = (certifications, index, field, value) => {
    if (certifications[index]) {
        certifications[index][field] = value;
    }
};
