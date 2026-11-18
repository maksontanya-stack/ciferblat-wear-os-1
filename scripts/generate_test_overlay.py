"""Emulator-only defaults use genuine Android test complication services, never production data."""
from pathlib import Path
from xml.etree import ElementTree as ET
root=Path(__file__).resolve().parents[1]
w=ET.parse(root/'watchface/src/main/res/raw/watchface.xml')
for slot in w.iter('ComplicationSlot'):
 name=slot.attrib['displayName'].title()
 policy=slot.find('DefaultProviderPolicy')
 policy.set('primaryProvider',f'ru.meta.wearos.classic1.fixtures/ru.meta.wearos.classic1.fixtures.FixtureService${name}')
 policy.set('primaryProviderType','RANGED_VALUE' if name=='Heart' else 'SHORT_TEXT')
folder=root/'watchface/src/debug/res/raw';folder.mkdir(parents=True,exist_ok=True)
w.write(folder/'watchface.xml',encoding='utf-8',xml_declaration=True)
