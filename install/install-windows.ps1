param([switch]$UpdateOnly)
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Set-Location $PSScriptRoot
try {
    $apk = Join-Path $PSScriptRoot 'wearos1.apk'
    if (-not (Test-Path $apk)) { throw 'wearos1.apk is missing. Extract the entire installation ZIP first.' }
    $adb = Join-Path $PSScriptRoot 'platform-tools\adb.exe'
    if (-not (Test-Path $adb)) {
        Write-Host 'Downloading official Android Platform Tools from Google...'
        $archive = Join-Path $PSScriptRoot 'platform-tools.zip'
        Invoke-WebRequest 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip' -OutFile $archive -UseBasicParsing
        Expand-Archive $archive -DestinationPath $PSScriptRoot -Force
        Remove-Item $archive
    }
    Write-Host 'Connect the watch and computer to the same Wi-Fi.'
    if ($UpdateOnly) {
        Write-Host 'Watch: Wireless debugging > IP address and port (main screen).'
        $target = (Read-Host 'Watch IP:connection-port, for example 192.168.0.108:43651').Trim()
        if ($target -notmatch '^\d{1,3}(\.\d{1,3}){3}:\d{1,5}$') { throw 'Enter IP:port from the main Wireless debugging screen.' }
    } else {
    Write-Host 'Watch: Developer options > Wireless debugging > Pair new device.'
    $watchIp = (Read-Host 'Watch IP address (example 192.168.1.25)').Trim()
    if ($watchIp -notmatch '^\d{1,3}(\.\d{1,3}){3}$') { throw 'Enter an IPv4 address, without a port.' }
    $pairPort = (Read-Host 'Pairing port from the pairing-code screen').Trim()
    if ($pairPort -notmatch '^\d{1,5}$') { throw 'Invalid pairing port.' }
    $code = (Read-Host 'Six-digit pairing code displayed on the watch').Trim()
    if ($code -notmatch '^\d{6}$') { throw 'The pairing code must contain six digits.' }
    & $adb pair "${watchIp}:${pairPort}" $code
    if ($LASTEXITCODE -ne 0) { throw 'Pairing failed. Keep the pairing-code screen open and try again.' }
    Write-Host 'Return to the main Wireless debugging screen. The connection port is DIFFERENT from the pairing port.'
    $connectPort = (Read-Host 'Connection port from IP address and port').Trim()
    if ($connectPort -notmatch '^\d{1,5}$') { throw 'Invalid connection port.' }
    $target = "${watchIp}:${connectPort}"
    }
    & $adb connect $target
    if ($LASTEXITCODE -ne 0) { throw 'Connection failed.' }
    $sdk = (& $adb -s $target shell getprop ro.build.version.sdk | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $sdk -notmatch '^\d+$') { throw 'Confirm the prompt on the watch. If this computer is no longer paired, run install.cmd to pair again.' }
    if ([int]$sdk -lt 36) { throw 'This watchface needs Wear OS 6 or newer. Update the watch software first.' }
    & $adb -s $target install -r $apk
    if ($LASTEXITCODE -ne 0) { throw 'APK installation failed. Read the ADB error above; do not uninstall an existing version just to bypass a signature mismatch.' }
    & $adb disconnect $target
    Write-Host 'Installed. Long-press the current watchface > Add watchface > find Wear OS 1 near the end.' -ForegroundColor Green
    Write-Host 'Choose Customize to select the light theme and data sources. Disable Wireless debugging when finished.'
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}
Read-Host 'Press Enter to close'
