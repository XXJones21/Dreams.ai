"""Colored-ink drawing -> smooth line art, in multiple formats.

Stages:
  1. Isolate the purple ink by HSV hue+saturation (rejects the warm paper texture
     that a bare edge detector / saturation-only mask lets through).
  2. Smooth the jagged stroke edges via upscale -> Gaussian blur -> threshold
     -> area-downscale (rounds corners and anti-aliases in one shot).
  3. Emit:
       *_bw.png    black ink on solid white   (anti-aliased)
       *_alpha.png black ink, transparent bg  (RGBA, alpha = ink coverage)
       *_hires.pbm bilevel hi-res bitmap for potrace -> SVG (run separately)
"""
import os
import sys
import cv2
import numpy as np

src = sys.argv[1]
out_dir = sys.argv[2]
stem = sys.argv[3] if len(sys.argv) > 3 else "lineart"
sat_thresh = int(sys.argv[4]) if len(sys.argv) > 4 else 50
smooth = float(sys.argv[5]) if len(sys.argv) > 5 else 2.5  # blur sigma at 4x scale

os.makedirs(out_dir, exist_ok=True)
img = cv2.imread(src, cv2.IMREAD_COLOR)
if img is None:
    raise SystemExit(f"could not read {src}")
h, w = img.shape[:2]
print(f"loaded {w}x{h}")

# --- 1. isolate ink (white=ink on black) ---
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
hue, sat = hsv[:, :, 0], hsv[:, :, 1]
hue_ok = (hue >= 120) & (hue <= 175)           # purple band; paper is orange/tan
mask = (hue_ok & (sat > sat_thresh)).astype(np.uint8) * 255

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

# drop speckles
n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
min_area = max(40, int(0.0001 * h * w))
clean = np.zeros_like(mask)
kept = 0
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] >= min_area:
        clean[labels == i] = 255
        kept += 1
print(f"ink coverage {100*clean.mean()/255:.2f}%  components kept={kept}/{n-1}  min_area={min_area}")

# --- 2. smooth: upscale, blur, threshold (hi-res bilevel), then area-downscale (AA) ---
scale = 4
big = cv2.resize(clean, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
k = int(smooth * scale) | 1  # odd kernel
big = cv2.GaussianBlur(big, (k, k), smooth * scale)
_, big_bin = cv2.threshold(big, 127, 255, cv2.THRESH_BINARY)   # smooth shape, hi-res
# anti-aliased ink-coverage map at original resolution (0..255, white=ink)
ink_aa = cv2.resize(big_bin, (w, h), interpolation=cv2.INTER_AREA)

# --- 3. outputs ---
bw = 255 - ink_aa                                   # black ink on white
bw_path = os.path.join(out_dir, f"{stem}_bw.png")
cv2.imwrite(bw_path, bw)

rgba = np.zeros((h, w, 4), dtype=np.uint8)          # black ink, transparent bg
rgba[:, :, 3] = ink_aa                              # alpha = ink coverage (RGB stays 0=black)
cv2.imwrite(os.path.join(out_dir, f"{stem}_alpha.png"), rgba)

# hi-res bilevel for potrace; PBM convention: write as black-ink-on-white via PNG->PBM
# potrace traces dark pixels, so invert the hi-res shape (ink->black) before saving.
pbm = 255 - big_bin
pbm_path = os.path.join(out_dir, f"{stem}_hires.pbm")
cv2.imwrite(pbm_path, pbm)  # OpenCV writes .pbm as P4 bilevel

print("wrote:")
for p in (f"{stem}_bw.png", f"{stem}_alpha.png", f"{stem}_hires.pbm"):
    print("  ", os.path.join(out_dir, p))
