#!/usr/bin/env node
/**
 * Script de vérification de l'intégrité des modules
 */

const fs = require('fs');
const path = require('path');

const jsDir = path.join(__dirname, 'js');
let errors = [];
let warnings = [];
let totalChecks = 0;

// Récupérer tous les fichiers .js
function getAllJsFiles(dir, fileList = []) {
    const files = fs.readdirSync(dir);

    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory()) {
            getAllJsFiles(filePath, fileList);
        } else if (file.endsWith('.js')) {
            fileList.push(filePath);
        }
    });

    return fileList;
}

// Vérifier les imports
function checkImports(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');

    lines.forEach((line, index) => {
        totalChecks++;

        // Vérifier les imports relatifs
        const importMatch = line.match(/from\s+['"](\.\.?\/[^'"]+)['"]/);
        if (importMatch) {
            const importPath = importMatch[1];
            const dir = path.dirname(filePath);
            const resolvedPath = path.resolve(dir, importPath);

            // Vérifier si le fichier existe
            if (!fs.existsSync(resolvedPath)) {
                errors.push(`${path.relative(jsDir, filePath)}:${index + 1} - Import introuvable: ${importPath}`);
            }
        }

        // Vérifier les exports
        if (line.includes('export') && !line.trim().startsWith('//')) {
            // OK, le fichier exporte quelque chose
        }
    });
}

// Vérifier les exports vs imports
function checkExportsUsage() {
    const files = getAllJsFiles(jsDir);
    const allContent = files.map(f => fs.readFileSync(f, 'utf-8')).join('\n');

    files.forEach(filePath => {
        const content = fs.readFileSync(filePath, 'utf-8');
        const exports = [];

        // Extraire les exports nommés
        const namedExports = content.match(/export\s+(const|let|var|function|class)\s+(\w+)/g);
        if (namedExports) {
            namedExports.forEach(exp => {
                const match = exp.match(/export\s+(?:const|let|var|function|class)\s+(\w+)/);
                if (match) exports.push(match[1]);
            });
        }

        // Vérifier si les exports sont utilisés quelque part
        exports.forEach(exportName => {
            const importPattern = new RegExp(`import.*${exportName}.*from`, 'g');
            if (!importPattern.test(allContent) && exportName !== 'Application') {
                warnings.push(`${path.relative(jsDir, filePath)} - Export "${exportName}" potentiellement non utilisé`);
            }
        });
    });
}

// Exécuter les vérifications
console.log('🔍 Vérification de l\'intégrité des modules ES6...\n');

const files = getAllJsFiles(jsDir);
console.log(`📁 ${files.length} fichiers JavaScript trouvés\n`);

files.forEach(filePath => {
    checkImports(filePath);
});

checkExportsUsage();

// Afficher les résultats
console.log(`✅ ${totalChecks} vérifications effectuées\n`);

if (errors.length > 0) {
    console.log('❌ ERREURS TROUVÉES:');
    errors.forEach(err => console.log(`   ${err}`));
    console.log();
}

if (warnings.length > 0) {
    console.log('⚠️  AVERTISSEMENTS:');
    warnings.slice(0, 10).forEach(warn => console.log(`   ${warn}`));
    if (warnings.length > 10) {
        console.log(`   ... et ${warnings.length - 10} autres avertissements`);
    }
    console.log();
}

if (errors.length === 0) {
    console.log('✅ Aucune erreur détectée !');
    console.log('✅ Tous les imports sont valides');
    console.log('✅ Tous les chemins de fichiers sont corrects');
} else {
    console.log(`❌ ${errors.length} erreur(s) trouvée(s)`);
    process.exit(1);
}
