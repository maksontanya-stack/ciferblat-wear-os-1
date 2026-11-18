$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
try {
    $adb = Join-Path $PSScriptRoot 'platform-tools\adb.exe'
    if (-not (Test-Path $adb)) { throw 'Run update.cmd first to download Android Platform Tools.' }
    $target = (Read-Host 'Watch IP:port from the main Wireless debugging screen').Trim()
    if ($target -notmatch '^\d{1,3}(\.\d{1,3}){3}:\d{1,5}$') { throw 'Enter IP:port.' }
    & $adb connect $target
    & $adb -s $target get-state
    if ($LASTEXITCODE -ne 0) { throw 'The watch is not connected. Check the current IP:port.' }
    Read-Host 'Open Customize on the watch. If it hangs, wait 15 seconds, then press Enter here'
    $folder = Join-Path $PSScriptRoot 'watchface-diagnostics'
    New-Item -ItemType Directory -Force $folder | Out-Null
    & $adb -s $target shell getprop ro.build.version.sdk | Out-File "$folder\android-api.txt" -Encoding utf8
    & $adb -s $target shell dumpsys package ru.meta.wearos.classic1 | Out-File "$folder\watchface-package.txt" -Encoding utf8
    & $adb -s $target shell dumpsys meminfo com.google.wear.watchface.runtime | Out-File "$folder\runtime-memory.txt" -Encoding utf8
    & $adb -s $target logcat -d -t 4000 | Select-String -Pattern 'watchface|watch.face|ru.meta.wearos.classic1|FATAL EXCEPTION|AndroidRuntime|ANR in|OutOfMemory|DWF' | Out-File "$folder\editor-errors.txt" -Encoding utf8
    $archive = Join-Path $PSScriptRoot 'watchface-diagnostics.zip'
    Compress-Archive -Path "$folder\*" -DestinationPath $archive -Force
    & $adb disconnect $target
    Write-Host 'Saved watchface-diagnostics.zip in this folder. No files were sent automatically.' -ForegroundColor Green
} catch { Write-Host $_.Exception.Message -ForegroundColor Red }
Read-Host 'Press Enter to close'
