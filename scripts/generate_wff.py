"""Generate WFF v1 markup in the unchanged 920-unit reference coordinate grid."""
from pathlib import Path
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
S(u,'BooleanConfiguration',id='light',displayName='light',defaultValue='FALSE')
scene=S(w,'Scene',backgroundColor='#000000')

def ambient(el,value='0'):
 S(el,'Variant',mode='AMBIENT',target='alpha',value=value)
def group(el,name,x=0,y=0,width=920,height=920,**kw):
 return S(el,'Group',name=name,x=str(x),y=str(y),width=str(width),height=str(height),**kw)
def themed(parent):
 choice=S(parent,'BooleanConfiguration',id='light')
 for theme,flag,fg in [('dark','FALSE','#ddddda'),('light','TRUE','#222a31')]:
  option=S(choice,'BooleanOption',id=flag)
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
 text(g,470,747,133,62,47,fg,'%d%%',('[BATTERY_PERCENT]',),-6)
 text(g,690,539,171,62,43,fg,'%d',('[STEP_COUNT]',),-62)
# Slots are deliberately outside the interactive Group: WFF owns the data-source editor.
for slot_id,label,x,y,width,height,angle in [(1,'heart',498,91,92,65,15),(2,'weather',140,165,160,180,0),(3,'floors',200,660,86,70,47)]:
 slot=S(scene,'ComplicationSlot',slotId=str(slot_id),displayName=label,x=str(x),y=str(y),width=str(width),height=str(height),angle=str(angle),supportedTypes='SHORT_TEXT EMPTY',isCustomizable='TRUE')
 ambient(slot)
 S(slot,'DefaultProviderPolicy',defaultSystemProvider='EMPTY',defaultSystemProviderType='EMPTY')
 S(slot,'BoundingBox',x='0',y='0',width=str(width),height=str(height))
 for ctype in ['SHORT_TEXT','EMPTY']:
  comp=S(slot,'Complication',type=ctype)
  # Group is permitted inside Complication; it lets both themes use the same slot ID.
  cg=group(comp,f'{label}_{ctype}',width=width,height=height)
  for theme,fg,g in themed(cg):
   if ctype=='EMPTY':
    text(g,20 if label=='weather' else 0,20 if label=='weather' else 0,140 if label=='weather' else width,65,43,fg,'—',angle=-45 if label=='weather' else 0)
   else:
    text(g,20 if label=='weather' else 0,20 if label=='weather' else 0,140 if label=='weather' else width,65,43,fg,'%s',('[COMPLICATION.TEXT]',),angle=-45 if label=='weather' else 0)
    if label=='weather':
     condition=S(g,'Condition');ex=S(condition,'Expressions')
     e=S(ex,'Expression',name='has_weather_icon');e.text='[COMPLICATION.MONOCHROMATIC_IMAGE] != null'
     compare=S(condition,'Compare',expression='has_weather_icon')
     pi=S(compare,'PartImage',x='0',y='100',width='72',height='72',tintColor=fg)
     S(pi,'Image',resource='[COMPLICATION.MONOCHROMATIC_IMAGE]')
# AMOLED ambient: no light background and no active complication rendering.
aod=group(scene,'ambient',alpha='0');ambient(aod,'255')
clock=S(aod,'DigitalClock',x='0',y='0',width='920',height='920')
t=S(clock,'TimeText',x='190',y='345',width='540',height='165',format='hh:mm',hourFormat='24',align='CENTER')
S(t,'Font',family='oswald',size='125',weight='LIGHT',color='#999999')
text(aod,280,530,360,60,36,'#777777','%s.%s',('[DAY_Z]','[MONTH_Z]'))
indent(w)
ElementTree(w).write(ROOT/'watchface/src/main/res/raw/watchface.xml',encoding='utf-8',xml_declaration=True)
