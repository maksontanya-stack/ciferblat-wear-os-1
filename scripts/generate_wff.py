"""Generate WFF v4 markup in the unchanged 920-unit reference coordinate grid."""
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
CATALOG=json.loads((ROOT/'design/metric-captions.json').read_text())
METRICS={item['title']:index for index,item in enumerate(CATALOG,1)}
DEFAULT_CAPTIONS={'heart':'ПУЛЬС','weather':'ПОГОДА','floors':'ЭТАЖИ','battery':'ЗАРЯД','steps':'ШАГИ'}
# Preserve existing theme/slot identifiers, adding an explicit escape hatch for
# providers that omit TITLE. No static text is painted into the artwork.
for label in DEFAULT_CAPTIONS:
 config=S(u,'ListConfiguration',id='caption_'+label,displayName='caption_'+label,defaultValue='0')
 S(config,'ListOption',id='0',displayName='caption_auto_'+label)
 for item in CATALOG:
  index=METRICS[item['title']]
  S(config,'ListOption',id=str(index),displayName='metric_'+str(index))
 S(config,'ListOption',id='99',displayName='caption_none')
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
FIELD_COLOR='([CONFIGURATION.theme] == "1" ? #222a31 : #ddddda)'

SECTORS={'heart':(330,390),'weather':(270,330),'floors':(210,270),'battery':(150,210),'steps':(90,150)}

def radial_text(parent,label,fg,fmt,params,scope,width_em=None,known=False):
 import math
 start,end=SECTORS[label]; start+=4;end-=4
 if label=='weather': start+=16
 clockwise=label in ('heart','weather')
 if not clockwise: start,end=end,start
 capacity=math.radians(abs(end-start))*350
 if width_em is None: width_em=" + ".join(f"textLength({param}) * 1.06" for param in params)+" + 0.3"
 sizes=[43,34,24,12,4,0.25] if known else [43,34,26,18,12,8,6,3,1,0.25]
 # Fit width is evaluated once per update, rather than being copied into
 # eighteen threshold expressions. This empty group has no drawing children.
 cache=group(parent,'fit_cache_'+scope,width=1,height=1)
 S(cache,'Transform',target='width',value=f'({width_em}) + 0.00001')
 S(cache,'Reference',name='fit_width_'+scope,source='width',defaultValue='4')
 width_em=f'[REFERENCE.fit_width_{scope}]'
 cond=S(parent,'Condition');exprs=S(cond,'Expressions')
 for index,size in enumerate(sizes[:-1]):
  e=S(exprs,'Expression',name=f'fit_{scope}_{index}');e.text=f'({width_em}) * {size} <= {capacity:.3f}'
  if index: e.text+=f' && ({width_em}) * {sizes[index-1]} > {capacity:.3f}'
 for index,size in enumerate(sizes):
  dest=S(cond,'Compare',expression=f'fit_{scope}_{index}') if index<len(sizes)-1 else S(cond,'Default')
  part=S(dest,'PartText',x='0',y='0',width='920',height='920')
  circular=S(part,'TextCircular',centerX='460',centerY='452',width='700',height='700',startAngle=str(start),endAngle=str(end),direction='CLOCKWISE' if clockwise else 'COUNTER_CLOCKWISE',align='CENTER')
  font=S(circular,'Font',family='oswald',size=str(size),weight='BOLD',color=fg)
  S(font,'Transform',target='color',value=FIELD_COLOR)
  upper=S(font,'Upper');template=S(upper,'Template');template.text=fmt
  for param in params: S(template,'Parameter',expression=param)


def clock_images(parent,theme,scope,alpha='255'):
 # Select immutable artwork directly from live system time. This keeps word sprites
 # pixel-identical while avoiding bitmap-font word caching in older WFF runtimes.
 for kind,count,x,y,width,height,source in [('hour',24,267,337,310,300,'HOUR_0_23'),('minute',60,610,309,162,122,'MINUTE')]:
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
 # Russian weekday regardless of device locale; WFF numbers Sunday as one.
 p=S(g,'PartText',x='599',y='237',width='170',height='52')
 t=S(p,'Text',align='CENTER'); f=S(t,'Font',family='oswald',size='43',weight='BOLD',color=fg)
 up=S(f,'Upper'); template=S(up,'Template');template.text='%s %s.%s'
 russian_weekday='"СБ"'
 for day,name in reversed(list(enumerate(['ВС','ПН','ВТ','СР','ЧТ','ПТ'],1))): russian_weekday=f'([DAY_OF_WEEK] == {day} ? "{name}" : {russian_weekday})'
 for value in [russian_weekday,'[DAY_Z]','[MONTH_Z]']:S(template,'Parameter',expression=value)
