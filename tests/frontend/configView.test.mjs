import { test, describe, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { setupDom, isHidden, $ } from './dom-harness.mjs';

let cvStateService;
let ConfigView;
let view;

beforeEach(async () => {
    ({ cvStateService } = await setupDom());
    ({ ConfigView } = await import('../../frontend/js/ui/views/configView.js'));
    view = new ConfigView();
    view.init();
});

describe('panneau suisse', () => {
    // Ce comportement est le premier des 4 sites que la migration
    // .is-hidden toucherait : il lit/ecrit style.display directement.
    test('est masque par defaut', () => {
        assert.ok(isHidden($('swiss-fields-section')));
    });

    test("s'ouvre au passage en format suisse", () => {
        const select = $('cv-type');
        select.value = 'swiss';
        select.dispatchEvent(new globalThis.Event('change'));

        assert.ok(!isHidden($('swiss-fields-section')));
        assert.equal(cvStateService.getConfig().cv_type, 'swiss');
    });

    test('se referme au retour en standard', () => {
        const select = $('cv-type');
        for (const value of ['swiss', 'standard']) {
            select.value = value;
            select.dispatchEvent(new globalThis.Event('change'));
        }

        assert.ok(isHidden($('swiss-fields-section')));
        assert.equal(cvStateService.getConfig().cv_type, 'standard');
    });
});

describe('selecteur de langue', () => {
    test('bascule les 6 intitules en anglais', () => {
        const select = $('cv-language');
        select.value = 'en';
        select.dispatchEvent(new globalThis.Event('change'));

        assert.equal($('label-education').value, 'Education');
        assert.equal($('label-experience').value, 'Professional Experience');
        assert.equal($('label-skills').value, 'Skills');
        assert.equal(cvStateService.getConfig().language, 'en');
    });

    test('revient au francais', () => {
        const select = $('cv-language');
        for (const value of ['en', 'fr']) {
            select.value = value;
            select.dispatchEvent(new globalThis.Event('change'));
        }

        assert.equal($('label-education').value, 'Formations');
        assert.equal(cvStateService.getConfig().language, 'fr');
    });
});

describe('bascules de sections', () => {
    test('decocher une section la desactive dans la config', () => {
        const toggle = $('toggle-skills');
        toggle.checked = false;
        toggle.dispatchEvent(new globalThis.Event('change'));

        assert.equal(cvStateService.getConfig().sections.skills, false);
    });
});

describe('intitules personnalises', () => {
    test('la saisie est reportee dans la config', () => {
        const input = $('label-education');
        input.value = 'Parcours';
        input.dispatchEvent(new globalThis.Event('input'));

        assert.equal(cvStateService.getConfig().labels.education, 'Parcours');
    });

    test('un intitule vide retombe sur le defaut cote backend', () => {
        const input = $('label-education');
        input.value = '   ';
        input.dispatchEvent(new globalThis.Event('input'));

        assert.equal(cvStateService.getConfig().labels.education, undefined);
    });
});

describe('syncFromConfig', () => {
    const remplirTout = () => {
        for (const id of ['contact-email', 'contact-phone', 'contact-address',
                          'contact-nationality', 'contact-birth-date', 'profile-headline']) {
            $(id).value = 'a-vider';
        }
        for (const [id, value] of [['cv-language', 'en'], ['cv-type', 'swiss']]) {
            const el = $(id);
            el.value = value;
            el.dispatchEvent(new globalThis.Event('change'));
        }
        const creative = globalThis.document.querySelector('input[name="template"][value="creative"]');
        creative.checked = true;
        creative.dispatchEvent(new globalThis.Event('change'));
    };

    test('vide les 9 champs personnels', () => {
        remplirTout();
        cvStateService.reset();
        view.syncFromConfig();

        for (const id of ['contact-email', 'contact-phone', 'contact-address',
                          'contact-nationality', 'contact-birth-date', 'profile-headline']) {
            assert.equal($(id).value, '', `${id} aurait du etre vide`);
        }
    });

    test('remet les selecteurs et referme le panneau suisse', () => {
        remplirTout();
        cvStateService.reset();
        view.syncFromConfig();

        assert.equal($('cv-language').value, 'fr');
        assert.equal($('cv-type').value, 'standard');
        assert.ok(isHidden($('swiss-fields-section')));
    });

    test('restaure les intitules et les couleurs', () => {
        remplirTout();
        cvStateService.reset();
        view.syncFromConfig();

        assert.equal($('label-education').value, 'Formations');
        assert.equal($('color-primary').value, '#3498db');
    });

    test('repositionne le bouton radio du template', () => {
        // Un vrai DOM gere l'exclusion des groupes `name` : mon ancien stub
        // maison rendait les deux radios coches, un faux positif.
        remplirTout();
        cvStateService.reset();
        view.syncFromConfig();

        const { document } = globalThis;
        assert.ok(document.querySelector('input[name="template"][value="modern"]').checked);
        assert.ok(!document.querySelector('input[name="template"][value="creative"]').checked);
    });

    test('ne leve pas sur une config partielle', () => {
        // La methode vide les champs personnels en premier : lever a mi-chemin
        // laisserait le formulaire a moitie reinitialise.
        for (const partielle of [{}, { language: 'fr' }, { sections: null }, { colors: null }]) {
            assert.doesNotThrow(() => view.syncFromConfig(partielle));
            assert.equal($('contact-email').value, '');
            assert.equal($('cv-language').value, 'fr');
        }
    });
});
