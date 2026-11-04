# Lance l'agent de veille IA et écrit la sortie dans data\logs\AAAA-MM-JJ.log.
# Utilisé par la tâche planifiée (voir register_task.ps1), lançable à la main.
# La redirection est faite par cmd : en PowerShell 5.1, 2>&1 transforme les messages stderr de Python en fausses erreurs.
Set-Location (Split-Path -Parent $PSScriptRoot)
$env:PYTHONUTF8 = "1"

New-Item -ItemType Directory -Force -Path "data\logs" | Out-Null
$log = Join-Path "data\logs" ((Get-Date -Format "yyyy-MM-dd") + ".log")

"=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') debut ===" | Out-File -Append -Encoding ascii $log
cmd /c "python scripts\run_agent.py >> $log 2>&1"
$code = $LASTEXITCODE
"=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') fin (code $code) ===" | Out-File -Append -Encoding ascii $log
exit $code
