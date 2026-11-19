# Démarrer en local

Prérequis : Python 3.11+.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e "robot-stub[dev]" -e "server[dev]"   # Windows
# .venv/bin/python ... sous Linux / macOS
```

## Lancer

```bash
# 1. Robot simulé (profil tonypi ou ainex)
cd robot-stub && ../.venv/Scripts/python -m robot_stub --profile ainex --port 8100

# 2. Serveur (SQLite par défaut ; AUTOALFRED_DATABASE_URL pour PostgreSQL)
cd server && ../.venv/Scripts/python -m uvicorn autoalfred.main:app --reload --port 8000
```

API documentée sur http://localhost:8000/docs.
Enregistrer la cible : `POST /targets` avec `{"name": "sim-ainex", "kind": "simulator", "mcp_url": "http://127.0.0.1:8100/mcp", "robot_model": "ainex"}`.

## Tests

```bash
cd robot-stub && ../.venv/Scripts/python -m pytest
cd server && ../.venv/Scripts/python -m pytest
```

## Organisation

| Dossier | Contenu |
|---|---|
| `robot-stub/` | Serveur MCP simulé : monde, scénarios (ranger, retrouver, lire_web, imprevu), profils TonyPi / AiNex |
| `server/` | API FastAPI : cibles, versions du harness (immuables, diff, rollback), missions, traces |
| `webapp/` | À venir |

## Règles d'architecture

- L'agent n'utilise que `navigate_to`, `look`, `detect`, `pick`, `place`, `read_text` (robot) et `web_search`, `ask_human` (fournis par le serveur). Les outils `sim_*` et `robot_info` sont réservés à la plateforme.
- Une version du harness ne se modifie jamais : on en crée une nouvelle (`parent_id`), et le rollback consiste à réactiver une ancienne version sur la cible.
- Les échecs de mission sont des résultats (`ok: false` + message), pas des exceptions : l'agent doit pouvoir les analyser.
