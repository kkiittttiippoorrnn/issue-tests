# ตั้ง Task Scheduler "ClaudeAdminRunner" — รันแบบ Admin ครั้งเดียว (มี UAC)
# ใช้เมื่อแอปที่ทดสอบต้องรันแบบ Admin แต่ terminal ของ Claude ไม่ใช่ Admin (UIPI กดไม่ติด)
# Task รันในเซสชันของผู้ใช้ที่ล็อกอินอยู่ (Interactive) แบบ Highest -> เห็นหน้าจอและกดแอปที่รันแบบ Admin ได้
# ลบทิ้ง: Unregister-ScheduledTask -TaskName ClaudeAdminRunner -Confirm:$false
$here   = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $here 'run_admin.ps1'
$user   = "$env:USERDOMAIN\$env:USERNAME"

# จด path เต็มของ python ไว้ (ใน Task Scheduler ตัว alias ของ WindowsApps อาจหาไม่เจอ)
$py = if ($env:ADMIN_RUNNER_PYTHON) { $env:ADMIN_RUNNER_PYTHON } else { (& python -c "import sys; print(sys.executable)") }
Set-Content -Path (Join-Path $here 'python_path.txt') -Value $py -Encoding utf8

$action    = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$runner`""
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 3) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName 'ClaudeAdminRunner' -Action $action -Principal $principal -Settings $settings -Force | Out-Null
Get-ScheduledTask -TaskName 'ClaudeAdminRunner' | Select-Object TaskName, State, @{n='RunLevel';e={$_.Principal.RunLevel}} |
    Format-List | Out-File (Join-Path $here 'setup_result.txt') -Encoding utf8
Write-Host "ตั้ง Task แล้ว (python: $py)"
