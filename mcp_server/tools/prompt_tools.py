"""MCP prompt bodies. Rendering one costs nothing server-side: it only
assembles text that the client's own LLM then executes.
"""

from __future__ import annotations

import json

from mcp_server.core.storage import StorageRepository

_NO_PROFILE_BRIEF = """\
Aucun profil de base n'est enregistré sur le serveur CV.

Avant de préparer un CV sur-mesure, enregistre le profil réel de l'utilisateur :
- soit avec le tool `import_linkedin_csv` (chemins locaux vers l'export LinkedIn),
- soit avec le tool `set_base_profile`.
Ensuite, redemande ce prompt.
"""

_CUSTOM_CV_BRIEF = """\
Tu prépares un CV sur-mesure pour une offre précise. Tu as trois sources, et
seulement ces trois sources :

## 1. Offre d'emploi
{job_posting}

## 2. Recherche sur l'entreprise (fournie par l'utilisateur)
{company_research}

## 3. Profil de base réel de l'utilisateur (JSON)
```json
{profile_json}
```

## Ce que tu dois faire
1. Choisis les expériences les plus pertinentes pour l'offre parmi
   `positions` du profil, et ordonne-les de la plus pertinente à la moins
   pertinente. Désigne-les par leur index (0 = première position du JSON).
2. Pour chaque expérience retenue, tu peux reformuler sa `description` pour
   mettre en avant ce qui correspond à l'offre. Le titre, l'entreprise, les
   dates, le lieu et les missions ne sont pas modifiables : le serveur les
   verrouille sur le profil de base.
3. Rédige la section « À propos » (`about`) : relie l'entreprise (uniquement
   des faits présents dans la recherche ci-dessus) à l'expérience réelle de
   l'utilisateur (uniquement des faits présents dans le profil ci-dessus).
4. Optionnel : un `headline` adapté au poste, et `skills_selected` (compétences
   du profil, ordonnées par pertinence).

## Règles impératives
- Vrai : n'invente jamais d'employeur, de date, de chiffre, de résultat, de
  compétence ou de fait sur l'entreprise absent de ces deux sources. Si une
  information manque, omets-la plutôt que de la supposer.
- Original : pas de formules creuses ni de clichés génériques (« passionné »,
  « dynamique », « force de proposition »...). Chaque phrase doit être
  spécifique à cette entreprise et à ce parcours.
- Langue : français par défaut, sauf si l'offre est rédigée dans une autre
  langue.
- `about` : 3 à 5 phrases, sauts de ligne autorisés.

## Ensuite
Appelle le tool `generate_custom_cv` avec : `job_title`, `company`, `about`,
`experiences` (liste ordonnée de `{{"index": <int>, "description": <str ou null>}}`),
`company_research` (le texte de recherche tel quel, pour traçabilité), et si
besoin `headline`, `skills_selected`.
"""


def custom_cv_brief(repo: StorageRepository, job_posting: str, company_research: str) -> str:
    profile = repo.load_base_profile()
    if profile is None:
        return _NO_PROFILE_BRIEF

    # The photo (base64) is useless to the LLM and was ~20% of the prompt.
    profile = {key: value for key, value in profile.items() if key != "photo"}
    return _CUSTOM_CV_BRIEF.format(
        job_posting=job_posting,
        company_research=company_research,
        profile_json=json.dumps(profile, indent=2, ensure_ascii=False),
    )
