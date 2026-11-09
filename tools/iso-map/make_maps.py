"""Assemble the isometric study map in two layouts.

Run `python3 build.py` first (writes nap.frag, lug.frag, bounds.json, anchors.json),
then `python3 make_maps.py`. Outputs go to ../../_includes/ (inline SVGs for the site)
and ../../images/ (standalone SVG).
"""
import json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_INC = os.environ.get("OUT_INC", os.path.join(ROOT, "_includes"))
OUT_IMG = os.environ.get("OUT_IMG", os.path.join(ROOT, "images"))

b = json.load(open(os.path.join(HERE, "bounds.json")))
A = json.load(open(os.path.join(HERE, "anchors.json")))
NAP = open(os.path.join(HERE, "nap.frag")).read()
LUG = open(os.path.join(HERE, "lug.frag")).read()

LIGHT = dict(bg="#F7F6F2", gnd="#EFEDE7", ink="#0B0B0C", ctx="#9A988F", acc="#0E87BC", grid="#E3E1DA")
DARK = dict(bg="#0B0B0C", gnd="#121214", ink="#F2F1EC", ctx="#6B6A66", acc="#12A0D7", grid="#232326")


def tokens(p):
    return ";".join(f"--m-{k}:{v}" for k, v in p.items())


def place(bb, cx, top):
    x0, x1, y0, y1 = bb
    return cx - (x0 + x1) / 2, top - y0


def T(a, t):
    return a[0] + t[0], a[1] + t[1]


def callout(anchor, label_xy, title, sub=None, side="start", accent=False, k=1.0):
    ax, ay = anchor
    lx, ly = label_xy
    cls = "lead a" if accent else "lead"
    o = f'<circle class="dot{" acc" if accent else ""}" cx="{ax:.1f}" cy="{ay:.1f}" r="{2.6 * k:.1f}"/>'
    o += f'<polyline class="{cls}" points="{ax:.1f},{ay:.1f} {ax:.1f},{ly:.1f} {lx:.1f},{ly:.1f}"/>'
    pad = 6 * k if side == "start" else -6 * k
    o += f'<text class="lbl" x="{lx + pad:.1f}" y="{ly - 4 * k:.1f}" text-anchor="{side}">{title}</text>'
    if sub:
        o += f'<text class="sub" x="{lx + pad:.1f}" y="{ly + 13 * k:.1f}" text-anchor="{side}">{sub}</text>'
    return o


def north(pair, at, k=1.0):
    (x0, y0), (x1, y1) = pair
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    cx, cy = at
    s = 16 * k
    tip = (cx + ux * s, cy + uy * s)
    tail = (cx - ux * s, cy - uy * s)
    px, py = -uy * 5 * k, ux * 5 * k
    o = f'<line class="lead" x1="{tail[0]:.1f}" y1="{tail[1]:.1f}" x2="{tip[0]:.1f}" y2="{tip[1]:.1f}"/>'
    o += (f'<polygon class="arrow" points="{tip[0]:.1f},{tip[1]:.1f} {cx + ux * 6 * k + px:.1f},{cy + uy * 6 * k + py:.1f} '
          f'{cx + ux * 6 * k - px:.1f},{cy + uy * 6 * k - py:.1f}"/>')
    o += f'<text class="sub" x="{tip[0] + ux * 12 * k:.1f}" y="{tip[1] + uy * 12 * k + 4 * k:.1f}" text-anchor="middle">N</text>'
    return o


def scalebar(pair, k=1.0, label="50 m"):
    (x0, y0), (x1, y1) = pair
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * 4 * k, dx / L * 4 * k
    o = f'<line class="lead" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}"/>'
    for (x, y) in ((x0, y0), (x1, y1)):
        o += f'<line class="lead" x1="{x - nx:.1f}" y1="{y - ny:.1f}" x2="{x + nx:.1f}" y2="{y + ny:.1f}"/>'
    o += f'<text class="sub" x="{(x0 + x1) / 2:.1f}" y="{max(y0, y1) + 16 * k:.1f}" text-anchor="middle">{label}</text>'
    return o


