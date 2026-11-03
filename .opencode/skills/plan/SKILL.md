---
name: plan
description: Cadrer une tâche de code en plusieurs étapes. Écrit un plan court (objectif, phases avec vérification, preuves attendues) dans plan/, puis attend la validation. À utiliser avant d'implémenter une fonctionnalité, un refactor ou un bug non trivial.
---

# Plan — cadrer avant de coder

Ce skill ne code rien. Il applique la méthode de `RULES.md` (plan court par phases, puis choix du mode d'exécution) et laisse une trace écrite.

## Étapes
1. Lis `memoire/ROUTEUR.md` puis les fichiers de mémoire qui correspondent à la tâche, et `memoire/principes.md` (commandes de vérification, principes, interdits).
2. S'il reste un flou sur la demande, pose les questions **avant** d'écrire le plan.
3. Écris le plan dans `plan/AAAA-MM-JJ-<sujet-en-kebab-case>.md` avec ce modèle :

   ```
   # <Sujet>
   Statut : proposé

   ## Objectif
   Une ou deux phrases. Ce qui est hors périmètre.

   ## Phases
   | N° | Idée phare | Vérification |
   |---|---|---|
   | 1 | ... | commande ou contrôle précis |

   ## Risques et hypothèses
   - ...

   ## Preuves attendues
   - Test qui échoue avant la correction, puis qui passe
   - Résultat de la relecture (`/review`)
   - Résultat de `.\scripts\routeur.ps1 -Verifier` si la mémoire est touchée
   ```

4. Présente le plan à l'utilisateur en quelques lignes (idées phares, pas le détail) et **attends sa validation**. N'implémente rien.
5. Après validation : passe le statut à `validé` et propose les deux modes d'exécution de `RULES.md` (step by step ou one shot).
6. Pendant l'exécution, tiens le statut à jour (`en cours`, `terminé`) et note dans « Preuves attendues » ce qui a été réellement obtenu.

## Règles
- Chaque phase a une vérification concrète et lançable. Pas de « vérifier que ça marche ».
- Pas de phase spéculative : tout se rattache à la demande.
- Le dossier `plan/` est dans le projet : committe-le seulement si l'utilisateur le demande.
- Si tu es en mode Plan d'OpenCode, l'écriture dans `plan/` est refusée : présente le plan dans la réponse, puis demande de passer en mode build pour l'enregistrer.
