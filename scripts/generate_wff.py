"""Generate WFF v1 markup in the unchanged 920-unit reference coordinate grid."""
from pathlib import Path
import json
from xml.etree.ElementTree import Element, SubElement as S, ElementTree, indent
ROOT=Path(__file__).resolve().parents[1]
w=Element('WatchFace', width='920',height='920')
S(w,'Metadata',key='CLOCK_TYPE',value='DIGITAL')
S(w,'Metadata',key='PREVIEW_TIME',value='10:10:00')
bf=S(w,'BitmapFonts')
for theme in ('dark','light'):
 for kind,count,width,height in [('hour',24,310,260),('minute',60,162,122)]:
  f=S(bf,'BitmapFont',name=f'{kind}_{theme}')
  for n in range(count):
   text=f'{n:02}'
   S(f,'Word',name=text,resource=f'{kind}_{theme}_{text}',width=str(width),height=str(height))
u=S(w,'UserConfigurations')
theme_config=S(u,'ListConfiguration',id='theme',displayName='theme',defaultValue='dark')
S(theme_config,'ListOption',id='dark',displayName='dark')
S(theme_config,'ListOption',id='light',displayName='light')
scene=S(w,'Scene',backgroundColor='#000000')

def ambient(el,value='0'):
 S(el,'Variant',mode='AMBIENT',target='alpha',value=value)
def group(el,name,x=0,y=0,width=920,height=920,**kw):
 return S(el,'Group',name=name,x=str(x),y=str(y),width=str(width),height=str(height),**kw)
def themed(parent):
 choice=S(parent,'ListConfiguration',id='theme')
 for theme,flag,fg in [('dark','dark','#ddddda'),('light','light','#222a31')]:
  option=S(choice,'ListOption',id=flag)
  yield theme,fg,group(option,theme)
def text(el,x,y,width,height,size,fg,fmt,params=(),angle=0):
 p=S(el,'PartText',x=str(x),y=str(y),width=str(width),height=str(height),angle=str(angle))
 t=S(p,'Text',align='CENTER',ellipsis='TRUE',maxLines='1')
 f=S(t,'Font',family='oswald',size=str(size),weight='BOLD',color=fg)
 if params:
  template=S(f,'Template');template.text=fmt
  for param in params:S(template,'Parameter',expression=param)
 else:f.text=fmt
 return p

def replace_caption(parent,label,theme,fg,slot_x,slot_y,slot_w,slot_h,angle):
 if label=='weather': return  # Weather is identified by the provider icon, not a baked caption.
 original={'heart':'ПУЛЬС','floors':'ЭТАЖИ','battery':'ЗАРЯД','steps':'ШАГИ'}[label]
 condition=S(parent,'Condition'); expressions=S(condition,'Expressions')
 e=S(expressions,'Expression',name='changed_caption')
 e.text=f'[COMPLICATION.TITLE] != null && [COMPLICATION.TITLE] != "{original}"'
 compare=S(condition,'Compare',expression='changed_caption')
 world=group(compare,'caption_'+label+'_'+theme)
 patch=json.loads((ROOT/'design/caption-layout.json').read_text())[label]
 image=S(world,'PartImage',**{key:str(value) for key,value in patch.items()})
 S(image,'Image',resource='caption_'+label+'_'+theme)
 angles={'heart':(340,370,'CLOCKWISE',640),'floors':(258,226,'COUNTER_CLOCKWISE',730),'battery':(205,178,'COUNTER_CLOCKWISE',730),'steps':(145.5,125,'COUNTER_CLOCKWISE',730)}
 start,end,direction,diameter=angles[label]
 part=S(world,'PartText',x='0',y='0',width='920',height='920')
 curved=S(part,'TextCircular',centerX='460',centerY='452',width=str(diameter),height=str(diameter),startAngle=str(start),endAngle=str(end),direction=direction,align='CENTER',ellipsis='TRUE')
 font=S(curved,'Font',family='oswald',size='43',weight='BOLD',color=fg)
 upper=S(font,'Upper'); template=S(upper,'Template');template.text='%s'
 S(template,'Parameter',expression='[COMPLICATION.TITLE]')

interactive=group(scene,'interactive')
ambient(interactive)
for theme,fg,g in themed(interactive):
 p=S(g,'PartImage',x='0',y='0',width='920',height='920')
 S(p,'Image',resource=f'background_{theme}')
 clock=S(g,'DigitalClock',x='0',y='0',width='920',height='920')
 for kind,x,y,width,height,size,fmt in [('hour',267,337,310,260,260,'hh'),('minute',610,309,162,122,122,'mm')]:
  tt=S(clock,'TimeText',x=str(x),y=str(y),width=str(width),height=str(height),format=fmt,hourFormat='24',align='CENTER')
  S(tt,'BitmapFont',family=f'{kind}_{theme}',size=str(size))
 # Device-localized weekday/date; no hard-coded calendar date.
 p=S(g,'PartText',x='599',y='237',width='170',height='52')
 t=S(p,'Text',align='CENTER'); f=S(t,'Font',family='oswald',size='43',weight='BOLD',color=fg)
 up=S(f,'Upper'); template=S(up,'Template');template.text='%s %s.%s'
 for value in ['[DAY_OF_WEEK_S]','[DAY_Z]','[MONTH_Z]']:S(template,'Parameter',expression=value)
