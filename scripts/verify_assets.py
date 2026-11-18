"""Check the fidelity and device dimensions of the committed artwork."""
from pathlib import Path
import math
import re
from PIL import Image

root = Path(__file__).resolve().parents[1]
reference = Image.open(root / 'references/29937.jpg').convert('RGB')
expected = reference.crop((139, 140, 1059, 1060))
actual = Image.open(root / 'design/dark-master.png').convert('RGB')
if actual.size != expected.size or actual.tobytes() != expected.tobytes():
    raise SystemExit('Dark master differs from the original reference crop')
for theme in ('dark', 'light'):
    with Image.open(root / f'design/{theme}-450.png') as image:
        if image.size != (450, 450) or image.mode != 'RGBA':
            raise SystemExit(f'{theme}: expected 450x450 RGBA')
        if image.getpixel((0, 0))[3] != 0:
            raise SystemExit(f'{theme}: outside of dial must be transparent')
ticks = Image.open(root/'watchface/src/main/res/drawable-nodpi/background_dark.png').convert('RGB')
def tick_peak(angle):
    peak=0
    for offset in (-.5,-.25,0,.25,.5):
        values=[]
        for radius in range(205,215):
            radians=math.radians(angle+offset)
            x=round(225+radius*math.sin(radians));y=round(221-radius*math.cos(radians))
            values.append(max(ticks.getpixel((x,y))))
        peak=max(peak,sum(values)/len(values))
    return peak
for angle in (97.5,102.5,108,113,127.5,132.5,137.5,142.5):
    if tick_peak(angle)<60:raise SystemExit(f'Missing mirrored outer tick at {angle} degrees')
for angle in (111,129):
    if tick_peak(angle)>30:raise SystemExit(f'Uneven obsolete outer tick remains at {angle} degrees')

# The five deliberate inner arcs (the date sector has none) must all use the
# same six-degree clearance from the red markers.  Keeping this mathematical
# check alongside the bitmap checks prevents a one-pixel hand adjustment from
# reintroducing uneven gaps.
svg = (root / 'design/continuous-arcs.svg').read_text()
paths = re.findall(r'M([0-9.]+),([0-9.]+) A300,300 0 0 1 ([0-9.]+),([0-9.]+)', svg)
expected_arcs = ((336, 24), (276, 324), (216, 264), (96, 144), (156, 204))
if len(paths) != len(expected_arcs):
    raise SystemExit(f'Expected {len(expected_arcs)} inner arcs, got {len(paths)}')
def polar_angle(x, y):
    return round(math.degrees(math.atan2(float(x) - 460, 452 - float(y))) % 360)
actual_arcs = tuple((polar_angle(x1, y1), polar_angle(x2, y2)) for x1, y1, x2, y2 in paths)
if actual_arcs != expected_arcs:
    raise SystemExit(f'Inner-arc clearances are uneven: {actual_arcs!r}')
print('PASS: original geometry preserved; outer ticks and all inner-arc clearances are uniform')
