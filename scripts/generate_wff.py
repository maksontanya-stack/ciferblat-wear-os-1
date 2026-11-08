"""Generate WFF v1 markup in the unchanged 920-unit reference coordinate grid."""
from pathlib import Path
import json
from xml.etree.ElementTree import Element, SubElement as S, ElementTree, indent
ROOT=Path(__file__).resolve().parents[1]
w=Element('WatchFace', width='920',height='920')
S(w,'Metadata',key='CLOCK_TYPE',value='DIGITAL')
S(w,'Metadata',key='PREVIEW_TIME',value='10:10:00')
u=S(w,'UserConfigurations')
theme_config=S(u,'ListConfiguration',id='theme',displayName='theme',defaultValue='0')
S(theme_config,'ListOption',id='0',displayName='dark')
S(theme_config,'ListOption',id='1',displayName='light')
scene=S(w,'Scene',backgroundColor='#000000')

def ambient(el,value='0'):
 S(el,'Variant',mode='AMBIENT',target='alpha',value=value)
def group(el,name,x=0,y=0,width=920,height=920,**kw):
 return S(el,'Group',name=name,x=str(x),y=str(y),width=str(width),height=str(height),**kw)
def themed(parent):
 choice=S(parent,'ListConfiguration',id='theme')
 for theme,flag,fg in [('dark','0','#ddddda'),('light','1','#222a31')]:
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

# Clockwise angles are measured from twelve o'clock. Keep four degrees clear
# of each red marker; all geometry uses the same reference center and radii.
SECTORS={'heart':(330,390),'weather':(270,330),'floors':(210,270),'battery':(150,210),'steps':(90,150)}

def radial_text(parent,label,fg,fmt,params,scope,width_em=None):
 import math
 start,end=SECTORS[label]; start+=4;end-=4
 if label=='weather': start+=16 # Leave room for the provider icon at the left end.
 clockwise=label in ('heart','weather')
 if not clockwise: start,end=end,start
 # Oswald's widest supported glyph at this weight is bounded by 1.06 em.
 # Choose the largest size whose conservative line width fits the available arc.
 capacity=math.radians(abs(end-start))*350
 if width_em is None: width_em=" + ".join(f"textLength({param}) * 1.06" for param in params)+" + 0.3"
 cond=S(parent,'Condition');exprs=S(cond,'Expressions')
 sizes=[43,34,26,18,12,8,4,1]
 for size in sizes[:-1]:
  key=f'fit_{scope}_{size}'
  e=S(exprs,'Expression',name=key);e.text=f'({width_em}) * {size} <= {capacity:.3f}'
  if size!=sizes[0]: e.text+=f' && ({width_em}) * {sizes[sizes.index(size)-1]} > {capacity:.3f}'
 for size in sizes:
  dest=S(cond,'Compare',expression=f'fit_{scope}_{size}') if size!=1 else S(cond,'Default')
  part=S(dest,'PartText',x='0',y='0',width='920',height='920')
  circular=S(part,'TextCircular',centerX='460',centerY='452',width='700',height='700',startAngle=str(start),endAngle=str(end),direction='CLOCKWISE' if clockwise else 'COUNTER_CLOCKWISE',align='CENTER',ellipsis='FALSE')
  font=S(circular,'Font',family='oswald',size=str(size),weight='BOLD',color=fg)
  upper=S(font,'Upper');template=S(upper,'Template');template.text=fmt
  for param in params: S(template,'Parameter',expression=param)

def clock_images(parent,theme,scope,alpha='255'):
 # Select immutable artwork directly from live system time. This keeps word sprites
 # pixel-identical while avoiding bitmap-font word caching in older WFF runtimes.
 for kind,count,x,y,width,height,source in [('hour',24,267,337,310,260,'HOUR_0_23'),('minute',60,610,309,162,122,'MINUTE')]:
  clock=group(parent,f'{scope}_{theme}_{kind}',x=x,y=y,width=width,height=height,alpha=alpha)
  condition=S(clock,'Condition'); expressions=S(condition,'Expressions')
  for number in range(count):
   key=f'{scope}_{theme}_{kind}_{number:02}'
   expression=S(expressions,'Expression',name=key);expression.text=f'[{source}] == {number}'
  for number in range(count):
   compare=S(condition,'Compare',expression=f'{scope}_{theme}_{kind}_{number:02}')
   image=S(compare,'PartImage',x='0',y='0',width=str(width),height=str(height))
   S(image,'Image',resource=f'{kind}_{theme}_{number:02}')

interactive=group(scene,'interactive')
ambient(interactive)
for theme,fg,g in themed(interactive):
 p=S(g,'PartImage',x='0',y='0',width='920',height='920')
 S(p,'Image',resource=f'background_{theme}')
 clock_images(g,theme,'active')
 # Device-localized weekday/date; no hard-coded calendar date.
 p=S(g,'PartText',x='599',y='237',width='170',height='52')
 t=S(p,'Text',align='CENTER'); f=S(t,'Font',family='oswald',size='43',weight='BOLD',color=fg)
 up=S(f,'Upper'); template=S(up,'Template');template.text='%s %s.%s'
 for value in ['[DAY_OF_WEEK_S]','[DAY_Z]','[MONTH_Z]']:S(template,'Parameter',expression=value)
