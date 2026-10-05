# Dette technique : fuite d'information, classe de base des éditeurs, migration `.is-hidden`

> ## ⏸️ Statut : REPORTÉ — à reprendre plus tard
>
> Décision prise après audit de ce plan lui-même : **le refactor est trop risqué en
> l'état**. Non pas parce qu'il est mal conçu, mais parce que le filet de tests sur
> lequel il repose s'est révélé plus troué que je ne l'affirmais.
>
> **Ce qui a motivé le report :**
>
> 1. **Le harnais de test casserait silencieusement.** Une classe de base partagée
>    rompt le contournement `?dom=N` : la sous-classe tokenisée importe la base sans
>    jeton, la chaîne de prototypes s'enracine sur un `HTMLElement` périmé, et
>    l'upgrade échoue dès le deuxième DOM. Reproduit : `DOM 1 : true`,
>    `DOM 2 : upgrade = false`. Les 25 tests d'éditeurs passeraient **au vert sur un
>    DOM inerte**, sans rien valider. C'est le pire mode de défaillance possible pour
>    un filet censé sécuriser un refactor.
> 2. **Trois zones que le refactor touche ne sont couvertes par rien** : le
>    désabonnement au démontage, l'état coché des cases de visibilité, et 4 des
>    5 éléments masqués d'`index.html` (détail au lot 0).
>
> **Ce qui reste vrai et acquis :** l'analyse, les mesures et l'ordonnancement de ce
> document ont été vérifiés trois fois. Le lot 0 et la refonte du harnais sont les
> prérequis identifiés ; le plan est exécutable tel quel une fois ceux-ci faits.
>
> **Si on ne devait en garder qu'une chose :** le **lot 1** (fuite d'information) est
> indépendant des deux refactors, sans risque de régression, et corrige un défaut de
> sécurité réel. Il peut être fait seul, à tout moment.

## Context

La PR #22 est mergée. Elle a corrigé la rétention des PDF, durci CORS et la CSP, et
surtout **posé un filet de tests là où il n'y en avait aucun** : 95 tests frontend dont
25 sur les chemins de mutation des éditeurs. Ce filet débloque deux refactors que
j'avais explicitement écartés faute de couverture.

Restent trois chantiers, issus des audits de la session :

**1. Une fuite d'information, toujours ouverte.** `backend/app.py` renvoie le message
d'exception interne au client sur les réponses 500, à **deux endroits** (l. 155 et 224)
et non un seul comme l'audit le disait. `SECURITY.md:171` classe pourtant
« Information Disclosure » comme *Fixed* — la documentation affirme le contraire du code.

**2. Les 5 éditeurs partagent 13 blocs de 6 lignes identiques.** C'est du code vivant,
exécuté, qu'il faut modifier cinq fois à chaque évolution — le vrai coût du frontend,
bien plus que ses 196 lignes inertes.

**3. La CSP porte `'unsafe-hashes'`** pour tolérer les 12 attributs `style="display:
none;"`. C'était le bon arbitrage quand aucun test ne couvrait les sites couplés ; ce
n'est plus le cas.

**Ordre retenu, et c'est le point non évident : la classe de base passe AVANT
`.is-hidden`.** Le bloc de bascule est identique au octet près dans les 3 éditeurs qui
le portent (vérifié par empreinte MD5). Le factoriser d'abord ramène la migration de
**3 sites couplés à 1**.

Décisions prises avec l'utilisateur : les en-têtes HTTP (`frame-ancestors`,
`X-Content-Type-Options`, `Referrer-Policy`) sont **écartés** — ils exigeraient de faire
servir le frontend par Flask, ce qui déplacerait la route `/`, changerait `API_URL`,
`start.bat` et la config Playwright. La structure morte (dossier `cv/`, 3 modules
orphelins, règles CSS) reste **en l'état**. Tout sur une branche
`chore/dette-technique`, un commit par lot, une seule PR.

---

## Lot 0 — Combler les trous du filet, AVANT tout refactor (P0)

Un audit du plan lui-même a montré qu'il **surestimait la protection des tests**.
Trois zones que les lots 2 et 3 vont toucher ne sont couvertes par rien — vérifié :

**Le nettoyage au démontage.** `disconnectedCallback` appelle `unsubscribeData()`, et
**aucun test ne démonte un éditeur**. Si la classe de base casse ce chemin, l'écouteur
`data-parsed` survit : chaque remontage en empile un de plus et le rendu se déclenche
N fois. Symptôme tardif et confus, zéro détection.

