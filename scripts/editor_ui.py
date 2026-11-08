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
  if any(label.casefold() in val.casefold() for label in labels):
   coords=list(map(int,re.findall(r'\d+',node.get('bounds',''))))
   if len(coords)==4:
    adb('shell','input','tap',str((coords[0]+coords[2])//2),str((coords[1]+coords[3])//2));time.sleep(2);return True
 return False
# Editor is open on complication page after the shell harness taps Customize.
tree=state('editor-five-fields')
if sum(n.get('clickable')=='true' and ('complication' in n.get('content-desc','').lower() or n.get('content-desc','').strip()) for n in tree.iter('node'))<5:
 print('Inspect editor XML for all five field outlines')
adb('shell','input','swipe','360','227','90','227','400');time.sleep(2)
tree=state('editor-options')
click(tree,['Тема','Theme'])
tree=state('editor-theme-options')
if not click(tree,['Светлая','Light']): raise SystemExit('Native light theme option was not found')
state('editor-light-selected')
for _ in range(3):adb('shell','input','keyevent','KEYCODE_BACK');time.sleep(1)
adb('shell','input','keyevent','KEYCODE_HOME');time.sleep(2)
state('active-light')
# Reopen native editor and capture real provider chooser (no simulated UI).
adb('shell','input','swipe','227','227','227','227','1500');time.sleep(2)
adb('shell','input','tap','227','380');time.sleep(2)
state('editor-reopened')
adb('shell','input','tap','108','125');time.sleep(3)
state('provider-chooser')
