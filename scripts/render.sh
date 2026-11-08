#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Uniform crop and scale. No typography or stripe reconstruction.
magick references/29937.jpg -crop 920x920+139+140 +repage design/dark-master.png
# Sample the actual unlettered LCD field in reference 2.
magick references/29886.jpg -crop 110x70+550+655 +repage design/texture-sample.png
magick -size 920x920 tile:design/texture-sample.png design/texture-field.png
# Derive all glyphs and stripes from the same source pixels.
# RGB source luminance is the coverage mask; red indices are recolored separately.
magick design/dark-master.png design/texture-field.png -fx 'sqrt((i-459.5)^2+(j-459.5)^2)<396 ? (u.r>u.g*1.8 && u.r>0.25 ? channel(0.62,0.35,0.37) : v*(1-max(u.r,max(u.g,u.b)))+channel(0.12,0.16,0.19)*max(u.r,max(u.g,u.b))) : channel(0.20,0.25,0.30)*(1-max(u.r,max(u.g,u.b)))+0.82*max(u.r,max(u.g,u.b))' design/light-master.png
for theme in dark light; do
 magick -size 920x920 xc:none -fill white -draw 'circle 459.5,459.5 459.5,0' design/mask.png
 magick "design/$theme-master.png" design/mask.png -alpha off -compose CopyOpacity -composite "design/$theme-920.png"
 magick "design/$theme-920.png" -filter Lanczos -resize 450x450 "design/$theme-450.png"
done
rm design/mask.png
magick design/dark-450.png design/light-450.png +append -background '#24272b' -alpha remove design/preview.png
