"""Keep the original hour scale/origin, with transparent space below the glyphs."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1];out=root/'watchface/src/main/res/drawable-nodpi'
def run(*args):subprocess.run(['magick',*map(str,args)],check=True)
with tempfile.TemporaryDirectory() as temporary:
 working=Path(temporary)/'hour.png'
 for theme,ink in [('dark','#ddddda'),('light','#222a31')]:
  for hour in range(24):
   target=out/f'hour_{theme}_{hour:02}.png'
   if hour==10:
    run(root/f'design/{theme}-master.png','-crop','310x260+267+337','+repage','-background','none','-gravity','north','-extent','310x300','-resize','155x150','-strip',target)
   else:
    # Growing by 40px moves the center by 20px. Compensate the annotation
    # offset so the glyph position and 310px type size remain unchanged.
    run('-size','310x300','xc:none','-font',root/'watchface/src/main/res/font/oswald.ttf','-pointsize','310','-fill',ink,'-gravity','center','-annotate','+0-25',f'{hour:02}',working)
    run(working,'-alpha','on','-channel','A','-fx','(j>0.8*i-62 && mod(i-j+1008,14)<4) ? 0 : u.a','+channel','-resize','155x150','-strip',target)
