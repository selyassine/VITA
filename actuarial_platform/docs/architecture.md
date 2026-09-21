# Graphe de dépendances entre modules

```
M1 (Mortalité, HMD)
 ├─→ M2 (Pricing)
 │    └─→ M3 (Reserving)
 │         └─→ M4 (SCR) ←── EIOPA (courbes de taux)
 │              └─→ M8 (ALM) ←── EIOPA
 ├─→ M7 (Longevity)
 └─→ M9 (Optimizer) ←── M2, M4

M5 (Lapse) ←── Kaggle Retention (label dérivé)
M6 (Underwriting) ←── Kaggle Prudential          [indépendant, déjà fonctionnel]

M9, M1-M8 ─→ M11 (ORSA)
M1-M11    ─→ M12 (Dashboard)
Tous       ─→ M13 (Copilot, orchestration API)
EIOPA/ACPR ─→ M14 (Compliance)
Tous       ─→ M15 (Digital Twin)                  [à construire en dernier]

M10 (Emerging Risk) — isolé, source de données non tranchée
```

## Ordre d'implémentation recommandé

1. **M1** ✅ — fait, base de tout le reste
2. **M6** ✅ — fait, indépendant, peut être fait en parallèle
3. **M2** — dépend uniquement de M1 (déjà disponible)
4. **M3** — dépend de M1 + M2
5. **M4** — dépend de M3 + données EIOPA (à redéposer)
6. **M5** — dépend uniquement des données Retention (à redéposer + label à définir)
7. **M7** — dépend uniquement de M1
8. **M8** — dépend de M4
9. **M9** — dépend de M1, M2, M4 (orchestration, pas de nouveau calcul lourd)
10. **M11** — dépend de M1-M9 (orchestration)
11. **M12** — dépend de tout (visualisation)
13. **M14** — indépendant des autres modules calculatoires (textes réglementaires)
14. **M13** — dépend de tout (copilote, wrappers)
15. **M15** — dépend de tout, à construire en tout dernier

## Portefeuille synthétique — schéma des colonnes

Généré par `src/common/synthetic_portfolio.py`, persisté dans
`data/processed/synthetic_portfolio.csv` :

| Colonne | Type | Description |
|---|---|---|
| `policy_id` | str | Identifiant unique du contrat |
| `age_souscription` | int | Âge à la souscription (18-70) |
| `anciennete_annees` | int | Ancienneté du contrat (0-25 ans) |
| `age_actuel` | int | Âge actuel de l'assuré |
| `genre` | str | M / F |
| `produit` | str | Un des 5 produits (Temporaire Décès, Vie Entière, Épargne Euro, Épargne UC, Prévoyance) |
| `fumeur` | int | 0 / 1 |
| `statut_sante` | str | standard / aggrave / surprime |
| `prime_annuelle_eur` | float | Prime annuelle payée |
| `capital_assure_eur` | float | Capital sous risque |

## Config partagée — `config/config.yaml`

Toute constante réutilisée par plusieurs modules (chemins de données, chocs
SCR réglementaires, paramètres Lee-Carter) vit dans ce fichier unique. Un
module métier ne doit jamais coder en dur un chemin de fichier ou un
paramètre partagé.
