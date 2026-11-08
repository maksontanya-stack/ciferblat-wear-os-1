"""WFF packages must contain resources, with no generated Java/Kotlin bytecode."""
from pathlib import Path
import sys,zipfile
apk=Path(sys.argv[1])
with zipfile.ZipFile(apk) as archive:
    names=archive.namelist()
    if any(n.endswith('.dex') for n in names):
        raise SystemExit('Unexpected DEX in resource-only Watch Face Format APK')
    if 'AndroidManifest.xml' not in names or 'resources.arsc' not in names:
        raise SystemExit('Missing compiled Android resources')
print(f'PASS: {apk.name} is a resource-only Android package without DEX')
