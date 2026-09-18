"""Extract clean black-on-white line art from a colored-ink drawing on textured paper.

The ink is high-saturation (purple); the paper is low-saturation beige. We isolate
the ink by HSV saturation (color independent of the paper texture), clean it up with
morphology, and render black lines on a white background.
"""
import sys
import cv2
import numpy as np

src = sys.argv[1]
dst = sys.argv[2]
sat_thresh = int(sys.argv[3]) if len(sys.argv) > 3 else 60

img = cv2.imread(src, cv2.IMREAD_COLOR)
if img is None:
    raise SystemExit(f"could not read {src}")
h, w = img.shape[:2]
print(f"loaded {w}x{h}")

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
hue = hsv[:, :, 0]
sat = hsv[:, :, 1]

# Ink is PURPLE: OpenCV hue ~120-175. Warm paper texture is orange/tan (low hue),
# so a hue band rejects the texture that bare saturation lets through.
hue_ok = (hue >= 120) & (hue <= 175)
mask = (hue_ok & (sat > sat_thresh)).astype(np.uint8) * 255

# Clean: close small gaps inside strokes, then remove tiny speckles.
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

# Drop connected components smaller than this fraction of the image (specks).
n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
min_area = max(20, int(0.00005 * h * w))
clean = np.zeros_like(mask)
kept = 0
for i in range(1, n):
    if stats[i, cv2.CC_STAT_AREA] >= min_area:
        clean[labels == i] = 255
        kept += 1
print(f"ink coverage {100*clean.mean()/255:.2f}%  components kept={kept}/{n-1}  min_area={min_area}")

# Black lines on white.
out = 255 - clean
cv2.imwrite(dst, out)
print(f"wrote {dst}")
