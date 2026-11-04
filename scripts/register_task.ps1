# Crée (ou remplace) la tâche planifiée quotidienne de l'agent de veille IA.
# -StartWhenAvailable : si la machine était éteinte à l'heure prévue, la tâche part dès que possible.
param([string]$Heure = "08:00")

$script = Join-Path $PSScriptRoot "run_daily.ps1"
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`"" `
    -WorkingDirectory (Split-Path -Parent $PSScriptRoot)
$trigger = New-ScheduledTaskTrigger -Daily -At $Heure
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName "VeilleIA" -Action $action -Trigger $trigger `
    -Settings $settings -Description "Veille IA quotidienne (data\ia\AAAA-MM-JJ.json)" -Force
