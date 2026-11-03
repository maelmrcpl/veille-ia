---
description: Relecture indépendante des modifications en cours (sous-agent en lecture seule)
agent: reviewer
subagent: true
---

Demande d'origine ou point à examiner : $ARGUMENTS

Fichiers modifiés :
!`git status -s`

Diff :
!`git diff HEAD`

Charge le skill `review` et suis-le sur ces modifications.
