#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
[[ -f wearos1.apk ]] || { echo 'Extract the full installation ZIP: wearos1.apk is missing.'; exit 1; }
if [[ ! -x platform-tools/adb ]]; then
 case "$(uname -s)" in
  Darwin) platform=darwin;;
  Linux) platform=linux;;
  *) echo 'Use install.cmd on Windows.'; exit 1;;
 esac
 curl --fail --location --retry 3 "https://dl.google.com/android/repository/platform-tools-latest-${platform}.zip" -o platform-tools.zip
 unzip -qo platform-tools.zip
 rm platform-tools.zip
fi
adb=./platform-tools/adb
echo 'Watch and computer must use the same Wi-Fi.'
echo 'Watch: Developer options > Wireless debugging > Pair new device.'
read -r -p 'Watch IPv4 address (without port): ' watch_ip
[[ "$watch_ip" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] || { echo 'Invalid address'; exit 1; }
read -r -p 'Pairing port from pairing-code screen: ' pair_port
[[ "$pair_port" =~ ^[0-9]{1,5}$ ]] || exit 1
read -r -p 'Six-digit pairing code: ' pair_code
[[ "$pair_code" =~ ^[0-9]{6}$ ]] || exit 1
"$adb" pair "${watch_ip}:${pair_port}" "$pair_code"
echo 'Return to the main Wireless debugging screen; use its DIFFERENT connection port.'
read -r -p 'Connection port: ' connect_port
[[ "$connect_port" =~ ^[0-9]{1,5}$ ]] || exit 1
target="${watch_ip}:${connect_port}"
"$adb" connect "$target"
sdk=$("$adb" -s "$target" shell getprop ro.build.version.sdk | tr -d '\r')
[[ "$sdk" =~ ^[0-9]+$ && "$sdk" -ge 36 ]] || { echo 'Wear OS 6 or newer is required. Update the watch software.'; exit 1; }
"$adb" -s "$target" install -r wearos1.apk
"$adb" disconnect "$target"
echo 'Installed. Long-press watchface > Add watchface > Wear OS 1. Customize theme/data sources. Disable wireless debugging after installation.'
