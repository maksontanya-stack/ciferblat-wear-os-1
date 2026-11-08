#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
r=watchface/src/main/res/drawable-nodpi
# Geometry is still the original 920x920 grid; no independent scaling of the face.
# Clear dynamic values, preserving static lettering and separators.
magick -size 920x920 xc:black -fill white -draw 'rectangle 267,337 580,600 rectangle 610,309 772,431 rectangle 599,238 769,289 polygon 505,89 586,109 572,157 489,135 polygon 476,765 592,747 610,805 478,815 polygon 716,614 785,492 839,518 767,644 polygon 215,684 250,659 283,705 235,734 polygon 174,237 250,161 289,201 213,278 rectangle 127,263 203,337' design/dynamic-mask.png
for theme in dark light; do
 if [ "$theme" = dark ]; then
   magick -size 920x920 xc:black -fx 'max(5,23-0.018*i-0.010*j)/255' design/runtime-fill.png
 else
   cp design/texture-field.png design/runtime-fill.png
 fi
 magick design/runtime-fill.png design/dynamic-mask.png -alpha off -compose CopyOpacity -composite design/runtime-overlay.png
 magick "design/$theme-master.png" design/runtime-overlay.png -compose Over -composite "$r/background_$theme.png"
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
 for number in {0..23}; do
  printf -v word '%02d' "$number"
  if [ "$word" != 10 ]; then
   magick -size 310x260 xc:none -font "$font" -pointsize 310 -fill "$fg" -gravity center -annotate +0-5 "$word" design/hour-working.png
   magick design/hour-working.png -alpha on -channel A -fx '(j>0.8*i-62 && mod(i-j+1008,14)<4) ? 0 : u.a' +channel "$r/hour_${theme}_$word.png"
  fi
  magick "$r/hour_${theme}_$word.png" -resize 155x130 "$r/hour_${theme}_$word.png"
 done
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
rm -f design/runtime-fill.png design/runtime-overlay.png design/stripe-pattern.png design/hour-working.png "$r"/digit_*.png "$r"/striped_*.png

magick mogrify -strip "$r"/*.png
