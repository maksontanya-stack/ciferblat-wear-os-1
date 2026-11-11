"""Remove every baked sector caption, preserving tick rings, arcs and red markers."""
from pathlib import Path
import math
from PIL import Image
root=Path(__file__).resolve().parents[1]
for theme in ('dark','light'):
 p=root/f'watchface/src/main/res/drawable-nodpi/background_{theme}.png'
 im=Image.open(p).convert('RGBA');texture=Image.open(root/'design/texture-field.png').convert('RGBA') if theme=='light' else None
 assert im.size==(920,920)
 for y in range(920):
  for x in range(920):
   r=math.hypot(x-460,y-452);a=math.degrees(math.atan2(x-460,452-y))%360
   if 305<r<376 and min(abs((a-mark+180)%360-180) for mark in (30,90,150,210,270,330))>4:
    v=round(max(5,23-.018*x-.010*y))
    im.putpixel((x,y),texture.getpixel((x,y)) if texture else (v,v,v,255))
 im.save(p)