→ Test, dans la suite paramétrée : monter, `el.remove()`, modifier les données, émettre
`data-parsed`, et vérifier que l'élément détaché n'a **pas** re-rendu.

**L'état coché des cases de visibilité.** Les tests comptent les cases, jamais leur
état. C'est pourtant exactement le paramètre que la classe de base devra câbler
(`visibleConfigKey`, lu pour `experience` et `education` seulement). Un câblage faux
viderait `visibleIndices`, décocherait tout, et la sélection de l'utilisateur
disparaîtrait jusque dans le PDF via `config.experience_visible` — au vert.

→ Test : poser `experience_visible = [1]` avant montage, vérifier que la 1ʳᵉ case est
décochée et la 2ᵉ cochée. Ajouter `visibleConfigKey` à la table `EDITEURS`.

**Quatre des cinq éléments masqués d'`index.html`.** Seul `swiss-fields-section` est
couvert ; `previewLoading`, `success-section`, `loading` et `errorMessage` ne le sont
par rien. La bascule vers une classe est mécaniquement sûre — vérifié qu'aucun code ne
fait `style.display = ''` sur eux — mais retirer l'attribut en oubliant la classe sur
l'un d'eux le rendrait **définitivement visible** : un spinner ou une boîte d'erreur
bloqués à l'écran, indétectés.

→ Test Playwright : au chargement, ces quatre éléments sont masqués.

Ces tests doivent être verts **sur le code actuel** avant d'entamer le lot 2 : ils
décrivent le comportement à préserver, pas celui à obtenir.

## Lot 1 — Ne plus divulguer les exceptions (P0)

