import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const MOCK = path.resolve('mock');
const CSV = ['Profile.csv', 'Positions.csv', 'Education.csv', 'Skills.csv',
             'Languages.csv', 'Certifications.csv'].map(f => path.join(MOCK, f));

// PNG 1x1 valide, construit en memoire : aucun binaire ajoute au depot.
const PNG = Buffer.from(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
    'base64'
);

/**
 * Collecte les violations CSP. C'est le fil conducteur de ces 4 tests :
 * sans navigateur, rien ne verifie la politique posee dans index.html.
 */
function watchCsp(page) {
    const violations = [];
    const look = (text) => {
        if (/Content Security Policy/i.test(text)) violations.push(text);
    };
    page.on('console', (msg) => look(msg.text()));
    page.on('pageerror', (err) => look(String(err)));
    return violations;
}

test('la page se charge sans violation CSP', async ({ page }) => {
    const csp = watchCsp(page);

    await page.goto('/');
    await expect(page.locator('#step-1')).toBeVisible();

    // La CSP est bien presente et appliquee
    const policy = await page.locator('meta[http-equiv="Content-Security-Policy"]')
        .getAttribute('content');
    expect(policy).toContain("script-src 'self'");
    expect(policy).not.toContain("script-src 'self' 'unsafe-inline'");

    expect(csp, csp.join('\n')).toEqual([]);
});

test('le televersement des CSV atteint l API (connect-src)', async ({ page }) => {
    const csp = watchCsp(page);

    await page.goto('/');
    await page.locator('input[type="file"]#fileInput').setInputFiles(CSV);
    await page.locator('#nextStep1').click();

    await expect(page.locator('#step-2')).toBeVisible({ timeout: 30_000 });
    expect(csp, csp.join('\n')).toEqual([]);
});

test('l apercu photo s affiche (img-src data:)', async ({ page }) => {
    const csp = watchCsp(page);

    await page.goto('/');
    await page.locator('#photoInput').setInputFiles({
        name: 'photo.png', mimeType: 'image/png', buffer: PNG
    });

    const img = page.locator('#photoPreviewImg');
    await expect(img).toBeVisible();
    await expect(img).toHaveAttribute('src', /^data:image\//);

    expect(csp, csp.join('\n')).toEqual([]);
});

test('l apercu PDF s affiche dans l iframe (frame-src blob:)', async ({ page }) => {
    const csp = watchCsp(page);

    // Garde-fou. `reuseExistingServer` reprend n'importe quel backend deja
    // lance sur le port 5000, y compris une instance tournant avec du code
    // perime : les tests passaient alors en silence sans rien valider du
    // backend. L'ancienne version renvoyait `filename=cv.pdf`, la nouvelle
    // renvoie le nom calcule — un serveur perime fait donc echouer ce test.
    const pdfResponse = page.waitForResponse(
        (r) => r.url().includes('/api/generate-pdf') && r.status() === 200
    );

    await page.goto('/');
    await page.locator('input[type="file"]#fileInput').setInputFiles(CSV);
    await page.locator('#nextStep1').click();
    await expect(page.locator('#step-2')).toBeVisible({ timeout: 30_000 });

    await page.locator('#nextStep2').click();
    const frame = page.locator('#pdfPreviewFrame');
    await expect(frame).toHaveAttribute('src', /^blob:/, { timeout: 30_000 });

    const disposition = (await pdfResponse).headers()['content-disposition'] || '';
    expect(disposition, `backend perime ? en-tete recu : "${disposition}"`)
        .toMatch(/filename=CV_.+\.pdf/);

    expect(csp, csp.join('\n')).toEqual([]);
});
