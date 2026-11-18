"""Check runtime coverage, references and configuration rather than only packaging."""
from pathlib import Path
import json
import struct
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
xml = root / 'watchface/src/main/res/raw/watchface.xml'
before = xml.read_bytes()
exec(compile((root/'scripts/generate_wff.py').read_text(), 'generate_wff.py', 'exec'), {'__file__':str(root/'scripts/generate_wff.py')})
if xml.read_bytes() != before:
    raise SystemExit('Generated WFF XML was stale; regenerate and commit it')
w = ET.parse(xml).getroot()
# Removed caption choices keep their old numeric IDs reserved so an update
# cannot reinterpret a previously saved setting as another metric.
catalog = json.loads((root/'design/metric-captions.json').read_text())
expected_captions = {2:'ПУЛЬС',3:'ШАГИ',5:'ЗАРЯД',6:'КРОВ. ДАВЛ.',8:'КАЛОРИИ',9:'КИСЛОРОД',10:'СОН',11:'ВОСХОД',12:'ЗАКАТ',13:'БУДИЛЬНИК',14:'ПОГОДА',15:'ТЕМП.',16:'УФ'}
if {item['id']:item['title'] for item in catalog} != expected_captions:
    raise SystemExit('Unexpected manual caption catalog or unstable IDs')
for config in w.find('UserConfigurations').findall('ListConfiguration'):
    if not config.attrib['id'].startswith('caption_'): continue
    ids = [int(option.attrib['id']) for option in config.findall('ListOption')]
    if ids != [0,*expected_captions,99]:
        raise SystemExit(f'Unexpected caption options: {config.attrib["id"]} {ids}')
print('PASS: approved caption catalog with stable update IDs')
# Samsung's phone editor shows icon-only round tiles for ListOptions. Missing
# icons render as the blank circles reported on the physical Galaxy device.
drawable_dir = root / 'watchface/src/main/res/drawable-nodpi'
for option in w.find('UserConfigurations').iter('ListOption'):
    icon = option.attrib.get('icon')
    if not icon:
        raise SystemExit(f'Missing editor icon for ListOption {option.attrib["id"]}')
    icon_file = drawable_dir / f'{icon}.png'
    if not icon_file.is_file():
        raise SystemExit(f'Missing editor drawable: {icon_file.name}')
    width,height = struct.unpack('>II',icon_file.read_bytes()[16:24])
    if width > 400 or height > 400:
        raise SystemExit(f'Editor icon exceeds WFF 400px limit: {icon_file.name}')
preview = drawable_dir / 'preview.png'
if preview.read_bytes() != (root/'design/dark-450.png').read_bytes():
    raise SystemExit('Packaged phone preview is stale')
print('PASS: every list option has a phone-editor icon and current preview')
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