# Each slot uses scene coordinates so captions and data have a shared, stable transform.
for slot_id,label,x,y,width,height,angle in [(1,'heart',498,91,92,65,15),(2,'weather',140,165,160,180,0),(3,'floors',200,660,86,70,47),(4,'battery',470,747,133,62,-6),(5,'steps',690,539,171,62,-62)]:
 slot=S(scene,'ComplicationSlot',slotId=str(slot_id),displayName=label,x='0',y='0',width='920',height='920',supportedTypes='SHORT_TEXT RANGED_VALUE LONG_TEXT EMPTY',isCustomizable='TRUE')
 ambient(slot)
 provider={'battery':'WATCH_BATTERY','steps':'STEP_COUNT'}.get(label,'EMPTY')
 S(slot,'DefaultProviderPolicy',defaultSystemProvider=provider,defaultSystemProviderType='SHORT_TEXT' if provider!='EMPTY' else 'EMPTY')
 start,end=SECTORS[label]
 S(slot,'BoundingArc',centerX='460',centerY='452',width='752',height='752',thickness='73',startAngle=str(start+4),endAngle=str(end-4),direction='CLOCKWISE')
 for ctype in ['SHORT_TEXT','RANGED_VALUE','LONG_TEXT','EMPTY']:
  comp=S(slot,'Complication',type=ctype)
  cg=group(comp,f'{label}_{ctype}')
  # One scene graph serves both themes; WFF 4 changes the font colour directly.
  for theme,fg,g in [('shared','#ddddda',cg)]:
   scope=f'{label}_{ctype}_{theme}'
   if ctype=='EMPTY':
    caption=json.dumps(DEFAULT_CAPTIONS[label],ensure_ascii=False)
    for item in CATALOG:
     caption=f'([CONFIGURATION.caption_{label}] == "{METRICS[item["title"]]}" ? '+json.dumps(item['title'],ensure_ascii=False)+f' : {caption})'
    caption=f'([CONFIGURATION.caption_{label}] == "99" ? "" : {caption})'
    radial_text(g,label,fg,'%s %s',(caption,'"—"'),scope)
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
    # WFF 4 numeric references resolve aliases once, rather than expanding a
    # full fitting subtree for each metric. This is deliberately an empty group:
    # its alpha carries a numeric code and cannot alter any visible content.
    metric_expr='0'
    for item in reversed(CATALOG):
     matches=' || '.join('[COMPLICATION.TITLE] == '+json.dumps(alias,ensure_ascii=False) for alias in item['aliases'])
     metric_expr=f'(({matches}) ? {METRICS[item["title"]]} : {metric_expr})'
    default_id=METRICS[DEFAULT_CAPTIONS[label]]
    metric_expr=f'(({has_title}) ? {metric_expr} : {default_id})'
    if label=='weather': metric_expr=f'(({temperature}) ? {METRICS["ПОГОДА"]} : {metric_expr})'
    # List selections are string-valued sources. A forced caption is useful for
    # e.g. altitude from a provider that sends "182" and no title.
    override=f'[CONFIGURATION.caption_{label}]'
    for index in [*METRICS.values(),99]:
     metric_expr=f'({override} == "{index}" ? {index} : {metric_expr})'
    cache=group(g,'metric_cache_'+scope,width=1,height=1)
    S(cache,'Transform',target='alpha',value=metric_expr)
    refname='metric_'+scope
    S(cache,'Reference',name=refname,source='alpha',defaultValue=str(default_id))
    ref=f'[REFERENCE.{refname}]'
    caption=title
    prefix=f'textLength({title}) * 1.06 + 0.3'
    for item in reversed(CATALOG):
     index=METRICS[item['title']]
     caption=f'({ref} == {index} ? '+json.dumps(item['title'],ensure_ascii=False)+f' : {caption})'
     prefix=f'({ref} == {index} ? {item["prefix_em"]} : {prefix})'
    caption=f'({ref} == 99 ? "" : {caption})'
    prefix=f'({ref} == 99 ? 0 : {prefix})'
    # The weather sector retains the reference icon+temperature composition.
    if label=='weather':
     caption=f'({ref} == {METRICS["ПОГОДА"]} ? "" : {caption})'
     prefix=f'({ref} == {METRICS["ПОГОДА"]} ? 0 : {prefix})'
    radial_text(g,label,fg,'%s %s',(caption,value),scope,f'{prefix} + textLength({value}) * 1.06')
    if label=='weather':
     condition=S(g,'Condition');ex=S(condition,'Expressions')
     icon_expression=f'icon_{label}_{ctype}_{theme}'
     e=S(ex,'Expression',name=icon_expression);e.text='[COMPLICATION.MONOCHROMATIC_IMAGE] != null'
     compare=S(condition,'Compare',expression=icon_expression)
     icon_group=group(compare,'weather_icon_'+scope,x=97,y=269,width=100,height=100,angle='-67')
     pi=S(icon_group,'PartImage',x='14',y='14',width='72',height='72',tintColor=fg)
     S(pi,'Transform',target='tintColor',value=FIELD_COLOR)
     S(pi,'Image',resource='[COMPLICATION.MONOCHROMATIC_IMAGE]')

# AMOLED ambient: no light background and no active complication rendering.
aod=group(scene,'ambient',alpha='0');ambient(aod,'255')
clock_images(aod,'dark','ambient',alpha='100')
text(aod,599,237,170,52,43,'#777777','%s.%s',('[DAY_Z]','[MONTH_Z]'))
ElementTree(w).write(ROOT/'watchface/src/main/res/raw/watchface.xml',encoding='utf-8',xml_declaration=True)
