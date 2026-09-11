# Référence gitmoji — Prism

Utiliser **un seul** emoji par commit, en première position. Le type Conventional Commit reste obligatoire après l'emoji.

## Mapping principal

| Gitmoji | Type | Quand l'utiliser |
|---------|------|------------------|
| ✨ | `feat` | Nouvelle fonctionnalité, endpoint, module, capability |
| 🐛 | `fix` | Correction de bug |
| 🔧 | `chore` | Maintenance, tooling, config, deps mineures, housekeeping |
| ♻️ | `refactor` | Restructuration sans changement de comportement |
| 📝 | `docs` | Documentation uniquement |
| ✅ | `test` | Ajout ou modification de tests |
| 🎨 | `style` | Formatage, lint, whitespace (pas de logique) |
| ⚡️ | `perf` | Amélioration de performance |
| 🔒 | `fix` ou `chore` | Correctif ou durcissement sécurité |
| 🏗️ | `refactor` | Changement structurel d'architecture |
| 🚚 | `refactor` | Déplacement / renommage de fichiers |
| 🔥 | `chore` | Suppression de code ou fichiers morts |
| ➕ | `chore` | Ajout de dépendance |
| ➖ | `chore` | Suppression de dépendance |
| ⬆️ | `chore` | Mise à jour de dépendances |
| 🐳 | `chore` | Docker / conteneurs |
| 💚 | `ci` | Correction ou amélioration CI |
| 👷 | `ci` | Ajout ou modification de pipeline CI |
| 🔀 | `chore` | Merge de branches (rare en commit direct) |

## Scopes Prism

| Scope | Périmètre |
|-------|-----------|
| `ml-engine` | `services/ml-engine/` — API Python, notebooks, modèles |
| `gateway` | `services/gateway/` — API Node.js |
| `dashboard` | `apps/dashboard/` — frontend React |
| `infra` | Docker, Compose, CI, déploiement |
| `root` | Racine du monorepo (README, config globale, `.ai/`) |

Choisir le scope le plus précis. En cas de doute entre deux scopes, **scinder en deux commits**.

## Types rares

| Type | Gitmoji suggéré | Usage |
|------|-----------------|-------|
| `build` | 📦 | Système de build, bundler |
| `revert` | ⏪ | Revert d'un commit précédent |

Pour un `BREAKING CHANGE`, ajouter en footer :

```
BREAKING CHANGE: description courte de l'impact
```

Le sujet peut rester au format habituel ; le breaking change va dans le corps/footer (Conventional Commits).