def style(k, tag):
    """k scales strokes and type, so the tall (mobile) layout stays legible once shrunk."""
    sw = lambda v: f"{v * k:.2f}"
    P = f".study-map--{tag}"
    return f"""<style>
  :where({P}) :is(polygon, line, polyline, path, circle) {{ stroke-width:{sw(.9)}; stroke-linejoin:round; stroke-linecap:round; fill:none; }}
  {P} .gnd {{ stroke:none; }}
  {P} .grid {{ stroke-width:{sw(.5)}; }}
  {P} .road {{ stroke-width:{sw(.7)}; }}
  {P} .lane {{ stroke-width:{sw(.6)}; stroke-dasharray:{sw(4)} {sw(3)}; }}
  {P} .wave {{ stroke-width:{sw(.6)}; }}
  {P} .o {{ fill:none; }}
  {P} .d {{ stroke-width:{sw(.45)}; }}
  {P} .w {{ stroke-width:{sw(.3)}; }}
  {P} .e {{ stroke-width:{sw(1.1)}; }}
  {P} .nostroke {{ stroke:none; }}
  {P} .lead {{ stroke-width:{sw(.7)}; }}
  {P} .dash {{ stroke-dasharray:{sw(3)} {sw(4)}; }}
  .study-map .dot, .study-map .arrow {{ stroke:none; }}
  :where(.study-map) text {{ font-family:"Inter","Helvetica Neue",Helvetica,Arial,sans-serif; stroke:none; }}
  {P} .kick {{ font-family:"JetBrains Mono",ui-monospace,monospace; font-size:{12 * k:.0f}px; letter-spacing:.08em; font-weight:500; }}
  {P} .ttl {{ font-size:{24 * k:.0f}px; font-weight:600; letter-spacing:-.01em; }}
  {P} .lbl {{ font-size:{14 * k:.0f}px; font-weight:600; }}
  {P} .sub {{ font-size:{12 * k:.0f}px; }}
  .study-map .bgr,.study-map .f{{fill:var(--m-bg)}} .study-map .gnd{{fill:var(--m-gnd)}} .study-map .grid{{stroke:var(--m-grid)}}
  .study-map .road,.study-map .s,.study-map .lead{{stroke:var(--m-ink)}} .study-map .lane,.study-map .wave,.study-map .c{{stroke:var(--m-ctx)}}
  .study-map .a,.study-map .lead.a,.study-map .dash{{stroke:var(--m-acc)}}
  .study-map .dot,.study-map .arrow,:where(.study-map) text{{fill:var(--m-ink)}} .study-map .dot.acc,.study-map .kick{{fill:var(--m-acc)}} .study-map .sub{{fill:var(--m-ctx)}}
  .study-map {{ {tokens(LIGHT)} }}
  @media (prefers-color-scheme: dark) {{ .study-map {{ {tokens(DARK)} }} }}
  html[data-theme="light"] .study-map {{ {tokens(LIGHT)} }}
  html[data-theme="dark"] .study-map {{ {tokens(DARK)} }}
  .study-map .anim :is(polygon,line,polyline,path,circle):not(.lane):not(.dash):not(.gnd):not(.dot):not(.arrow) {{
    stroke-dasharray:1; stroke-dashoffset:1;
    animation:iso-draw 1.3s cubic-bezier(.55,0,.25,1) var(--d,0s) forwards, iso-fill .4s ease var(--d,0s) both;
  }}
  .study-map .anim.slow :is(polygon,line,polyline,path,circle) {{ animation-duration:2.2s,.6s; }}
  .study-map .anim :is(.lane,.dash,.gnd,.dot,.arrow) {{ animation:iso-fade .8s ease var(--d,0s) both; }}
  .study-map .lbls text {{ animation:iso-rise .7s ease var(--d,0s) both; }}
  @keyframes iso-draw {{ to {{ stroke-dashoffset:0; }} }}
  @keyframes iso-fill {{ from {{ fill-opacity:0; }} to {{ fill-opacity:1; }} }}
  @keyframes iso-fade {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
  @keyframes iso-rise {{ from {{ opacity:0; transform:translateY(6px); }} to {{ opacity:1; transform:none; }} }}
  svg.study-map[data-scroll]:not(.in-view) * {{ animation-play-state:paused !important; }}
  @media (prefers-reduced-motion: reduce) {{
    .study-map .anim *, .study-map .lbls text {{ animation:none !important; stroke-dasharray:none !important; stroke-dashoffset:0 !important; }}
  }}
</style>"""


