"""Regression: real Android providers may omit TITLE in both short and ranged data."""
from pathlib import Path
import subprocess,time,math
from PIL import Image
p=Path('smoke-output')
def adb(*args):return subprocess.check_output(['adb',*args])
def set_titleless(enabled):
 adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','titleless','--ez','enabled',str(enabled).lower())
 time.sleep(8)
before=Image.open(p/'active-next-minute.png').convert('RGB')
set_titleless(True)
(p/'active-dark-titleless.png').write_bytes(adb('exec-out','screencap','-p'))
after=Image.open(p/'active-dark-titleless.png').convert('RGB')
# Ignore the independently advancing minute/date. Only compare the actual five
# annular data sectors. Explicit titles and slot-default titles must match.
changed=0
for py in range(before.height):
 for px in range(before.width):
  dx=px*920/before.width-460;dy=py*920/before.height-452
  r=math.hypot(dx,dy)
  if 310<r<375 and max(abs(a-b) for a,b in zip(before.getpixel((px,py)),after.getpixel((px,py))))>30:
   changed+=1
if changed>20:raise SystemExit(f'Omitting TITLE removed or changed default sector captions ({changed} pixels)')
set_titleless(False)
print('PASS: titleless SHORT_TEXT and RANGED_VALUE preserve all five radial captions')
