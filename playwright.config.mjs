import { defineConfig, devices } from '@playwright/test';

/**
 * Tests de fumée en vrai navigateur.
 *
 * Leur raison d'être principale : vérifier la CSP, qu'aucun test jsdom ne
 * peut valider puisque jsdom n'applique aucune politique. Ils restent
 * volontairement peu nombreux — c'est la pointe de la pyramide.
 */
export default defineConfig({
    testDir: './tests/e2e',
    fullyParallel: false,
    workers: 1,
    reporter: [['list']],

    use: {
        // Obligatoire dès que `webServer` est un tableau, même avec une
        // seule entrée : sans baseURL, la configuration est rejetée.
        baseURL: 'http://localhost:8080',
        trace: 'retain-on-failure',
    },

    projects: [
        { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    ],

    // Les deux serveurs que start.bat lance aujourd'hui à la main.
    webServer: [
        {
            name: 'backend',
            command: 'python backend/app.py',
            url: 'http://localhost:5000/',
            reuseExistingServer: true,
            timeout: 60_000,
        },
        {
            name: 'frontend',
            command: 'python -m http.server 8080 --directory frontend',
            url: 'http://localhost:8080/',
            reuseExistingServer: true,
            timeout: 60_000,
        },
    ],
});
