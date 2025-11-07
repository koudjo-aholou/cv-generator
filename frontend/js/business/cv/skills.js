/**
 * Skills business logic
 */

export const addSkill = (skills, skillName, selectedSkills) => {
    const trimmedSkill = skillName.trim();

    // Check if skill already exists
    if (skills.includes(trimmedSkill)) {
        return { success: false, message: 'Cette compétence existe déjà !' };
    }

    skills.push(trimmedSkill);

    if (selectedSkills) {
        selectedSkills.push(trimmedSkill);
    }

    return { success: true, skill: trimmedSkill };
};

export const deleteSkill = (skills, skillName, selectedSkills) => {
    const skillIndex = skills.indexOf(skillName);
    if (skillIndex > -1) {
        skills.splice(skillIndex, 1);
    }

    if (selectedSkills) {
        return selectedSkills.filter(s => s !== skillName);
    }
    return null;
};

export const toggleSkillSelection = (skill, checked, selectedSkills) => {
    if (checked) {
        if (!selectedSkills.includes(skill)) {
            selectedSkills.push(skill);
        }
    } else {
        return selectedSkills.filter(s => s !== skill);
    }
    return selectedSkills;
};
