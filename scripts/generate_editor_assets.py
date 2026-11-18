"""Generate Samsung editor thumbnails from the current runtime artwork.

The phone editor does not render ListOption names inside its round tiles.  It
expects an explicit drawable for every option, so these assets contain the
visible label as well as a current full-face preview for the two themes.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'watchface/src/main/res/drawable-nodpi'
FONT = ROOT / 'watchface/src/main/res/font/oswald.ttf'
SS = 4
SIZE = 450
CENTER = (225, 221)


def font(size):
    result = ImageFont.truetype(str(FONT), size)
    try:
        result.set_variation_by_name('Bold')
    except OSError:
        pass
    return result


def curved_text(image, value, angle, radius, max_span, size, color, clockwise=True):
    """Draw a centered, fitted circular label using the same dial geometry."""
    canvas = image.resize((SIZE * SS, SIZE * SS), Image.Resampling.LANCZOS)
    radius *= SS
    current_size = size * SS
    while current_size > 20:
        face = font(round(current_size))
        widths = [face.getlength(char) + current_size * .025 for char in value]
        if sum(widths) / radius <= math.radians(max_span):
            break
        current_size -= 2
    direction = 1 if clockwise else -1
    total = sum(widths) / radius
    cursor = math.radians(angle) - direction * total / 2
    for char, width in zip(value, widths):
        advance = width / radius
        char_angle = cursor + direction * advance / 2
        degrees = math.degrees(char_angle)
        box = max(96, round(current_size * 2.2))
        tile = Image.new('RGBA', (box, box))
        draw = ImageDraw.Draw(tile)
        draw.text((box / 2, box / 2), char, font=face, fill=color,
                  anchor='mm', stroke_width=0)
        rotation = -degrees if clockwise else -(degrees - 180)
        tile = tile.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)
        x = (CENTER[0] * SS + radius * math.sin(char_angle) - tile.width / 2)
        y = (CENTER[1] * SS - radius * math.cos(char_angle) - tile.height / 2)
        canvas.alpha_composite(tile, (round(x), round(y)))
        cursor += direction * advance
    return canvas.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def weather_icon(image, color):
    """Small tilted cloud/rain icon matching the radial weather sector."""
    tile = Image.new('RGBA', (72 * SS, 72 * SS))
    d = ImageDraw.Draw(tile)
    c = tuple(color)
    w = 3 * SS
    d.arc((8*SS, 25*SS, 40*SS, 55*SS), 120, 310, fill=c, width=w)
    d.arc((24*SS, 14*SS, 55*SS, 48*SS), 175, 350, fill=c, width=w)
    d.arc((43*SS, 27*SS, 65*SS, 50*SS), 240, 70, fill=c, width=w)
    d.line((13*SS, 48*SS, 58*SS, 48*SS), fill=c, width=w)
    for x in (23, 36, 49):
        d.line((x*SS, 55*SS, (x-6)*SS, 68*SS), fill=c, width=3*SS)
    tile = tile.rotate(67, resample=Image.Resampling.BICUBIC, expand=True)
    tile = tile.resize((48, 48), Image.Resampling.LANCZOS)
    image.alpha_composite(tile, (44, 128))


def face_preview(theme):
    fg = (221, 221, 218, 255) if theme == 'dark' else (34, 42, 49, 255)
    base = Image.open(OUT / f'background_{theme}.png').convert('RGBA')
    # Galaxy Wearable displays a round dial, not the photographed watch case.
    mask = Image.new('L', (SIZE, SIZE))
    ImageDraw.Draw(mask).ellipse((1, 1, SIZE-2, SIZE-2), fill=255)
    transparent = Image.new('RGBA', (SIZE, SIZE))
    transparent.paste(base, mask=mask)
    image = transparent

    hour = Image.open(OUT / f'hour_{theme}_10.png').convert('RGBA')
    minute = Image.open(OUT / f'minute_{theme}_10.png').convert('RGBA')
    image.alpha_composite(hour, (131, 165))
    image.alpha_composite(minute, (298, 151))

    d = ImageDraw.Draw(image)
    date_font = font(21)
    d.text((334, 128), 'СР 18.11', font=date_font, fill=fg, anchor='mm')

    image = curved_text(image, 'ПУЛЬС 72', 0, 171, 52, 21, fg, True)
    image = curved_text(image, 'КАЛОРИИ 420', 240, 171, 52, 21, fg, False)
    image = curved_text(image, 'ЗАРЯД 82%', 180, 171, 52, 21, fg, False)
    image = curved_text(image, 'ШАГИ 10 780', 120, 171, 52, 21, fg, False)
    image = curved_text(image, '+4°C', 312, 171, 28, 20, fg, True)
    weather_icon(image, fg)
    return image


def option_icon(text, filename, accent=(255, 0, 27, 255)):
    size = 320
    image = Image.new('RGBA', (size, size))
    d = ImageDraw.Draw(image)
    d.ellipse((5, 5, size-6, size-6), fill=(10, 11, 12, 255), outline=(65, 68, 72, 255), width=4)
    d.arc((44, 44, size-45, size-45), 205, 335, fill=(221, 221, 218, 255), width=5)
    d.rounded_rectangle((146, 34, 174, 76), radius=4, fill=accent)
    words = text.split('\n')
    target = 60 if len(words) == 1 else 48
    while target >= 24:
        f = font(target)
        if max(d.textbbox((0, 0), line, font=f)[2] for line in words) <= 245:
            break
        target -= 2
    y = size / 2 - (len(words)-1) * target * .48
    for line in words:
        d.text((size/2, y), line, font=f, fill=(221, 221, 218, 255), anchor='mm')
        y += target * .95
    image.save(OUT / filename)


dark = face_preview('dark')
light = face_preview('light')
dark.save(OUT / 'preview.png')
dark.save(ROOT / 'design/dark-450.png')
light.save(ROOT / 'design/light-450.png')
Image.new('RGBA', (900, 450)).save(ROOT / 'design/preview.png')
side = Image.open(ROOT / 'design/preview.png')
side.alpha_composite(dark, (0, 0)); side.alpha_composite(light, (450, 0)); side.save(ROOT / 'design/preview.png')
dark.resize((400, 400), Image.Resampling.LANCZOS).save(OUT / 'editor_theme_dark.png')
light.resize((400, 400), Image.Resampling.LANCZOS).save(OUT / 'editor_theme_light.png')

option_icon('АВТО', 'editor_caption_auto.png')
option_icon('ТОЛЬКО\nЗНАЧЕНИЕ', 'editor_caption_none.png')
labels = {
    2:'ПУЛЬС', 3:'ШАГИ', 5:'ЗАРЯД', 6:'КРОВ.\nДАВЛ.', 8:'КАЛОРИИ',
    9:'КИСЛОРОД', 10:'СОН', 11:'ВОСХОД', 12:'ЗАКАТ',
    13:'БУДИЛЬНИК', 14:'ПОГОДА', 15:'ТЕМП.', 16:'УФ', 17:'ТАЙМЕР'
}
for metric_id, label in labels.items():
    option_icon(label, f'editor_metric_{metric_id}.png')
