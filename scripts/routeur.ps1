# Génère memoire/ROUTEUR.md à partir des en-têtes des fichiers de memoire/.
#   .\scripts\routeur.ps1             écrit memoire/ROUTEUR.md
#   .\scripts\routeur.ps1 -Verifier   contrôle la cohérence sans rien écrire (code retour 1 si erreur) :
#     erreurs       : routeur à jour, chemins 'couvre' existants, JSON de configuration valide,
#                     fichiers Git non couverts, secrets probables
#     avertissements : mémoire plus ancienne que le code qu'elle couvre (champ 'verifie: AAAA-MM-JJ' de
#                      l'en-tête, sinon date du dernier commit du fichier), budget de contexte dépassé
# Uniquement des cmdlets : compatible avec le mode PowerShell restreint (Constrained Language Mode).
param(
    [string]$Racine = (Split-Path $PSScriptRoot -Parent),
    [switch]$Verifier
)

# Budget de contexte, en caractères (environ 4 caractères par token)
$maxChargeEnPermanence = 10000   # AGENTS.md + memoire/ROUTEUR.md, chargés à chaque session
$maxFichierMemoire = 6000        # un fichier de memoire/

$dossier = Join-Path $Racine "memoire"
$routeur = Join-Path $dossier "ROUTEUR.md"
$erreurs = @()
$avertissements = @()

function Lire-EnTete($fichier) {
    $texte = Get-Content $fichier -Raw -Encoding UTF8
    $valeurs = @{}
    if ($texte -match '(?s)^---\r?\n(.*?)\r?\n---') {
        foreach ($ligne in $Matches[1] -split '\r?\n') {
            if ($ligne -match '^(\w+)\s*:\s*(.*)$') { $valeurs[$Matches[1]] = $Matches[2].Trim() }
        }
    }
    return $valeurs
}

function Jour-Commit($chemin) {
    $jour = git -C $Racine log -1 --format=%cs -- $chemin 2>$null
    if ($LASTEXITCODE -eq 0 -and $jour) { return "$jour".Trim() }
    return ""
}

$lignes = @()
$couverts = @()
$couvertParFichier = @{}
$verifieParFichier = @{}
$fichiers = Get-ChildItem $dossier -Filter *.md | Where-Object { $_.Name -ne "ROUTEUR.md" -and -not $_.Name.StartsWith("_") } | Sort-Object Name

if (-not (Test-Path (Join-Path $dossier "architecture.md"))) {
    $erreurs += "memoire/architecture.md est obligatoire (fichier de repli du routeur)"
}

