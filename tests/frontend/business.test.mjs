/**
 * Logique metier pure : aucun DOM requis.
 *
 * Ces 5 modules (~160 lignes) portent des decisions qui atteignent le PDF —
 * dataMapper construit la charge envoyee au backend, les validateurs
 * conditionnent le passage d'etape — et n'etaient couverts par rien.
 */
import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

const { prepareDataForPdf } = await import('../../frontend/js/business/workflow/dataMapper.js');
const { initializeConfigFromData } = await import('../../frontend/js/business/workflow/stepFlow.js');
const { validateCsvFiles, hasRequiredFiles } = await import('../../frontend/js/business/validation/fileValidator.js');
const { isValidEmail, isValidUrl, isEmpty, isValidFileSize, isValidFileType, isArrayOfStrings } =
    await import('../../frontend/js/core/utils/validators.js');
const { validateStep1, validateStep2 } = await import('../../frontend/js/business/validation/stepValidator.js');
const { notifications } = await import('../../frontend/js/core/ui/notifications.js');

const parsed = () => ({
    profile: { first_name: 'Jean', last_name: 'Dupont' },
    positions: [], education: [], skills: [], languages: [], certifications: []
});
const configVide = () => ({ sections: {}, skills_selected: null });

describe('dataMapper - champs de contact', () => {
    test('reporte les champs renseignes dans le profil', async () => {
        const out = await prepareDataForPdf(parsed(), configVide(), {
            headline: 'Dev', email: 'a@b.c', phone: '+41', address: 'Lausanne', summary: 'resume'
        }, null);

        assert.equal(out.profile.headline, 'Dev');
        assert.equal(out.profile.email, 'a@b.c');
        assert.equal(out.profile.phone, '+41');
        assert.equal(out.profile.address, 'Lausanne');
        assert.equal(out.profile.summary, 'resume');
    });

    test('ignore les champs vides plutot que d ecraser le profil parse', async () => {
        const data = parsed();
        data.profile.email = 'origine@exemple.fr';
        const out = await prepareDataForPdf(data, configVide(), { email: '' }, null);

        assert.equal(out.profile.email, 'origine@exemple.fr');
    });

    test('cree le profil s il est absent des donnees parsees', async () => {
        const data = parsed();
        delete data.profile;
        const out = await prepareDataForPdf(data, configVide(), { email: 'a@b.c' }, null);

        assert.equal(out.profile.email, 'a@b.c');
    });
});

describe('dataMapper - champs suisses', () => {
    // Le renommage camelCase -> snake_case est ce que le backend attend :
    // une faute ici fait disparaitre le champ du PDF, en silence.
    test('traduit les 4 champs vers les cles attendues par le backend', async () => {
        const out = await prepareDataForPdf(parsed(), configVide(), {
            birthDate: '1990-05-21', nationality: 'Suisse',
            civilStatus: 'Celibataire', permit: 'Permis C'
        }, null);

        assert.equal(out.profile.birth_date, '1990-05-21');
        assert.equal(out.profile.nationality, 'Suisse');
        assert.equal(out.profile.civil_status, 'Celibataire');
        assert.equal(out.profile.permit, 'Permis C');
    });

    test('n ajoute aucune cle suisse quand les champs sont vides', async () => {
        const out = await prepareDataForPdf(parsed(), configVide(), {
            birthDate: '', nationality: '', civilStatus: '', permit: ''
        }, null);

        for (const cle of ['birth_date', 'nationality', 'civil_status', 'permit']) {
            assert.ok(!(cle in out.profile), cle + ' n aurait pas du etre ajoute');
        }
    });
});

describe('dataMapper - competences et config', () => {
    test('remplace les competences quand une selection existe', async () => {
        const data = parsed();
        data.skills = ['A', 'B', 'C'];
        const out = await prepareDataForPdf(data, { sections: {}, skills_selected: ['B'] }, {}, null);

        assert.deepEqual(out.skills, ['B']);
    });

    test('conserve les competences parsees si la selection est vide', async () => {
        const data = parsed();
        data.skills = ['A', 'B'];
        const out = await prepareDataForPdf(data, { sections: {}, skills_selected: [] }, {}, null);

        assert.deepEqual(out.skills, ['A', 'B']);
    });

    test('joint la config a la charge envoyee', async () => {
        const config = { sections: {}, language: 'en', cv_type: 'swiss' };
        const out = await prepareDataForPdf(parsed(), config, {}, null);

        assert.equal(out.config.language, 'en');
        assert.equal(out.config.cv_type, 'swiss');
    });

    test('encode la photo en base64 quand elle est fournie', async () => {
        // FileReader n'existe pas dans Node : stub minimal. Le but est de
        // verifier le branchement, pas l implementation du navigateur.
        globalThis.FileReader = class {
            readAsDataURL() {
                this.result = 'data:image/png;base64,AAAA';
                this.onload();
            }
        };
        try {
            const out = await prepareDataForPdf(parsed(), configVide(), {}, { name: 'p.png' });
            assert.equal(out.photo, 'data:image/png;base64,AAAA');
        } finally {
            delete globalThis.FileReader;
        }
    });

    test('n ajoute pas de cle photo sans fichier', async () => {
        const out = await prepareDataForPdf(parsed(), configVide(), {}, null);
        assert.ok(!('photo' in out));
    });
});

