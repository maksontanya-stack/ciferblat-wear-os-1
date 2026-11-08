"""Navigate actual native editor via accessibility text; save evidence of each step."""
import re,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
p=Path('smoke-output')
def adb(*args):return subprocess.check_output(['adb',*args])
def state(name):
 adb('shell','uiautomator','dump','/sdcard/window.xml')
 data=adb('shell','cat','/sdcard/window.xml');(p/f'{name}.xml').write_bytes(data)
 (p/f'{name}.png').write_bytes(adb('exec-out','screencap','-p'))
 return ET.fromstring(data)
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
adb('shell','input','swipe','360','227','90','227','400');time.sleep(2)
tree=state('editor-five-fields')
if sum(n.get('clickable')=='true' for n in tree.iter('node'))<5:
 raise SystemExit('The native editor did not expose all five fields')
adb('shell','input','swipe','90','227','360','227','400');time.sleep(2)
tree=state('editor-options')
if not click(tree,['Тёмная','Тема','Dark','Theme']): raise SystemExit('Native theme control was not found')
tree=state('editor-theme-options')
if not click(tree,['Светлая','Light']): raise SystemExit('Native light theme option was not found')
state('editor-light-selected')
for _ in range(3):adb('shell','input','keyevent','KEYCODE_BACK');time.sleep(1)
adb('shell','input','keyevent','KEYCODE_HOME');time.sleep(2)
state('active-light')
from PIL import Image
img=Image.open(p/'active-light.png').convert('RGB')
if min(img.getpixel((img.width//2,round(img.height*.72))))<120:
 raise SystemExit('Selecting Light in the editor did not change the actual watchface background')
# Reopen native editor and capture real provider chooser (no simulated UI).
adb('shell','input','swipe','227','227','227','227','1500');time.sleep(2)
adb('shell','input','tap','227','380');time.sleep(2)
tree=state('editor-reopened')
if any('Swipe to edit Complications' in n.get('content-desc','') for n in tree.iter('node')):
 adb('shell','input','swipe','360','227','90','227','400');time.sleep(2)
state('editor-fields-light')
adb('shell','input','tap','108','125');time.sleep(3)
state('provider-chooser')
