"""Turn rough line art into PURE smooth uniform-width curves (handwriting wobble removed).

Geometric, not generative:
  1. Binarize ink, skeletonize to 1px centerlines.
  2. Split the skeleton at junctions into simple strokes; order each stroke's pixels.
  3. Fit a smoothing spline to each stroke and resample (irons out the wobble).
  4. Redraw every stroke at a constant thickness with round caps/joins (anti-aliased).
Outputs black-on-white PNG, transparent PNG, and a hi-res bilevel PBM for potrace -> SVG.
"""
import os
import sys
import cv2
import numpy as np
from scipy.interpolate import splprep, splev
from skimage.morphology import skeletonize

src = sys.argv[1]
out_dir = sys.argv[2]
stem = sys.argv[3] if len(sys.argv) > 3 else "clean"
thickness = int(sys.argv[4]) if len(sys.argv) > 4 else 14   # uniform stroke width (px)
smooth = float(sys.argv[5]) if len(sys.argv) > 5 else 8.0    # spline smoothing factor scale

os.makedirs(out_dir, exist_ok=True)
img = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
if img is None:
    raise SystemExit(f"could not read {src}")
h, w = img.shape
ink = img < 128                      # dark = ink
print(f"loaded {w}x{h}  ink coverage {100*ink.mean():.2f}%")

skel = skeletonize(ink)
print(f"skeleton pixels {skel.sum()}")

# --- split skeleton into simple strokes at junctions ---
nb = cv2.filter2D(skel.astype(np.uint8), -1, np.ones((3, 3), np.uint8), borderType=cv2.BORDER_CONSTANT)
degree = (nb - 1) * skel             # neighbor count along the skeleton
junction = (degree >= 3) & skel
strokes_mask = skel & ~junction      # drop junction pixels -> disjoint simple arcs
n, labels = cv2.connectedComponents(strokes_mask.astype(np.uint8), connectivity=8)


def order_path(coords):
    """Order a thin (1px) set of (y,x) pixels into a walk from one end."""
    pts = {tuple(p) for p in coords}
    # find an endpoint (a pixel with <=1 neighbor in the set); else any pixel (loop)
    def neigh(p):
        y, x = p
        return [(y+dy, x+dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                if (dy or dx) and (y+dy, x+dx) in pts]
    start = next((p for p in pts if len(neigh(p)) <= 1), next(iter(pts)))
    path, cur, prev = [start], start, None
    seen = {start}
    while True:
        nxt = [q for q in neigh(cur) if q not in seen]
        if not nxt:
            break
        # prefer continuing roughly straight
        cur, prev = nxt[0], cur
        seen.add(cur)
        path.append(cur)
    return np.array(path)


canvas = np.zeros((h, w), np.uint8)   # white strokes on black; invert at the end
drawn = 0
for i in range(1, n):
    coords = np.column_stack(np.where(labels == i))   # (y,x)
    if len(coords) < 6:                                # skip tiny fragments
        continue
    path = order_path(coords)
    if len(path) < 6:
        continue
    ys, xs = path[:, 0].astype(float), path[:, 1].astype(float)
    s = smooth * len(path)
    try:
        tck, _ = splprep([xs, ys], s=s, k=min(3, len(path) - 1))
        u = np.linspace(0, 1, max(50, len(path)))
        sx, sy = splev(u, tck)
    except Exception:
        sx, sy = xs, ys
    poly = np.stack([sx, sy], axis=1).astype(np.int32)
    cv2.polylines(canvas, [poly], False, 255, thickness=thickness,
                  lineType=cv2.LINE_AA)
    drawn += 1
print(f"strokes drawn {drawn}/{n-1}")

# Reconnect junctions: the split dropped junction pixels, leaving gaps where
# strokes met. Paint a filled disk (stroke-width) at each junction to bridge them.
jy, jx = np.where(junction)
for y, x in zip(jy, jx):
    cv2.circle(canvas, (int(x), int(y)), thickness // 2, 255, -1, lineType=cv2.LINE_AA)

# round the joints/caps and anti-alias via upscale-blur-threshold-downscale
scale = 2
big = cv2.resize(canvas, (w*scale, h*scale), interpolation=cv2.INTER_CUBIC)
k = (3*scale) | 1
big = cv2.GaussianBlur(big, (k, k), scale)
_, big_bin = cv2.threshold(big, 110, 255, cv2.THRESH_BINARY)
ink_aa = cv2.resize(big_bin, (w, h), interpolation=cv2.INTER_AREA)

bw = 255 - ink_aa
cv2.imwrite(os.path.join(out_dir, f"{stem}_bw.png"), bw)
rgba = np.zeros((h, w, 4), np.uint8)
rgba[:, :, 3] = ink_aa
cv2.imwrite(os.path.join(out_dir, f"{stem}_alpha.png"), rgba)
cv2.imwrite(os.path.join(out_dir, f"{stem}_hires.pbm"), 255 - big_bin)
print("wrote", f"{stem}_bw.png", f"{stem}_alpha.png", f"{stem}_hires.pbm")
