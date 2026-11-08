"""Check runtime coverage, references and configuration rather than only packaging."""
from pathlib import Path
import struct
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
xml = root / 'watchface/src/main/res/raw/watchface.xml'
before = xml.read_bytes()
exec(compile((root/'scripts/generate_wff.py').read_text(), 'generate_wff.py', 'exec'), {'__file__':str(root/'scripts/generate_wff.py')})
if xml.read_bytes() != before:
    raise SystemExit('Generated WFF XML was stale; regenerate and commit it')
w = ET.parse(xml).getroot()
resources = root / 'watchface/src/main/res/drawable-nodpi'
for theme in ('dark', 'light'):
    for kind, count in [('hour', 24), ('minute', 60)]:
        font = w.find(f"BitmapFonts/BitmapFont[@name='{kind}_{theme}']")
        if font is None: raise SystemExit('Missing bitmap family')
        words = {x.attrib['name'] for x in font}
        if words != {f'{n:02}' for n in range(count)}:
            raise SystemExit(f'{kind}_{theme}: incomplete time coverage')
        for word in font:
            if not (resources/(word.attrib['resource']+'.png')).is_file():
                raise SystemExit('Missing bitmap image')
slots = list(w.iter('ComplicationSlot'))
if len({s.attrib['slotId'] for s in slots}) != 3: raise SystemExit('Invalid data slot IDs')
for slot in slots:
    if slot.find("Complication[@type='EMPTY']") is None:
        raise SystemExit('Missing empty-data fallback')
if w.find("Scene/Group[@name='ambient']") is None: raise SystemExit('Missing ambient mode')
# A conservative sum of *all* decoded images, including unused theme and preview.
# Real runtime loads fewer images; this bounds bitmap storage, not total WFF engine memory.
byte_count = 0
for file in resources.glob('*.png'):
    data = file.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n': raise SystemExit('Invalid PNG')
    width,height = struct.unpack('>II', data[16:24])
    byte_count += width*height*4
print(f'PASS: complete 24h/60min bitmap coverage, three unique slots, empty fallbacks, AOD; all decoded bitmaps total {byte_count/1024/1024:.2f} MiB')
