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
# Prevent a repeat of the large per-theme/per-metric scene expansion. This is a
# complexity budget, not a claim about FPS or execution time on physical watches.
text_nodes=len(list(w.iter('PartText')))
if len(before)>1_100_000 or text_nodes>250:
    raise SystemExit(f'Runtime complexity budget exceeded: {len(before)} bytes, {text_nodes} text nodes')
print(f'PASS: runtime complexity budget ({len(before)} bytes, {text_nodes} text nodes)')
resources = root / 'watchface/src/main/res/drawable-nodpi'
for theme in ('dark', 'light'):
    for kind, count in [('hour', 24), ('minute', 60)]:
        expected = {f'{kind}_{theme}_{n:02}' for n in range(count)}
        group = w.find(f"Scene/Group[@name='interactive']/ListConfiguration/ListOption/Group[@name='{theme}']/Group[@name='active_{theme}_{kind}']")
        if group is None: raise SystemExit('Missing live time group')
        images = {x.attrib['resource'] for x in group.iter('Image')}
        if images != expected: raise SystemExit(f'{kind}_{theme}: incomplete time coverage')
        for resource in expected:
            if not (resources/(resource+'.png')).is_file(): raise SystemExit('Missing time image')
            if kind=='hour':
                dimensions=struct.unpack('>II',(resources/(resource+'.png')).read_bytes()[16:24])
                if dimensions!=(155,150) or group.attrib['height']!='300': raise SystemExit('Hour sprite padding/scale mismatch')
slots = list(w.iter('ComplicationSlot'))
if len({s.attrib['slotId'] for s in slots}) != 5: raise SystemExit('Invalid data slot IDs')
for slot in slots:
    if slot.find('BoundingArc') is None or slot.find('BoundingBox') is not None: raise SystemExit('Data field must have radial interaction bounds')
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
print(f'PASS: complete 24h/60min bitmap coverage, five unique slots, empty fallbacks, AOD; all decoded bitmaps total {byte_count/1024/1024:.2f} MiB')
