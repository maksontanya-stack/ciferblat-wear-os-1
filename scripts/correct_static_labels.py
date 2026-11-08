"""Correct two baked labels on the 920-unit background, before final downsampling."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parents[1]
for theme in ('dark','light'):
 path=root/f'watchface/src/main/res/drawable-nodpi/background_{theme}.png'
 im=Image.open(path).convert('RGBA'); original=im.copy()
 for y in range(920):
  for x in range(920):
   dx,dy=x-460,y-452;r=math.hypot(dx,dy);a=math.degrees(math.atan2(dx,-dy))%360
   # Copy adjacent blank material at the same radius, preserving the ring texture.
   shift=0
   if 311<r<375 and 246<a<255: shift=9
   if 410<r<454 and 117<a<127: shift=8
   if shift:
    t=math.radians(a+shift)
    im.putpixel((x,y),original.getpixel((round(460+r*math.sin(t)),round(452-r*math.cos(t)))))
 ink='#ddddda' if theme=='dark' else '#222a31'
 def lettering(value,font,center,rotation,color):
  tile=Image.new('RGBA',(180,120));d=ImageDraw.Draw(tile)
  d.text((90,60),value,font=font,fill=color,anchor='mm')
  tile=tile.rotate(rotation,resample=Image.Resampling.BICUBIC,expand=True)
  im.alpha_composite(tile,(round(center[0]-tile.width/2),round(center[1]-tile.height/2)))
 font=ImageFont.truetype(str(root/'watchface/src/main/res/font/oswald.ttf'),50);font.set_variation_by_name('Bold')
 lettering('Э',font,(146,571),-57,ink)
 lettering('20',ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',38),(837,680),58,'#ddddda' if theme=='dark' else '#b8bec0')
 im.save(path)
