# unregister_context_menu.ps1
# Remove "Remove CodeCV Watermark" right-click menu entry.

$regPath = "HKCU\Software\Classes\*\shell\RemoveCodecvWatermark"

& reg delete $regPath /f 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  [SUCCESS] Context menu entry removed.`n" -ForegroundColor Green
} else {
    Write-Host "`n  [INFO] No menu entry found, nothing to do.`n" -ForegroundColor Yellow
}
Start-Sleep 2
