# register_context_menu.ps1
# Register "Remove CodeCV Watermark" right-click menu for .pdf files.
# Uses HKCU -- no admin privileges needed.

$ErrorActionPreference = "Stop"

# Locate the exe
$scriptDir = Split-Path -Parent $PSCommandPath
$exeCandidates = @(
    Join-Path $scriptDir "RemoveCodecvWatermark.exe"
    Join-Path $scriptDir "..\dist\RemoveCodecvWatermark.exe"
)

$exePath = $null
foreach ($candidate in $exeCandidates) {
    $resolved = Resolve-Path $candidate -ErrorAction SilentlyContinue
    if ($resolved) { $exePath = $resolved; break }
}

if (-not $exePath) {
    Write-Host "[ERROR] Cannot find RemoveCodecvWatermark.exe" -ForegroundColor Red
    Write-Host "        Run build.bat first to build it." -ForegroundColor Yellow
    Start-Sleep 3
    exit 1
}

# .reg format requires doubled backslashes in paths
$escapedPath = $exePath.ToString().Replace('\', '\\')

# Build a .reg file (most reliable way to set quoted registry values)
$regContent = @"
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Classes\*\shell\RemoveCodecvWatermark]
@="Remove CodeCV Watermark"

[HKEY_CURRENT_USER\Software\Classes\*\shell\RemoveCodecvWatermark\command]
@="\"$escapedPath\" \"%1\""
"@

$tempReg = Join-Path ([System.IO.Path]::GetTempPath()) "remove_codecv_watermark.reg"
$regContent | Out-File -FilePath $tempReg -Encoding Unicode

& reg import $tempReg
$result = $LASTEXITCODE

Remove-Item $tempReg -Force -ErrorAction SilentlyContinue

if ($result -eq 0) {
    Write-Host "`n  [SUCCESS] Right-click menu registered!" -ForegroundColor Green
    Write-Host "  exe:  $exePath" -ForegroundColor Gray
    Write-Host "  Usage: Right-click any PDF -> `"Remove CodeCV Watermark`"`n" -ForegroundColor Cyan
} else {
    Write-Host "`n  [ERROR] Failed to register context menu.`n" -ForegroundColor Red
}
Start-Sleep 2
