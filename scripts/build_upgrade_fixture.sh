#!/usr/bin/env bash
# Build the previous published preview layout with the same debug certificate as this run.
# Neither the legacy APK nor emulator providers enter the production ZIP.
set -euo pipefail
legacy_commit=33b8eaf383399282e986997a3161c690660d0007
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
git show "${legacy_commit}:watchface/src/main/AndroidManifest.xml" > watchface/src/main/AndroidManifest.xml
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
PY
./gradlew :watchface:assembleDebug --console=plain
mkdir -p upgrade-fixture
cp watchface/build/outputs/apk/debug/watchface-debug.apk upgrade-fixture/legacy-debug.apk
