# AGENTS.md

Consignes de comportement pour réduire les erreurs courantes des LLM en programmation. À combiner avec les instructions propres au projet.

**Compromis :** ces consignes privilégient la prudence plutôt que la vitesse.

## Environnement

- Windows, terminal PowerShell 5.1 en mode restreint (Constrained Language Mode) : n'utilise que des cmdlets. Pas d'appel de méthode statique .NET (`[IO.File]::…`), pas de `New-Object`, pas de `Add-Type`. Un script qui doit durer s'écrit dans `scripts/`.
- Fichiers en UTF-8. Chemins Windows avec `\`, sauf dans les fichiers de configuration multi-plateformes.
- Ne lis, n'affiche et ne copie jamais le contenu d'un `.env` ni aucun secret (clés, jetons, mots de passe). `opencode.json` bloque déjà l'accès, ne cherche pas à le contourner.

## 1. Réfléchir avant de coder

**Ne pas supposer. Ne pas cacher la confusion. Exposer les compromis.**

Avant d'implémenter :
- Énonce explicitement les hypothèses que tu poses sur le code (comportement existant, contraintes). Tout flou sur l'intention de l'utilisateur relève de `RULES.md` : question d'abord.
- Si plusieurs interprétations existent, présente-les au lieu d'en choisir une en silence.
- S'il existe une approche plus simple, dis-le. Conteste la demande si c'est justifié.
- Si quelque chose n'est pas clair, arrête-toi. Dis ce qui est confus. Demande.

## 2. La simplicité d'abord

**Le minimum de code qui résout le problème. Rien de spéculatif.**

- Aucune fonctionnalité au-delà de ce qui est demandé.
- Aucune abstraction pour du code à usage unique.
- Aucune « flexibilité » ou « configurabilité » non demandée.
- Aucune gestion d'erreur pour des scénarios impossibles.
- Si tu écris 200 lignes alors que 50 suffiraient, réécris.

Demande-toi : « Un ingénieur senior dirait-il que c'est trop compliqué ? » Si oui, simplifie.

## 3. Modifications chirurgicales

**Ne touche que ce qui est nécessaire. Ne nettoie que ce que tu as toi-même sali.**

En modifiant du code existant :
- N'« améliore » pas le code, les commentaires ou la mise en forme voisins.
- Ne refactorise pas ce qui n'est pas cassé.
- Respecte le style existant, même si tu ferais autrement.
- Si tu remarques du code mort sans rapport, signale-le sans le supprimer.

Quand tes modifications créent des orphelins :
- Supprime les imports, variables et fonctions que TES modifications ont rendus inutiles.
- Ne supprime pas le code mort préexistant, sauf demande explicite.

Le test : chaque ligne modifiée doit se rattacher directement à la demande de l'utilisateur (sauf la correction de `memoire/` prévue en §5).

## 4. Exécution guidée par des objectifs

**Définir des critères de succès. Boucler jusqu'à vérification.**

Les commandes de test, de lint et de build du projet sont dans `memoire/principes.md`. Lance-les avant de conclure une tâche de code, et dis lesquelles tu as lancées.

Transforme les tâches en objectifs vérifiables :
- « Ajouter une validation » → « Écrire des tests pour les entrées invalides, puis les faire passer »
- « Corriger le bug » → « Écrire un test qui le reproduit, puis le faire passer »
- « Refactoriser X » → « S'assurer que les tests passent avant et après »

Pour une tâche de code en plusieurs étapes, suis la méthode de `RULES.md` : plan court par phases, puis choix du mode d'exécution une fois le plan validé. Chaque étape ajoute seulement une courte mention de vérification, sans détail supplémentaire :
```
1. [Étape] → vérifier : [contrôle]
2. [Étape] → vérifier : [contrôle]
3. [Étape] → vérifier : [contrôle]
```

- **Dans une étape :** vérifie et corrige seul jusqu'à ce que le critère soit atteint.
- **Entre deux étapes (step by step) :** arrête-toi et attends l'accord de l'utilisateur.
- **One shot :** enchaîne toutes les étapes, avec leurs vérifications.

Des critères de succès solides permettent de boucler seul. Des critères faibles (« faire que ça marche ») obligent à demander sans cesse des précisions.

---

**Ces consignes fonctionnent si :** les diffs contiennent moins de modifications inutiles, il y a moins de réécritures dues à la sur-complication, et les questions de clarification arrivent avant l'implémentation plutôt qu'après les erreurs.

---

## 5. Mémoire du projet

La mémoire du projet est dans `memoire/`. `memoire/ROUTEUR.md` est chargé en contexte à chaque session (via `instructions` dans `opencode.json`) et indique, pour chaque fichier de mémoire, quand le lire. Il est **généré** : ne pas le modifier à la main.

- Avant de modifier du code ou de répondre sur le code (lire la mémoire reste possible avant de poser une question), consulte la colonne « Quand le lire » de `memoire/ROUTEUR.md` et lis les fichiers qui correspondent à la tâche ; si aucun ne correspond, lis `memoire/architecture.md`.
- Chaque fichier de `memoire/` commence par un en-tête `quand_lire` (quand le lire) et `couvre` (fichiers de code décrits). Modèle : `memoire/_modele.md`.
- Si tu ajoutes, renommes ou supprimes un fichier de `memoire/`, ou si tu modifies un en-tête, régénère le routeur : `.\scripts\routeur.ps1`.
- Avant de terminer une tâche qui touche à `memoire/` ou qui ajoute un fichier au projet, lance `.\scripts\routeur.ps1 -Verifier`. Il échoue si un fichier suivi par Git n'est cité dans aucun `couvre` (ajoute-le au `couvre` du fichier de mémoire concerné, ou à `memoire/_ignore.txt` s'il n'a pas besoin d'être documenté) ou s'il contient un secret probable. Ses avertissements (mémoire plus ancienne que le code qu'elle couvre, budget de contexte) ne bloquent pas : traite-les ou signale-les à l'utilisateur.
- Un fait de la mémoire qui contredit le code est une erreur de la mémoire : corrige-la et signale-la à l'utilisateur.
