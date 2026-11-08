"""Check the fidelity and device dimensions of the committed artwork."""
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
reference = Image.open(root / 'references/29937.jpg').convert('RGB')
expected = reference.crop((139, 140, 1059, 1060))
actual = Image.open(root / 'design/dark-master.png').convert('RGB')
if actual.size != expected.size or actual.tobytes() != expected.tobytes():
    raise SystemExit('Dark master differs from the original reference crop')
for theme in ('dark', 'light'):
    with Image.open(root / f'design/{theme}-450.png') as image:
        if image.size != (450, 450) or image.mode != 'RGBA':
            raise SystemExit(f'{theme}: expected 450x450 RGBA')
        if image.getpixel((0, 0))[3] != 0:
            raise SystemExit(f'{theme}: outside of dial must be transparent')
print('PASS: original dark geometry preserved; both themes are 450x450 RGBA')