foreach ($f in $fichiers) {
    $entete = Lire-EnTete $f.FullName
    if (-not $entete["quand_lire"]) {
        $erreurs += "$($f.Name) : en-tête 'quand_lire' manquant ou vide"
        continue
    }
    $couverts_fichier = @()
    if ($entete["couvre"]) {
        foreach ($chemin in $entete["couvre"] -split ',') {
            $chemin = $chemin.Trim()
            if ($chemin) {
                $couverts += $chemin.Replace('\', '/')
                $couverts_fichier += $chemin.Replace('\', '/')
            }
            if ($chemin -and -not (Test-Path (Join-Path $Racine $chemin))) {
                $erreurs += "$($f.Name) : 'couvre' cite un chemin qui n'existe pas : $chemin"
            }
        }
    }
    $couvertParFichier[$f.Name] = $couverts_fichier
    $verifieParFichier[$f.Name] = $entete["verifie"]
    $lignes += "| ``memoire/$($f.Name)`` | $($entete['quand_lire'] -replace '\|', '\|') |"
}

$contenu = @"
# ROUTEUR DE MÉMOIRE

> Fichier généré par ``scripts/routeur.ps1`` : ne pas le modifier à la main. Modifier l'en-tête ``quand_lire`` du fichier concerné, puis relancer le script.

Index de ``memoire/`` : une ligne par fichier, avec le moment où le lire. Ce fichier ne contient aucune connaissance du projet. Chemins relatifs à la racine.

## 1. Fichiers de mémoire
Lis un fichier quand la tâche correspond à sa colonne « Quand le lire ». Plusieurs peuvent s'appliquer. Un fichier déjà lu dans la session et non modifié depuis ne se relit pas.

| Fichier | Quand le lire |
|---|---|
$($lignes -join "`n")

Aucune ligne ne correspond : lis ``memoire/architecture.md``, avertis l'utilisateur que la tâche n'est pas couverte par le routeur et n'invente rien.

## 2. Cohérence
- Un fait de la mémoire qui contredit le code est une erreur de la mémoire : corrige-la et signale-la à l'utilisateur.
- Un chemin listé ici qui n'existe pas : signale-le à l'utilisateur.
"@
$contenu = ($contenu -replace '\r?\n', "`n").TrimEnd() + "`n"

if ($Verifier) {
    # JSON de configuration : OpenCode ignore sans avertissement un opencode.json invalide
    foreach ($fichierJson in @("opencode.json", ".opencode/opencode.json")) {
        $cheminJson = Join-Path $Racine $fichierJson
        if (Test-Path $cheminJson) {
            try { $null = Get-Content $cheminJson -Raw -Encoding UTF8 | ConvertFrom-Json }
            catch { $erreurs += "$fichierJson : JSON invalide, OpenCode l'ignore sans avertissement ($($_.Exception.Message))" }
        }
    }

    # Fichiers suivis par Git (la suite est ignorée hors dépôt Git)
    $suivis = @()
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $suivis = @(git -C $Racine ls-files 2>$null)
        if ($LASTEXITCODE -ne 0) { $suivis = @() }
    }

    # Couverture : tout fichier suivi doit être cité dans un 'couvre' (un chemin finissant par / couvre un dossier)
    # ou correspondre à un motif de memoire/_ignore.txt
    $motifs = @()
    $fichierIgnore = Join-Path $dossier "_ignore.txt"
    if (Test-Path $fichierIgnore) {
        $motifs = Get-Content $fichierIgnore -Encoding UTF8 | Where-Object { $_.Trim() -and -not $_.StartsWith("#") }
    }
    foreach ($suivi in $suivis) {
        $ignore = ($suivi -eq ".harness-base")
        foreach ($motif in $motifs) { if ($suivi -like $motif.Trim()) { $ignore = $true } }
        foreach ($c in $couverts) { if ($suivi -eq $c -or ($c.EndsWith("/") -and $suivi.StartsWith($c))) { $ignore = $true } }
        if (-not $ignore) { $erreurs += "Fichier non couvert par la mémoire : $suivi (l'ajouter à un 'couvre' ou à memoire/_ignore.txt)" }
    }

    # Secrets : motifs de clés connues dans les fichiers suivis. Une ligne contenant 'secret-ok' est ignorée.
    $motifsSecrets = @{
        "cle sk-"        = '\bsk-[A-Za-z0-9_-]{20,}'
        "jeton GitHub"   = 'ghp_[A-Za-z0-9]{30,}'
        "cle AWS"        = 'AKIA[0-9A-Z]{16}'
        "cle privee"     = '-----BEGIN [A-Z ]*PRIVATE KEY-----'
        "en-tete Bearer" = 'Bearer\s+[A-Za-z0-9._-]{20,}'
    }
    foreach ($suivi in $suivis) {
        if ($suivi -match '\.(png|jpe?g|gif|ico|pdf|zip|gz|exe|dll|woff2?|lock)$') { continue }
        $chemin = Join-Path $Racine $suivi
        if (-not (Test-Path $chemin -PathType Leaf)) { continue }
        if ((Get-Item $chemin).Length -gt 1MB) { continue }
        $texte = (Get-Content $chemin -Encoding UTF8 | Where-Object { $_ -notmatch 'secret-ok' }) -join "`n"
        foreach ($nom in $motifsSecrets.Keys) {
            if ($texte -match $motifsSecrets[$nom]) { $erreurs += "Secret probable ($nom) dans $suivi : le retirer, ou ajouter 'secret-ok' sur la ligne si c'est un faux positif" }
        }
    }

    # Péremption : le code couvert a été commité après la date 'verifie' du fichier de mémoire (au jour près).
    # Repli, si 'verifie' est absent ou invalide : après le dernier commit du fichier de mémoire.
    foreach ($nom in $couvertParFichier.Keys) {
        $verifie = $verifieParFichier[$nom]
        if ($verifie -match '^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$') {
            $reference = $verifie
            $origine = "verifie: $verifie"
            $conseil = "Relire le fichier, puis mettre à jour 'verifie' dans son en-tête"
        } else {
            if ($verifie) { $avertissements += "memoire/$nom : 'verifie' invalide ('$verifie'), attendu AAAA-MM-JJ" }
            $reference = Jour-Commit "memoire/$nom"
            $origine = "sans 'verifie', dernier commit du fichier le $reference"
            $conseil = "Relire le fichier, puis ajouter 'verifie: AAAA-MM-JJ' (date du jour) dans son en-tête"
        }
        if (-not $reference) { continue }
        foreach ($c in $couvertParFichier[$nom]) {
            $jourCode = Jour-Commit $c
            if ($jourCode -and $jourCode -gt $reference) {
                $avertissements += "memoire/$nom ($origine) est plus ancien que le code qu'il couvre : $c modifié le $jourCode. $conseil"
            }
        }
    }

    # Budget de contexte
    $chargeEnPermanence = 0
    foreach ($nom in @((Join-Path $Racine "AGENTS.md"), $routeur)) {
        if (Test-Path $nom) { $chargeEnPermanence += (Get-Content $nom -Raw -Encoding UTF8).Length }
    }
    if ($chargeEnPermanence -gt $maxChargeEnPermanence) {
        $avertissements += "Contexte chargé à chaque session : $chargeEnPermanence caractères (AGENTS.md + ROUTEUR.md), au-dessus de $maxChargeEnPermanence"
    }
    foreach ($f in $fichiers) {
        $taille = (Get-Content $f.FullName -Raw -Encoding UTF8).Length
        if ($taille -gt $maxFichierMemoire) {
            $avertissements += "memoire/$($f.Name) : $taille caractères, au-dessus de $maxFichierMemoire (le découper par sujet)"
        }
    }

    $actuel = ""
    if (Test-Path $routeur) { $actuel = (Get-Content $routeur -Raw -Encoding UTF8) -replace '\r?\n', "`n" }
    if ($actuel -ne $contenu) { $erreurs += "memoire/ROUTEUR.md n'est pas à jour : lancer .\scripts\routeur.ps1" }

    $avertissements | ForEach-Object { Write-Host "AVERTISSEMENT : $_" }
    if ($erreurs) { $erreurs | ForEach-Object { Write-Host "ERREUR : $_" }; exit 1 }
    Write-Host "Mémoire cohérente ($($fichiers.Count) fichier(s), $($avertissements.Count) avertissement(s))."
    exit 0
}

if ($erreurs) { $erreurs | ForEach-Object { Write-Host "ERREUR : $_" }; exit 1 }
Set-Content -Path $routeur -Value $contenu -Encoding UTF8 -NoNewline
Write-Host "memoire/ROUTEUR.md généré ($($fichiers.Count) fichier(s))."
