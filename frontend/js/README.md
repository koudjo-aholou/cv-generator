# Architecture Frontend - CV Generator

## Vue d'ensemble

L'application a été refactorisée en une **architecture modulaire en couches** utilisant des **modules ES6 vanilla JavaScript** (sans framework).

## Structure des dossiers

```
js/
├── core/                     # Infrastructure technique (bas niveau)
│   ├── api/                  # Client HTTP générique
│   ├── dom/                  # Utilitaires DOM
│   ├── state/                # Gestion d'état centralisée
│   ├── ui/                   # Composants UI de base
│   └── utils/                # Utilitaires génériques
│
├── services/                 # Orchestration (couche intermédiaire)
│   ├── api/                  # Services API
│   ├── file/                 # Services fichiers
│   ├── ui/                   # Services UI
│   └── state/                # Services d'état
│
├── business/                 # Logique métier
│   ├── cv/                   # Règles métier CV
│   ├── validation/           # Validations métier
│   ├── template/             # Gestion templates
│   └── workflow/             # Flux de travail
│
├── ui/                       # Composants UI (présentation)
│   ├── components/           # Composants réutilisables
│   ├── editors/              # Éditeurs de sections
│   └── views/                # Vues par étape
│
├── config/                   # Configuration
│   ├── constants.js          # Constantes
│   ├── endpoints.js          # Endpoints API
│   └── defaults.js           # Configurations par défaut
│
└── main.js                   # Point d'entrée
```

## Couches d'architecture

### 1. Core (Infrastructure)
**Responsabilité**: Outils techniques réutilisables, aucune logique métier

- `api/client.js`: Client HTTP générique (fetch wrapper)
- `dom/elements.js`: Cache et sélection d'éléments DOM
- `dom/builder.js`: Construction d'éléments DOM
- `dom/events.js`: Système d'événements (EventBus)
- `state/store.js`: Store d'état centralisé avec observers
- `ui/loading.js`: Gestion des loaders
- `ui/notifications.js`: Système de notifications
- `utils/validators.js`: Validateurs génériques
- `utils/formatters.js`: Formatage de données
- `utils/helpers.js`: Utilitaires divers

### 2. Services (Orchestration)
**Responsabilité**: Coordination entre Core et Business, appels API

- `api/parseService.js`: Service parsing LinkedIn
- `api/pdfService.js`: Service génération PDF
- `state/cvStateService.js`: Gestion d'état du CV
- `file/fileService.js`: Gestion des fichiers
- `file/photoService.js`: Gestion des photos
- `ui/stepperService.js`: Navigation entre étapes
- `ui/previewService.js`: Génération d'aperçu

### 3. Business (Métier)
**Responsabilité**: Règles métier pures, indépendantes de l'UI

- `cv/experience.js`: Logique expériences professionnelles
- `cv/education.js`: Logique formations
- `cv/skills.js`: Logique compétences
- `cv/languages.js`: Logique langues
- `cv/certifications.js`: Logique certifications
- `cv/profile.js`: Logique profil
- `cv/sections.js`: Gestion ordre des sections
- `validation/stepValidator.js`: Validation par étape
- `validation/fileValidator.js`: Validation fichiers
- `template/presets.js`: Presets de templates
- `template/colorManager.js`: Gestion couleurs
- `workflow/dataMapper.js`: Préparation données pour PDF
- `workflow/stepFlow.js`: Flux entre étapes

### 4. UI (Présentation)
**Responsabilité**: Composants visuels et interaction utilisateur

**Composants**:
- `fileUploader.js`: Upload de fichiers CSV
- `photoUploader.js`: Upload de photo
- `stepperNav.js`: Navigation du stepper

**Éditeurs**:
- `experienceEditor.js`: Édition des expériences
- `educationEditor.js`: Édition des formations
- `skillsEditor.js`: Sélection des compétences
- `languagesEditor.js`: Édition des langues
- `certificationsEditor.js`: Édition des certifications

**Vues**:
- `configView.js`: Vue de configuration (Step 2)
- `previewView.js`: Vue d'aperçu (Step 3)

## Flux de données

```
Utilisateur → UI → Services → Business → Core
                     ↓            ↓
                   API      Validation
```

### Exemple de flux

1. **Utilisateur clique sur "Supprimer expérience"**
2. **UI** (experienceEditor) reçoit l'événement
3. **UI** appelle **Service** (cvStateService)
4. **Service** utilise **Business** (experience.deleteExperience)
5. **Business** applique les règles métier et validation
6. **Service** met à jour le **Core** (store)
7. **Core** notifie via EventBus
8. **UI** se re-rend automatiquement

## Gestion d'état

L'application utilise un **store centralisé** (`core/state/store.js`) avec un pattern Observer:

```javascript
// Lire l'état
const config = cvStateService.getConfig();

// Modifier l'état
cvStateService.setConfig(newConfig);

// Observer les changements
store.observe('currentStep', (newValue, oldValue) => {
    // Réagir au changement
});
```

## Système d'événements

L'EventBus permet la communication entre modules sans couplage:

```javascript
// Émettre un événement
eventBus.emit('data:parsed', parsedData);

// Écouter un événement
eventBus.on('data:parsed', (data) => {
    // Réagir à l'événement
});
```

## Événements principaux

- `files:changed`: Fichiers modifiés
- `photo:uploaded`: Photo uploadée
- `photo:removed`: Photo supprimée
- `data:parsed`: Données parsées avec succès
- `stepper:change`: Changement d'étape
- `stepper:beforeNext`: Avant passage à l'étape suivante
- `preview:generated`: Aperçu PDF généré
- `preview:error`: Erreur génération aperçu
- `pdf:downloaded`: PDF téléchargé
- `state:change`: État global modifié
- `state:reset`: État réinitialisé

## Avantages de cette architecture

### ✅ Séparation des responsabilités
Chaque couche a un rôle bien défini

### ✅ Réutilisabilité
Les modules Core sont réutilisables dans d'autres projets

### ✅ Testabilité
Chaque module peut être testé indépendamment

### ✅ Maintenabilité
Code organisé et facile à comprendre

### ✅ Évolutivité
Facile d'ajouter de nouvelles fonctionnalités

### ✅ Pas de build step
Modules ES6 natifs du navigateur

### ✅ Découplage
Communication via EventBus et Services

## Utilisation

### Import d'un module

```javascript
// Import nommé
import { loading } from './core/ui/loading.js';
import { cvStateService } from './services/state/cvStateService.js';

// Import par défaut
import { ApiClient } from './core/api/client.js';
```

### Créer un nouveau composant

1. Créer le fichier dans le bon dossier (ui/components, ui/editors, etc.)
2. Exporter la classe ou les fonctions
3. Importer dans main.js
4. Initialiser dans Application.init()

### Ajouter une nouvelle règle métier

1. Ajouter la fonction dans business/cv/
2. L'utiliser dans le Service approprié
3. Appeler le Service depuis l'UI

## Migration depuis l'ancien code

L'ancien fichier monolithique `script.js` (1906 lignes) a été sauvegardé en `script.js.backup`.

La nouvelle architecture maintient exactement les mêmes fonctionnalités mais avec:
- **43 modules** au lieu d'1 fichier
- Code organisé par **responsabilité**
- **Réutilisable** et **testable**
- **Maintenable** sur le long terme

## Notes techniques

- **Pas de transpilation** nécessaire
- Fonctionne dans tous les navigateurs modernes
- Les modules sont chargés de manière asynchrone
- Le type `module` dans le script HTML active le mode strict automatiquement
