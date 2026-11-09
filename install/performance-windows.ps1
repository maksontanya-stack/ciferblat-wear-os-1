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
    $folder = Join-Path $PSScriptRoot 'watchface-performance'
    New-Item -ItemType Directory -Force $folder | Out-Null
    & $adb -s $target shell getprop ro.build.version.sdk | Out-File "$folder\android-api.txt" -Encoding utf8
    & $adb -s $target shell dumpsys package ru.meta.wearos.classic1 | Out-File "$folder\watchface-package.txt" -Encoding utf8
    Read-Host 'Keep the watchface visible and the watch awake, then press Enter'
    & $adb -s $target shell date | Out-File "$folder\face-time.txt" -Encoding utf8
    & $adb -s $target shell top -b -n 3 -d 2 -m 25 | Out-File "$folder\face-cpu.txt" -Encoding utf8
    & $adb -s $target shell dumpsys meminfo com.google.wear.watchface.runtime | Out-File "$folder\face-memory.txt" -Encoding utf8
    Read-Host 'Press Enter, then open Customize on the watch and swipe its pages for 10 seconds'
    & $adb -s $target shell date | Out-File "$folder\editor-time.txt" -Encoding utf8
    & $adb -s $target shell top -b -n 6 -d 2 -m 25 | Out-File "$folder\editor-cpu.txt" -Encoding utf8
    & $adb -s $target shell dumpsys meminfo com.google.wear.watchface.runtime | Out-File "$folder\editor-memory.txt" -Encoding utf8
    foreach ($package in @('com.google.wear.watchface.runtime','com.google.android.wearable.sysui','com.android.systemui')) {
        & $adb -s $target shell dumpsys gfxinfo $package framestats | Out-File "$folder\frames-$package.txt" -Encoding utf8
    }
    & $adb -s $target logcat -d -t 4000 | Select-String -Pattern 'watchface|watch.face|ru.meta.wearos.classic1|FATAL EXCEPTION|AndroidRuntime|ANR in|OutOfMemory|DWF|Choreographer|Skipped.*frames' | Out-File "$folder\errors.txt" -Encoding utf8
    Compress-Archive -Path "$folder\*" -DestinationPath (Join-Path $PSScriptRoot 'watchface-performance.zip') -Force
    & $adb disconnect $target
    Write-Host 'Saved watchface-performance.zip. No files were sent automatically. No watch settings were changed.' -ForegroundColor Green
} catch { Write-Host $_.Exception.Message -ForegroundColor Red }
Read-Host 'Press Enter to close'