Retirer `"details": str(e)` des deux réponses 500 de
[app.py:155](backend/app.py#L155) et [app.py:224](backend/app.py#L224). Le message
d'exception reste journalisé côté serveur — `logger.error(..., exc_info=True)` est déjà
en place juste au-dessus — mais ne part plus au client.

Corriger [SECURITY.md:171](SECURITY.md#L171), qui affirme le contraire du code.

**Tests** (`tests/test_api.py`) : provoquer une erreur de génération et vérifier que la
réponse 500 ne contient pas de clé `details`, et qu'aucun chemin de fichier ni nom de
module n'apparaît dans le corps. `tests/core/test_app.py:357` commente déjà cette
intention sans la vérifier sur ce chemin.

## Lot 2 — Classe de base des éditeurs (P1)

Créer `frontend/js/ui/editors/data-editor.js` exportant `DataEditor extends HTMLElement`.

Mesuré sur les 5 éditeurs :

| Méthode | État |
|---|---|
| `connectedCallback` | **identique partout** → monte telle quelle |
| `disconnectedCallback` | **identique partout** → monte telle quelle |
| `subscribeToData` | même forme, 3 paramètres varient |
| bascule « Modifier » | **identique au octet près** dans les 3 qui l'ont |
| bouton d'ajout | une seule variante sur les 5 |
| `render`, CRUD | spécifiques → restent dans les sous-classes |

`subscribeToData` ne diffère que par la clé de données (`positions`, `education`…), le
nom du champ d'instance (`this.experiences`, `this.languages`…) et la lecture ou non des
indices de visibilité. La classe de base les expose en descripteurs statiques
(`dataKey`, `itemsField`, `visibleConfigKey`), de sorte que les sous-classes gardent
leurs noms de champ actuels — **ne pas renommer `this.experiences` en `this.items`**,
cela toucherait chaque usage dans chaque éditeur pour un gain nul.

La bascule « Modifier » remonte dans la classe de base : c'est elle qui rend le lot 3
ponctuel.

**Contrainte de test.** La suite `tests/frontend/editors.test.mjs` est déjà paramétrée
sur les 5 éditeurs et **ne doit pas être modifiée** par ce lot : c'était sa raison
d'être. Toute adaptation nécessaire signale que le refactor change un comportement
observable — à traiter comme un défaut, pas comme un ajustement de test.

### Prérequis bloquant : refondre le harnais d'abord

Ce n'est pas une précaution, c'est un blocage **vérifié par expérience**. Le harnais
crée un jsdom par test et contourne la capture de `HTMLElement` en réimportant chaque
éditeur avec un jeton `?dom=N` ([dom-harness.mjs](tests/frontend/dom-harness.mjs)).

Une classe de base casse ce contournement : la sous-classe tokenisée fait
`import './data-editor.js'` **sans jeton**, donc la base reste celle du premier realm.
La chaîne de prototypes s'enracine dans un `HTMLElement` périmé et **l'upgrade échoue
en silence dès le deuxième DOM** — reproduit en isolant le mécanisme : `test 1 : true`,
puis `DOM 2 : upgrade = false`. Les 25 tests d'éditeurs passeraient au vert sur un DOM
inerte, sans rien valider.

Tokeniser aussi la base ne résout rien : l'import relatif interne de la sous-classe ne
porte pas le jeton.

**Parade retenue, vérifiée :** un seul jsdom par fichier de test, et réinitialisation de
`document.body.innerHTML` entre les tests à partir du corps d'origine capturé une fois.
Les éléments réinsérés sont alors upgradés automatiquement — confirmé sur 4 cycles
successifs. Bénéfice secondaire : le bricolage `?dom=N` disparaît.

Ordre d'exécution imposé : **refondre le harnais d'abord**, vérifier que les 95 tests
restent verts *sans* toucher aux fichiers de test, et seulement ensuite introduire la
classe de base. Le `<head>` (où la feuille de style est injectée) n'est pas réinitialisé,
seul le `<body>` l'est.

## Lot 3 — Migration `.is-hidden` et CSP sans `'unsafe-hashes'` (P1)

Ajouter `.is-hidden { display: none; }` dans `frontend/style.css`, remplacer les
12 attributs `style="display: none;"` (5 dans `index.html`, 7 dans les gabarits JS),
puis retirer `'unsafe-hashes'` et le hash de la CSP — `style-src 'self'` suffira.

Les sites couplés, qui **lisent** l'état pour décider :

- la bascule « Modifier » — **un seul site après le lot 2**, contre 3 aujourd'hui
- [configView.js:107](frontend/js/ui/views/configView.js#L107) :
  `style.display = cvType === 'swiss' ? '' : 'none'`. Remettre `''` retomberait sur la
  classe et masquerait le panneau suisse en permanence → `classList.toggle`.

Les ~50 assignations `element.style.X = …` ailleurs **ne sont pas concernées** : la CSP
ne régit que les attributs du balisage, pas le CSSOM.

Les tests DOM assertent la visibilité via `getComputedStyle` et non `style.display` :
ils doivent rester valables **sans modification**. C'est le critère de réussite du lot,
pas un effet de bord.

---

## Vérification

0. Les tests du lot 0 passent **sur le code actuel, avant tout refactor**. S'ils
   échouent d'emblée, c'est un défaut existant à traiter d'abord, pas un test à ajuster.
1. `python -m pytest -q` — référence **317 verts**, plus les nouveaux tests du lot 1.
2. `npm test` — référence **95 verts**, plus ceux du lot 0. Les lots 2 et 3 ne doivent
   en modifier aucun ; si l'un casse, c'est le refactor qui est en cause.
3. `npx playwright test` — **4 verts**, dont l'absence de violation CSP. Le lot 3 change
   la politique : cette étape est le contrôle qui compte.
4. Après le lot 3 : `grep -r 'style="' frontend/index.html frontend/js/` ne doit plus
   rien rendre, et `'unsafe-hashes'` doit avoir disparu de `index.html`.
5. Mutation, sur le modèle employé jusqu'ici : casser la bascule dans la classe de base
   doit faire échouer les tests des 3 éditeurs concernés, pas d'un seul. **Ce contrôle
   est obligatoire après la refonte du harnais** : il est le seul à distinguer « les
   tests passent » de « les tests passent sur un DOM inerte », qui est précisément le
   mode de défaillance identifié ci-dessus.
6. Contrôle navigateur sur `start.bat` : déplier/replier une fiche dans chaque éditeur,
   ouvrir et fermer le panneau suisse, et vérifier la console — le lot 3 touche à
   l'affichage, et c'est là que les tests sont les plus faibles.

## Limite assumée

`sections.js` reste à **0 % de couverture de branches** et `section-order-editor.js` à
35 %. Le glisser-déposer n'est pas couvert : **ce refactor ne doit pas toucher
`section-order-editor.js`**, qui n'a pas de filet. Il n'est pas un Web Component et ne
sera donc pas une sous-classe de `DataEditor` — il reste hors périmètre.

## Hors périmètre, documenté

- En-têtes HTTP via Flask : écarté par l'utilisateur.
- Dossier `cv/` et ses 147 PDF, 3 modules orphelins, 9 exports morts, 11 règles CSS,
  3 verbes d'`ApiClient` : laissés en l'état.
