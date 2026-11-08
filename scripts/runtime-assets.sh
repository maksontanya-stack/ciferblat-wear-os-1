#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
r=watchface/src/main/res/drawable-nodpi
# Geometry is still the original 920x920 grid; no independent scaling of the face.
# Clear dynamic values, preserving static lettering and separators.
magick -size 920x920 xc:black -fill white -draw 'rectangle 267,337 580,600 rectangle 610,309 772,431 rectangle 599,238 769,289 polygon 520,95 586,109 572,157 510,140 polygon 476,765 592,747 610,805 478,815 polygon 716,614 785,492 839,518 767,644 polygon 215,684 250,659 283,705 235,734 polygon 174,237 250,161 289,201 213,278 rectangle 127,263 203,337 circle 231,711 251,711 circle 737,634 749,634' design/dynamic-mask.png
inkscape design/continuous-arcs.svg --export-filename=design/arc-white.png >/dev/null 2>&1
for theme in dark light; do
 if [ "$theme" = dark ]; then
   magick -size 920x920 xc:black -fx 'max(5,23-0.018*i-0.010*j)/255' design/runtime-fill.png
 else
   cp design/texture-field.png design/runtime-fill.png
 fi
 magick design/runtime-fill.png design/dynamic-mask.png -alpha off -compose CopyOpacity -composite design/runtime-overlay.png
 magick "design/$theme-master.png" design/runtime-overlay.png -compose Over -composite "$r/background_$theme.png"
 # Numeric masks must never cut through the arc layer.
 magick "$r/background_$theme.png" design/runtime-fill.png -fx 'abs(hypot(i-460,j-452)-300)<9 ? v : u' "$r/background_$theme.png"
 arc_ink='#ddddda'; [ "$theme" = light ] && arc_ink='#222a31'
 magick design/arc-white.png -channel RGB -fill "$arc_ink" -colorize 100 +channel design/arc-overlay.png
 magick "$r/background_$theme.png" design/arc-overlay.png -compose Over -composite "$r/background_$theme.png"
 accent='#ff001b'; [ "$theme" = light ] && accent='#9d5e61'
done
python3 scripts/correct_static_labels.py
python3 scripts/clear_radial_labels.py
python3 scripts/redraw_tick_rings.py
# Draw after clearing the radial captions, which overlap the right end of this line.
for theme in dark light; do
 accent='#ff001b'; [ "$theme" = light ] && accent='#9d5e61'
 magick "$r/background_$theme.png" -stroke "$accent" -strokewidth 5 -draw 'line 599,298 769,298' "$r/background_$theme.png"
done
# Exact original hour and minute 10; opaque backing intentionally matches its theme.
for theme in dark light; do
 magick "design/$theme-master.png" -crop 310x260+267+337 +repage "$r/hour_${theme}_10.png"
 magick "design/$theme-master.png" -crop 162x122+610+309 +repage "$r/minute_${theme}_10.png"
done
# Bitmap words keep a single scale and a consistent diagonal mask for changing time.
font=watchface/src/main/res/font/oswald.ttf
for theme in dark light; do
 fg='#ddddda'; [ "$theme" = light ] && fg='#222a31'
 for number in {0..59}; do
  printf -v word '%02d' "$number"
  if [ "$word" != 10 ]; then
   magick -size 162x122 xc:none -font "$font" -pointsize 142 -fill "$fg" -gravity center -annotate +0-3 "$word" "$r/minute_${theme}_$word.png"
  fi
  magick "$r/minute_${theme}_$word.png" -resize 81x61 "$r/minute_${theme}_$word.png"
 done
 magick "$r/background_$theme.png" -resize 450x450 "$r/background_$theme.png"
done
cp design/dark-450.png "$r/preview.png"
rm -f design/arc-white.png design/arc-overlay.png design/runtime-fill.png design/runtime-overlay.png design/stripe-pattern.png design/hour-working.png "$r"/digit_*.png "$r"/striped_*.png

magick mogrify -strip "$r"/*.png

python3 scripts/generate_hour_sprites.py
python3 scripts/generate_clock_characters.py