# Each slot uses scene coordinates so captions and data have a shared, stable transform.
for slot_id,label,x,y,width,height,angle in [(1,'heart',498,91,92,65,15),(2,'weather',140,165,160,180,0),(3,'floors',200,660,86,70,47),(4,'battery',470,747,133,62,-6),(5,'steps',690,539,171,62,-62)]:
 slot=S(scene,'ComplicationSlot',slotId=str(slot_id),displayName=label,x='0',y='0',width='920',height='920',supportedTypes='SHORT_TEXT RANGED_VALUE LONG_TEXT EMPTY',isCustomizable='TRUE')
 ambient(slot)
 provider={'battery':'WATCH_BATTERY','steps':'STEP_COUNT'}.get(label,'EMPTY')
 S(slot,'DefaultProviderPolicy',defaultSystemProvider=provider,defaultSystemProviderType='SHORT_TEXT' if provider!='EMPTY' else 'EMPTY')
 start,end=SECTORS[label]
 S(slot,'BoundingArc',centerX='460',centerY='452',width='786',height='786',thickness='90',startAngle=str(start+4),endAngle=str(end-4),direction='CLOCKWISE',isRoundEdge='FALSE')
 for ctype in ['SHORT_TEXT','RANGED_VALUE','LONG_TEXT','EMPTY']:
  comp=S(slot,'Complication',type=ctype)
  cg=group(comp,f'{label}_{ctype}')
  for theme,fg,g in themed(cg):
   scope=f'{label}_{ctype}_{theme}'
   if ctype=='EMPTY':
    radial_text(g,label,fg,'%s',('"—"',),scope)
   else:
    has_text='[COMPLICATION.TEXT] != null && textLength([COMPLICATION.TEXT]) > 0'
    has_title='[COMPLICATION.TITLE] != null && textLength([COMPLICATION.TITLE]) > 0'
    fallback='([COMPLICATION.RANGED_VALUE_VALUE] != null ? numberFormat("0.##", [COMPLICATION.RANGED_VALUE_VALUE]) : "—")' if ctype=='RANGED_VALUE' else '"—"'
    value=f'(({has_text}) ? [COMPLICATION.TEXT] : {fallback})'
    title=f'(({has_title}) ? [COMPLICATION.TITLE] : "")'
    if label=='weather':
     source='[COMPLICATION.TITLE]';length=f'textLength({source})'
     temperature=f'{source} != null && {length} >= 2 && (subText({source}, {length}-1, {length}) == "°" || subText({source}, {length}-2, {length}) == "°C" || subText({source}, {length}-2, {length}) == "°F")'
     value=f'(({temperature}) ? {source} : {value})'
     title=f'(({temperature}) ? "ПОГОДА" : {title})'
    # Resolve standard provider labels before fitting. Values remain independent
    # template parameters: WFF v1 does not support '+' string concatenation.
    metric=S(g,'Condition'); expressions=S(metric,'Expressions')
    catalog=json.loads((ROOT/'design/metric-captions.json').read_text())
    for index,item in enumerate(catalog):
     e=S(expressions,'Expression',name=f'metric_{scope}_{index}')
     e.text=' || '.join('[COMPLICATION.TITLE] == '+json.dumps(alias,ensure_ascii=False) for alias in item['aliases'])
     if label=='weather' and item['title']=='ПОГОДА': e.text+=f' || ({temperature})'
    for index,item in enumerate(catalog):
     dest=S(metric,'Compare',expression=f'metric_{scope}_{index}')
     if label=='weather' and item['title']=='ПОГОДА':
      radial_text(dest,label,fg,'%s',(value,),scope+f'_metric_{index}')
     else:
      prefix=json.dumps(item['title'],ensure_ascii=False)
      radial_text(dest,label,fg,'%s %s',(prefix,value),scope+f'_metric_{index}',f'{item["prefix_em"]} + textLength({value}) * 1.06')
    dest=S(metric,'Default')
    radial_text(dest,label,fg,'%s %s',(title,value),scope+'_unknown')
    if label=='weather':
     condition=S(g,'Condition');ex=S(condition,'Expressions')
     icon_expression=f'icon_{label}_{ctype}_{theme}'
     e=S(ex,'Expression',name=icon_expression);e.text='[COMPLICATION.MONOCHROMATIC_IMAGE] != null'
     compare=S(condition,'Compare',expression=icon_expression)
     pi=S(compare,'PartImage',x='90',y='357',width='60',height='60',angle='-80',tintColor=fg)
     S(pi,'Image',resource='[COMPLICATION.MONOCHROMATIC_IMAGE]')

# AMOLED ambient: no light background and no active complication rendering.
aod=group(scene,'ambient',alpha='0');ambient(aod,'255')
clock_images(aod,'dark','ambient',alpha='100')
text(aod,599,237,170,52,43,'#777777','%s.%s',('[DAY_Z]','[MONTH_Z]'))
indent(w)
ElementTree(w).write(ROOT/'watchface/src/main/res/raw/watchface.xml',encoding='utf-8',xml_declaration=True)
