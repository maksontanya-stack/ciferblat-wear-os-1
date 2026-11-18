"""Package an existing signed APK for phone installation; never rebuild or re-sign it."""
from pathlib import Path
import argparse,hashlib,html,re,shutil,zipfile
from reportlab.lib.enums import TA_LEFT
GUIDE_PAGE=(420,850)  # Narrow portrait pages readable at phone width.
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--apk',type=Path,required=True)
p.add_argument('--version',required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
apk_name=f'wearos1-{a.version}.apk'
shutil.copy2(a.apk,a.output/apk_name)
assert (a.output/apk_name).read_bytes()==a.apk.read_bytes()
source=(ROOT/'docs/INSTALL-GEMINIMAN-RU.md').read_text()
doc_version=re.search(r'Сборка ([\w.-]+)\.',source).group(1)
source=source.replace(doc_version,a.version)
(a.output/'INSTALL-GEMINIMAN-RU.txt').write_text(source,encoding='utf-8')
font_root=Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('Guide',str(font_root/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('GuideBold',str(font_root/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('Guide',normal='Guide',bold='GuideBold',italic='Guide',boldItalic='GuideBold')
styles={
 'body':ParagraphStyle('body',fontName='Guide',fontSize=11,leading=15,spaceAfter=7,textColor=colors.HexColor('#202b38')),
 'h1':ParagraphStyle('h1',fontName='GuideBold',fontSize=17,leading=21,spaceAfter=12,textColor=colors.HexColor('#125cb1')),
 'h2':ParagraphStyle('h2',fontName='GuideBold',fontSize=11.5,leading=16,spaceBefore=9,spaceAfter=6,textColor=colors.HexColor('#125cb1'),keepWithNext=True),
}
def markup(t):
 t=html.escape(t,quote=False)
 t=re.sub(r'\[([^\]]+)\]\((https://[^\s)]+)\)',r'<link color="#125cb1" href="\2">\1</link>',t)
 return re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',t)
story=[]
for block in source.strip().split('\n\n'):
 if block=='<!-- PAGEBREAK -->':story.append(PageBreak());continue
 if block.startswith('# '):
  lines=block.splitlines()
  story.append(Paragraph(markup(lines[0][2:]),styles['h1']))
  if len(lines)>1:story.append(Paragraph(markup(' '.join(lines[1:])),styles['body']))
 elif block.startswith('## '):
  lines=block.splitlines()
  story.append(Paragraph(markup(lines[0][3:]),styles['h2']))
  if len(lines)>1:story.append(Paragraph(markup(' '.join(lines[1:])),styles['body']))
 else:story.append(Paragraph(markup(' '.join(block.splitlines())),styles['body']))
def footer(canvas,doc):
 canvas.setFont('Guide',8)
 canvas.setFillColor(colors.HexColor('#607080'))
 canvas.drawString(32,18,f'Wear OS 1 · {a.version}')
 canvas.drawRightString(GUIDE_PAGE[0]-32,18,str(doc.page))
pdf=a.output/'INSTALL-GEMINIMAN-RU.pdf'
doc=SimpleDocTemplate(str(pdf),pagesize=GUIDE_PAGE,leftMargin=32,rightMargin=32,topMargin=30,bottomMargin=34,title='Установка циферблата через GeminiMan',author='Wear OS 1')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
files=[apk_name,'INSTALL-GEMINIMAN-RU.pdf','INSTALL-GEMINIMAN-RU.txt']
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=a.output/'SHA256SUMS-phone.txt'
checks.write_text(''.join(digest(a.output/n)+'  '+n+'\n' for n in files),encoding='utf-8')
archive=a.output/f'wearos1-geminiman-{a.version}.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for n in [*files,checks.name]:z.write(a.output/n,n)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert z.read(apk_name)==a.apk.read_bytes()
with checks.open('a') as f:f.write(digest(archive)+'  '+archive.name+'\n')
print(f'Packaged unchanged signed APK, PDF and phone instructions: {archive}')
