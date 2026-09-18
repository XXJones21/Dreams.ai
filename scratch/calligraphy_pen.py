"""Re-stroke clean line art with a broad-nib calligraphy pen (variable width).

Model: a flat pen nib held at a FIXED angle. As the nib travels a path, the
stroke's width = the nib's footprint projected perpendicular to the travel
direction. So strokes running across the nib are wide; strokes running along
it taper thin -- the signature calligraphic thick/thin. Implemented by offsetting
each centerline point by a constant nib vector (+/- half the nib width).

  1. skeletonize -> centerlines, split at junctions, order + spline-smooth each.
  2. build a ribbon per stroke: top = c + (L/2)*nib, bottom = c - (L/2)*nib; fill.
  3. thin base stroke along the centerline keeps strokes connected at the thin bits.
  4. heavy upscale-blur-threshold smooth -> potrace = glassy vector edges.

args: src out_dir stem  [nib_deg=40] [max_w=30] [min_w=4] [smooth=6]
"""
import os, sys, cv2, numpy as np
from scipy.interpolate import splprep, splev
from skimage.morphology import skeletonize

src, out_dir, stem = sys.argv[1], sys.argv[2], sys.argv[3]
nib_deg = float(sys.argv[4]) if len(sys.argv) > 4 else 40.0
max_w   = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0
min_w   = int(sys.argv[6])   if len(sys.argv) > 6 else 4
smooth  = float(sys.argv[7]) if len(sys.argv) > 7 else 6.0

g = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
h, w = g.shape
ink = g < 128
skel = skeletonize(ink)

nb = cv2.filter2D(skel.astype(np.uint8), -1, np.ones((3, 3), np.uint8), borderType=cv2.BORDER_CONSTANT)
junction = ((nb - 1) * skel >= 3) & skel
n, labels = cv2.connectedComponents((skel & ~junction).astype(np.uint8), connectivity=8)

def order_path(coords):
    pts = {tuple(p) for p in coords}
    def neigh(p):
        y, x = p
        return [(y+dy, x+dx) for dy in (-1,0,1) for dx in (-1,0,1)
                if (dy or dx) and (y+dy, x+dx) in pts]
    start = next((p for p in pts if len(neigh(p)) <= 1), next(iter(pts)))
    path, cur, seen = [start], start, {start}
    while True:
        nxt = [q for q in neigh(cur) if q not in seen]
        if not nxt:
            break
        cur = nxt[0]; seen.add(cur); path.append(cur)
    return np.array(path)

ang = np.deg2rad(nib_deg)
nib = np.array([np.cos(ang), np.sin(ang)]) * (max_w / 2.0)   # half-nib vector (x,y)

canvas = np.zeros((h, w), np.uint8)
drawn = 0
for i in range(1, n):
    coords = np.column_stack(np.where(labels == i))
    if len(coords) < 6:
        continue
    path = order_path(coords)
    if len(path) < 6:
        continue
    ys, xs = path[:, 0].astype(float), path[:, 1].astype(float)
    try:
        tck, _ = splprep([xs, ys], s=smooth * len(path), k=3)
        u = np.linspace(0, 1, max(60, len(path)))
        sx, sy = splev(u, tck)
    except Exception:
        sx, sy = xs, ys
    c = np.stack([sx, sy], axis=1)                      # (x,y) centerline
    top = c + nib
    bot = c - nib
    ribbon = np.concatenate([top, bot[::-1]], axis=0).astype(np.int32)
    cv2.fillPoly(canvas, [ribbon], 255, lineType=cv2.LINE_AA)
    cv2.polylines(canvas, [c.astype(np.int32)], False, 255, thickness=min_w, lineType=cv2.LINE_AA)
    drawn += 1
# bridge junction gaps
jy, jx = np.where(junction)
for y, x in zip(jy, jx):
    cv2.circle(canvas, (int(x), int(y)), max(min_w, int(max_w*0.18)), 255, -1, lineType=cv2.LINE_AA)
print(f"strokes drawn {drawn}/{n-1}  nib {nib_deg} deg  max_w {max_w}")

# glassy smoothing
s = 3
big = cv2.resize(canvas, (w*s, h*s), interpolation=cv2.INTER_CUBIC)
k = (4*s) | 1
big = cv2.GaussianBlur(big, (k, k), 2.0*s)
_, bigb = cv2.threshold(big, 128, 255, cv2.THRESH_BINARY)
aa = cv2.resize(bigb, (w, h), interpolation=cv2.INTER_AREA)
cv2.imwrite(os.path.join(out_dir, f"{stem}_bw.png"), 255 - aa)
rgba = np.zeros((h, w, 4), np.uint8); rgba[:, :, 3] = aa
cv2.imwrite(os.path.join(out_dir, f"{stem}_alpha.png"), rgba)
cv2.imwrite(os.path.join(out_dir, f"{stem}_hires.pbm"), 255 - bigb)
print("wrote", f"{stem}_bw.png", f"{stem}_alpha.png", f"{stem}_hires.pbm")
