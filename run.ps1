<#
.SYNOPSIS
    รันเทสของ issue ด้วย Robot Framework

.EXAMPLE
    .\run.ps1 -Issue 1234 -DryRun          # เช็ค syntax/keyword โดยไม่เปิดแอป
    .\run.ps1 -Issue 1234                  # รันจริง (คุมเมาส์/คีย์บอร์ด ห้ามแตะเครื่อง)
    .\run.ps1 -Issue 1234 -Include TC1     # เฉพาะ tag TC1
    .\run.ps1 -Issue 1234 -RerunFailed     # รันซ้ำเฉพาะตัวที่ fail แล้วรวมผล

.NOTES
    ค่าเฉพาะเครื่องอยู่ใน local.ps1 (คัดลอกจาก local.example.ps1) - ไฟล์นี้ไม่ขึ้น git
    AUTOMATION_HOME = โปรเจกต์ Robot ที่มี keyword พื้นฐานของแอป (ไม่ตั้ง = ใช้ repo นี้)
    ผลรันอยู่ที่ issues/<ID>/evidence/<วันเวลา>/
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Issue,
    [string[]]$Include = @(),
    [string[]]$Exclude = @(),
    [string[]]$Variable = @(),
    [switch]$DryRun,
    [switch]$RerunFailed
)

$root = $PSScriptRoot
$localConfig = Join-Path $root 'local.ps1'
if (Test-Path $localConfig) { . $localConfig }

$automationHome = if ($env:AUTOMATION_HOME) { $env:AUTOMATION_HOME } else { $root }

# หา robot: ROBOT_EXE > venv ของ AUTOMATION_HOME > venv ของ repo นี้ > robot ใน PATH
$robotCandidates = @($env:ROBOT_EXE,
                     (Join-Path $automationHome '.venv\Scripts\robot.exe'),
                     (Join-Path $root '.venv\Scripts\robot.exe')) | Where-Object { $_ -and (Test-Path $_) }
$robot = if ($robotCandidates) { @($robotCandidates)[0] } else { (Get-Command robot -ErrorAction SilentlyContinue).Source }
if (-not $robot) {
    Write-Error "ไม่พบ Robot Framework - ดู ADAPTING.md (ติดตั้ง requirements.txt หรือตั้ง ROBOT_EXE / AUTOMATION_HOME ใน local.ps1)"
    exit 2
}

$issueDir = Join-Path $root "issues\$Issue"
if (-not (Test-Path $issueDir)) {
    Write-Error "ไม่พบ $issueDir - คัดลอกจาก issues\_template ก่อน"
    exit 2
}

$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'

$outDir = Join-Path $issueDir ("evidence\" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$robotArgs = @('--outputdir', $outDir,
               '--variable', "AUTOMATION_HOME:$($automationHome.Replace('\', '/'))",
               '--variable', "ISSUE_TESTS:$($root.Replace('\', '/'))",
               '--pythonpath', (Join-Path $root 'libraries'))
$automationLibs = Join-Path $automationHome 'libraries'
if ((Test-Path $automationLibs) -and ($automationHome -ne $root)) { $robotArgs += @('--pythonpath', $automationLibs) }
foreach ($tag in $Include) { $robotArgs += @('--include', $tag) }
foreach ($tag in $Exclude) { $robotArgs += @('--exclude', $tag) }
foreach ($var in $Variable) { $robotArgs += @('--variable', $var) }
if ($DryRun) { $robotArgs += '--dryrun' }
$robotArgs += $issueDir

# รันจาก AUTOMATION_HOME เพราะ keyword พื้นฐานมักอ้าง path แบบ relative กับโปรเจกต์ตัวเอง
Push-Location $automationHome
try {
    & $robot @robotArgs
    $rc = $LASTEXITCODE

    if ($RerunFailed -and -not $DryRun -and $rc -gt 0) {
        $rerunDir = Join-Path $outDir 'rerun'
        $rerunArgs = @($robotArgs | Select-Object -Skip 2)
        & $robot --rerunfailed (Join-Path $outDir 'output.xml') --outputdir $rerunDir @rerunArgs
        $rc = $LASTEXITCODE
        $rebot = Join-Path (Split-Path $robot -Parent) 'rebot.exe'
        & $rebot --merge --outputdir (Join-Path $outDir 'merged') (Join-Path $outDir 'output.xml') (Join-Path $rerunDir 'output.xml')
    }
} finally {
    Pop-Location
}
exit $rc
