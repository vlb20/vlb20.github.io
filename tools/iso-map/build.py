import math
from iso import *

# ---------------------------------------------------------------- NAPLES
# local metres: x = east, y = south. Viewer from the south-west.
W = 400
SCALE = 1.4  # px per metre, shared by both scenes
na = Scene(SCALE, lambda x, y: (y, W - x))
N = []  # sorted items
FL = 3.5


def B(sc, lst, x0, x1, y0, y1, h, tone=INK, floors=None, mull=0, roof=None):
    foot = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    f = floors if floors is not None else max(1, round(h / FL))
    lst.append(prism(sc, foot, 0, h, tone, f, mull, roof))
    return foot


def roofbox(sc, x0, x1, y0, y1, z, h, tone=INK):
    foot = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    it = prism(sc, foot, z, h, tone)
    return it.fn


# north-west: civil engineering wing + transportation building
B(na, N, 19.5, 38, 109, 154, 14)
B(na, N, 38, 95, 128, 148, 17.5, mull=6, roof=roofbox(na, 70, 82, 132, 142, 17.5, 2.5))
# industrial engineering: long block + taller light block
B(na, N, 19.5, 78.5, 156, 179.5, 14, mull=6)
B(na, N, 78.5, 96, 157, 177, 21, mull=4.5)
# entrance pavilion + gate canopy on Via Claudio
B(na, N, 100, 110, 176, 192, 7)
N.append(prism(na, [(110, 178), (119, 178), (119, 190), (110, 190)], 4.2, 1.0, ACC, 0))
for cy in (179, 189):
    N.append(prism(na, [(117.6, cy - 0.4), (118.4, cy - 0.4), (118.4, cy + 0.4), (117.6, cy + 0.4)], 0, 4.2, ACC, 0))
# DIETI (highlighted)
B(na, N, 23, 36, 186, 250, 14, ACC, mull=6)
B(na, N, 36, 78.5, 186, 197, 10.5, ACC)
B(na, N, 36, 97, 197, 215, 17.5, ACC, floors=5, mull=4,
  roof=roofbox(na, 70, 92, 199, 207, 17.5, 3, ACC))
# solar hall
sh = B(na, N, 37, 60, 219, 255, 9, floors=2)
N[-1] = prism(na, sh, 0, 9, INK, 2, 0, solar(na, sh, 9, 2.6, 2))
# courtyard building (Knome lab block)
B(na, N, 63, 80, 220, 256, 14, mull=6)
B(na, N, 80, 90, 220, 234, 14)
B(na, N, 90, 112, 220, 256, 14, mull=6)
# southern bar
B(na, N, 41, 91, 258, 271, 10.5, mull=6)
# brick buildings around the garden
B(na, N, 32, 108, 282, 297, 11, mull=7)
B(na, N, 32, 56, 297, 358, 8)
rw = [(89, 297), (108, 297), (108, 358), (89, 358)]
N.append(prism(na, rw, 0, 9, INK, 2, 0, solar(na, rw, 9, 2.6, 1.5)))
# low labs
B(na, N, 35, 70, 364, 395, 6, floors=2)
B(na, N, 73, 111, 364, 395, 6.5, floors=2)
B(na, N, 35, 111, 398, 432, 5.5, floors=1)
# trees: west boulevard and along Via Claudio
for y in range(118, 445, 13):
    N.append(tree(na, 10, y, 3.6, 9))
for y in range(160, 440, 15):
    N.append(tree(na, 130, y, 3.4, 8))

SCX, SCY = 262.7, 296.8
SA, SB = 123, 147.6