def heading(x, y, kick, ttl, sub, anchor, k):
    return (f'<text class="kick" x="{x}" y="{y}" text-anchor="{anchor}">{kick}</text>'
            f'<text class="ttl" x="{x}" y="{y + 32 * k:.0f}" text-anchor="{anchor}">{ttl}</text>'
            f'<text class="sub" x="{x}" y="{y + 54 * k:.0f}" text-anchor="{anchor}">{sub}</text>')


def svg_doc(tag, W, H, k, head, route, nt, lt, nlabels, llabels, scroll=True, size=False):
    sz = f' width="{W}" height="{H}"' if size else ""
    ds = " data-scroll" if scroll else ""
    s = f"""<svg class="study-map study-map--{tag}"{ds} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"{sz} role="img" aria-labelledby="map-{tag}-t map-{tag}-d">
<title id="map-{tag}-t">Where I studied: Naples and Lugano</title>
<desc id="map-{tag}-d">Isometric wireframe map of the University of Naples Federico II engineering campus on Via Claudio, next to the Diego Armando Maradona Stadium, and of USI Campus Est in Lugano-Viganello.</desc>
{style(k, tag)}
<rect class="bgr" width="{W}" height="{H}"/>
<g class="head anim lbls" style="--d:0s">{head}</g>
<g class="route anim" style="--d:0.4s">{route}</g>
<g class="scene" data-scene="naples"><g transform="translate({nt[0]:.1f},{nt[1]:.1f})">{NAP}</g><g class="anim lbls" style="--d:2.9s">{nlabels}</g></g>
<g class="scene" data-scene="lugano"><g transform="translate({lt[0]:.1f},{lt[1]:.1f})">{LUG}</g><g class="anim lbls" style="--d:2.9s">{llabels}</g></g>
</svg>"""

    def add_len(m):
        t = m.group(0)
        if re.search(r'class="[^"]*\b(lane|dash)\b', t):
            return t
        return t.replace(m.group(1), m.group(1) + ' pathLength="1"', 1)

    return re.sub(r'(<(?:polygon|line|polyline|path|circle))\b[^>]*>', add_len, s)


