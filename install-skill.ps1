# ลิงก์ skill /test-issue เข้า Claude Code (~/.claude/skills/test-issue -> claude-skill/test-issue)
# ใช้ junction จึงไม่ต้องสิทธิ์ Admin และแก้ skill ใน repo แล้วมีผลทันที
$source = Join-Path $PSScriptRoot 'claude-skill\test-issue'
$target = Join-Path $env:USERPROFILE '.claude\skills\test-issue'

if (Test-Path $target) {
    $item = Get-Item $target -Force
    if ($item.LinkType -eq 'Junction') {
        Write-Host "มี junction อยู่แล้ว -> $($item.Target)"
        exit 0
    }
    Write-Error "$target มีอยู่แล้วและไม่ใช่ junction - ย้ายออกก่อน"
    exit 1
}
New-Item -ItemType Junction -Path $target -Target $source | Out-Null
Write-Host "ติดตั้งแล้ว: $target -> $source"
