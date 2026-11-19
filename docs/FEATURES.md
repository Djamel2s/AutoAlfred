# AutoAlfred — Fonctionnalités de la plateforme (Serveur + Webapp)

Ce document liste les fonctionnalités de la partie **Data/IA** : le serveur (agent, mémoire, auto-amélioration, traces) et la webapp (missions, suivi, évaluation, validation).
La partie **Robot / Simulateur** est vue ici uniquement comme un serveur MCP exposant les primitives (`navigate_to`, `look`, `detect`, `pick`, `place`, `read_text`, `web_search`, `ask_human`).

Priorités :

- **MVP** : nécessaire pour la démonstration cible (une mission ratée → nouvelle stratégie → testée en simulation → comparée → adoptée).
- **V1** : rend la plateforme confortable et fiable au quotidien.
- **V2** : utile, mais peut attendre.

---

## 1. Robots & environnements

| # | Fonctionnalité | Priorité |
|---|---|---|
| 1.1 | Enregistrer une cible d'exécution : simulateur ou robot physique (nom, type, URL du serveur MCP) | MVP |
| 1.2 | Statut de connexion en temps réel (en ligne / hors ligne / occupé) | MVP |
| 1.3 | Lister les outils MCP exposés par une cible et leur schéma | MVP |
| 1.4 | Fiche robot (capacités, limites) utilisée comme connaissance CAG | V1 |
| 1.5 | Gestion de plusieurs environnements de simulation (scènes, cartes) | V1 |

## 2. Missions

| # | Fonctionnalité | Priorité |
|---|---|---|
| 2.1 | Catalogue de missions types (ranger, retrouver, lire + web, imprévu, instruction ambiguë) | MVP |
| 2.2 | Lancer une mission : instruction en langage naturel + cible + version du harness | MVP |
| 2.3 | Historique des missions avec statut (en cours, réussie, échouée, annulée) et filtres | MVP |
| 2.4 | Annuler une mission en cours | MVP |
| 2.5 | File d'attente quand une cible est occupée | V1 |
| 2.6 | Critères de réussite par mission (vérification automatique côté simulateur ou jugement du Critic) | MVP |

## 3. Suivi en direct

| # | Fonctionnalité | Priorité |
|---|---|---|
| 3.1 | Timeline de la mission : étapes Perceive → Plan → Execute → Analyze, en direct | MVP |
| 3.2 | Affichage du plan courant et des replanifications | MVP |
| 3.3 | Journal des appels d'outils (entrée, sortie, durée, erreur) | MVP |
| 3.4 | Réponse aux demandes `ask_human` depuis la webapp | MVP |
| 3.5 | Bouton d'arrêt d'urgence (transmis au robot, qui garde sa sécurité locale) | MVP |
| 3.6 | Flux caméra / dernières images capturées par `look` | V1 |
| 3.7 | Raisonnement du modèle (pensées, décisions du Critic) dépliable | V1 |

## 4. Agent (serveur)

| # | Fonctionnalité | Priorité |
|---|---|---|
| 4.1 | Boucle Planner / Executor / Critic | MVP |
| 4.2 | Client MCP connecté à la cible choisie | MVP |
| 4.3 | Chargement d'une version du harness (prompts, skills, règles, config) au démarrage d'une mission | MVP |
| 4.4 | Routing de modèles : local pour les tâches simples, API pour les tâches complexes | V1 |
| 4.5 | Perception : VLM, OCR, détection via les outils | MVP (via outils) |
| 4.6 | Guardrails appliqués à chaque action, non modifiables par l'agent | MVP |
| 4.7 | Limites par mission : nombre d'étapes, durée, budget en tokens | MVP |

## 5. Mémoire

| # | Fonctionnalité | Priorité |
|---|---|---|
| 5.1 | CAG : règles, carte, fiche robot préchargées dans le contexte | MVP |
| 5.2 | RAG : mémoire épisodique (missions passées, échecs, stratégies efficaces) | V1 |
| 5.3 | Reflexion : génération d'une leçon après chaque échec, stockée en mémoire | MVP |
| 5.4 | Explorateur de mémoire dans la webapp (consulter, supprimer une leçon erronée) | V1 |

## 6. Traces & observabilité

| # | Fonctionnalité | Priorité |
|---|---|---|
| 6.1 | Enregistrement complet de chaque mission (étapes, appels modèles, appels outils, images) | MVP |
| 6.2 | Coût par mission : tokens, appels API, coût en € | MVP |
| 6.3 | Latence par étape et durée totale | MVP |
| 6.4 | Vue détaillée d'une trace passée (rejouer la timeline) | MVP |
| 6.5 | Export des traces (JSON) | V2 |

## 7. Versioning du harness

| # | Fonctionnalité | Priorité |
|---|---|---|
| 7.1 | Chaque version du harness est immuable et identifiée (prompts, skills, stratégie, règles de récupération, routing) | MVP |
| 7.2 | Version « active » par cible (simulation / robot physique) | MVP |
| 7.3 | Diff entre deux versions | MVP |
| 7.4 | Rollback vers une version précédente en un clic | MVP |
| 7.5 | Arbre de généalogie des versions (qui descend de qui, pourquoi) | V1 |
| 7.6 | Bibliothèque de skills : liste, versions, statistiques d'usage et de réussite | V1 |

