# Plateforme Actuarielle Vie — 15 Modules

Plateforme modulaire simulant les fonctions clés d'une compagnie d'assurance-vie :
tarification, provisionnement, capital réglementaire (Solvabilité II), rachats,
souscription, longévité, ALM, ORSA, dashboard exécutif, copilote IA, conformité
réglementaire et jumeau numérique.

## Architecture

```
.
├── config/
│   └── config.yaml          # Point de vérité unique : chemins, paramètres, chocs SCR
├── data/
│   ├── raw/                 # Données sources, jamais modifiées à la main
│   └── processed/           # Données nettoyées / générées (ex: portefeuille synthétique)
├── src/
│   ├── common/               # Code partagé par tous les modules
│   │   ├── config_loader.py
│   │   └── synthetic_portfolio.py
│   ├── m1_mortality/         # ✅ Fonctionnel (Lee-Carter sur données HMD réelles)
│   ├── m2_pricing/           # ✅ Fonctionnel (prime pure par équivalence actuarielle)
│   ├── m3_reserving/         # ✅ Fonctionnel (provision mathématique, méthode prospective)
│   ├── m4_scr/                # ✅ Fonctionnel (SCR mortalité/longévité/taux, données EIOPA réelles)
│   ├── m5_lapse/              # ✅ Fonctionnel (label de résiliation dérivé, données synthétiques)
│   ├── m6_underwriting/      # ✅ Fonctionnel (baseline Random Forest sur Prudential réel)
│   ├── m7_longevity/          # ✅ Fonctionnel (VaR 99.5% par simulation Monte-Carlo Lee-Carter)
│   ├── m8_alm/                 # ✅ Fonctionnel (duration gap actif/passif, sensibilité NAV aux taux)
│   ├── m9_optimizer/          # ✅ Fonctionnel (chargement optimal, arbitrage marge/rachat)
│   ├── m10_emerging_risk/    # ✅ Fonctionnel (comparaison thématique EIOPA vs ACPR — voir limites ci-dessous)
│   ├── m11_orsa/               # ✅ Fonctionnel (projection pluriannuelle run-off)
│   ├── m12_dashboard/         # ✅ Fonctionnel (6 graphiques de synthèse, robustesse par échec isolé)
│   ├── m13_copilot/           # ✅ Fonctionnel (outils testés ; boucle API nécessite ANTHROPIC_API_KEY)
│   ├── m14_compliance/        # ✅ Fonctionnel (checklist documentaire ORSA/Solvabilité II)
│   └── m15_digital_twin/     # ✅ Fonctionnel (orchestration complète M1-M14, export JSON)
├── notebooks/                 # Exploration UNIQUEMENT — jamais de logique de production ici
├── tests/                      # Tests unitaires pytest
├── outputs/
│   ├── figures/               # Graphiques générés
│   └── reports/               # Rapports/exports générés
└── requirements.txt
```

## Principe d'architecture

**Séparation stricte exploration / production.** Les notebooks servent à explorer
un dataset ou tester une idée rapidement — ils ne contiennent jamais de logique
réutilisée par un autre module. Toute logique qui doit être réutilisée (par un
autre module, par les tests, ou par le mémoire final) est extraite dans un
fichier `.py` de `src/`.

**Un seul portefeuille synthétique.** Généré une fois via
`src/common/synthetic_portfolio.py`, persisté dans
`data/processed/synthetic_portfolio.csv`, puis réutilisé à l'identique par
M2, M3, M8, M9, M11, M12, M13, M15. Ne jamais le régénérer avec une seed
différente en cours de projet.

**Une seule configuration.** Tous les chemins et paramètres (y compris les
chocs réglementaires SCR, valeurs fixes publiques) sont dans `config/config.yaml`,
chargés via `src/common/config_loader.py`. Aucun chemin ou paramètre ne doit
être codé en dur dans un module métier.

## Données requises (à déposer avant utilisation)

| Fichier | Destination | Source | Statut |
|---|---|---|---|
| `Mx_1x1.txt` | `data/raw/hmd/` | mortality.org (compte requis) | À redéposer |
| `Exposures_1x1.txt` | `data/raw/hmd/` | mortality.org | À redéposer |
| `EIOPA_RFR_20260531.zip` | `data/raw/eiopa/EIOPA_RFR_20260531/` (dézippé) | eiopa.europa.eu (public) | ✅ **Déjà en place** |
| `archive (8).zip` (Retention) | `data/raw/kaggle_retention/` (dézippé) | Kaggle | ✅ **Déjà en place** |
| `train.csv` (Prudential) | `data/raw/kaggle_prudential/` | Kaggle | ✅ **Déjà en place** |

