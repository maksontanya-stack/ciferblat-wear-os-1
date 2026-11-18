"""Create tintable masks for the static red and light face details.

The untouched background remains the default state. Masks are used only after a
user chooses a non-default colour, so the reference artwork stays pixel-stable
for the original red/light palette.
"""
from pathlib import Path
import math
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'watchface/src/main/res/drawable-nodpi'

for theme in ('dark', 'light'):
    source = Image.open(OUT / f'background_{theme}.png').convert('RGBA')
    accent = Image.new('RGBA', source.size)
    foreground = Image.new('RGBA', source.size)
    for y in range(source.height):
        for x in range(source.width):
            # Do not recolour the photographed bezel/case outside the face.
            if math.hypot(x - source.width / 2, y - source.height / 2) > source.width * .49:
                continue
            red, green, blue, alpha = source.getpixel((x, y))
            high, low = max(red, green, blue), min(red, green, blue)
            if red > 90 and red > green * 1.45 and red > blue * 1.3:
                opacity = min(255, int((red - max(green, blue)) * 1.8))
                accent.putpixel((x, y), (255, 255, 255, opacity))
            # Dark face: neutral bright markings. Light face: the dark blue-gray
            # lettering/marks. Both masks preserve anti-aliasing in alpha.
            if theme == 'dark':
                if high > 80 and high - low < 24:
                    foreground.putpixel((x, y), (255, 255, 255, min(255, int(high / 221 * 255))))
            elif high < 100 and high - low < 45:
                foreground.putpixel((x, y), (255, 255, 255, min(255, int((100 - high) / 78 * 255))))
    accent.save(OUT / f'accent_mask_{theme}.png')
    foreground.save(OUT / f'foreground_mask_{theme}.png')
