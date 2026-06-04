# ============================================
# PINUS PACKINDO - AUTO SYNC
# Berjalan di background, otomatis push ke
# GitHub setiap ada file yang berubah
# ============================================

$projectPath = "C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1"
$debounceSeconds = 10   # tunggu 10 detik setelah perubahan terakhir sebelum push

Write-Host "AUTO SYNC aktif - memantau perubahan file..." -ForegroundColor Green
Write-Host "Folder: $projectPath" -ForegroundColor Gray
Write-Host "Tekan Ctrl+C untuk berhenti." -ForegroundColor Gray
Write-Host ""

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $projectPath
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.Filter = "*.*"

# Abaikan file/folder yang tidak perlu di-sync
$ignore = @('.git', '__pycache__', '.pyc', '.log', 'auto_sync.ps1')

$lastChange = [datetime]::MinValue
$timer = $null

$action = {
    $path = $Event.SourceEventArgs.FullPath
    foreach ($ign in $ignore) {
        if ($path -like "*$ign*") { return }
    }

    $global:lastChange = Get-Date
    Write-Host "Perubahan terdeteksi: $($Event.SourceEventArgs.Name)" -ForegroundColor Yellow
}

Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null
Register-ObjectEvent $watcher "Created" -Action $action | Out-Null
Register-ObjectEvent $watcher "Deleted" -Action $action | Out-Null

while ($true) {
    Start-Sleep -Seconds 2

    if ($global:lastChange -ne [datetime]::MinValue) {
        $elapsed = (Get-Date) - $global:lastChange
        if ($elapsed.TotalSeconds -ge $debounceSeconds) {
            $global:lastChange = [datetime]::MinValue

            Set-Location $projectPath
            $status = git status --porcelain
            if ($status) {
                Write-Host ""
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Mengirim ke GitHub..." -ForegroundColor Cyan
                git add .
                $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
                # Jika HANYA okr_data.json yang berubah -> tambahkan [vercel skip]
                # supaya update data TIDAK memicu build Vercel (cegah limit deploy habis).
                # Jika ada file kode (index.html, dll) -> commit normal supaya Vercel deploy.
                $staged = git diff --cached --name-only
                $codeChanged = $staged | Where-Object { $_ -and $_ -ne 'okr_data.json' }
                if ($codeChanged) {
                    git commit -m "Auto sync $timestamp" | Out-Null
                } else {
                    git commit -m "chore: update OKR data $timestamp [vercel skip]" | Out-Null
                }
                git push origin main
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Selesai - GitHub & server online diupdate otomatis" -ForegroundColor Green
                Write-Host ""
            }
        }
    }
}
