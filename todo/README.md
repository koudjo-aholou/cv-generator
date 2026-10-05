# Todo

Travaux identifiés, analysés, mais **non engagés**. Chaque document ici est un plan
exécutable : contexte, lots, critères de vérification, et surtout les raisons qui ont
conduit à le reporter.

L'intérêt de les garder versionnés avec le code plutôt que dans un outil externe : ils
restent à jour avec le dépôt, et une relecture du diff montre si le plan est devenu
caduc.

| Document | Sujet | Pourquoi c'est en attente |
|---|---|---|
| [refacto-editeurs-et-is-hidden.md](refacto-editeurs-et-is-hidden.md) | Fuite d'information sur les réponses 500, classe de base pour les 5 éditeurs, migration `.is-hidden` et retrait de `'unsafe-hashes'` de la CSP | Le filet de tests s'est révélé plus troué que prévu. Une classe de base casserait le harnais jsdom **silencieusement** : les tests passeraient au vert sur un DOM inerte. Trois zones touchées par le refactor ne sont couvertes par rien. |

## À savoir avant de reprendre

Le **lot 1** de ce document — la fuite `"details": str(e)` sur les deux réponses 500 de
`backend/app.py` — est indépendant des refactors, sans risque de régression, et corrige
un défaut de sécurité réel. Il peut être traité seul, sans rien des prérequis.

Les lots 2 et 3 exigent d'abord le **lot 0** (combler les trous du filet) et la refonte
du harnais de test. L'ordre est imposé et expliqué dans le document.
