---
quand_lire: Tu écris ou modifies du code ; tu dois lancer les tests, le lint ou le build ; tu hésites sur un choix de conception ou de nommage
couvre: pytest.ini, requirements.txt, tests/test_smoke.py, scripts/routeur.ps1
verifie: 2026-11-03
---
# Principes et commandes du projet

## Commandes
Ces commandes servent de critère de succès (voir AGENTS.md §4) : lance-les avant de conclure une tâche de code.
| Action | Commande |
|---|---|
| Tests | `python -m pytest` (`pytest.ini` : `pythonpath = src`, `testpaths = tests`) |
| Installer les dépendances | `pip install -r requirements.txt` (`pytest`, `requests`, `python-dotenv`, `trafilatura`) |
| Lint / format | `à compléter` (aucun outil configuré) |
| Lancement de l'agent (quota LLM consommé) | `python scripts\run_agent.py`, ou `.\scripts\run_daily.ps1` (avec log dans `data\logs`) |
| Planifier l'agent chaque jour à 8h | `.\scripts\register_task.ps1` (voir `memoire/resume.md`) |
| Build | `à compléter` (aucun build) |
| Essai réel du client LLM (un appel, quota consommé) | `python scripts\try_llm.py` |
| Essai réel de la collecte HN | `python scripts\try_hn.py` |
| Régénérer le routeur de mémoire | `.\scripts\routeur.ps1` |
| Vérifier la mémoire (aussi lancé par la CI) | `.\scripts\routeur.ps1 -Verifier` |

## Principes non négociables
- Aucun `.env` n'est lu, affiché, copié ni édité (`opencode.json` le bloque ; `*.env.example` reste autorisé). Aucune clé dans `.env.example` ni dans le code.
- Les tests ne font aucun appel réseau : `requests` et le client LLM sont remplacés par de faux objets (`monkeypatch`).
- Pas de commit, de push ni de changement de branche sans demande explicite de l'utilisateur (`RULES.md`).
- `memoire/ROUTEUR.md` est généré : ne pas le modifier à la main.

## Conventions de code
- Code (variables, noms de fichiers) en anglais ; documentation et échanges en français.
- Python, fonctions simples, pas d'abstraction inutile ; constantes de réglage en tête de module (`MIN_POINTS`, `MAX_CHARS`…).
- Fichiers en UTF-8, chemins Windows avec `\` (sauf fichiers de configuration multi-plateformes).
- Un script durable s'écrit dans `scripts/`. Les scripts d'essai insèrent `src` dans `sys.path`.
- Une branche par phase de développement, merge par PR.

## Interdits
- Sous PowerShell 5.1 en mode restreint : pas de méthode statique .NET (`[IO.File]::…`), pas de `New-Object`, pas de `Add-Type`.
- `git push`, `git reset --hard`, `git clean` et les suppressions demandent confirmation (`opencode.json`).
