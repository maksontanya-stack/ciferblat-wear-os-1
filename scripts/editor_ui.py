"""Navigate actual native editor via accessibility text; save evidence of each step."""
import re,subprocess,time,xml.etree.ElementTree as ET
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
 args=['shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command',action]
 if text: args+=['--es','text',text]
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
from PIL import Image
for attempt in range(8):
 state('active-light',ui=False)
 img=Image.open(p/'active-light.png').convert('RGB')
 if min(img.getpixel((img.width//2,round(img.height*.72))))>=120: break
 time.sleep(2)
else: raise SystemExit('Selecting Light in the editor did not persist on the actual watchface')
# Samsung-style payload can put temperature in TITLE and location in TEXT.
adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','weather_swapped','--ez','enabled','true');time.sleep(3)
for attempt in range(15):
 if 'ТЕСТ ГОРОД' in adb('logcat','-d').decode(errors='replace'): break
 time.sleep(2)
else: raise SystemExit('Weather swapped payload was not delivered to the runtime')
time.sleep(2)
state('active-light-weather-swapped',ui=False)
from PIL import ImageChops
weather=Image.open(p/'active-light-weather-swapped.png').convert('RGB')
box=(round(img.width*.18),round(img.height*.17),round(img.width*.30),round(img.height*.30))
if sum(max(v)>30 for v in ImageChops.difference(img.crop(box),weather.crop(box)).getdata())>20:
 raise SystemExit('Weather swapped TITLE/TEXT payload changed temperature into the city name')
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
adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','long_title','--ez','enabled','false');time.sleep(3)
adb('shell','am','broadcast','-n','ru.meta.wearos.classic1.fixtures/.EditorReceiver','--es','command','alternate','--ez','enabled','false');time.sleep(3)
# Reopen native editor and capture real provider chooser (no simulated UI).
adb('shell','settings','put','secure','accessibility_enabled','1');time.sleep(2)
adb('shell','input','swipe','227','227','227','227','1500');time.sleep(2)
adb('shell','input','tap','227','380');time.sleep(2)
tree=state('editor-reopened')
if any('Swipe to edit Complications' in n.get('content-desc','') for n in tree.iter('node')):
 command('next')
tree=state('editor-five-fields')
if sum(n.get('clickable')=='true' for n in tree.iter('node'))<5:
 raise SystemExit('The native editor did not expose all five fields')
adb('shell','input','tap','108','125');time.sleep(3)
state('provider-chooser')
