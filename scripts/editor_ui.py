"""Navigate actual native editor via accessibility text; save evidence of each step."""
import re,subprocess,time,shlex,os,xml.etree.ElementTree as ET
from pathlib import Path
p=Path('smoke-output')
def adb(*args):return subprocess.check_output(['adb',*args])
def state(name,ui=True):
 if ui:
  command('dump')
  data=adb('shell','run-as','ru.meta.wearos.classic1.fixtures','cat','files/window.xml')
 else: data=b'<hierarchy capture="screenshot-only" />'
 (p/f'{name}.xml').write_bytes(data)
 (p/f'{name}.png').write_bytes(adb('exec-out','screencap','-p'))
 return ET.fromstring(data)
def command(action,text=''):
 # Count actual input as user activity, then move exactly one native page.
 # Short drag gestures can stop short of the next page in a slow emulator.
 if action in ('next','previous'):
  adb('shell','input','tap','227','227')
 args=['shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command',action]
 if text: args+=['--es','text',shlex.quote(text)]
 adb(*args)
 time.sleep(2)
def click(tree,labels):
 for node in tree.iter('node'):
  val=(node.get('text','')+' '+node.get('content-desc','')).strip()
  if any(node.get('text','').casefold()==label.casefold() or (node.get('clickable')=='true' and label.casefold() in node.get('content-desc','').casefold()) for label in labels):
   coords=list(map(int,re.findall(r'\d+',node.get('bounds',''))))
   if len(coords)==4:
    adb('shell','input','tap',str((coords[0]+coords[2])//2),str((coords[1]+coords[3])//2));time.sleep(2);return True
 return False
# Editor is open on complication page after the shell harness taps Customize.
tree=state('editor-initial')
command('tap','Тёмная')
tree=state('editor-theme-options')
command('tap','Светлая')
state('editor-light-selected')
# Finish the editor Activity so the style transaction is committed, then show Home.
adb('shell','input','keyevent','KEYCODE_BACK');time.sleep(3)
tree=state('after-editor-confirm')
if any('Customize Watch Faces' in n.get('content-desc','') for n in tree.iter('node')):
 adb('shell','input','keyevent','KEYCODE_BACK');time.sleep(2)
# BACK already returns to the face. HOME is a launcher shortcut on Wear OS,
# not an Android-phone-style return-to-face operation.
from PIL import Image, ImageChops
for attempt in range(8):
 state('active-light',ui=False)
 img=Image.open(p/'active-light.png').convert('RGB')
 if min(img.getpixel((img.width//2,round(img.height*.72))))>=120: break
 time.sleep(2)
else: raise SystemExit('Selecting Light in the editor did not persist on the actual watchface')
roi=(round(img.width*.37),round(img.height*.09),round(img.width*.54),round(img.height*.18))
if os.environ.get('EDITOR_ONLY') != 'true':
 # Samsung-style payload can put temperature in TITLE and location in TEXT.
 adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','weather_swapped','--ez','enabled','true');time.sleep(3)
 for attempt in range(15):
  if 'ТЕСТ ГОРОД' in adb('logcat','-d').decode(errors='replace'): break
  time.sleep(2)
 else: raise SystemExit('Weather swapped payload was not delivered to the runtime')
 time.sleep(2)
 state('active-light-weather-swapped',ui=False)
 weather=Image.open(p/'active-light-weather-swapped.png').convert('RGB')
 import math
 changed=0
 for py in range(img.height):
  for px in range(img.width):
   dx=px*920/img.width-460;dy=py*920/img.height-452
   radius=math.hypot(dx,dy);angle=math.degrees(math.atan2(dx,-dy))%360
   if 305<radius<393 and 274<angle<326 and max(abs(a-b) for a,b in zip(img.getpixel((px,py)),weather.getpixel((px,py))))>30: changed+=1
 if changed>20:
  raise SystemExit('Weather swapped TITLE/TEXT payload changed the displayed weather sector')
 adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','weather_swapped','--ez','enabled','false');time.sleep(3)
 # Real complication update changes both its title and value in the same sector.
 adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','alternate','--ez','enabled','true');time.sleep(4)
 roi=(round(img.width*.37),round(img.height*.09),round(img.width*.54),round(img.height*.18))
 for attempt in range(15):
  state('active-light-altitude',ui=False)
  alt=Image.open(p/'active-light-altitude.png').convert('RGB')
  if sum(max(v)>25 for v in ImageChops.difference(img.crop(roi),alt.crop(roi)).getdata())>=30: break
  time.sleep(2)
 else: raise SystemExit('Changing the source title did not update the sector caption within 30 seconds')
 # A long provider title must remain inside its radial sector.
 adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','long_title','--ez','enabled','true')
 for attempt in range(15):
  if 'МАКСИМАЛЬНАЯ ВЫСОТА' in adb('logcat','-d').decode(errors='replace'): break
  time.sleep(2)
 else: raise SystemExit('Long-title fixture was not delivered')
 time.sleep(3)
 state('active-light-long-title',ui=False)
 shortened=Image.open(p/'active-light-long-title.png').convert('RGB')
 # Both the ordinary and verbose height titles must resolve to the same caption.
 changed=0
 for py in range(img.height):
  for px in range(img.width):
   dx=px*920/img.width-460;dy=py*920/img.height-452
   radius=math.hypot(dx,dy);angle=math.degrees(math.atan2(dx,-dy))%360
   if 305<radius<393 and (angle>334 or angle<26) and max(abs(a-b) for a,b in zip(alt.getpixel((px,py)),shortened.getpixel((px,py))))>30: changed+=1
 if changed>20: raise SystemExit('Verbose height title was not shortened to the same ВЫСОТА caption')

 # An unrecognized long label exercises actual automatic font fitting.
 adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','unknown_long_title','--ez','enabled','true')
 for attempt in range(15):
  if 'ПРОИЗВОЛЬНЫЙ ПОКАЗАТЕЛЬ' in adb('logcat','-d').decode(errors='replace'): break
  time.sleep(2)
 else: raise SystemExit('Unknown long-title fixture was not delivered')
 time.sleep(3)
 state('active-light-fitted-title',ui=False)
 fitted=Image.open(p/'active-light-fitted-title.png').convert('RGB')
 inside=outside=0
 for py in range(img.height):
  for px in range(img.width):
   dx=px*920/img.width-460;dy=py*920/img.height-452
   radius=math.hypot(dx,dy);angle=math.degrees(math.atan2(dx,-dy))%360
   if 599<=px*920/img.width<=772 and 237<=py*920/img.height<=431: continue # Advancing date/minute fields.
   if 305<radius<393 and max(abs(a-b) for a,b in zip(shortened.getpixel((px,py)),fitted.getpixel((px,py))))>30:
    if angle>334 or angle<26: inside+=1
    else: outside+=1
 ink=0
 for py in range(img.height):
  for px in range(img.width):
   dx=px*920/img.width-460;dy=py*920/img.height-452
   radius=math.hypot(dx,dy);angle=math.degrees(math.atan2(dx,-dy))%360
   if 310<radius<375 and (angle>334 or angle<26) and max(fitted.getpixel((px,py)))<140: ink+=1
 if ink<20: raise SystemExit(f'Fitted long title is absent ({ink} dark pixels)')
 if inside<20: raise SystemExit('Long label did not render after automatic fitting')
 if outside>20: raise SystemExit('Fitted label changed pixels outside its radial sector')
 adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','unknown_long_title','--ez','enabled','false');time.sleep(3)
 adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','long_title','--ez','enabled','false');time.sleep(3)
 adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','alternate','--ez','enabled','false');time.sleep(3)
# A titleless source can be relabelled through a real native setting.
# Verify the CONFIGURATION source changes rendered text, not just editor labels.
def open_editor():
 adb('shell','input','swipe','227','227','227','227','1500');time.sleep(2)
 adb('shell','input','tap','227','380');time.sleep(2)
def choose_top_caption(current,selected,tag):
 open_editor()
 for page in range(8):
  tree=state(tag+'-page-'+str(page))
  visible=[]
  for n in tree.iter('node'):
   coords=list(map(int,re.findall(r'-?\d+',n.get('bounds',''))))
   if n.get('text')==current and len(coords)==4 and 0<=coords[0]<coords[2]<=454 and 0<=coords[1]<coords[3]<=454:visible.append(n)
  if visible:break
  command('next')
 else:raise SystemExit('Native caption setting missing: '+current)
 command('tap',current)
 tree=state(tag+'-options')
 command('tap',selected)
 state(tag+'-selected')
 adb('shell','input','keyevent','KEYCODE_BACK');time.sleep(4)
# The fixture has its ordinary title here; an explicit label must take precedence.
choose_top_caption('Авто (без названия: Пульс)','ВЫСОТА','caption-height')
for attempt in range(10):
 state('active-light-forced-caption',ui=False)
 forced=Image.open(p/'active-light-forced-caption.png').convert('RGB')
 if sum(max(v)>25 for v in ImageChops.difference(img.crop(roi),forced.crop(roi)).getdata())>=30:break
 time.sleep(2)
else:raise SystemExit('Changing the caption setting did not change the actual radial text')
choose_top_caption('ВЫСОТА','Авто (без названия: Пульс)','caption-auto')
for attempt in range(10):
 state('active-light-auto-caption',ui=False)
 restored=Image.open(p/'active-light-auto-caption.png').convert('RGB')
 if sum(max(v)>25 for v in ImageChops.difference(img.crop(roi),restored.crop(roi)).getdata())<20:break
 time.sleep(2)
else:raise SystemExit('Restoring Auto did not restore the provider caption')
# Reopen native editor and capture real provider chooser (no simulated UI).
adb('shell','settings','put','secure','accessibility_enabled','1');time.sleep(2)
adb('shell','input','swipe','227','227','227','227','1500');time.sleep(2)
adb('shell','input','tap','227','380');time.sleep(2)
tree=state('editor-reopened')
# Five caption settings precede the complications page. Navigate the actual
# pager until all five source controls are visible, rather than assuming two pages.
for page in range(9):
 tree=state('editor-page-'+str(page))
 sources=[]
 for n in tree.iter('node'):
  coords=list(map(int,re.findall(r'-?\d+',n.get('bounds',''))))
  if n.get('clickable')=='true' and n.get('content-desc','').startswith('TEST ') and len(coords)==4 and 0<=coords[0]<coords[2]<=454 and 0<=coords[1]<coords[3]<=454:sources.append(n)
 if len(sources)>=5:break
 command('next')
else:raise SystemExit('Native editor did not expose five complication fields')
state('editor-five-fields')
adb('shell','input','tap','108','125');time.sleep(3)
state('provider-chooser')