describe('stepFlow - initialisation depuis les donnees', () => {
    const base = () => ({ sections: {}, experience_visible: null, education_visible: null });

    test('rend toutes les experiences visibles', () => {
        const out = initializeConfigFromData({ positions: [{}, {}, {}], education: [] }, base());

        assert.deepEqual(out.experience_visible, [0, 1, 2]);
    });

    test('active une section seulement si elle a des donnees', () => {
        const out = initializeConfigFromData({
            profile: { summary: 'x' }, positions: [{}], education: [],
            skills: ['A'], languages: [], certifications: []
        }, base());

        assert.equal(out.sections.summary, true);
        assert.equal(out.sections.experience, true);
        assert.equal(out.sections.skills, true);
        assert.equal(out.sections.education, false);
        assert.equal(out.sections.languages, false);
        assert.equal(out.sections.certifications, false);
    });

    test('desactive tout sur des donnees vides, sans lever', () => {
        const out = initializeConfigFromData({}, base());

        for (const s of ['summary', 'experience', 'education', 'skills', 'languages', 'certifications']) {
            assert.equal(out.sections[s], false, s + ' aurait du etre desactivee');
        }
    });

    test('un profil sans resume desactive la section a propos', () => {
        const out = initializeConfigFromData({ profile: { first_name: 'A' } }, base());
        assert.equal(out.sections.summary, false);
    });
});

describe('fileValidator', () => {
    const f = (name) => ({ name });

    test('ne garde que les .csv', () => {
        const gardes = validateCsvFiles([f('a.csv'), f('b.txt'), f('c.CSV'), f('d.csv.exe')]);
        assert.deepEqual(gardes.map(x => x.name), ['a.csv']);
    });

    test('rejette une extension en majuscules', () => {
        // Comportement actuel : endsWith('.csv') est sensible a la casse.
        assert.equal(validateCsvFiles([f('PROFILE.CSV')]).length, 0);
    });

    test('detecte les fichiers requis presents', () => {
        assert.ok(hasRequiredFiles([f('A.csv'), f('B.csv')], ['A.csv', 'B.csv']));
    });

    test('detecte un fichier requis manquant', () => {
        assert.ok(!hasRequiredFiles([f('A.csv')], ['A.csv', 'B.csv']));
    });

    test('une liste requise vide est toujours satisfaite', () => {
        assert.ok(hasRequiredFiles([], []));
    });
});

describe('validators', () => {
    test('isValidEmail accepte les adresses usuelles', () => {
        for (const ok of ['a@b.c', 'jean.dupont@exemple.fr', 'x+y@z.co.uk']) {
            assert.ok(isValidEmail(ok), ok);
        }
    });

    test('isValidEmail rejette les malformees', () => {
        for (const ko of ['', 'a@b', 'a b@c.fr', '@b.fr', 'a@']) {
            assert.ok(!isValidEmail(ko), ko);
        }
    });

    test('isValidUrl distingue URL et texte', () => {
        assert.ok(isValidUrl('https://exemple.fr'));
        assert.ok(!isValidUrl('pas une url'));
        assert.ok(!isValidUrl(''));
    });

    test('isEmpty couvre tous les types', () => {
        for (const vide of [null, undefined, '', '   ', [], {}]) {
            assert.ok(isEmpty(vide), JSON.stringify(vide));
        }
        for (const plein of ['x', [1], { a: 1 }, 0, false]) {
            assert.ok(!isEmpty(plein), JSON.stringify(plein));
        }
    });

    test('isValidFileSize borne inclusive', () => {
        assert.ok(isValidFileSize({ size: 100 }, 100));
        assert.ok(!isValidFileSize({ size: 101 }, 100));
    });

    test('isValidFileType filtre sur le type MIME', () => {
        assert.ok(isValidFileType({ type: 'image/png' }, ['image/png', 'image/jpeg']));
        assert.ok(!isValidFileType({ type: 'application/pdf' }, ['image/png']));
    });

    test('isArrayOfStrings', () => {
        assert.ok(isArrayOfStrings(['a', 'b']));
        assert.ok(isArrayOfStrings([]));
        assert.ok(!isArrayOfStrings(['a', 1]));
        assert.ok(!isArrayOfStrings('abc'));
    });
});

describe('stepValidator', () => {
    const f = (name) => ({ name });
    const REQUIS = ['Profile.csv', 'Positions.csv', 'Education.csv'];

    test('accepte les 3 fichiers requis', () => {
        assert.ok(validateStep1(REQUIS.map(f)));
    });

    test('accepte des fichiers optionnels en plus', () => {
        assert.ok(validateStep1([...REQUIS, 'Skills.csv', 'Languages.csv'].map(f)));
    });

    test('refuse quand un requis manque', () => {
        assert.ok(!validateStep1([f('Profile.csv'), f('Positions.csv')]));
    });

    test('refuse une liste vide', () => {
        assert.ok(!validateStep1([]));
    });

    test('nomme les fichiers manquants a l utilisateur', () => {
        // Sans DOM, showError est un no-op silencieux : on injecte une cible
        // minimale pour verifier que le message indique QUOI manque, et pas
        // seulement que l etape est bloquee.
        notifications.errorElement = { textContent: '', style: {} };
        try {
            validateStep1([f('Profile.csv')]);
            assert.match(notifications.errorElement.textContent, /Positions\.csv/);
            assert.match(notifications.errorElement.textContent, /Education\.csv/);
            assert.doesNotMatch(notifications.errorElement.textContent, /Profile\.csv/);
        } finally {
            notifications.errorElement = null;
        }
    });

    test('validateStep2 passe toujours', () => {
        assert.ok(validateStep2());
    });
});