> Ces fichiers ne sont volontairement pas inclus dans cette archive (trop
> volumineux / conditions de licence Kaggle). Une fois redéposés aux bons
> emplacements, tous les modules fonctionnels (M1, M6) et les tests associés
> s'exécutent directement.

## Nature des données (à rappeler dans le mémoire)

| Source | Nature |
|---|---|
| HMD | Réelle officielle |
| EIOPA | Réelle officielle |
| Kaggle Prudential | Réelle tierce, anonymisée |
| Kaggle Retention | **Synthétique tierce** (plateforme Mostly AI — corrigé après inspection, classée "réelle" par erreur initialement), **label de résiliation dérivé** (absent du dataset d'origine) |
| Portefeuille synthétique | Synthétique maison, généré une seule fois |

### Limite méthodologique — label de résiliation dérivé (M5)

Le dataset Kaggle Retention ne contient aucune colonne de résiliation. Le
label binaire `lapsed` est **entièrement dérivé** via un score de propension
combinant des facteurs actuariels connus (ratio prime/revenu, "bosse de
rachat" par ancienneté, personnes à charge, statut de santé, type de police),
transformé en probabilité (fonction logistique) puis tiré aléatoirement,
calibré pour un taux global cible de 17,5%. **Ce label ne reflète aucun
événement réel de rachat** — c'est une construction statistique plausible
pour démontrer la méthodologie de modélisation (voir docstring complète dans
`src/m5_lapse/loader.py`), à rappeler explicitement à chaque utilisation des
résultats de M5 dans le mémoire.

### Limite méthodologique connue — portefeuille synthétique

Pour les produits à risque décès, la **prime commerciale** du portefeuille
synthétique (`prime_annuelle_eur`) est calibrée via une courbe de mortalité
approximative de type Gompertz (voir `_approx_mortality_rate` dans
`src/common/synthetic_portfolio.py`) — volontairement indépendante de M1,
pour que le portefeuille reste générable seul, sans dépendre d'un fit
Lee-Carter préalable. La **prime pure** calculée par M2 utilise, elle, les
vraies données HMD via Lee-Carter. Les deux courbes ne coïncident pas
exactement, ce qui explique un chargement implicite (`chargement_implicite_pct`)
parfois marqué à la hausse ou à la baisse selon l'âge — **à documenter
explicitement comme limite du caractère synthétique du portefeuille**, pas
comme un résultat de tarification représentatif d'un vrai assureur.

Ordre de grandeur observé après recalibrage (chargement implicite médian) :
Temporaire Décès ~180%, Prévoyance ~185%, Vie Entière ~-4% (proche de 0).
Une médiane élevée sur les produits temporaires reste cohérente avec la
réalité (frais fixes proportionnellement plus lourds sur les petits
capitals), mais la dispersion (jusqu'à ~1900% en queue) est un artefact du
caractère synthétique, pas une prédiction de marge réelle.

Voir `docs/architecture.md` pour le détail des dépendances entre modules.

## Installation

```bash
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## Utilisation

```bash
# Depuis la racine du projet, avec le venv activé :

# M1 - Ajuster Lee-Carter et projeter la mortalité
python -m src.m1_mortality.lee_carter

# M2 - Calculer les primes pures du portefeuille (dépend de M1 + HMD)
python -m src.m2_pricing.pricing

# M3 - Calculer les provisions mathématiques du portefeuille (dépend de M1 + HMD)
python -m src.m3_reserving.reserving

# M4 - Calculer le SCR (dépend de M1 + M3 + HMD + EIOPA)
python -m src.m4_scr.scr

# M7 - Simuler le risque de longévité par Monte-Carlo (dépend de M1 + HMD)
python -m src.m7_longevity.longevity

# M5 - Charger les données de rachat et dériver le label de résiliation
python -m src.m5_lapse.loader

# M9 - Optimiser le chargement commercial (dépend de M1 + M2 + M4 + HMD)
python -m src.m9_optimizer.optimizer

# M8 - Calculer le bilan ALM et la duration gap (dépend de M1 + M4 + HMD + EIOPA)
python -m src.m8_alm.alm

# M10 - Comparaison thématique des risques émergents (EIOPA vs ACPR)
python -m src.m10_emerging_risk.emerging_risk

# M6 - Entraîner le modèle d'underwriting baseline
python -m src.m6_underwriting.model

# M11 - Projection ORSA pluriannuelle (run-off)
python -m src.m11_orsa.orsa

# M12 - Générer le dashboard exécutif (6 graphiques PNG dans outputs/figures/)
python -m src.m12_dashboard.dashboard

# M13 - Copilote IA (nécessite ANTHROPIC_API_KEY)
python -m src.m13_copilot.copilot

# M14 - Checklist de conformité documentaire ORSA/Solvabilité II
python -m src.m14_compliance.compliance

# M15 - Digital Twin : orchestration complète, export JSON dans outputs/reports/
python -m src.m15_digital_twin.digital_twin

# Lancer tous les tests
pytest tests/ -v

# Lancer les tests avec couverture
pytest tests/ --cov=src --cov-report=html
```

> **Note sur le temps d'exécution des tests** : la suite complète (103 tests)
> peut prendre plusieurs minutes, notamment les tests d'intégration de M11,
> M12, M14 et M15 qui exécutent plusieurs modules lourds en chaîne (Lee-Carter,
> SCR, ALM...). Si `pytest tests/ -v` semble bloqué, c'est normal — laisser
> tourner, ou lancer les fichiers de test un par un pour un retour plus rapide.

## État d'avancement des modules

**Les 15 modules sont fonctionnels et testés.**

- M1 (mortalité, Lee-Carter complet)
- M2 (pricing, prime pure par équivalence actuarielle)
- M3 (reserving, provision mathématique par méthode prospective)
- M4 (SCR — mortalité +15%, longévité -20%, taux via courbes EIOPA réelles)
- M5 (lapse — label de résiliation dérivé par score actuariel calibré)
- M6 (underwriting, baseline Random Forest entraîné)
- M7 (longevity — VaR 99.5% par simulation Monte-Carlo des trajectoires
  Lee-Carter, complémentaire du choc déterministe de M4)
- M8 (ALM — bilan actif synthétique vs passif réel, duration de Macaulay,
  sensibilité du NAV aux chocs de taux EIOPA)
- M9 (optimizer — chargement commercial optimal par arbitrage marge/rachat,
  impact sur le SCR via M4)
- M10 (emerging risk — comparaison thématique EIOPA vs ACPR, voir limites ci-dessous)
- M11 (ORSA — projection pluriannuelle run-off du Best Estimate, du SCR et
  du ratio de couverture)
- M12 (dashboard — 6 graphiques de synthèse exportés en PNG, robuste aux
  échecs partiels de modules sous-jacents)
- M13 (copilot — outils de requête en langage naturel sur les résultats de
  la plateforme ; la boucle d'appel API nécessite `ANTHROPIC_API_KEY`, non
  configurée dans l'environnement de développement de ce projet — voir note
  ci-dessous)
- M14 (compliance — checklist documentaire de complétude ORSA/Solvabilité II,
  PAS un avis juridique — voir note ci-dessous)
- M15 (digital twin — orchestration complète de M1 à M14 en un seul passage,
  export JSON dans `outputs/reports/`)

### Note méthodologique M13 — copilote non testé de bout en bout

Le module M13 (copilot) sépare volontairement les définitions d'outils et
leur dispatch (`tools.py`, entièrement testé sans réseau) de la boucle
d'appel à l'API Anthropic (`copilot.py`, nécessite `ANTHROPIC_API_KEY`).
Cette clé n'était pas configurée dans l'environnement de développement de
ce projet : la boucle d'appel API n'a donc **pas pu être testée de bout en
bout**. Pour l'utiliser, définir la variable d'environnement puis lancer
`python -m src.m13_copilot.copilot`.

### Note méthodologique M14 — ce que la checklist n'est PAS

M14 est une checklist d'**auto-vérification documentaire** (la plateforme
a-t-elle produit une preuve chiffrée pour chaque grande rubrique qu'un
rapport ORSA/SFCR est censé couvrir ?) — **pas un avis juridique**, ni une
certification de conformité réglementaire réelle. À rappeler explicitement
si cette section est citée dans le mémoire.

### Note méthodologique M10 — recadrage de périmètre et limites de reproductibilité

**Recadrage assumé** : l'ambition initiale ("détecteur de tendance temporelle
des risques émergents") nécessitait des éditions SUCCESSIVES d'un même
rapport. Les 3 documents disponibles (1 EIOPA Financial Stability Report +
2 rapports ACPR différents, pas des éditions successives) ne permettent pas
cela. Le module a été recadré en **comparaison thématique inter-rapports**
(européen EIOPA vs français ACPR) — un résultat différent mais tout aussi
valide et défendable : le rapport EIOPA aborde massivement cyber, IA et
immobilier/liquidité (~7-8 occurrences pour 1000 mots), tandis que les
publications ACPR analysées restent quasi silencieuses sur ces thèmes,
davantage centrées sur les flux/solvabilité. Ce contraste entre niveaux de
supervision est en soi un résultat citable.

**Limite de reproductibilité importante** : contrairement à HMD/EIOPA(taux)/
Kaggle, les comptages de mots-clés (`data/raw/m10_emerging_risk/keyword_counts.csv`)
n'ont PAS été extraits par un script déterministe propre à ce projet — ils
proviennent d'une analyse assistée par un autre modèle de langage sur le
texte des PDF sources (nécessaire car l'environnement de développement ne
pouvait pas télécharger les PDF lui-même). **À documenter explicitement dans
le mémoire comme limite de reproductibilité stricte.** Un script d'extraction
déterministe est fourni (`src/m10_emerging_risk/extract_from_pdfs.py`,
regex + `pdfplumber`) mais n'a pas pu être exécuté faute d'accès direct aux
PDF dans cet environnement — si les PDF sources sont un jour déposés dans
`data/raw/m10_emerging_risk/*.pdf`, lancer ce script régénère la table de
façon entièrement auditable, remplaçant les comptages actuels.

Édition EIOPA manquante pour une vraie analyse de tendance temporelle (ex.
juin 2025) : peut être ajoutée plus tard, non bloquant pour l'état actuel.

### Note méthodologique M8

Résultat observé sur données de test : duration du passif ~13 ans (calculée
sur les prestations seules — voir correction ci-dessous), duration de
l'actif obligataire ~9 ans (maturité max 20 ans) — un décalage de duration
modéré mais réel. Le NAV réagit de façon cohérente aux chocs de taux (gain
si les taux montent, perte si les taux baissent).

**Correction importante n°1 — instabilité de la duration du passif** : la
duration était initialement calculée sur le flux NET (prestations - primes)
du portefeuille. Sur données réelles, cela produisait une duration
**négative** (-2,9 ans), résultat inutilisable. Cause : les produits
Temporaire/Prévoyance ont un chargement commercial élevé (voir note M2),
générant un flux net fortement négatif sur une grande partie de leur durée,
tandis que la Vie Entière génère un flux positif étalé sur plusieurs
décennies — la combinaison peut faire basculer la moyenne pondérée par le
temps en territoire négatif (démontré par un test de non-régression dédié).
**Corrigé** : la duration de référence du passif est désormais calculée sur
les **prestations seules** (toujours positive par construction), conforme à
la pratique standard en ALM qui aligne l'actif sur l'écoulement attendu des
sinistres plutôt que sur un flux net potentiellement instable.

**Correction importante n°2 — passif et bilan entièrement négatifs** :
suite à la correction n°1, un second problème est apparu : la VALEUR du
passif (`liability_value_central`) était calculée en agrégeant D'ABORD tous
les flux de prestations et de primes du portefeuille, PUIS en soustrayant —
sans jamais plafonner à 0 par contrat comme le font M3/M4. L'excès de primes
de contrats Temporaire/Prévoyance surchargés compensait artificiellement les
prestations d'autres contrats, faisant passer le passif total en négatif,
ce qui se propageait en cascade (montant cible des obligations négatif ->
notional négatif -> bilan actif entièrement négatif). **Corrigé** : la
valeur du passif réutilise désormais directement la fonction de M4 déjà
testée et validée (`compute_total_best_estimate_with_curve`), qui applique
le plafonnement à 0 **par contrat**, garantissant la cohérence avec M3/M4.
Un test de non-régression vérifie désormais que toutes les valeurs du bilan
(passif, obligations, actions, immobilier, total) restent strictement
positives. **Si tu as déjà des chiffres M8 cités quelque part, il faut les
relancer avec cette version corrigée.**

Limites d'assumées : actions et immobilier traités comme des montants de
valeur de marché sans sensibilité aux taux modélisée (duration = 0, leur
risque relève d'autres sous-modules SCR hors périmètre).

### Note méthodologique M5

Voir la section "Nature des données" plus haut pour le détail complet de la
règle de dérivation du label. Résultat observé sur les données réelles :
taux global 17,8% (cible 17,5%), avec un gradient cohérent par type de police
(Term Life 24,4% > Universal Life 11,4% > Variable Life 9,6% > Whole Life
7,5%) — comportement actuariel attendu (les produits sans valeur de rachat
sont davantage résiliés), qui valide que la règle produit un signal cohérent,
pas seulement un taux global correct par coïncidence.

### Note méthodologique M7

Le portefeuille est regroupé par profil (produit, genre, âge) avant simulation
pour rester performant (des milliers de contrats × centaines de trajectoires
serait sinon prohibitif). Le nombre de simulations est réduit à 200 (contre
1000 dans M1/M4) pour un temps de calcul raisonnable — limite à documenter,
un intervalle de confiance sur la VaR elle-même nécessiterait davantage de
simulations. Un léger écart entre le Best Estimate moyen simulé et le Best
Estimate central déterministe de M3 est normal (effet de convexité en
modélisation stochastique), pas une erreur.

### Note méthodologique M9 — périmètre restreint à la protection pure

Le modèle d'arbitrage marge/rachat (chargement commercial vs élasticité de
rachat) est appliqué UNIQUEMENT aux produits de protection pure (Temporaire
Décès, Prévoyance). La Vie Entière est explicitement exclue : appliquer un
chargement commercial uniforme optimisé sur ce seul critère écraserait sa
provision mathématique à 0 (observé et corrigé en développement), car sa
fonction d'épargne implicite est incompatible avec ce modèle simplifié. Le
chargement optimal obtenu (fermé analytiquement à `1 + 1/lapse_elasticity`)
est aussi indépendant de la prime pure et de la rente de survie de chaque
contrat, du fait de l'hypothèse d'élasticité de rachat uniforme sur tout le
périmètre — une version plus fine ferait varier cette élasticité par segment.

### Correction importante — horizon de projection Lee-Carter

L'horizon de projection (`lee_carter.forecast_horizon`) était initialement
fixé à 50 ans, insuffisant pour couvrir un contrat Vie Entière souscrit à 18
ans (jusqu'à 82 ans de projection nécessaires jusqu'à l'âge limite de 100
ans). Cela tronquait **silencieusement** la couverture des jeunes assurés
dans M2/M3/M4, sous-estimant le Best Estimate (~87M€ au lieu de ~99M€ sur
données de test, soit un écart de 2,6x avant correction). Le bug a été
détecté par recoupement avec M7 (dont l'horizon est calculé dynamiquement).
Corrigé à 90 ans avec marge de sécurité ; une troncature est désormais
explicitement journalisée (avertissement) si elle survient malgré tout.
**Si tu as déjà cité des résultats M2/M3/M4 dans une version antérieure du
mémoire, il faut les relancer avec cette version corrigée.**

## Prochaines étapes suggérées

Les 15 modules sont fonctionnels. Pistes d'amélioration optionnelles :

1. Configurer `ANTHROPIC_API_KEY` et tester M13 (copilot) de bout en bout
2. Ajouter une édition EIOPA supplémentaire (ex. juin 2025) pour une vraie
   analyse de tendance temporelle sur M10 (actuellement une comparaison
   thématique inter-rapports, pas une tendance dans le temps)
3. Déposer les PDF sources dans `data/raw/m10_emerging_risk/` et lancer
   `extract_from_pdfs.py` pour une extraction pleinement reproductible
   (remplacerait les comptages obtenus par analyse assistée par IA)
4. Relire l'ensemble des notes méthodologiques ci-dessus (M2, M5, M7, M8, M9,
   M10, M13, M14) pour la partie limites/discussion du mémoire — chaque bug
   trouvé et corrigé pendant le développement y est documenté avec sa cause
   racine, ce qui constitue en soi une démonstration de rigueur méthodologique
5. (Optionnel) Étendre M6 (`quick=False` dans M15) pour inclure l'entraînement
   complet du modèle à chaque exécution du digital twin, actuellement limité
   aux statistiques du jeu de données en mode rapide
