# Windows Task Scheduler - RWA News Auto-Post System の自動登録スクリプト

$TaskName = "RWA_News_AutoPost"
$ScriptPath = "C:\Users\yuji\rwanews\run_rwanews.bat"
$WorkingDir = "C:\Users\yuji\rwanews"

# 既存タスクを削除（存在する場合）
Write-Host "Checking for existing tasks..."
$existingTask = Get-ScheduledTask -TaskName "$TaskName*" -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing tasks..."
    Get-ScheduledTask -TaskName "$TaskName*" | Unregister-ScheduledTask -Confirm:$false
}

Write-Host "Registering scheduled tasks..."
Write-Host ""

# タスク1: 08:00 実行
Write-Host "1. Registering morning task (08:00)..."
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$ScriptPath`"" -WorkingDirectory $WorkingDir
$trigger08 = New-ScheduledTaskTrigger -Daily -At 08:00
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "${TaskName}_08:00" `
    -Action $action `
    -Trigger $trigger08 `
    -Principal $principal `
    -Settings $settings `
    -Force | Out-Null

Write-Host "   ✅ Morning task registered (08:00)"

# タスク2: 18:00 実行
Write-Host "2. Registering evening task (18:00)..."
$trigger18 = New-ScheduledTaskTrigger -Daily -At 18:00

Register-ScheduledTask -TaskName "${TaskName}_18:00" `
    -Action $action `
    -Trigger $trigger18 `
    -Principal $principal `
    -Settings $settings `
    -Force | Out-Null

Write-Host "   ✅ Evening task registered (18:00)"

Write-Host ""
Write-Host "✅ Task Scheduler registration completed!"
Write-Host ""
Write-Host "Registered tasks:"
Get-ScheduledTask -TaskName "$TaskName*" | Format-Table -Property TaskName, @{Name="NextRunTime";Expression={$_.Triggers.StartBoundary}}
