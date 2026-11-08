#!/usr/bin/env bash
set -euo pipefail
mkdir -p smoke-output
trap 'adb logcat -d > smoke-output/logcat.txt' EXIT
# A fresh Wear image resets its default face late in initial boot.
# Wait for first-run initialization before selecting the package under test.
sleep 60
adb shell input keyevent KEYCODE_HOME
sleep 2
adb install -r testprovider/build/outputs/apk/debug/testprovider-debug.apk
adb install -r watchface/build/outputs/apk/debug/watchface-debug.apk
adb shell settings put system screen_off_timeout 1800000
adb shell settings put global stay_on_while_plugged_in 3
adb shell input keyevent KEYCODE_WAKEUP
adb shell wm dismiss-keyguard
adb shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId ru.meta.wearos.classic1
sleep 15
# Activate the face through the same picker confirmation used on a watch.
adb shell input swipe 227 227 227 227 1500
sleep 2
adb shell input tap 227 227
sleep 3
adb exec-out screencap -p > smoke-output/active-first.png
adb shell date > smoke-output/time-first.txt
sleep 65
adb shell input keyevent KEYCODE_WAKEUP
sleep 2
adb exec-out screencap -p > smoke-output/active-next-minute.png
adb shell date > smoke-output/time-second.txt
adb logcat -d > smoke-output/logcat.txt
python3 scripts/verify_screenshots.py
adb shell settings put secure enabled_accessibility_services ru.meta.wearos.classic1.fixtures/.EditorAccessibilityService
adb shell settings put secure accessibility_enabled 1
sleep 2

# Capture the real native watchface editor after Editable=true.
adb shell input swipe 227 227 227 227 1500
sleep 3
adb exec-out screencap -p > smoke-output/picker.png
adb shell input tap 227 380
sleep 4
adb exec-out screencap -p > smoke-output/editor.png

python3 scripts/editor_ui.py
