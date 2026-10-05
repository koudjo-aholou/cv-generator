/**
 * Languages business logic
 */

export const createLanguage = () => {
    return {
        name: '',
        proficiency: ''
    };
};

export const deleteLanguage = (languages, index) => {
    languages.splice(index, 1);
};

export const updateLanguage = (languages, index, field, value) => {
    if (languages[index]) {
        languages[index][field] = value;
    }
};
