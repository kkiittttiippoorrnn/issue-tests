# ตัวรันงานแบบ Admin (ถูกเรียกโดย Task Scheduler "ClaudeAdminRunner" ซึ่งตั้งเป็น Run with highest privileges)
# อ่านงานจาก job.json -> รัน -> เขียนผลลง job_out.txt และ job_done.txt (exit code)
# จำกัดให้รันได้เฉพาะ python/robot ที่ชี้ไปยังไฟล์ใน repo นี้ (+ โฟลเดอร์ใน ADMIN_RUNNER_EXTRA_ROOTS คั่นด้วย ;)
# ห้ามทำเป็น daemon/ตัวรับคำสั่งค้างไว้ — Task รันทีละงานแล้วจบ
$ErrorActionPreference = 'Stop'
$here     = Split-Path -Parent $MyInvocation.MyCommand.Path
$jobFile  = Join-Path $here 'job.json'
$outFile  = Join-Path $here 'job_out.txt'
$doneFile = Join-Path $here 'job_done.txt'
$allowedRoots = @((Resolve-Path (Join-Path $here '..\..')).Path)
$extraFile = Join-Path $here 'extra_roots.txt'   # ไม่ขึ้น git ถ้าต้องการ ให้เพิ่มใน .gitignore
if (Test-Path $extraFile) { $allowedRoots += Get-Content $extraFile -Encoding utf8 | Where-Object { $_.Trim() } }

function Finish($code, $msg) {
    if ($msg) { Add-Content -Path $outFile -Value $msg -Encoding utf8 }
    Set-Content -Path $doneFile -Value $code -Encoding ascii
    exit 0
}

Remove-Item $outFile, $doneFile -ErrorAction SilentlyContinue
if (-not (Test-Path $jobFile)) { Finish 2 'ไม่มี job.json' }
$job = Get-Content $jobFile -Raw -Encoding utf8 | ConvertFrom-Json
Remove-Item $jobFile -ErrorAction SilentlyContinue

$exe     = [string]$job.exe
$jobArgs = @($job.args | ForEach-Object { [string]$_ })
$cwd     = [string]$job.cwd

if ($exe -notin @('python', 'robot')) { Finish 3 "ไม่อนุญาต exe: $exe" }
$scriptArg = $jobArgs | Where-Object { $_ -match '\.(py|robot)$' } | Select-Object -First 1
if (-not $scriptArg) { Finish 3 'ต้องระบุไฟล์ .py หรือ .robot' }
$full = if ([IO.Path]::IsPathRooted($scriptArg)) { $scriptArg } else { Join-Path $cwd $scriptArg }
$full = [IO.Path]::GetFullPath($full)
if (-not ($allowedRoots | Where-Object { $full.StartsWith($_, [StringComparison]::OrdinalIgnoreCase) })) {
    Finish 3 "ไฟล์อยู่นอกโฟลเดอร์ที่อนุญาต: $full"
}

$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = [Text.Encoding]::UTF8
$pyFile = Join-Path $here 'python_path.txt'
if (-not (Test-Path $pyFile)) { Finish 4 'ไม่มี python_path.txt - รัน setup_task.ps1 ก่อน' }
$py = (Get-Content $pyFile -Encoding utf8 | Select-Object -First 1).Trim()
if ($exe -eq 'robot') { $jobArgs = @('-X', 'utf8', '-m', 'robot') + $jobArgs }
Set-Location $cwd
"[$(Get-Date -Format s)] admin run: $exe $($jobArgs -join ' ')  (cwd=$cwd)" | Out-File $outFile -Encoding utf8
try {
    & $py @jobArgs 2>&1 | ForEach-Object { "$_" } | Out-File -FilePath $outFile -Append -Encoding utf8
    Finish $LASTEXITCODE $null
} catch {
    Finish 1 "error: $_"
}
