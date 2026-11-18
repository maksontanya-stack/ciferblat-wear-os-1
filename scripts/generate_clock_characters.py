"""Complete digit fallback for WFF bitmap clocks while preserving exact two-digit word overrides."""
from pathlib import Path
import subprocess
p=Path(__file__).resolve().parents[1]/'watchface/src/main/res/drawable-nodpi'
for theme in ['dark','light']:
 for kind,width,height,offset in [('hour',77,150,78),('minute',40,61,41)]:
  for digit in range(10):
   source=p/f'{kind}_{theme}_{digit:02}.png'
   x=0 if digit==0 else offset
   subprocess.run(['magick',str(source),'-crop',f'{width}x{height}+{x}+0','+repage','-strip',str(p/f'fallback_{kind}_{theme}_{digit}.png')],check=True)
