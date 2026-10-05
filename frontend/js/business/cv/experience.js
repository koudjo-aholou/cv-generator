/**
 * Experience business logic
 */

export const createExperience = () => {
    return {
        title: '',
        company: '',
        description: '',
        started_on: '',
        finished_on: ''
    };
};

export const deleteExperience = (positions, index, visibleIndices) => {
    positions.splice(index, 1);

    // Update visibility indices
    if (visibleIndices) {
        return visibleIndices
            .filter(i => i !== index)
            .map(i => i > index ? i - 1 : i);
    }
    return null;
};

export const toggleExperienceVisibility = (index, checked, visibleIndices) => {
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

export const updateExperience = (positions, index, field, value) => {
    if (positions[index]) {
        positions[index][field] = value;
    }
};
