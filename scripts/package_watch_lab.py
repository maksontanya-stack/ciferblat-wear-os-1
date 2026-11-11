#!/usr/bin/env python3
"""Package the one-click Windows launcher and unpacked Chrome extension."""
from pathlib import Path
import json, shutil, zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist' / 'galaxy-watch-lab'
EXTENSION = OUT / 'chrome-extension'

def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    # A local HTML file can load sibling JavaScript and images without a server.
    for name in ('index.html', 'profiles.js', 'profiles.json'):
        copy(ROOT/'lab'/name, OUT/'lab'/name)
    copy(ROOT/'design'/'dark-450.png', OUT/'design'/'dark-450.png')
    copy(ROOT/'install'/'OPEN-GALAXY-WATCH-LAB.cmd', OUT/'OPEN-GALAXY-WATCH-LAB.cmd')
    copy(ROOT/'docs'/'WATCH-LAB-RU.md', OUT/'ИНСТРУКЦИЯ-RU.md')

    # Chrome extensions are self-contained. The default picture is deliberately
    # omitted: users select the image they want to test.
    for name in ('index.html', 'profiles.js', 'profiles.json'):
        copy(ROOT/'lab'/name, EXTENSION/name)
    manifest = {
        'manifest_version': 3, 'name': 'Galaxy Watch Lab', 'version': '1.0.0',
        'description': 'Local visual test bench for Samsung Galaxy Watch faces.',
        'action': {'default_title': 'Open Galaxy Watch Lab'},
        'background': {'service_worker': 'service-worker.js'}
    }
    (EXTENSION/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (EXTENSION/'service-worker.js').write_text("chrome.action.onClicked.addListener(() => chrome.tabs.create({url: 'index.html'}));\n", encoding='utf-8')
    with zipfile.ZipFile(OUT/'Galaxy-Watch-Lab-Chrome-extension.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in EXTENSION.rglob('*'):
            archive.write(path, path.relative_to(OUT))
    with zipfile.ZipFile(OUT/'Galaxy-Watch-Lab-one-click-Windows.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in OUT.rglob('*'):
            if path.is_file() and path.name != 'Galaxy-Watch-Lab-one-click-Windows.zip': archive.write(path, path.relative_to(OUT))
    print(f'PASS: {OUT}')

if __name__ == '__main__': main()
