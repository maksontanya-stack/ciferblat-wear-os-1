#!/usr/bin/env bash
set -euo pipefail
mkdir -p smoke-output
adb install -r watchface/build/outputs/apk/debug/watchface-debug.apk
adb shell settings put system screen_off_timeout 1800000
adb shell settings put global stay_on_while_plugged_in 3
adb shell input keyevent KEYCODE_WAKEUP
adb shell wm dismiss-keyguard
adb shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId ru.meta.wearos.classic1
sleep 15
adb exec-out screencap -p > smoke-output/active-first.png
adb shell date > smoke-output/time-first.txt
sleep 65
adb shell input keyevent KEYCODE_WAKEUP
sleep 2
adb exec-out screencap -p > smoke-output/active-next-minute.png
adb shell date > smoke-output/time-second.txt
adb logcat -d > smoke-output/logcat.txt
python3 scripts/verify_screenshots.py
