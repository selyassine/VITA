# Dashboard Plateforme Actuarielle Vie

Site web de présentation des résultats du mémoire d'actuariat - 15 modules simulant une compagnie d'assurance-vie.

## Installation

```bash
cd actuarial-dashboard
npm install
```

## Lancement du site

```bash
npm run dev
```

Le site sera accessible sur `http://localhost:3000` (ou 3001 si le port 3000 est déjà utilisé).

## Identifiants de connexion

- **Identifiant** : `jury`
- **Mot de passe** : `actuariat2026`

Ces identifiants sont codés en dur dans `src/auth.ts` pour la démo. En production, ils devraient être remplacés par des variables d'environnement.

## Structure du site

### Pages principales

- **`/login`** - Page de connexion
- **`/accueil`** - Page d'accueil avec contexte, architecture et vue d'ensemble des 15 modules
- **`/modules`** - Index des 15 modules organisés par groupes thématiques
- **`/modules/[id]`** - Pages individuelles de chaque module (M1-M15)
- **`/methodologie`** - Notes méthodologiques (bugs trouvés et corrigés)
- **`/demo`** - Tester en direct (calculs interactifs M2 et M9)

### Modules détaillés créés

- **M1 - Mortalité** (`/modules/m1-mortalite`) : Modèle Lee-Carter
- **M4 - SCR** (`/modules/m4-scr`) : Capital réglementaire Solvabilité II
- **M8 - ALM** (`/modules/m8-alm`) : Bilan actif/passif, duration gap

Les autres modules peuvent être ajoutés sur le même modèle.

## Stack technique

- **Next.js 16** avec App Router
- **TypeScript**
- **Tailwind CSS 4**
- **NextAuth** pour l'authentification
- **Lucide React** pour les icônes
- **Recharts** (installé, non utilisé dans cette version)

## Design

- Palette sobre : bleu marine, gris, blanc, bleu accent
- Typographie Inter
- Responsive (desktop et mobile)
- Navigation sidebar/menu hamburger

## Données

Le site lit directement les fichiers générés par le pipeline Python :

- `../actuarial_platform/outputs/reports/digital_twin_report.json` - Résultats agrégés
- `../actuarial_platform/outputs/figures/*.png` - Graphiques

## Personnalisation

Pour modifier les identifiants de connexion, éditez `src/auth.ts` :

```typescript
const validUsername = "votre_identifiant";
const validPassword = "votre_mot_de_passe";
```

## Déploiement

Pour un déploiement en production :

1. Configurer les variables d'environnement pour NextAuth
2. Remplacer les identifiants codés en dur
3. Builder avec `npm run build`
4. Lancer avec `npm start`
