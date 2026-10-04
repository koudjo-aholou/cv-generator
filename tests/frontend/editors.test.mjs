/**
 * Une SEULE suite, parametree sur les 5 editeurs.
 *
 * Les 5 editeurs partagent 13 blocs de 6 lignes strictement identiques et une
 * refacto par classe de base y est pendante. Ecrire 5 suites jumelles
 * figerait cette duplication et multiplierait par cinq le cout de cette
 * refacto : des tests peuvent cimenter une mauvaise architecture. Le cycle de
 * vie commun s'ecrit donc une fois et s'execute cinq fois.
 */
import { test, describe, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { setupDom, isHidden, defineEditor } from './dom-harness.mjs';

const EDITEURS = [
    {
        tag: 'experience-editor', module: 'experience-editor.js', classe: 'ExperienceEditor',
        cle: 'positions', liste: 'experience-list', visibilite: true,
        bascule: true, champ: 'title',
        entree: { title: 'Dev', company: 'Acme', description: 'x' }
    },
    {
        tag: 'education-editor', module: 'education-editor.js', classe: 'EducationEditor',
        cle: 'education', liste: 'education-list', visibilite: true,
        bascule: true, champ: 'school',
        entree: { school: 'EPFL', degree: 'MSc' }
    },
    {
        tag: 'skills-editor', module: 'skills-editor.js', classe: 'SkillsEditor',
        cle: 'skills', liste: 'skills-list', visibilite: false,
        bascule: false, champ: null, invite: 'Nouvelle competence',
        entree: 'Python'
    },
    {
        tag: 'languages-editor', module: 'languages-editor.js', classe: 'LanguagesEditor',
        cle: 'languages', liste: 'languages-list', visibilite: false,
        bascule: false, champ: 'name', btnSuppr: '.editor-delete-btn-small',
        entree: { name: 'Francais', proficiency: 'Natif' }
    },
    {
        tag: 'certifications-editor', module: 'certifications-editor.js', classe: 'CertificationsEditor',
        cle: 'certifications', liste: 'certifications-list', visibilite: false,
        bascule: true, champ: 'name',
        entree: { name: 'AWS', authority: 'Amazon' }
    }
];

const donneesAvec = (cle, entrees) => ({
    profile: { first_name: 'A', last_name: 'B' },
    positions: [], education: [], skills: [], languages: [], certifications: [],
    [cle]: entrees
});

let cvStateService;

beforeEach(async () => {
    ({ cvStateService } = await setupDom());
});

for (const ed of EDITEURS) {
    describe(ed.tag, () => {
        const monter = async (entrees) => {
            await defineEditor(ed.tag, ed.module, ed.classe);
            cvStateService.setParsedData(donneesAvec(ed.cle, entrees));
            globalThis.document.dispatchEvent(new globalThis.CustomEvent('data-parsed'));
            return globalThis.document.querySelector(ed.tag);
        };

        test('est masque quand la collection est vide', async () => {
            const el = await monter([]);
            assert.ok(isHidden(el));
        });

        test('est visible et rend une entree', async () => {
            const el = await monter([ed.entree]);
            assert.ok(!isHidden(el));
            assert.ok(el.querySelector(`#${ed.liste}`).children.length >= 1);
        });

        test('rend autant de lignes que d entrees', async () => {
            const el = await monter([ed.entree, ed.entree, ed.entree]);
            assert.equal(el.querySelector(`#${ed.liste}`).children.length, 3);
        });

        test('echappe les donnees hostiles sans perdre de texte', async () => {
            // Regression : une guillemet dans un intitule tronquait la valeur
            // de l'attribut et la donnee etait silencieusement perdue.
            const hostile = typeof ed.entree === 'string'
                ? 'C++ "pro" <x>'
                : Object.fromEntries(Object.keys(ed.entree).map(k => [k, 'A "b" <c>']));
            const el = await monter([hostile]);

            // Les competences sont rendues en cases a cocher, pas en champs
            // editables : prendre le premier input REELLEMENT rempli evite
            // d'attraper la barre de recherche, vide.
            const champ = [...el.querySelectorAll('input:not([type=checkbox]):not([type=radio])')]
                .find(i => i.value);
            if (champ) {
                assert.ok(champ.value.includes('"b"'),
                    `valeur tronquee : ${JSON.stringify(champ.value)}`);
                assert.ok(champ.value.includes('<c>'),
                    `fragment perdu : ${JSON.stringify(champ.value)}`);
            }
            // Le marqueur ne doit jamais devenir un element : c'est la seule
            // chose qui compte. Chercher '<c>' dans innerHTML testerait le
            // serialiseur, qui n'echappe pas '<' dans un attribut — ce qui est
            // conforme a la spec et sans danger.
            assert.equal(el.querySelector('c'), null, 'balise injectee dans le DOM');
            assert.equal(el.querySelector('x'), null, 'balise injectee dans le DOM');

            // Universel : la donnee survit quelque part, en entier. Selon
            // l'editeur elle apparait en texte (libelle recapitulatif) ou
            // seulement dans un champ editable — languages n'a pas de libelle.
            const marqueur = typeof hostile === 'string' ? hostile : 'A "b" <c>';
            const rendu = el.textContent
                + [...el.querySelectorAll('input, textarea')].map(i => i.value).join(' ');
            assert.ok(rendu.includes(marqueur),
                `donnee perdue au rendu, attendu ${JSON.stringify(marqueur)}`);
        });
    });
}

describe('bascule de visibilite', () => {
    // Elle n'existe que dans experience et education : verifie, elle est
    // absente de certifications, languages et skills.
    for (const ed of EDITEURS.filter(e => e.visibilite)) {
        test(`${ed.tag} expose des cases de visibilite`, async () => {
            await defineEditor(ed.tag, ed.module, ed.classe);
            cvStateService.setParsedData(donneesAvec(ed.cle, [ed.entree, ed.entree]));
            globalThis.document.dispatchEvent(new globalThis.CustomEvent('data-parsed'));

            const el = globalThis.document.querySelector(ed.tag);
            const cases = el.querySelectorAll('input[data-visibility-index]');
            assert.equal(cases.length, 2);
        });
    }

    for (const ed of EDITEURS.filter(e => !e.visibilite)) {
        test(`${ed.tag} n'en expose pas`, async () => {
            await defineEditor(ed.tag, ed.module, ed.classe);
            cvStateService.setParsedData(donneesAvec(ed.cle, [ed.entree]));
            globalThis.document.dispatchEvent(new globalThis.CustomEvent('data-parsed'));

            const el = globalThis.document.querySelector(ed.tag);
            assert.equal(el.querySelectorAll('input[data-visibility-index]').length, 0);
        });
    }
});

/**
 * Chemins de MUTATION des editeurs.
 *
 * La suite ci-dessus ne couvrait que le rendu : les branches de
 * business/cv/*.js etaient a 0 %. Surtout, la bascule « Modifier » est l'un
 * des quatre sites que la migration vers une classe .is-hidden devra
 * toucher, puisqu'elle LIT style.display pour decider du sens. C'est
 * precisement le test qui manquait pour rendre cette refacto sure.
 */
const monterEditeur = async (ed, entrees, cvStateService) => {
    await defineEditor(ed.tag, ed.module, ed.classe);
    cvStateService.setParsedData(donneesAvec(ed.cle, entrees));
    globalThis.document.dispatchEvent(new globalThis.CustomEvent('data-parsed'));
    return globalThis.document.querySelector(ed.tag);
};

describe('bascule « Modifier »', () => {
    for (const ed of EDITEURS.filter(e => e.bascule)) {
        test(`${ed.tag} deplie puis replie la fiche`, async () => {
            const el = await monterEditeur(ed, [ed.entree], cvStateService);
            const bouton = el.querySelector('.editor-toggle-btn');
            const fiche = el.querySelector('.editor-fields');

            assert.ok(isHidden(fiche), 'la fiche devrait etre repliee au depart');
            assert.equal(bouton.textContent.trim(), 'Modifier');

            bouton.click();
            assert.ok(!isHidden(fiche), 'la fiche devrait etre depliee apres un clic');
            assert.equal(bouton.textContent.trim(), 'Masquer');

            bouton.click();
            assert.ok(isHidden(fiche), 'la fiche devrait etre repliee apres deux clics');
            assert.equal(bouton.textContent.trim(), 'Modifier');
        });

        test(`${ed.tag} ne deplie que la fiche cliquee`, async () => {
            const el = await monterEditeur(ed, [ed.entree, ed.entree], cvStateService);
            const fiches = el.querySelectorAll('.editor-fields');

            el.querySelectorAll('.editor-toggle-btn')[1].click();

            assert.ok(isHidden(fiches[0]), 'la premiere fiche aurait du rester repliee');
            assert.ok(!isHidden(fiches[1]));
        });
    }

    for (const ed of EDITEURS.filter(e => !e.bascule)) {
        test(`${ed.tag} n'a pas de bascule`, async () => {
            const el = await monterEditeur(ed, [ed.entree], cvStateService);
            assert.equal(el.querySelectorAll('.editor-toggle-btn').length, 0);
        });
    }
});

describe('ajout d une entree', () => {
    for (const ed of EDITEURS) {
        test(`${ed.tag} ajoute une ligne`, async () => {
            const el = await monterEditeur(ed, [ed.entree], cvStateService);
            const avant = el.querySelector(`#${ed.liste}`).children.length;

            // skills demande le nom par prompt(), non implemente dans jsdom
            if (ed.invite) globalThis.prompt = () => ed.invite;
            try {
                el.querySelector('.add-item-btn').click();
                assert.equal(el.querySelector(`#${ed.liste}`).children.length, avant + 1);
            } finally {
                delete globalThis.prompt;
            }
        });
    }
});

describe('suppression d une entree', () => {
    for (const ed of EDITEURS.filter(e => e.champ)) {
        test(`${ed.tag} supprime apres confirmation`, async () => {
            const el = await monterEditeur(ed, [ed.entree, ed.entree], cvStateService);
            // jsdom laisse confirm() non implemente : il rend undefined, donc
            // sans stub la suppression ne se declencherait jamais.
            globalThis.confirm = () => true;
            try {
                el.querySelector(ed.btnSuppr || '.editor-delete-btn').click();
                assert.equal(el.querySelector(`#${ed.liste}`).children.length, 1);
            } finally {
                delete globalThis.confirm;
            }
        });

        test(`${ed.tag} ne supprime rien si l utilisateur refuse`, async () => {
            const el = await monterEditeur(ed, [ed.entree, ed.entree], cvStateService);
            globalThis.confirm = () => false;
            try {
                el.querySelector(ed.btnSuppr || '.editor-delete-btn').click();
                assert.equal(el.querySelector(`#${ed.liste}`).children.length, 2);
            } finally {
                delete globalThis.confirm;
            }
        });
    }
});

describe('modification d une entree', () => {
    for (const ed of EDITEURS.filter(e => e.champ)) {
        test(`${ed.tag} reporte la saisie dans l etat`, async () => {
            const el = await monterEditeur(ed, [ed.entree], cvStateService);
            const champ = el.querySelector(`[data-field="${ed.champ}"]`);
            assert.ok(champ, `champ ${ed.champ} introuvable`);

            champ.value = 'Valeur modifiee';
            champ.dispatchEvent(new globalThis.Event('input', { bubbles: true }));

            const etat = cvStateService.getParsedData()[ed.cle];
            assert.equal(etat[0][ed.champ], 'Valeur modifiee');
        });
    }
});
