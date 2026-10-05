/**
 * Education business logic
 */

export const createEducation = () => {
    return {
        school: '',
        degree: '',
        field_of_study: '',
        start_date: '',
        end_date: ''
    };
};

export const deleteEducation = (education, index, visibleIndices) => {
    education.splice(index, 1);

    // Update visibility indices
    if (visibleIndices) {
        return visibleIndices
            .filter(i => i !== index)
            .map(i => i > index ? i - 1 : i);
    }
    return null;
};

export const toggleEducationVisibility = (index, checked, visibleIndices) => {
    if (checked) {
        if (!visibleIndices.includes(index)) {
            visibleIndices.push(index);
            visibleIndices.sort((a, b) => a - b);
        }
    } else {
        return visibleIndices.filter(i => i !== index);
    }
    return visibleIndices;
};

export const updateEducation = (education, index, field, value) => {
    if (education[index]) {
        education[index][field] = value;
    }
};
