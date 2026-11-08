"""Make small, transparent background patches for replacing legacy raster captions."""
from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[1]
out=root/'watchface/src/main/res/drawable-nodpi'
sectors={'heart':(340,370),'floors':(226,258),'battery':(177,205.5),'steps':(124,145.5)}
layout={}
for label,(start,end) in sectors.items():
 for theme in ['dark','light']:
  fill=root/'design/texture-field.png' if theme=='light' else Path('/tmp/caption-blank.png')
  if theme=='dark': subprocess.run(['magick','-size','920x920','xc:black','-fx','max(5,23-0.018*i-0.010*j)/255',str(fill)],check=True)
  expr=f'caprad=hypot(i-460,j-452); captheta=mod(atan2(i-460,452-j)*180/pi+360,360); caprad>315 && caprad<400 && ((captheta>={start} && captheta<={min(end,360)})'+(f' || captheta<={end-360}' if end>360 else '')+') ? 1 : 0'
  target=out/f'caption_{label}_{theme}.png'
  subprocess.run(['magick',str(fill),'-alpha','on','-channel','A','-fx',expr,'+channel','-trim',str(target)],check=True)
  desc=subprocess.check_output(['magick','identify','-format','%w %h %X %Y',str(target)],text=True).split()
  layout[label]=dict(zip(['width','height','x','y'],map(int,desc)))
  subprocess.run(['magick',str(target),'+repage','-strip',str(target)],check=True)
(root/'design/caption-layout.json').write_text(json.dumps(layout,indent=2)+'\n')