def wide(size=False, scroll=True):
    W, H, k = 1600, 820, 1.0
    nt = place(b["nap"], 480, 190)
    lt = place(b["lug"], 1262, 300)
    nd, ng, ns, nc = (T(A[n], nt) for n in ("dieti", "gate", "stadium", "claudio"))
    lu, lr, lsn = (T(A[n], lt) for n in ("usi", "river", "santa"))
    nl = (callout(nd, (190, 705), "DIETI", "Electrical Engineering &amp; IT", "end", True)
          + callout(ng, (320, 765), "Main gate", "Via Claudio 21", "start", True)
          + callout(ns, (ns[0] + 70, 215), "Diego Armando Maradona Stadium")
          + f'<text class="sub" x="{nc[0] + 10:.1f}" y="{nc[1] + 26:.1f}" text-anchor="middle">Via Claudio</text>'
          + north([T(p, nt) for p in A["nnorth"]], (80, 215))
          + scalebar([T(p, nt) for p in A["nscale"]]))
    ll = (callout(lu, (lu[0] + 90, lu[1] + 175), "Campus Est · Sector C", "Software Institute", "start", True)
          + callout(lr, (lr[0] - 40, lr[1] + 110), "Cassarate river", None, "end")
          + f'<text class="sub" x="{lsn[0] + 75:.1f}" y="{lsn[1] + 26:.1f}" text-anchor="middle">Via la Santa</text>'
          + north([T(p, lt) for p in A["lnorth"]], (1530, 300))
          + scalebar([T(p, lt) for p in A["lscale"]]))
    head = (heading(60, 70, "01 — NAPLES, ITALY", "University of Naples Federico II", "School of Engineering · Fuorigrotta", "start", k)
            + heading(W - 60, 70, "02 — LUGANO, SWITZERLAND", "Università della Svizzera italiana", "Campus Est · Lugano-Viganello", "end", k))
    route = ('<path class="lead dash" d="M 700 95 C 760 40, 840 40, 900 95"/>'
             '<circle class="dot acc" cx="700" cy="95" r="3"/><circle class="dot acc" cx="900" cy="95" r="3"/>'
             '<text class="sub" x="800" y="72" text-anchor="middle">~715 km</text>')
    return svg_doc("wide", W, H, k, head, route, nt, lt, nl, ll, scroll, size)


def tall():
    W, k = 1000, 2.0
    nt = place(b["nap"], W / 2 + 40, 300)
    nbot = nt[1] + b["nap"][3]
    lhead_y = nbot + 330
    lt = place(b["lug"], W / 2 + 40, lhead_y + 150)
    H = int(lt[1] + b["lug"][3] + 260)
    nd, ng, ns = (T(A[n], nt) for n in ("dieti", "gate", "stadium"))
    lu, lr = (T(A[n], lt) for n in ("usi", "river"))
    nl = (callout(nd, (70, nbot + 70), "DIETI", None, "start", True, k)
          + callout(ng, (ng[0] + 140, nbot + 150), "Main gate", None, "start", True, k)
          + callout(ns, (ns[0] + 110, 250), "Maradona Stadium", None, "start", False, k)
          + scalebar([T(p, nt) for p in A["nscale"]], k))
    ll = (callout(lu, (lu[0] + 90, lt[1] + b["lug"][3] + 110), "Campus Est · C", "Software Institute", "start", True, k)
          + callout(lr, (60, lr[1] + 150), "Cassarate", None, "start", False, k)
          + scalebar([T(p, lt) for p in A["lscale"]], k))
    head = (heading(40, 70, "01 — NAPLES, ITALY", "Federico II", "Via Claudio · Fuorigrotta", "start", k)
            + heading(40, lhead_y, "02 — LUGANO, SWITZERLAND", "USI Campus Est", "Lugano-Viganello", "start", k))
    x = W - 90
    y0, y1 = nbot + 80, lhead_y - 40
    route = (f'<path class="lead dash" d="M {x} {y0:.0f} C {x + 60} {y0 + 120:.0f}, {x + 60} {y1 - 120:.0f}, {x} {y1:.0f}"/>'
             f'<circle class="dot acc" cx="{x}" cy="{y0:.0f}" r="6"/><circle class="dot acc" cx="{x}" cy="{y1:.0f}" r="6"/>'
             f'<text class="sub" x="{x - 24}" y="{(y0 + y1) / 2 + 8:.0f}" text-anchor="end">~715 km</text>')
    return svg_doc("tall", W, H, k, head, route, nt, lt, nl, ll, True, False)


if __name__ == "__main__":
    os.makedirs(OUT_INC, exist_ok=True)
    os.makedirs(OUT_IMG, exist_ok=True)
    open(os.path.join(OUT_INC, "study-map-wide.svg"), "w").write(wide())
    open(os.path.join(OUT_INC, "study-map-tall.svg"), "w").write(tall())
    open(os.path.join(OUT_IMG, "study-map.svg"), "w").write(wide(size=True, scroll=False))
    print("ok")
