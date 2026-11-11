#!/usr/bin/env python3
"""Create a reproducible visual test report for every Wear OS Galaxy Watch profile."""
import argparse, json, math
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PROFILES = json.loads((ROOT / 'lab' / 'profiles.json').read_text(encoding='utf-8'))['profiles']

def normalized(image, size):
    """Center an arbitrary source without changing its aspect ratio."""
    canvas = Image.new('RGBA', (size, size))
    scale = min(size / image.width, size / image.height)
    scaled = image.convert('RGBA').resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    canvas.alpha_composite(scaled, ((size - scaled.width) // 2, (size - scaled.height) // 2))
    return canvas

def edge_metrics(image):
    sample = normalized(image, 498)
    pixels = sample.load(); center = 248.5; radius = 249; minimum = radius; outside = 0
    for y in range(0, 498, 2):
        for x in range(0, 498, 2):
            red, green, blue, alpha = pixels[x, y]
            luminance = .2126 * red + .7152 * green + .0722 * blue
            if alpha > 20 and luminance > 18:
                distance = math.hypot(x - center, y - center)
                minimum = min(minimum, radius - distance)
                outside += distance > radius
    return {'bright_pixels_outside_round_screen': outside, 'edge_clearance_percent': round(max(0, minimum / radius * 100), 2)}

def render(source, profile, out):
    size = profile['resolution']
    image = normalized(source, size)
    overlay = Image.new('RGBA', image.size); draw = ImageDraw.Draw(overlay)
    inset = max(2, round(size * .04)); draw.ellipse((inset, inset, size-inset, size-inset), outline=(251,191,36,230), width=max(1,size//300))
    return Image.alpha_composite(image, overlay)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, default=ROOT/'design'/'dark-450.png')
    parser.add_argument('--output', type=Path, default=ROOT/'lab'/'reports')
    args = parser.parse_args()
    source = Image.open(args.image); args.output.mkdir(parents=True, exist_ok=True)
    metrics = edge_metrics(source); report = {'tool':'Galaxy Watch Lab','created':datetime.now(timezone.utc).isoformat(),'source':str(args.image),'source_pixels':source.size,'edge_analysis':metrics,'profiles':[],'limitations':'Visual scale and circular-edge check only; validate One UI, complications, sensors and battery on physical hardware.'}
    for profile in PROFILES:
        output = args.output / f"{profile['id']}.png"; render(source, profile, output).save(output)
        report['profiles'].append({**profile, 'image':output.name, 'scale_percent':round(min(profile['resolution']/source.width, profile['resolution']/source.height)*100,2)})
    report_path = args.output/'report.json'; report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'PASS: {len(PROFILES)} profiles, {report_path}')

if __name__ == '__main__': main()
