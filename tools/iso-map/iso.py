import math

C = math.cos(math.radians(30))
INK, ACC, CTX = "s", "a", "c"


def fmt(v):
    return f"{v:.1f}"


class Scene:
    def __init__(self, scale, tf):
        self.sc = scale
        self.tf = tf
        self.out = []
        self.pts = []

    def XY(self, x, y):
        return self.tf(x, y)

    def PXY(self, X, Y, z):
        p = ((X - Y) * C * self.sc, ((X + Y) * 0.5 - z) * self.sc)
        self.pts.append(p)
        return p

    def P(self, x, y, z):
        X, Y = self.XY(x, y)
        return self.PXY(X, Y, z)

    def poly(self, pts, cls, extra=""):
        s = " ".join(f"{fmt(a)},{fmt(b)}" for a, b in pts)
        return f'<polygon class="{cls}" points="{s}"{extra}/>'

    def line(self, a, b, cls):
        return f'<line class="{cls}" x1="{fmt(a[0])}" y1="{fmt(a[1])}" x2="{fmt(b[0])}" y2="{fmt(b[1])}"/>'

    def pline(self, pts, cls):
        s = " ".join(f"{fmt(a)},{fmt(b)}" for a, b in pts)
        return f'<polyline class="{cls}" points="{s}"/>'


def area(p):
    return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))) / 2


def clip_h(poly, y):
    xs = []
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 - y) * (y2 - y) < 0 or (y1 == y and y2 != y):
            t = (y - y1) / (y2 - y1)
            xs.append(x1 + t * (x2 - x1))
    if len(xs) < 2:
        return None
    return min(xs), max(xs)


class Item:
    def __init__(self, scene, bbox, fn):
        self.s, self.bbox, self.fn = scene, bbox, fn


def prism(sc, foot, z0, h, tone=INK, floors=0, mull=0, roof=None, ground_band=False):
    XY = [sc.XY(x, y) for x, y in foot]
    if area(XY) < 0:
        XY = XY[::-1]
    Xs = [p[0] for p in XY]
    Ys = [p[1] for p in XY]
    bbox = (min(Xs), max(Xs), min(Ys), max(Ys))

    def fn():
        o = []
        n = len(XY)
        for i in range(n):
            a, b = XY[i], XY[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            if dy - dx <= 1e-9:
                continue
            q = [sc.PXY(*a, z0), sc.PXY(*b, z0), sc.PXY(*b, z0 + h), sc.PXY(*a, z0 + h)]
            o.append(sc.poly(q, f"f {tone}"))
            L = math.hypot(dx, dy)
            if floors:
                for k in range(1, floors):
                    z = z0 + h * k / floors
                    o.append(sc.line(sc.PXY(*a, z), sc.PXY(*b, z), f"d {tone}"))
            if ground_band and floors:
                pass
            if mull:
                m = int(L / mull)
                for k in range(1, m):
                    t = k / m
                    X, Y = a[0] + dx * t, a[1] + dy * t
                    o.append(sc.line(sc.PXY(X, Y, z0 + 0.6), sc.PXY(X, Y, z0 + h - 0.6), f"w {tone}"))
        top = [sc.PXY(X, Y, z0 + h) for X, Y in XY]
        o.append(sc.poly(top, f"f {tone}"))
        if roof:
            o.append(roof())
        return "".join(o)

    return Item(sc, bbox, fn)


def solar(sc, foot, z, step=3.0, inset=3.0, tone=INK):
    def fn():
        ys = [p[1] for p in foot]
        o = []
        y = min(ys) + inset
        while y < max(ys) - inset + 0.01:
            r = clip_h(foot, y)
            if r:
                o.append(sc.line(sc.P(r[0] + inset, y, z + 0.1), sc.P(r[1] - inset, y, z + 0.1), f"w {tone}"))
            y += step
        return "".join(o)
    return fn


def tree(sc, x, y, r=3.2, h=7, tone=CTX):
    X, Y = sc.XY(x, y)
    bbox = (X - r * 0.4, X + r * 0.4, Y - r * 0.4, Y + r * 0.4)

    def fn():
        b = sc.PXY(X, Y, 0)
        t = sc.PXY(X, Y, h - r)
        cx, cy = sc.PXY(X, Y, h)
        rr = r * sc.sc
        return sc.line(b, t, f"d {tone}") + f'<circle class="f {tone}" cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(rr)}"/>'
    return Item(sc, bbox, fn)


def depth_sort(items):
    n = len(items)
    before = {i: set() for i in range(n)}
    e = 1e-6
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            A, B = items[i].bbox, items[j].bbox
            ab = A[1] <= B[0] + e or A[3] <= B[2] + e
            ba = B[1] <= A[0] + e or B[3] <= A[2] + e
            if ab and not ba:
                before[j].add(i)
    done, order = set(), []
    key = lambda i: (items[i].bbox[0] + items[i].bbox[1] + items[i].bbox[2] + items[i].bbox[3])
    while len(order) < n:
        ready = [i for i in range(n) if i not in done and before[i] <= done]
        if not ready:
            ready = [min((i for i in range(n) if i not in done), key=key)]
        i = min(ready, key=key)
        done.add(i)
        order.append(items[i])
    return order


def ellipse(sc, cx, cy, a, b, z, n=120):
    return [sc.P(cx + a * math.cos(2 * math.pi * k / n), cy + b * math.sin(2 * math.pi * k / n), z) for k in range(n)]
