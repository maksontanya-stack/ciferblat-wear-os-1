"""Uniform circular tick rings; preserve existing labels except the corrected 20."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont
root=Path(__file__).resolve().parents[1];ss=4;cx,cy=460,452
for theme in ('dark','light'):
 path=root/f'watchface/src/main/res/drawable-nodpi/background_{theme}.png'
 im=Image.open(path).convert('RGBA');assert im.size==(920,920)
 background=(7,7,7,255) if theme=='dark' else (50,63,73,255)
 for y in range(920):
  for x in range(920):
   r=math.hypot(x-cx,y-cy);angle=math.degrees(math.atan2(x-cx,cy-y))%360
   nearest=abs((angle+15)%30-15)
   twenty=abs((angle-120+180)%360-180)
   if 376<=r<=406 or (410<=r<=454 and (nearest>5 or twenty<7.5)):
    im.putpixel((x,y),background)
 overlay=Image.new('RGBA',(920*ss,920*ss));draw=ImageDraw.Draw(overlay)
 fine='#c0c0be' if theme=='dark' else '#b8c0c6';ink='#ddddda' if theme=='dark' else '#b8bec0'
 def pt(radius,angle):
  a=math.radians(angle);return ((cx+radius*math.sin(a))*ss,(cy-radius*math.cos(a))*ss)
 for angle in range(360):draw.line([pt(380,angle),pt(398,angle)],fill=fine,width=5)
 for radius in (378,400):
  draw.ellipse(((cx-radius)*ss,(cy-radius)*ss,(cx+radius)*ss,(cy+radius)*ss),outline='#707578' if theme=='dark' else '#75848e',width=3)
 for minute in range(60):
  if minute%5:draw.line([pt(431,minute*6),pt(448,minute*6)],fill=ink,width=10)
 # Same radial distance as the original 40; leave a clear gap to 114/126° ticks.
 center=pt(432,120)
 tile=Image.new('RGBA',(180*ss,120*ss));td=ImageDraw.Draw(tile)
 font=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',38*ss)
 td.text((90*ss,60*ss),'20',font=font,fill=ink,anchor='mm')
 tile=tile.rotate(60,resample=Image.Resampling.BICUBIC,expand=True)
 overlay.alpha_composite(tile,(round(center[0]-tile.width/2),round(center[1]-tile.height/2)))
 overlay=overlay.resize((920,920),Image.Resampling.LANCZOS)
 im.alpha_composite(overlay);im.save(path)
