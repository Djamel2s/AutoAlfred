# AutoAlfred
### Self-Improving

**Un robot autonome capable d'améliorer ses propres stratégies d'exécution grâce à l'expérimentation, à l'évaluation et à l'apprentissage de ses expériences.**

## Vision

Développer un robot multitâche capable d'exécuter des missions, d'analyser ses échecs et d'améliorer progressivement la manière dont il les réalise.

Contrairement à un robot reposant uniquement sur des comportements prédéfinis, AutoAlfred dispose d'un système d'auto-amélioration (*Self-Improving Harness*) qui expérimente différentes stratégies, mesure leurs performances et conserve uniquement les améliorations validées.

## Fonctionnement

1. **Perceive** — Observer et comprendre son environnement.
2. **Plan** — Décomposer une mission en actions et sélectionner les outils nécessaires.
3. **Execute** — Réaliser la mission à l'aide de ses outils + capacités robotiques.
4. **Analyze** — Collecter les traces d'exécution, détecter les erreurs et identifier les points faibles.
5. **Improve** — Générer et tester de nouvelles stratégies d'exécution.
6. **Validate** — Comparer les résultats, valider les améliorations et revenir en arrière en cas de régression.

## Self-Improving Harness

Le cœur du projet est un système capable de faire évoluer les mécanismes qui pilotent le robot :

- Stratégies de planification et d'exécution.
- Instructions et configurations des modèles.
- Sélection et utilisation des outils.
- Gestion de la mémoire et des expériences.
- Récupération après erreur et adaptation aux situations imprévues.

Les améliorations sont expérimentées dans un environnement contrôlé avant toute adoption sur le robot physique.

## Architecture

| Brique | Rôle |
|---|---|
| LLM / VLM | Raisonnement, planification, compréhension visuelle |
| Routing de modèles | Modèle local pour les tâches simples, modèle API pour les tâches complexes |
| Planner / Executor / Critic | Planifier la mission, l'exécuter, juger le résultat |
| MCP Tools | Capacités du robot (moteurs, caméra, capteurs) et recherche web |
| Skills | Procédures réutilisables, versionnées et améliorables |
| CAG | Connaissances stables préchargées : règles, carte, fiche robot |
| RAG | Mémoire épisodique : missions passées, échecs, stratégies efficaces |
| Reflexion | Analyse des échecs et formulation de leçons |
| Perception | VLM, OCR, détection d'objets |
| Simulation + ROS 2 | Tests des stratégies avant exécution réelle |
| Observabilité | Tracing, evals, versioning du harness |

## Architecture système

| Couche | Rôle | Responsable |
|---|---|---|
| Serveur | Agent IA, mémoire, skills, auto-amélioration, stockage des traces | Data/IA |
| Webapp | Lancement des missions, suivi en direct, monitoring, validation humaine, rollback | Data/IA |
| Robot / Simulateur | Serveur MCP exposant les primitives, contrôle moteur, sécurité locale | Robotique |

### Ce qui évolue / ce qui est fixe

| Harness (auto-amélioré) | Infrastructure (fixe) |
|---|---|
| Prompts, skills, stratégie de planification, guidage des outils, règles de récupération, mémoire, routing | Modèles, tools MCP, ROS 2, guardrails, plateforme d'évaluation, jeu de test |

Les guardrails et le jeu de test sont hors de portée de l'auto-amélioration : l'agent ne peut pas modifier ce qui le juge.

## Evaluation & Monitoring Platform

Une plateforme indépendante permet de suivre et comparer les performances du robot et de ses différentes versions.

| Dimension | Indicateurs |
|---|---|
| Réussite | Taux de réussite des missions |
| Qualité | Exactitude et respect des objectifs |
| Robotique | Précision des actions et erreurs physiques |
| IA | Performances des modèles et des outils |
| Performance | Latence et durée d'exécution |
| Coût | Tokens, appels API et coût par mission réussie |
| Fiabilité | Incidents, échecs et régressions |
| Évolution | Gains obtenus entre les versions |

Chaque expérimentation est tracée et reproductible. Toute amélioration doit être validée avant son déploiement, avec possibilité de rollback.

## Démonstration cible

Un robot reçoit une mission qu'il ne maîtrise pas parfaitement.

- Il tente de la réaliser.
- Le système identifie ses erreurs et ses inefficacités.
- Il propose une nouvelle stratégie.
- Il expérimente cette stratégie dans un environnement contrôlé.
- Il compare les résultats avec sa version précédente.
- Il adopte l'amélioration si elle apporte un gain mesurable.

La démonstration doit rendre visible l'évolution des capacités du robot, et pas seulement son aptitude à exécuter une tâche.

## Missions

| Mission | Capacité testée |
|---|---|
| Ranger des objets | Perception, planification, manipulation |
| Retrouver un objet décrit vaguement | Exploration, mémoire |
| Lire un document et compléter l'info via le web | OCR, web, raisonnement |
| Préparer un poste avec imprévu | Replanification, récupération d'erreur |
| Traiter une instruction ambiguë | Clarification plutôt que supposition |

Évaluation finale sur un jeu indépendant : mêmes types de missions, environnements et formulations jamais vus pendant l'optimisation.

## Outils MCP

`navigate_to` · `look` · `detect` · `pick` · `place` · `read_text` · `web_search` · `ask_human`

L'agent n'accède qu'à ces primitives de haut niveau. Le contrôle moteur bas niveau reste côté robotique.

## Objectif final

**Construire un robot qui ne se contente pas d'exécuter des instructions, mais qui améliore progressivement sa manière de les exécuter, tout en étant capable de démontrer et de mesurer ses progrès.**