## 8. Auto-amélioration

| # | Fonctionnalité | Priorité |
|---|---|---|
| 8.1 | Analyse des traces échouées : identifier les causes d'échec | MVP |
| 8.2 | Génération d'une version candidate du harness (modification ciblée + justification) | MVP |
| 8.3 | Test automatique de la candidate en simulation sur le jeu d'optimisation | MVP |
| 8.4 | Comparaison candidate vs version actuelle, décision selon un seuil de gain | MVP |
| 8.5 | Lancement manuel d'un cycle d'amélioration depuis la webapp | MVP |
| 8.6 | Cycles automatiques planifiés | V2 |
| 8.7 | Plusieurs candidates en parallèle | V2 |

## 9. Évaluation

| # | Fonctionnalité | Priorité |
|---|---|---|
| 9.1 | Jeux de test : jeu d'optimisation et jeu final indépendant, verrouillés (hors de portée de l'agent) | MVP |
| 9.2 | Lancer une évaluation : une version du harness sur un jeu de test, N répétitions | MVP |
| 9.3 | Résultats par dimension : réussite, qualité, robotique, IA, performance, coût, fiabilité | MVP |
| 9.4 | Comparaison de deux versions côte à côte, avec gain ou régression par métrique | MVP |
| 9.5 | Courbe d'évolution des métriques au fil des versions | MVP (cœur de la démo) |
| 9.6 | Détection automatique des régressions | V1 |
| 9.7 | Reproductibilité : chaque run d'évaluation enregistre version, modèles, seed, environnement | V1 |

## 10. Validation humaine & déploiement

| # | Fonctionnalité | Priorité |
|---|---|---|
| 10.1 | File des améliorations en attente de validation (diff + métriques + justification) | MVP |
| 10.2 | Approuver / rejeter une candidate | MVP |
| 10.3 | Promotion simulation → robot physique, uniquement après validation | MVP |
| 10.4 | Journal d'audit : qui a validé, déployé ou rollback quoi, et quand | V1 |

## 11. Comptes & accès

| # | Fonctionnalité | Priorité |
|---|---|---|
| 11.1 | Connexion simple (équipe projet) | MVP |
| 11.2 | Rôles : lecteur, opérateur (lance des missions), validateur (approuve, déploie) | V2 |

---

## Écrans de la webapp (MVP)

1. **Tableau de bord** : état des cibles, version active, dernières missions, courbe d'évolution.
2. **Missions** : lancement + historique.
3. **Mission en direct / trace** : timeline, plan, appels d'outils, `ask_human`, arrêt d'urgence.
4. **Versions** : liste, diff, rollback.
5. **Évaluations** : lancer, comparer deux versions.
6. **Améliorations** : cycles, candidates, file de validation.
7. **Robots** : cibles, statut, outils exposés.

## Robot cible : humanoïde Hiwonder (TonyPi ou AiNex, choix non arrêté)

Les deux candidats sont des petits humanoïdes bipèdes sur Raspberry Pi 5, avec servos bus et caméra HD sur tête 2 axes.

| | TonyPi | AiNex (Standard) |
|---|---|---|
| Servos | 16 | 24 |
| Mains | Préhension très limitée | Mains mécaniques (petits objets légers) |
| Logiciel | SDK Python, OpenCV, intégration LLM | ROS (version à confirmer), OpenCV, Gazebo |
| Autonomie | ~1 h | ~1 h |

**Règle : la plateforme reste agnostique du robot.**

- **Contrat MCP identique** : les 8 primitives sont les mêmes pour les deux robots. Le serveur MCP côté robot traduit vers le SDK Python (TonyPi) ou ROS (AiNex).
- **Profil robot** : chaque cible déclare un profil (`tonypi`, `ainex`, …) avec ses capacités et limites. Ce profil alimente la fiche robot CAG (1.4) pour que le Planner ne propose pas d'actions impossibles.
- **Contraintes communes** : pas de lidar, donc navigation grossière (marche + rotation + repères AprilTag) ; préhension limitée aux petits objets légers ; batterie ~1 h, donc l'essentiel des tests d'amélioration se fait en simulation.
- **Stub MCP** : simule les deux profils, pour développer et tester sans robot.

## Ordre de développement proposé

1. Socle serveur : modèle de données, API, stockage des traces.
2. Agent minimal (Planner / Executor / Critic) connecté à un serveur MCP **simulé** (stub) pour ne pas dépendre de la partie robotique.
3. Webapp : lancement de mission + suivi en direct + trace.
4. Versioning du harness + rollback.
5. Évaluation sur jeu de test + comparaison de versions.
6. Boucle d'auto-amélioration + file de validation.
7. Branchement sur le vrai simulateur, puis sur le robot physique.