def ground_naples():
    sc, o = na, []
    g = [sc.P(5, 95, 0), sc.P(392, 95, 0), sc.P(392, 455, 0), sc.P(5, 455, 0)]
    o.append(sc.poly(g, "gnd"))
    for x in range(25, 392, 25):
        o.append(sc.line(sc.P(x, 95, 0), sc.P(x, 455, 0), "grid"))
    for y in range(100, 455, 25):
        o.append(sc.line(sc.P(5, y, 0), sc.P(392, y, 0), "grid"))
    for x in (113, 125):
        o.append(sc.line(sc.P(x, 95, 0), sc.P(x, 455, 0), "road"))
    o.append(sc.line(sc.P(119, 95, 0), sc.P(119, 455, 0), "lane"))
    # garden path in the brick courtyard
    pts = [sc.P(70 + 8 * math.sin(t / 6), 300 + t * 2.9, 0) for t in range(0, 20)]
    o.append(sc.pline(pts, "lane"))
    return "".join(o)


def stadium():
    sc, o = na, []
    cx, cy = SCX, SCY
    o.append(sc.poly(ellipse(sc, cx, cy, SA, SB, 0), "f c nostroke"))
    # bowl: tiers from pitch edge up under the roof
    ra, rb = 75, 99.6
    fa, fb = 40, 71.5
    o.append(sc.poly(ellipse(sc, cx, cy, ra, rb, 20), "f s"))
    for k in range(0, 6):
        t = k / 5
        o.append(sc.poly(ellipse(sc, cx, cy, fa + (ra - fa) * t, fb + (rb - fb) * t, 1 + 19 * t),
                         "f s" if k == 0 else "o w s"))
    for k in range(0, 360, 12):
        th = math.radians(k)
        o.append(sc.line(sc.P(cx + fa * math.cos(th), cy + fb * math.sin(th), 1),
                         sc.P(cx + ra * math.cos(th), cy + rb * math.sin(th), 20), "w s"))
    # pitch 68 x 105, long axis north-south
    pw, pl = 34, 52.5
    P = lambda x, y: sc.P(cx + x, cy + y, 1.2)
    o.append(sc.poly([P(-pw, -pl), P(pw, -pl), P(pw, pl), P(-pw, pl)], "o d s pitch"))
    o.append(sc.line(P(-pw, 0), P(pw, 0), "d s pitch"))
    o.append(sc.poly([P(9.15 * math.cos(t / 12 * math.pi), 9.15 * math.sin(t / 12 * math.pi)) for t in range(24)], "o d s pitch"))
    for s in (-1, 1):
        o.append(sc.pline([P(-20.15, s * pl), P(-20.15, s * (pl - 16.5)), P(20.15, s * (pl - 16.5)), P(20.15, s * pl)], "o d s pitch"))
    # outer wall (visible half) with steel frames
    n = 120
    H = 30
    pts = [(cx + SA * math.cos(2 * math.pi * k / n), cy + SB * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]
    XY = [sc.XY(*p) for p in pts]
    vis = []
    for k in range(n):
        a, b = XY[k], XY[k + 1]
        # polygon goes clockwise in XY (mirror), outward normal = (-dy, dx)
        dx, dy = b[0] - a[0], b[1] - a[1]
        nx, ny = -dy, dx
        if area([sc.XY(*p) for p in pts[:-1]]) > 0:
            nx, ny = dy, -dx
        v = nx + ny > 0
        vis.append(v)
        if v:
            o.append(sc.poly([sc.PXY(*a, 0), sc.PXY(*b, 0), sc.PXY(*b, H), sc.PXY(*a, H)], "f s nostroke"))
    for z, cls in ((0, "e s"), (11, "d s"), (21, "d s")):
        seg = []
        for k in range(n):
            if vis[k]:
                seg.append(sc.PXY(*XY[k], z))
                seg.append(sc.PXY(*XY[k + 1], z))
            elif seg:
                o.append(sc.pline(seg, cls)); seg = []
        if seg:
            o.append(sc.pline(seg, cls))
    for k in range(0, n, 3):
        if vis[k] and vis[k - 1]:
            o.append(sc.line(sc.PXY(*XY[k], 0), sc.PXY(*XY[k], H), "d s"))
            if k + 3 <= n and vis[min(k + 2, n - 1)]:
                o.append(sc.line(sc.PXY(*XY[k], 21), sc.PXY(*XY[k + 3], H), "w s"))
                o.append(sc.line(sc.PXY(*XY[k], H), sc.PXY(*XY[k + 3], 21), "w s"))
    # roof ring
    outer = ellipse(sc, cx, cy, SA, SB, H)
    inner = ellipse(sc, cx, cy, ra, rb, H - 3)
    d = "M" + " L".join(f"{fmt(a)},{fmt(b)}" for a, b in outer) + "Z M" + " L".join(f"{fmt(a)},{fmt(b)}" for a, b in inner) + "Z"
    o.append(f'<path class="f e s" fill-rule="evenodd" d="{d}"/>')
    for k in range(0, 360, 3):
        th = math.radians(k)
        o.append(sc.line(sc.P(cx + SA * math.cos(th), cy + SB * math.sin(th), H),
                         sc.P(cx + ra * math.cos(th), cy + rb * math.sin(th), H - 3), "w s"))
    return "".join(o)


# ---------------------------------------------------------------- LUGANO
# local metres: x = east, y = south. Viewer from the south-east.
lu = Scene(SCALE, lambda x, y: (x, y))
L = []
FLL = 3.3


def LP(foot, h, tone=INK, floors=None, mull=3.2, roof=None):
    f = floors if floors is not None else max(1, round(h / FLL))
    L.append(prism(lu, foot, 0, h, tone, f, mull, roof))


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def lroof(x0, x1, y0, y1, z, tone=INK):
    return prism(lu, rect(x0, x1, y0, y1), z, 2.4, tone).fn


def terrace(pts, z, tone=INK):
    return prism(lu, pts, z, 1.2, tone).fn


ne = [(56, 0), (86.5, 0), (92, 35), (56, 35)]
sw = [(0, 94), (39, 94), (39, 130), (8, 130)]
# links (green roofs with rooftop pavilions)
LP(rect(30, 56, 6, 31), 11, roof=terrace([(38, 14), (46, 12), (49, 19), (43, 25), (37, 21)], 11))
LP(rect(70, 90.5, 35, 59.5), 11, roof=terrace([(74, 42), (82, 39), (86, 46), (80, 53), (75, 49)], 11))
LP(rect(2, 22, 71, 94), 11, roof=terrace([(6, 78), (13, 75), (18, 81), (13, 88), (7, 85)], 11))
LP(rect(39, 62, 99.5, 124.5), 11, roof=terrace([(44, 105), (52, 103), (56, 110), (50, 117), (45, 113)], 11))
# trapezoid blocks with PV roofs
LP(ne, 15, roof=solar(lu, ne, 15, 2.9, 2.5, INK))
LP(sw, 15, roof=solar(lu, sw, 15, 2.9, 2.5, INK))
# tall slabs
LP(rect(3, 30, 5, 71), 26, roof=lroof(9, 24, 14, 62, 26))
# Sector C (Software Institute)
LP(rect(62, 90, 59.5, 126), 26, ACC, roof=lroof(68, 84, 68, 117, 26, ACC))
# courtyard trees
for x, y in ((42, 43.7), (52.7, 45.4), (56.6, 62.2), (37, 67.7), (39.2, 76), (48, 88)):
    L.append(tree(lu, x, y, 2.6, 7.5))
# round building to the north (context)
L.append(prism(lu, [(39 + 7 * math.cos(t / 10 * 2 * math.pi), -30 + 7 * math.sin(t / 10 * 2 * math.pi)) for t in range(10)], 0, 8, CTX))
for k in range(5):
    t = 2 * math.pi * k / 5 + 0.3
    cxp, cyp = 39 + 12 * math.cos(t), -30 + 12 * math.sin(t)
    sq = [(cxp + 4.5 * math.cos(t + q), cyp + 4.5 * math.sin(t + q)) for q in (0.785, 2.356, 3.927, 5.498)]
    L.append(prism(lu, sq, 0, 6.5, CTX, 2))
# riverside trees
for y in range(-40, 162, 9):
    L.append(tree(lu, -13, y, 3.0, 9))
for x in range(5, 118, 12):
    L.append(tree(lu, x, 140, 2.4, 6.5))


def ground_lugano():
    sc, o = lu, []
    g = [sc.P(-34, -48, 0), sc.P(120, -48, 0), sc.P(120, 165, 0), sc.P(-34, 165, 0)]
    o.append(sc.poly(g, "gnd"))
    for x in range(-30, 121, 10):
        o.append(sc.line(sc.P(x, -48, 0), sc.P(x, 165, 0), "grid"))
    for y in range(-40, 166, 10):
        o.append(sc.line(sc.P(-34, y, 0), sc.P(120, y, 0), "grid"))
    # river Cassarate
    for x0 in (-31, -21):
        o.append(sc.line(sc.P(x0, -48, 0), sc.P(x0, 165, 0), "road"))
    for i, y0 in enumerate(range(-44, 160, 12)):
        pts = [sc.P(-29 + t * 1.5 + (i % 2) * 1.5, y0 + 4 * math.sin(t * 1.3), 0) for t in range(0, 4)]
        o.append(sc.pline(pts, "wave"))
    # Via la Santa
    for y in (146, 157):
        o.append(sc.line(sc.P(-20, y, 0), sc.P(120, y, 0), "road"))
    o.append(sc.line(sc.P(-20, 151.5, 0), sc.P(120, 151.5, 0), "lane"))
    # courtyard paving
    o.append(sc.poly([sc.P(30, 31, 0), sc.P(62, 31, 0), sc.P(62, 99.5, 0), sc.P(30, 99.5, 0)], "o lane"))
    return "".join(o)


def render(sc, ground, items, pre="", base=0.0, step=0.035):
    sc.out = [f'<g class="anim" style="--d:{base:.2f}s">' + ground() + '</g>']
    t = base + 0.35
    if pre:
        sc.out.append(f'<g class="anim slow stadium" style="--d:{t:.2f}s" tabindex="0" role="button" aria-label="Diego Armando Maradona Stadium">' + pre() + '</g>')
        t += 0.5
    for it in depth_sort(items):
        sc.out.append(f'<g class="anim" style="--d:{t:.2f}s">' + it.fn() + '</g>')
        t += step
    return "".join(sc.out)


nap_svg = render(na, ground_naples, N, stadium, 0.0, 0.03)
lug_svg = render(lu, ground_lugano, L, "", 0.6, 0.03)


def bounds(sc):
    xs = [p[0] for p in sc.pts]
    ys = [p[1] for p in sc.pts]
    return min(xs), max(xs), min(ys), max(ys)


import json
json.dump({"nap": bounds(na), "lug": bounds(lu)}, open("bounds.json", "w"))
open("nap.frag", "w").write(nap_svg)
open("lug.frag", "w").write(lug_svg)

# anchors for labels (screen coords before translation)
anchors = {
    "dieti": na.P(60, 206, 17.5),
    "gate": na.P(118, 184, 5.2),
    "stadium": na.P(SCX - SA * 0.5, SCY - SB * 0.85, 30),
    "claudio": na.P(119, 440, 0),
    "nnorth": (na.P(30, 120, 0), na.P(30, 100, 0)),
    "usi": lu.P(76, 92, 26),
    # 50 m scale bars, along each scene's east-west axis
    "nscale": (na.P(150, 452, 0), na.P(200, 452, 0)),
    "lscale": (lu.P(62, 163, 0), lu.P(112, 163, 0)),
    "usiw": lu.P(16, 38, 26),
    "river": lu.P(-26, 120, 0),
    "santa": lu.P(100, 151.5, 0),
    "lnorth": (lu.P(110, -30, 0), lu.P(110, -45, 0)),
}
json.dump(anchors, open("anchors.json", "w"))
print(bounds(na), bounds(lu))
