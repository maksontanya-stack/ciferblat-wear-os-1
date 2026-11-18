"""Check the fidelity and device dimensions of the committed artwork."""
from pathlib import Path
import math
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
print('PASS: original geometry preserved; lower-right ticks mirror 35/40 with no 111/129 degree artifacts')
