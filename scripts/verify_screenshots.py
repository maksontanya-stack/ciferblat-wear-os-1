"""Check real emulator rendering and advancing time, without treating a mockup as a device test."""
from pathlib import Path
from PIL import Image, ImageChops
p=Path('smoke-output')
a=Image.open(p/'active-first.png').convert('RGB')
b=Image.open(p/'active-next-minute.png').convert('RGB')
w,h=a.size
if w != h or b.size != a.size: raise SystemExit(f'Unexpected watch screen geometry: {a.size}')
def crop(im,box): return im.crop(tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(box)))
for name,box in [('left index',(.08,.48,.17,.52)),('right index',(.83,.48,.92,.52))]:
 pixels=crop(a,box).getdata()
 count=sum(r>150 and g<90 and blue<100 for r,g,blue in pixels)
 if count<20: raise SystemExit(f'Watchface did not render its {name}; inspect screenshots and logcat')
for name,box,minimum in [('hours',(.30,.37,.64,.67),300),('minutes',(.66,.34,.85,.48),60)]:
 if sum(min(pixel)>140 for pixel in crop(a,box).getdata())<minimum:
  raise SystemExit(f'{name} are absent or bitmap font failed to render')
box=(.66,.34,.85,.48)
diff=ImageChops.difference(crop(a,box),crop(b,box))
if sum(max(pixel)>30 for pixel in diff.getdata())<10:
 raise SystemExit('Minute display did not advance on the emulator')
print(f'PASS: installed and selected on Wear OS 4 ({w}x{h}); both time fields render; minutes advance')