# Each slot uses scene coordinates so captions and data have a shared, stable transform.
slot_bounds={'heart':(320,55,280,110),'weather':(100,145,200,205),'floors':(70,510,220,220),'battery':(280,735,350,120),'steps':(640,480,215,260)}
for slot_id,label,x,y,width,height,angle in [(1,'heart',498,91,92,65,15),(2,'weather',140,165,160,180,0),(3,'floors',200,660,86,70,47),(4,'battery',470,747,133,62,-6),(5,'steps',690,539,171,62,-62)]:
 slot=S(scene,'ComplicationSlot',slotId=str(slot_id),displayName=label,x='0',y='0',width='920',height='920',supportedTypes='SHORT_TEXT RANGED_VALUE LONG_TEXT EMPTY',isCustomizable='TRUE')
 ambient(slot)
 provider={'battery':'WATCH_BATTERY','steps':'STEP_COUNT'}.get(label,'EMPTY')
 S(slot,'DefaultProviderPolicy',defaultSystemProvider=provider,defaultSystemProviderType='SHORT_TEXT' if provider!='EMPTY' else 'EMPTY')
 bx,by,bw,bh=slot_bounds[label]
 S(slot,'BoundingBox',x=str(bx),y=str(by),width=str(bw),height=str(bh))
 for ctype in ['SHORT_TEXT','RANGED_VALUE','LONG_TEXT','EMPTY']:
  comp=S(slot,'Complication',type=ctype)
  cg=group(comp,f'{label}_{ctype}')
  for theme,fg,g in themed(cg):
   def slot_text(parent,fmt,params=()):
    return text(parent,x+(20 if label=='weather' else 0),y+(20 if label=='weather' else 0),140 if label=='weather' else width,65,43,fg,fmt,params,angle=-45 if label=='weather' else angle)
   if ctype=='EMPTY':
    slot_text(g,'—')
   else:
    replace_caption(g,label,theme,fg,x,y,width,height,angle)
    condition=S(g,'Condition'); expressions=S(condition,'Expressions')
    e=S(expressions,'Expression',name='has_display_text');e.text='[COMPLICATION.TEXT] != null'
    present=S(condition,'Compare',expression='has_display_text')
    display_value='[COMPLICATION.TEXT]'
    if label=='weather':
     title='[COMPLICATION.TITLE]';length=f'textLength({title})'
     temperature=f'{title} != null && {length} >= 2 && (subText({title}, {length}-1, {length}) == "°" || subText({title}, {length}-2, {length}) == "°C" || subText({title}, {length}-2, {length}) == "°F")'
     display_value=f'({temperature}) ? {title} : [COMPLICATION.TEXT]'
    slot_text(present,'%s',(display_value,))
    fallback=S(condition,'Default')
    if ctype=='RANGED_VALUE': slot_text(fallback,'%.0f',('[COMPLICATION.RANGED_VALUE_VALUE]',))
    else: slot_text(fallback,'—')
    if label=='weather':
     condition=S(g,'Condition');ex=S(condition,'Expressions')
     e=S(ex,'Expression',name='has_weather_icon');e.text='[COMPLICATION.MONOCHROMATIC_IMAGE] != null'
     compare=S(condition,'Compare',expression='has_weather_icon')
     pi=S(compare,'PartImage',x=str(x),y=str(y+100),width='72',height='72',tintColor=fg)
     S(pi,'Image',resource='[COMPLICATION.MONOCHROMATIC_IMAGE]')

# AMOLED ambient: no light background and no active complication rendering.
aod=group(scene,'ambient',alpha='0');ambient(aod,'255')
clock=S(aod,'DigitalClock',x='0',y='0',width='920',height='920')
# Ambient keeps the same measured positions and sizes; only brightness and background change.
for kind,x,y,width,height,size,fmt in [('hour',267,337,310,260,260,'hh'),('minute',610,309,162,122,122,'mm')]:
 t=S(clock,'TimeText',x=str(x),y=str(y),width=str(width),height=str(height),format=fmt,hourFormat='24',align='CENTER',alpha='100')
 S(t,'BitmapFont',family=f'{kind}_dark',size=str(size))
text(aod,599,237,170,52,43,'#777777','%s.%s',('[DAY_Z]','[MONTH_Z]'))
indent(w)
ElementTree(w).write(ROOT/'watchface/src/main/res/raw/watchface.xml',encoding='utf-8',xml_declaration=True)
