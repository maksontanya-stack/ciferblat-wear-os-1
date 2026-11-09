#!/usr/bin/env bash
# Build the previous WFF 1 layout with the same debug certificate as this run.
# Neither the legacy APK nor emulator providers enter the production ZIP.
set -euo pipefail
legacy_commit=8c4f4adc43d6c328b3d351b93827e743dbd056ac
git fetch --depth=1 origin "$legacy_commit"
fixture_tmp=$(mktemp -d)
cp watchface/src/debug/res/raw/watchface.xml "$fixture_tmp/current.xml"
cp watchface/src/main/AndroidManifest.xml "$fixture_tmp/manifest.xml"
restore_fixture() {
 cp "$fixture_tmp/current.xml" watchface/src/debug/res/raw/watchface.xml
 cp "$fixture_tmp/manifest.xml" watchface/src/main/AndroidManifest.xml
 rm -rf "$fixture_tmp"
}
trap restore_fixture EXIT
git show "${legacy_commit}:watchface/src/main/res/raw/watchface.xml" > "$fixture_tmp/legacy.xml"
python3 - "$fixture_tmp/legacy.xml" <<'PY'
from pathlib import Path
from xml.etree import ElementTree as E
import sys
w=E.parse(sys.argv[1])
for slot in w.iter('ComplicationSlot'):
 name=slot.attrib['displayName'].title()
 policy=slot.find('DefaultProviderPolicy')
 policy.set('primaryProvider',f'ru.meta.wearos.classic1.fixtures/ru.meta.wearos.classic1.fixtures.FixtureService${name}')
 policy.set('primaryProviderType','RANGED_VALUE' if name=='Heart' else 'SHORT_TEXT')
w.write('watchface/src/debug/res/raw/watchface.xml',encoding='utf-8',xml_declaration=True)
p=Path('watchface/src/main/AndroidManifest.xml')
p.write_text(p.read_text().replace('android:value="4"','android:value="1"'))
PY
./gradlew :watchface:assembleDebug --console=plain
mkdir -p upgrade-fixture
cp watchface/build/outputs/apk/debug/watchface-debug.apk upgrade-fixture/legacy-debug.apk
