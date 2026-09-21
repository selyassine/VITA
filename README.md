# VitaAI

**Plateforme actuarielle solo pour l'assurance-vie — projet de mémoire de fin d'études (alternance)**

VitaAI (nom de package interne : `actuarial_platform`) est une plateforme Python couvrant l'ensemble du cycle de vie actuariel en assurance-vie : modélisation de la mortalité, tarification, provisionnement, Solvabilité II / SCR, comportement de rachat (lapse), souscription, ALM, simulation de longévité, optimisation d'hypothèses, détection de risques émergents, ORSA, dashboard, copilote IA et conformité réglementaire — soit **15 modules**, construits en solo avec des données publiques uniquement (aucune donnée assureur interne).

> ⚠️ Noms candidats encore à l'étude pour le rebranding final : ActuarIA, VitaCore, SolvencyOS, RiskVita, ActuaCopilot. Ce README utilise « VitaAI » par défaut — à mettre à jour une fois le nom arrêté.

---

## Table des matières

- [Vision et périmètre](#vision-et-périmètre)
- [État d'avancement](#état-davancement)
- [Architecture des modules](#architecture-des-modules)
- [Sources de données](#sources-de-données)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Tests](#tests)
- [Choix méthodologiques clés](#choix-méthodologiques-clés)
- [Feuille de route](#feuille-de-route)
- [Stack technique](#stack-technique)
- [Auteur](#auteur)

---

## Vision et périmètre

VitaAI est développé dans le cadre d'un mémoire de fin d'études en alternance, avec validation complète de la vision par le tuteur. Le projet vise une profondeur professionnelle sur les modules cœur de métier actuariel (M1–M7), avec une profondeur illustrative/prototype assumée sur les modules applicatifs et périphériques (M8–M15), compte tenu de la contrainte de 4 mois en solo.

## État d'avancement

| Bloc | Statut | Détail |
|---|---|---|
| **M1–M7** | ✅ Qualité professionnelle | Lee-Carter avec décomposition SVD, provisions prospectives validées par le principe d'équivalence actuarielle, SCR via courbes EIOPA, VaR de longévité par Monte Carlo |
| **M8–M15** | 🚧 Majoritairement des stubs | Aucune couche applicative (API, UI, infrastructure) n'existe encore |
| **Suite de tests** | 🟡 62 passed, 9 skipped | Les skips sont liés à l'absence des fichiers HMD volumineux en local |

## Architecture des modules

| # | Module | Rôle | Statut |
|---|---|---|---|
| M1 | Modélisation de la mortalité | Lee-Carter, décomposition SVD | ✅ |
| M2 | Tarification | GLM pricing | ✅ |
| M3 | Provisionnement | Provisions prospectives, équivalence actuarielle | ✅ |
| M4 | Solvabilité II / SCR | Courbes EIOPA RFR | ✅ |
| M5 | Comportement de rachat (lapse) | Basé sur le dataset Kaggle Life Insurance Retention | ✅ |
| M6 | Souscription (underwriting) | Basé sur le dataset Prudential Life Insurance | ✅ |
| M7 | Simulation de longévité | VaR par Monte Carlo | ✅ |
| M8 | ALM (Asset-Liability Management) | Duration de Macaulay, appariement actif/passif | 🚧 |
| M9 | Optimisation des hypothèses | — | 🚧 |
| M10 | Détection de risques émergents | Pas de source de données assignée — reporté | ⏸️ |
| M11 | ORSA | — | 🚧 |
| M12 | Dashboard | — | 🚧 |
| M13 | Copilote IA | — | 🚧 |
| M14 | Conformité réglementaire | — | 🚧 |
| M15 | Jumeau numérique (digital twin) | — | 🚧 |

## Sources de données

Le projet repose exclusivement sur des données publiques :

- **Human Mortality Database (HMD)** — `Mx_1x1.txt` et `Exposures_1x1.txt`, couvrant 1816–2023 → utilisé pour M1, M7, M9
- **Courbes EIOPA RFR** (ZIP de mai 2026, scénarios de stress inclus) → utilisé pour M4, M8
- **Kaggle Life Insurance Retention** (10 000 lignes, 14 colonnes) → utilisé pour M5 ; ne contient pas de label de churn explicite, nécessitant une dérivation
- **Kaggle Prudential Life Insurance** (`train.csv`) → destiné à M6
- **M10** : aucune source assignée à ce jour, module reporté

## Installation

```bash
git clone <url-du-repo>
cd actuarial_platform
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

Placez les fichiers de données requis dans `data/raw/` selon la structure attendue par chaque module (voir [Sources de données](#sources-de-données)).

## Utilisation

Exemple d'exécution du module ALM (M8) :

```bash
python -m src.m8_alm.alm
```

> ⚠️ Avant de relancer les tests M8, supprimez le cache obsolète des obligations synthétiques :
> ```powershell
> Remove-Item .\data\processed\synthetic_bonds.csv
> ```

## Tests

```bash
pytest tests/ -v
```

État actuel : **62 passed, 9 skipped** (skips liés à l'absence des fichiers HMD volumineux).

## Choix méthodologiques clés

- **Horizon de projection** : corrigé de 50 à 90 ans (la troncature à 50 ans sous-estimait silencieusement les provisions des jeunes assurés)
- **Duration de Macaulay (M8)** : calculée sur les flux de trésorerie bruts (benefit cash flows), et non sur les flux nets — les flux nets proches de l'équivalence actuarielle sont numériquement instables (dénominateur proche de zéro)
- **Valorisation du passif (M8)** : chaque police est plafonnée à zéro individuellement avant agrégation, plutôt que d'agréger des flux nets non signés — cohérent avec la méthodologie M3/M4, via `compute_total_best_estimate_with_curve`
- **Cache et données obsolètes** : tout cache dérivé (ex. obligations synthétiques) doit être invalidé après une correction en amont, sous peine de tests reflétant silencieusement d'anciennes valeurs

## Feuille de route

- [ ] Confirmer que le correctif M8 ALM résout les valeurs actif/passif négatives (`pytest tests/ -v` + vérification de la sortie de `python -m src.m8_alm.alm`)
- [ ] Trancher la règle de dérivation du label de rachat pour le dataset M5
- [ ] Identifier le bon fichier `train.csv` Prudential pour M6
- [ ] Avancer les stubs M8–M15 (profondeur prototype acceptée)
- [ ] Arrêter le nom final du projet
- [ ] Compléter le document de présentation CV avec les figures manquantes (valeurs SCR, montants VaR, nombre de lignes, itérations Monte Carlo)

## Stack technique

- **Langage** : Python
- **Tests** : pytest
- **Cadres actuariels** : Lee-Carter, décomposition SVD, Solvabilité II / SCR, courbes EIOPA RFR, VaR par Monte Carlo, duration de Macaulay, ALM, provisionnement prospectif, principe d'équivalence actuarielle, ORSA

## Auteur

**Yassine** — étudiant en double diplôme Data Science Engineering (ESPRIT, Tunisie) et Master Actuariat (Université du Mans, France), diplômé en août 2027. Profil hybride actuariat (tarification GLM, IBNR/Chain Ladder, Bornhuetter-Ferguson, Lee-Carter, IFRS 9, Solvabilité II) et data science/ML (CamemBERT, FastAPI, Docker, MLOps, RAG).
