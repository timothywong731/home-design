"""CAD plan drafter: spec/house.json (+ docs/assets/footprints.json) -> plan.json, DXF, PDF.

    python tools/plan/draft.py [--footprints FILE] [--out DIR]   # -> docs/assets/{plan.json,ground-floor-plan.dxf,.pdf}
    python tools/plan/check.py            # re-reads/audits the DXF, rasterises DXF + PDF + plan.json into build/plan/

One entity list (the plan.json schema, world metres, +Y = rear = up the sheet) feeds all three outputs,
so on-screen plan, DXF and PDF cannot drift.  Needs shapely, ezdxf, matplotlib.

Fixtures/furniture: docs/assets/footprints.json [{name, room, plan_sym, obb:[[x,y]x4], height, front?:[dx,dy]}]
replaces the built-in SPEC_FOOTPRINTS (transcribed from spec/rooms/*.md) room by room: any room that has
at least one exported footprint is drawn only from the export.
"""
import json, math, sys, datetime
from pathlib import Path
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union, linemerge
import shapely

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets"
H = json.loads((ROOT / "spec" / "house.json").read_text(encoding="utf-8"))
ROOMS = {r["id"]: r for r in H["rooms"]}
WALLS = {w["id"]: w for w in H["walls"]}
RPOLY = {k: Polygon(r["polygon"]) for k, r in ROOMS.items()}
B = H["bounds"]

# name, dark-theme colour, paper colour, ACI, lineweight (paper mm)
LAYERS = [
    ("A-WALL-PATT", "#808080", "#555555", 8, 0.09),
    ("A-WALL", "#ffffff", "#000000", 7, 0.50),
    ("A-DOOR", "#ffff00", "#000000", 2, 0.25),
    ("A-GLAZ", "#00ffff", "#000000", 4, 0.18),
    ("A-STRS", "#00ff00", "#000000", 3, 0.18),
    ("A-FLOR-FIXT", "#ff00ff", "#000000", 6, 0.25),
    ("A-FLOR-OVHD", "#808080", "#333333", 8, 0.13),
    ("A-FURN", "#ff7f00", "#000000", 30, 0.13),
    ("A-ANNO-DIMS", "#ff0000", "#000000", 1, 0.13),
    ("A-ANNO-TEXT", "#ffffff", "#000000", 7, 0.18),
    ("A-ANNO-TTLB", "#ffffff", "#000000", 7, 0.35),
    ("A-ANNO-TTLB-BORD", "#ffffff", "#000000", 7, 0.70),
]
TAG = {"vestibule": "VESTIBULE", "hallway": "HALLWAY", "stairs": None, "living": "LIVING ROOM", "kitchen": "KITCHEN",
       "wc": "WC", "utility": "UTILITY", "dining": "DINING ROOM"}
TAG_AT = {"vestibule": (0.0, 1.02), "hallway": (0.0, 3.1), "living": (2.0, 1.42), "kitchen": (2.83, 7.3),
          "wc": (1.72, 9.82), "utility": (1.95, 11.05), "dining": (2.45, 16.25)}   # else representative point
CHAR_W = 0.826          # advance / cap height of the reference monospace face (DejaVu Sans Mono)
CAP = 0.72              # cap height / font size (em): plan.json text h is the font size, DXF TEXT height = CAP * h


def tw(s, h):
    return len(s) * CHAR_W * h


class Plan:
    def __init__(self):
        self.e = []

    def add(self, layer, typ, ls=None, **kw):
        d = {"layer": layer, "type": typ, **kw}
        if ls:
            d["ls"] = ls
        self.e.append(d)

    def line(self, layer, p1, p2, ls=None):
        self.add(layer, "line", ls, p1=list(p1), p2=list(p2))

    def pl(self, layer, pts, closed=False, ls=None):
        pts = [list(p) for p in pts]
        if closed and pts[0] == pts[-1]:
            pts.pop()
        self.add(layer, "polyline", ls, pts=pts, closed=closed)

    def rect(self, layer, x0, y0, x1, y1, ls=None):
        self.pl(layer, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], True, ls)

    def arc(self, layer, c, r, a0, a1, ls=None):
        self.add(layer, "arc", ls, c=list(c), r=r, a0=a0 % 360, a1=a1 % 360)

    def circle(self, layer, c, r, ls=None):
        self.add(layer, "circle", ls, c=list(c), r=r)

    def hatch(self, layer, pts, pattern="SOLID"):
        self.add(layer, "hatch", pts=[list(p) for p in pts], pattern=pattern)

    def text(self, layer, p, h, s, align="center", rot=0):
        """Drafted like CAD text (p = baseline point, h = cap height); stored the way the web viewer draws
        text: p = vertical middle of the capitals, h = font size (em), capitals = CAP x h."""
        r = math.radians(rot)
        self.add(layer, "text", p=[p[0] - math.sin(r) * h / 2, p[1] + math.cos(r) * h / 2], h=h / CAP, text=s, align=align, rot=rot)

    def dim(self, p1, p2, offset, tp=None):
        """tp = middle of a value moved off its default place. Such a dim carries text "" (so any consumer of
        the base schema draws no value) + value/tp, and the value follows as a text entity flagged of="dim";
        the DXF writer folds the two back into one DIMENSION with a user text location."""
        val = str(round(math.dist(p1, p2) * 1000))
        d = dict(p1=list(p1), p2=list(p2), offset=offset, text=val, h=T_DIM / CAP)
        if tp:
            d.update(text="", value=val, tp=list(tp))
        self.add("A-ANNO-DIMS", "dim", **d)
        if tp:
            rot = 0 if abs(p1[1] - p2[1]) < abs(p1[0] - p2[0]) else 90
            self.add("A-ANNO-DIMS", "text", p=list(tp), h=T_DIM / CAP, text=val, align="center", rot=rot, of="dim")

    def geom(self, g, layer, ls=None):
        """Emit shapely linework / polygon boundaries as polylines."""
        if g.is_empty:
            return
        if g.geom_type in ("Polygon",):
            for ring in [g.exterior, *g.interiors]:
                self.pl(layer, list(ring.coords), True, ls)
        elif g.geom_type in ("LineString", "LinearRing"):
            c = list(g.coords)
            self.pl(layer, c, c[0] == c[-1] and len(c) > 3, ls)
        else:
            for part in g.geoms:
                self.geom(part, layer, ls)


# ------------------------------------------------------------------ wall frames (as spec/validate_house.py)
def frame(w):
    (ax, ay), (bx, by) = w["a"], w["b"]
    L = math.hypot(bx - ax, by - ay)
    return ax, ay, (bx - ax) / L, (by - ay) / L, L


def wpt(w, s, n=0.0):
    """Point at distance s along the centreline a->b and n to its left."""
    ax, ay, ux, uy, _ = frame(w)
    return (ax + ux * s - uy * n, ay + uy * s + ux * n)


def along_perp(w, p):
    ax, ay, ux, uy, L = frame(w)
    dx, dy = p[0] - ax, p[1] - ay
    return dx * ux + dy * uy, dx * -uy + dy * ux, L


def end_ext(w, end):
    """Half-thickness of the thickest perpendicular wall through this end, so corners fill."""
    _, _, ux, uy, _ = frame(w)
    e = 0.0
    for o in WALLS.values():
        if o is w or o.get("virtual"):
            continue
        _, _, vx, vy, _ = frame(o)
        s, d, L = along_perp(o, w[end])
        if abs(ux * vx + uy * vy) < 0.1 and abs(d) < 0.01 and -0.01 <= s <= L + 0.01:
            e = max(e, o["thickness"] / 2)
    return e


def wquad(w, s0, s1, grow=0.0):
    h = w["thickness"] / 2 + grow
    return Polygon([wpt(w, s0, h), wpt(w, s1, h), wpt(w, s1, -h), wpt(w, s0, -h)])


def snap(g):
    return shapely.set_precision(g, 0.001)


def split_holes(poly):
    """Cut a polygon with holes into hole-free pieces (plan.json hatches carry one ring only)."""
    if not poly.interiors:
        return [poly]
    x = poly.interiors[0].centroid.x
    x0, y0, x1, y1 = poly.bounds
    out = []
    for half in (box(x0 - 1, y0 - 1, x, y1 + 1), box(x, y0 - 1, x1 + 1, y1 + 1)):
        g = poly.intersection(half)
        for p in getattr(g, "geoms", [g]):
            if p.geom_type == "Polygon" and p.area > 1e-6:
                out += split_holes(p)
    return out


FEATS = H["features"]
SOLID_F = unary_union([Polygon(f["polygon"]) for f in FEATS if f["type"] in ("pier", "pilaster", "chimney_breast", "nib", "poche")])
VOID_F = unary_union([Polygon(f["polygon"]) for f in FEATS if f["type"] in ("recess", "reveal")])


def opening_frame(o):
    """Wall, extent along it (s0, s1) and clear wall thickness (n0, n1) left after reveals are cut."""
    w = WALLS[o["wall"]]
    s = along_perp(w, o["center"])[0]
    s0, s1 = s - o["width"] / 2, s + o["width"] / 2
    n0, n1 = -w["thickness"] / 2, w["thickness"] / 2
    if n1 > 0:
        rem = wquad(w, s0 + 0.01, s1 - 0.01).difference(VOID_F)
        ns = [along_perp(w, c)[1] for c in rem.exterior.coords]
        n0, n1 = round(min(ns), 4), round(max(ns), 4)
    return w, s0, s1, n0, n1


def wall_solid():
    parts = [wquad(w, -end_ext(w, "a"), frame(w)[4] + end_ext(w, "b")) for w in WALLS.values() if not w.get("virtual")]
    solid = unary_union(parts + [SOLID_F]).difference(VOID_F)
    cuts = []
    for o in H["openings"]:
        w, s0, s1, _, _ = opening_frame(o)
        if not w.get("virtual"):
            cuts.append(wquad(w, s0, s1, 0.02))
    return snap(solid.difference(unary_union(cuts))), solid


WALL, WALL_UNCUT = wall_solid()          # poche as cut by the openings; and the shell with openings filled in
WALL = WALL.simplify(0.0005)

# ------------------------------------------------------------------ sheet: 1:50 on A3 if it fits, else next standard scale
A3 = (297.0, 420.0)
NEED_W, NEED_H = 32 + 135 + 20, 25 + 24 + 20      # paper mm around the house: dims, notes, title column, margins


def pick_sheet():
    hw, hh = B["maxX"] - B["minX"], B["maxY"] - B["minY"]
    W, Hs = A3 if hh >= hw else A3[::-1]
    for s in (50, 75, 100, 125, 150, 200, 250, 500):
        if hw * 1000 / s + NEED_W <= W and hh * 1000 / s + NEED_H <= Hs:
            return s, W, Hs
    raise SystemExit("house does not fit A3 at 1:500")


SCALE, SHEET_W, SHEET_H = pick_sheet()
MM = SCALE / 1000.0                                # model metres per paper millimetre
SX0 = B["minX"] - 42 * MM                          # sheet frame in model metres
SY0 = B["minY"] - (35 + (SHEET_H - NEED_H - (B["maxY"] - B["minY"]) / MM) / 2) * MM
SX1, SY1 = SX0 + SHEET_W * MM, SY0 + SHEET_H * MM
T_DIM, T_NAME, T_SUB, T_NOTE = 2.5 * MM, 2.5 * MM, 1.8 * MM, 3.0 * MM
# dim rules shared with docs/js/plan2d.js: ext lines start extGap off the point and pass the line by extBeyond,
# 45-degree ticks, text (font size h) centred 0.7 h above the line.  Line styles equal the viewer's at 1:50.
DIMSTYLE = {"h": T_DIM / CAP, "tick": 1.3 * MM, "extGap": 1.2 * MM, "extBeyond": 1.6 * MM}
HATCH_SPACING = 1.8 * MM
LINESTYLES = {"dashed": [2.4 * MM, 1.2 * MM], "hidden": [1.2 * MM, 0.8 * MM], "center": [6 * MM, 1.2 * MM, 1.2 * MM, 1.2 * MM]}


def draw_openings(P):
    for o in H["openings"]:
        w, s0, s1, n0, n1 = opening_frame(o)
        t = o["type"]
        if w.get("virtual"):
            continue
        if t == "arch":                                   # soffit overhead: dashed at both faces
            for n in (n0, n1):
                P.line("A-FLOR-OVHD", wpt(w, s0, n), wpt(w, s1, n), "dashed")
        elif t in ("window", "bay_window"):
            for n in (n0, n1):
                P.line("A-GLAZ", wpt(w, s0, n), wpt(w, s1, n))
            nm = (n0 + n1) / 2
            lights = [(s0, s1)]
            if o.get("lights"):                           # bay: lights separated by timber mullions, drawn true
                lw_, mu = o["lightWidth"], o["mullion"]
                a = s0 + (o["width"] - o["lights"] * lw_ - (o["lights"] - 1) * mu) / 2
                lights = [(a + i * (lw_ + mu), a + i * (lw_ + mu) + lw_) for i in range(o["lights"])]
                for (_, e0), (b1, _) in zip(lights, lights[1:]):
                    q = [wpt(w, e0, n0), wpt(w, b1, n0), wpt(w, b1, n1), wpt(w, e0, n1)]
                    P.hatch("A-GLAZ", q, "SOLID")
                    P.pl("A-GLAZ", q, True)
                for s in (lights[0][0], lights[-1][1]):
                    P.line("A-GLAZ", wpt(w, s, n0), wpt(w, s, n1))
            for a, b in lights:
                if n1 - n0 > 0.16:                        # frame set in a deeper wall
                    P.pl("A-GLAZ", [wpt(w, a, nm - 0.035), wpt(w, b, nm - 0.035), wpt(w, b, nm + 0.035), wpt(w, a, nm + 0.035)], True)
                P.line("A-GLAZ", wpt(w, a, nm), wpt(w, b, nm))
        elif o["hinge"] == "none":                        # pocket door: leaf slid into the wall, dashed
            sd = o["slideToward"]
            _, _, ux, uy, _ = frame(w)
            back = s0 if sd[0] * ux + sd[1] * uy < 0 else s1
            d = -1 if back == s0 else 1
            for n in (n0, n1):
                P.line("A-DOOR", wpt(w, s0, n), wpt(w, s1, n))
            stub = back - d * 0.09                        # ~90 mm of the leaf stays visible in the opening
            P.pl("A-DOOR", [wpt(w, back, -0.0175), wpt(w, stub, -0.0175), wpt(w, stub, 0.0175), wpt(w, back, 0.0175)])
            far = stub + d * o["width"]
            P.pl("A-DOOR", [wpt(w, back, -0.0175), wpt(w, far, -0.0175), wpt(w, far, 0.0175), wpt(w, back, 0.0175)], False, "hidden")
        else:                                             # hinged leaves: leaf at 90 deg + quarter-circle swing
            tgt, sign = o["swingInto"], 1
            if tgt == "outside":
                tgt, sign = next(r for r in o["connects"] if r != "outside"), -1
            left = RPOLY[tgt].contains(Point(wpt(w, (s0 + s1) / 2, w["thickness"] / 2 + 0.1)))
            side = sign * (1 if left else -1)
            nh = n1 if side > 0 else n0
            for n in (n0, n1):
                P.line("A-DOOR", wpt(w, s0, n), wpt(w, s1, n))
            if o["hinge"] == "both":
                leaves = [(s0, 1, o["width"] / 2), (s1, -1, o["width"] / 2)]
            else:
                ha = along_perp(w, o["hingeAt"])[0]
                leaves = [(ha, 1 if abs(ha - s0) < abs(ha - s1) else -1, o["width"])]
            for hs, d, lw_ in leaves:
                hp, tip, shut = wpt(w, hs, nh), wpt(w, hs, nh + side * lw_), wpt(w, hs + d * lw_, nh)
                P.pl("A-DOOR", [hp, wpt(w, hs + d * 0.04, nh), wpt(w, hs + d * 0.04, nh + side * lw_), tip], True)
                a_tip = math.degrees(math.atan2(tip[1] - hp[1], tip[0] - hp[0]))
                a_shut = math.degrees(math.atan2(shut[1] - hp[1], shut[0] - hp[0]))
                a0, a1 = (a_shut, a_tip) if round((a_tip - a_shut) % 360) == 90 else (a_tip, a_shut)
                P.arc("A-DOOR", hp, lw_, a0, a1)


def draw_stairs(P):
    S, L = H["stairs"], "A-STRS"
    x0, x1 = ROOMS["stairs"]["polygon"][0][0], ROOMS["stairs"]["polygon"][1][0]
    ytop = ROOMS["stairs"]["polygon"][2][1]
    nx, ny = S["newel"]
    y0s, g = S["start"][1], S["going"]
    # bottom three steps fan round the newel (stairs.md / validate_house.py): R1 quarter-ellipse bullnose, R2 arc, R3
    P.pl(L, [(0.65 - 0.53 * math.sin(i * math.pi / 32), ny - (ny - y0s - 0.02) * math.cos(i * math.pi / 32)) for i in range(17)])
    a, c = (nx + 0.05, ny - 0.03), (x1, ny - 0.22)
    P.pl(L, [(a[0] + (c[0] - a[0]) * k, a[1] + (c[1] - a[1]) * k - 0.24 * k * (1 - k)) for k in [i / 10 for i in range(11)]])
    P.line(L, (nx + 0.05, ny + 0.03), (x1, ny + 0.03))
    P.rect(L, nx - 0.05, ny - 0.05, nx + 0.05, ny + 0.05)                     # newel
    P.line(L, (x0, ny + 0.05), (x0, ytop))                                    # cut string / balustrade over spandrel
    # break line where the flight passes the 1.2 m cut plane (tread 6 is at 1.14 m)
    yb = S["firstStraightRiserY"] + 3.5 * g
    A_, B_ = (x0, yb - 0.17), (x1, yb + 0.17)
    lerp = lambda k: (A_[0] + (B_[0] - A_[0]) * k, A_[1] + (B_[1] - A_[1]) * k)
    m1, m2 = lerp(0.44), lerp(0.56)
    brk = [A_, m1, (m1[0] + 0.02, m1[1] + 0.09), (m2[0] - 0.02, m2[1] - 0.09), m2, B_]
    P.pl(L, brk)
    below = Polygon([(x0 - 1, y0s - 1), (x1 + 1, y0s - 1), (x1 + 1, B_[1]), *reversed(brk), (x0 - 1, A_[1])])
    n = 4
    while S["firstStraightRiserY"] + (n - 4) * g < ytop - 0.01:
        ln = LineString([(x0, S["firstStraightRiserY"] + (n - 4) * g), (x1, S["firstStraightRiserY"] + (n - 4) * g)])
        P.geom(ln.intersection(below), L)
        P.geom(ln.difference(below), L, "hidden")                             # treads above the cut plane
        n += 1
    xm = S["start"][0]
    tip = yb - 0.13
    P.circle(L, (xm, y0s + 0.12), 0.02)
    P.line(L, (xm, y0s + 0.14), (xm, tip - 0.1))
    tri = [(xm, tip), (xm - 0.04, tip - 0.12), (xm + 0.04, tip - 0.12)]
    P.hatch(L, tri, "SOLID")
    P.pl(L, tri, True)
    P.text(L, (xm + 0.08, ny + 0.03 + (g - 1.8 * MM) / 2 + 0.01), 1.8 * MM, "UP", "left")


def draw_features(P):
    for f in FEATS:
        if f["type"] == "hearth" or (f["type"] == "boxing" and f["z"][0] == 0):      # floor-standing: hearth slab, WC duct
            P.pl("A-FLOR-FIXT", f["polygon"], True)
        elif f["type"] == "arch_vault":                                               # overhead: dashed
            P.geom(Polygon(f["polygon"]).exterior.difference(WALL.buffer(0.005)), "A-FLOR-OVHD", "dashed")


# ------------------------------------------------------------------ fixtures & furniture footprints
FIXT = {"fireplace", "base_unit", "tall_unit", "worktop", "hob", "sink", "sink_belfast", "fridge", "oven_tower", "washer",
        "dryer", "wc", "basin", "radiator", "towel_rail"}                      # -> A-FLOR-FIXT
OVHD = {"wall_unit", "airer", "shelf"}                                         # -> A-FLOR-OVHD, dashed
SKIP = {"stair", "mirror"}                # stairs come from house.json; wall-hung mirrors are not plan items
MERGED = {"base_unit", "wall_unit", "worktop"}                                 # runs: shared edges drawn once
DIRS = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}


def fp(name, sym, x0, y0, x1, y1, front=None):
    r = {"name": name, "room": name.split(".")[0], "plan_sym": sym, "height": 0.0,
         "obb": [[round(v, 4) for v in p] for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]}
    if front:
        r["front"] = list(DIRS[front])
    return r


def fpc(name, sym, cx, cy, w, d, front):
    """Footprint from centre, width across, depth front-to-back and facing vector."""
    L = math.hypot(*front)
    fx, fy = front[0] / L, front[1] / L
    ux, uy = fy, -fx
    obb = [[round(cx + a * ux * w / 2 + b * fx * d / 2, 4), round(cy + a * uy * w / 2 + b * fy * d / 2, 4)]
           for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return {"name": name, "room": name.split(".")[0], "plan_sym": sym, "height": 0.0, "obb": obb, "front": [fx, fy]}


def spec_footprints():
    """FALLBACK ONLY - fitted and loose items transcribed from spec/rooms/*.md (reconciled world metres).
    Used for every room that has no entry in docs/assets/footprints.json; the Blender export replaces it."""
    k = lambda n, sym, x0, y0, x1, y1, f=None: fp("kitchen." + n, sym, 1.25 + x0 / 1000, 5.31 + y0 / 1000,
                                                  1.25 + x1 / 1000, 5.31 + y1 / 1000, f)       # kitchen.md local mm
    F = [  # kitchen 4.2-4.5: hob wall (x 3050), sink wall (y 0), door wall (x 0), bar nook (y 3420..3940)
        k("base.h2", "base_unit", 2450, 1890, 3050, 2508), k("base.h3", "base_unit", 2450, 1690, 3050, 1890),
        k("base.h4", "base_unit", 2450, 890, 3050, 1690), k("base.h5", "base_unit", 2450, 600, 3050, 890),
        k("base.corner", "base_unit", 2450, 0, 3050, 600), k("base.s1_dw", "base_unit", 1850, 0, 2450, 600),
        k("base.s2", "base_unit", 1050, 0, 1850, 600), k("base.s3", "base_unit", 600, 0, 1050, 600),
        k("base.s4", "base_unit", 0, 0, 600, 600),
        k("worktop.sink", "worktop", 0, 0, 3050, 620), k("worktop.hob", "worktop", 2430, 620, 3050, 2538),
        k("hob", "hob", 2485, 915, 3005, 1665, "W"), k("sink", "sink", 1080, 110, 1820, 510, "N"),
        k("wall.w1", "wall_unit", 2730, 1908, 3050, 2508), k("hood", "wall_unit", 2650, 840, 3050, 1740),
        k("wall.w2", "wall_unit", 2730, 320, 3050, 830), k("wall.t6r", "wall_unit", 0, 320, 320, 600),
        *[k(f"wall.t{i}", "wall_unit", a, 0, b, 320) for i, (a, b) in
          enumerate(zip((2730, 2425, 1825, 925, 625, 325, 0), (3050, 2730, 2425, 1825, 925, 625, 325)))],
        k("oven_tower", "oven_tower", 0, 600, 620, 1200, "E"), k("fridge_housing", "tall_unit", 0, 1200, 600, 2230, "E"),
        k("fridge", "fridge", 0, 1259, 716, 2171, "E"),
        k("nook.base1", "base_unit", 120, 3430, 420, 3940), k("nook.base2", "base_unit", 420, 3430, 770, 3940),
        k("nook.base3", "base_unit", 770, 3430, 1370, 3940), k("nook.worktop", "worktop", 120, 3435, 1370, 3940),
        k("nook.shelf", "shelf", 120, 3640, 1370, 3940),
        # utility 4.1-4.7 + reconciled appendix (W-rear items y + 10.51, W-wc items y + 10.26, x + 0.60)
        fp("utility.filler", "base_unit", 0.60, 11.63, 0.69, 12.23), fp("utility.washer", "washer", 0.69, 11.63, 1.29, 12.23, "S"),
        fp("utility.dryer", "dryer", 1.305, 11.63, 1.905, 12.23, "S"), fp("utility.base.sink", "base_unit", 1.91, 11.63, 2.51, 12.23),
        fp("utility.base.corner", "base_unit", 2.51, 11.63, 3.10, 12.23), fp("utility.base.a", "base_unit", 2.50, 11.25, 3.10, 11.63),
        fp("utility.base.b", "base_unit", 2.50, 10.88, 3.10, 11.25), fp("utility.tall", "tall_unit", 2.52, 10.28, 3.10, 10.88, "W"),
        fp("utility.worktop.1", "worktop", 0.60, 11.61, 3.10, 12.23), fp("utility.worktop.2", "worktop", 2.48, 10.88, 3.10, 11.61),
        fp("utility.sink", "sink_belfast", 1.91, 11.61, 2.505, 12.07, "S"),
        *[fp(f"utility.wall.d{i}", "wall_unit", a, 11.90, b, 12.23) for i, (a, b) in
          enumerate(zip((0.64, 0.94, 1.24, 1.74, 2.24), (0.94, 1.24, 1.74, 2.24, 2.56)))],
        fp("utility.airer", "airer", 0.90, 11.36, 2.80, 11.40),
        # wc 4.1-4.3 (x + 0.60, y + 9.36)
        fp("wc.pan", "wc", 2.37, 9.57, 2.90, 9.93, "W"), fp("wc.basin", "basin", 0.60, 9.45, 1.05, 10.05, "E"),
        fp("wc.towel_rail", "towel_rail", 1.60, 9.36, 2.00, 9.46, "N"),
        # dining 4.1, 4.2, 5.1, 5.2 (centre items x - 0.6625, y + 12.36)
        fp("dining.fireplace", "fireplace", 2.68, 13.915, 2.92, 15.305, "W"), fp("dining.tv", "tv", 0.86, 12.36, 2.75, 12.42, "N"),
        fp("dining.table", "table", 0.6875, 13.24, 1.5875, 15.98),
        fpc("dining.chair.s", "chair", 1.1375, 12.99, 0.53, 0.50, (0, 1)), fpc("dining.chair.n", "chair", 1.1375, 16.23, 0.53, 0.50, (0, -1)),
        fpc("dining.chair.w1", "chair", 0.5075, 13.54, 0.53, 0.50, (1, 0)), fpc("dining.chair.w3", "chair", 0.5075, 15.68, 0.53, 0.50, (1, 0)),
        fpc("dining.chair.e1", "chair", 1.7675, 13.54, 0.53, 0.50, (-1, 0)), fpc("dining.chair.e3", "chair", 1.7675, 15.68, 0.53, 0.50, (-1, 0)),
        fpc("dining.armchair.w", "armchair", 0.4575, 14.61, 0.64, 0.56, (1, 0)), fpc("dining.armchair.e", "armchair", 1.8175, 14.61, 0.64, 0.56, (-1, 0)),
        # living 4, 5, 6 (transforms in living.md "Reconciled dimensions")
        fp("living.sofa", "sofa", 3.57, 1.13, 4.27, 2.93, "W"), fp("living.rug", "rug", 1.90, 1.76, 3.30, 3.76),
        fp("living.coffee_table", "coffee_table", 2.49, 2.01, 3.11, 3.61), fp("living.bench", "stool", 2.325, 3.74, 3.475, 4.16),
        fp("living.bookcase", "bookcase", 2.055, 4.37, 3.805, 4.73, "S"), fp("living.tv_unit", "tv_unit", 0.80, 1.33, 1.25, 3.13, "E"),
        fp("living.tv", "tv", 0.80, 1.38, 0.86, 3.27, "E"), fp("living.side_table", "console", 3.89, 2.95, 4.25, 3.41, "W"),
        fp("living.aircon", "radiator", 4.065, 3.43, 4.30, 4.18, "W"), fp("living.plant_stand", "table_round", 3.92, 4.34, 4.24, 4.66),
        fp("living.lamp_table", "table_round", 2.24, 0.06, 2.86, 0.68),
        fpc("living.armchair.w", "armchair", 1.73, 0.55, 0.62, 0.68, (0.35, 1)), fpc("living.armchair.e", "armchair", 3.37, 0.55, 0.62, 0.68, (-0.35, 1)),
        fpc("living.footstool", "stool", 3.05, 1.40, 0.55, 0.45, (0, 1)),
        # hallway 5
        fp("hallway.console", "console", -0.65, 3.70, -0.29, 4.42, "E"),
    ]
    return F


def load_footprints(f):
    spec = spec_footprints()
    data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    if data is None or (isinstance(data, dict) and data.get("standin")):       # the viewer's stand-in file is not an export
        return spec, "spec/rooms/*.md fallback (no exported footprints.json)"
    items = data["items"] if isinstance(data, dict) else data
    exp = [{**r, "room": r.get("room") or str(r.get("name", "")).split(".")[0], "plan_sym": r.get("plan_sym") or r.get("sym"),
            "obb": r.get("obb") or r.get("poly")} for r in items]                # untagged / degenerate records are not plan items
    exp = [r for r in exp if r["plan_sym"] and r["obb"] and len(r["obb"]) == 4 and Polygon(r["obb"]).area > 1e-6]
    if not exp:                                                                 # shell-only export: nothing is "from the model"
        return spec, "spec/rooms/*.md fallback (exported footprints.json is empty)"
    rooms = {r["room"] for r in exp}
    left = sorted({r["room"] for r in spec} - rooms)
    return exp + [r for r in spec if r["room"] not in rooms], f"footprints.json ({len(exp)} items); spec fallback for {left or 'no rooms'}"


def local_frame(r, tables):
    """-> centre, u (across), v (front), width, depth. Front = record's `front`; without it a chair tucked
    under a table faces the table and everything else turns its back to the nearest wall (a guess)."""
    p = r["obb"]
    c = (sum(q[0] for q in p) / 4, sum(q[1] for q in p) / 4)
    cands = []
    for a, b in ((p[0], p[1]), (p[0], p[3])):
        L = math.dist(a, b)
        if L > 1e-9:
            d = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
            cands += [(d, L), ((-d[0], -d[1]), L)]
    f = r.get("front")
    if not f and r["plan_sym"] in ("chair", "armchair", "stool") and tables:      # tucked under a table: face it
        me = Polygon(p)
        t = min(tables, key=me.distance)
        if me.distance(t) < 0.12:
            q = shapely.ops.nearest_points(t, Point(c))[0]
            f = (q.x - c[0], q.y - c[1]) if q.distance(Point(c)) > 1e-6 else (t.centroid.x - c[0], t.centroid.y - c[1])
    if not f:                                                                    # back to the nearest wall (windows count)
        f = min(cands, key=lambda cd: WALL_UNCUT.distance(Point(c[0] - cd[0][0] * cd[1] / 2, c[1] - cd[0][1] * cd[1] / 2)))[0]
    v, d = max(cands, key=lambda cd: cd[0][0] * f[0] + cd[0][1] * f[1])
    w = next(L for dd, L in cands if abs(dd[0] * v[0] + dd[1] * v[1]) < 0.5)
    return c, (v[1], -v[0]), v, w, d


def draw_footprints(P, recs):
    recs = [r for r in recs if r["plan_sym"] not in SKIP]
    tables = [Polygon(r["obb"]) for r in recs if r["plan_sym"] in ("table", "table_round")]
    appliances = [Polygon(r["obb"]).centroid for r in recs if r["plan_sym"] in ("fridge", "oven_tower", "washer", "dryer")]
    for sym in ("base_unit", "worktop", "wall_unit"):            # runs: node the outlines so shared edges are drawn once
        for room in sorted({r["room"] for r in recs}):
            rings = [Polygon(r["obb"]).exterior for r in recs if r["plan_sym"] == sym and r["room"] == room]
            if rings:
                g = linemerge(snap(unary_union(rings)))
                P.geom(g, "A-FLOR-OVHD" if sym in OVHD else "A-FLOR-FIXT", "hidden" if sym in OVHD else None)
    tops = unary_union(tables)
    labs = []
    order = {"rug": 0}                                           # rugs under the furniture standing on them
    for r in sorted(recs, key=lambda r: order.get(r["plan_sym"], 1)):
        sym = r["plan_sym"]
        if sym in MERGED:
            continue
        n0 = len(P.e)
        c, u, v, w, d = local_frame(r, tables)
        hw, hd = w / 2, d / 2
        lay = "A-FLOR-OVHD" if sym in OVHD else "A-FLOR-FIXT" if sym in FIXT else "A-FURN"
        T = lambda a, b: (c[0] + a * u[0] + b * v[0], c[1] + a * u[1] + b * v[1])
        R = lambda a0, b0, a1, b1, ls=None: P.pl(lay, [T(a0, b0), T(a1, b0), T(a1, b1), T(a0, b1)], True, ls)
        Ln = lambda a0, b0, a1, b1, ls=None: P.line(lay, T(a0, b0), T(a1, b1), ls)
        C = lambda a, b, rad: P.circle(lay, T(a, b), rad)
        ell = lambda a, b, ra, rb, t0=0.0, t1=360.0, n=24: [T(a + ra * math.cos(math.radians(t0 + (t1 - t0) * i / n)),
                                                              b + rb * math.sin(math.radians(t0 + (t1 - t0) * i / n))) for i in range(n + 1)]
        rr = lambda a0, b0, a1, b1, rad: P.pl(lay, [T(*q) for q in box(a0, b0, a1, b1).buffer(-rad, join_style=2).buffer(rad, quad_segs=3).exterior.coords], True)
        label = lambda s: (P.text(lay, (c[0], c[1] - 0.75 * MM), 1.5 * MM, s),
                           labs.append(box(c[0] - tw(s, 1.5 * MM) / 2 - 0.5 * MM, c[1] - 1.3 * MM, c[0] + tw(s, 1.5 * MM) / 2 + 0.5 * MM, c[1] + 1.3 * MM)))
        full = lambda ls=None: R(-hw, -hd, hw, hd, ls)
        if sym == "sofa":
            full(); Ln(-hw, -hd + 0.18, hw, -hd + 0.18)
            for s in (-1, 1):
                Ln(s * (hw - 0.18), -hd + 0.18, s * (hw - 0.18), hd)
            if w > 1.4:
                Ln(0, -hd + 0.18, 0, hd)
        elif sym == "armchair":
            full(); Ln(-hw + 0.09, -hd + 0.12, hw - 0.09, -hd + 0.12)
            for s in (-1, 1):
                Ln(s * (hw - 0.09), -hd, s * (hw - 0.09), hd - 0.08)
        elif sym == "chair":
            full(); Ln(-hw, -hd + 0.07, hw, -hd + 0.07)
        elif sym in ("stool", "coffee_table"):
            full(); R(-hw + 0.05, -hd + 0.05, hw - 0.05, hd - 0.05)
        elif sym == "table_round":
            C(0, 0, min(hw, hd))
        elif sym in ("bookcase", "tv_unit"):
            full(); Ln(-hw, hd - 0.04, hw, hd - 0.04)
        elif sym == "rug":
            full("dashed")
        elif sym == "plant":
            rad = min(hw, hd)
            C(0, 0, rad); C(0, 0, rad * 0.35)
            for i in range(8):
                a = math.radians(i * 45 + 22.5)
                Ln(rad * 0.35 * math.cos(a), rad * 0.35 * math.sin(a), rad * math.cos(a), rad * math.sin(a))
        elif sym == "fireplace":
            full(); P.pl(lay, [T(-0.22 * w, hd), T(-0.22 * w, -hd + 0.05), T(0.22 * w, -hd + 0.05), T(0.22 * w, hd)])
        elif sym == "tall_unit":
            full()
            if not any(Polygon(r["obb"]).contains(a) for a in appliances):      # full-height unit: crossed
                Ln(-hw, -hd, hw, hd); Ln(-hw, hd, hw, -hd)
        elif sym == "hob":
            full()
            burners = ([(-0.33 * w, 0, 0.08), (0, -0.24 * d, 0.055), (0, 0.24 * d, 0.045), (0.33 * w, -0.24 * d, 0.055), (0.33 * w, 0.24 * d, 0.045)]
                       if w >= 0.7 else [(sx * 0.22 * w, sy * 0.22 * d, 0.05) for sx in (-1, 1) for sy in (-1, 1)])
            for a, b, rad in burners:
                C(a, b, rad); C(a, b, rad * 0.4)
        elif sym == "sink":
            full()
            n = 2 if w >= 0.7 else 1
            for i in range(n):
                a0, a1 = -hw + i * w / n, -hw + (i + 1) * w / n
                rr(a0 + 0.02, -hd + 0.02, a1 - 0.02, hd - 0.02, 0.04); C((a0 + a1) / 2, 0, 0.022)
        elif sym == "sink_belfast":
            full(); rr(-hw + 0.03, -hd + 0.03, hw - 0.03, hd - 0.03, 0.04); C(0, 0, 0.022)
        elif sym == "fridge":
            full(); Ln(-hw, hd - 0.07, hw, hd - 0.07); Ln(-0.08 * w, hd - 0.07, -0.08 * w, hd); label("FF")
        elif sym == "oven_tower":
            full(); Ln(-hw, hd - 0.04, hw, hd - 0.04); label("OV")
        elif sym in ("washer", "dryer"):
            full(); C(0, 0, 0.37 * min(w, d)); label("WM" if sym == "washer" else "TD")
        elif sym == "wc":
            b1 = -hd + 0.35 * d
            P.pl(lay, [T(-hw, -hd), *ell(0, b1, hw, hd - b1, 180, 0), T(hw, -hd)], True)
            P.pl(lay, ell(0, b1 + 0.08 * d, 0.62 * hw, 0.5 * (hd - b1)), True)
            if d > 0.6:
                Ln(-hw, -hd + 0.18, hw, -hd + 0.18)                              # close-coupled cistern
        elif sym == "basin":
            rr(-hw, -hd, hw, hd, 0.03); P.pl(lay, ell(0, 0.03, 0.72 * hw, 0.58 * hd), True); C(0, -hd + 0.05, 0.02)
        elif sym == "radiator":
            full(); Ln(-hw, 0, hw, 0)
        elif sym == "towel_rail":
            full()
            for i in range(1, int(w / 0.05)):
                Ln(-hw + i * 0.05, -hd, -hw + i * 0.05, hd)
        elif sym == "airer":
            (Ln(-hw, 0, hw, 0, "dashed") if w >= d else Ln(0, -hd, 0, hd, "dashed"))
        elif sym == "shelf":
            full("hidden")
        else:                                                    # table, console, tv and unknown keys: plain outline
            full()
        if sym in ("chair", "armchair", "stool") and not tops.is_empty:
            P.e[n0:] = clip(P.e[n0:], tops)                      # tucked under the table: hidden part not drawn
        elif sym == "rug":                                       # ... nor the rug edge under furniture standing on it
            over = [Polygon(q["obb"]) for q in recs if q["room"] == r["room"] and q["plan_sym"] not in OVHD | MERGED | {"rug"}]
            P.e[n0:] = clip(P.e[n0:], unary_union(over))
    if labs:                                                     # overhead lines give way to the appliance labels
        m = unary_union(labs)
        P.e = [x for e in P.e for x in (clip([e], m) if e["layer"] == "A-FLOR-OVHD" else [e])]


def mask_under_text(P, boxes):
    """Break furniture/fixture linework where it would run under a room tag (CAD text-mask look)."""
    m = unary_union([box(*b) for b in boxes])
    soft = ("A-FURN", "A-FLOR-FIXT", "A-FLOR-OVHD")
    P.e = [x for e in P.e for x in (clip([e], m) if e["layer"] in soft else [e])]


def clip(ents, m):
    """Cut line / polyline / circle / arc entities where they run inside polygon m; the rest pass through."""
    out = []
    for e in ents:
        if e["type"] not in ("line", "polyline", "circle", "arc"):
            out.append(e)
            continue
        if e["type"] == "line":
            pts = [e["p1"], e["p2"]]
        elif e["type"] == "polyline":
            pts = e["pts"] + ([e["pts"][0]] if e["closed"] else [])
        else:
            a0, a1 = (0, 360) if e["type"] == "circle" else (e["a0"], e["a1"] + (360 if e["a1"] < e["a0"] else 0))
            pts = [(e["c"][0] + e["r"] * math.cos(math.radians(a0 + (a1 - a0) * i / 48)),
                    e["c"][1] + e["r"] * math.sin(math.radians(a0 + (a1 - a0) * i / 48))) for i in range(49)]
        g = LineString(pts)
        if not g.intersects(m):
            out.append(e)
            continue
        g = g.difference(m)
        for part in getattr(g, "geoms", [g]):
            if part.geom_type == "LineString" and part.length > 1e-4:
                d = {"layer": e["layer"], "type": "polyline", "pts": [list(q) for q in part.coords], "closed": False}
                if e.get("ls"):
                    d["ls"] = e["ls"]
                out.append(d)
    return out


# ------------------------------------------------------------------ annotation
def chain(P, axis, coords, base, line_at):
    """Dimension chain along x (points (c, base)) or y (points (base, c)); `base` may be f(c0, c1).
    A value too wide to sit between its own extension lines (wall thicknesses) moves to the far side of the
    dimension line, where no extension lines run; at the two ends of a chain it also moves outside the chain."""
    n = len(coords) - 1
    for i, (c0, c1) in enumerate(zip(coords, coords[1:])):
        b = base(c0, c1) if callable(base) else base
        p1, p2 = ((c0, b), (c1, b)) if axis == "x" else ((b, c0), (b, c1))
        off = (line_at - b) if axis == "x" else (b - line_at)
        half = tw(str(round((c1 - c0) * 1000)), T_DIM) / 2
        tp = None
        if 2 * half + 1.0 * MM > c1 - c0:
            end = n > 1 and i in (0, n - 1)
            away = 1 if line_at > b else -1
            std_side = away == (1 if axis == "x" else -1)         # values normally sit above / left of the line
            perp = line_at + away * (0.7 * T_DIM / CAP if end and std_side else DIMSTYLE["extBeyond"] + 1.0 * MM + T_DIM / 2)
            along = (c0 + c1) / 2 if not end else c0 - half - 0.8 * MM if i == 0 else c1 + half + 0.8 * MM
            tp = (along, perp) if axis == "x" else (perp, along)
        P.dim(p1, p2, off, tp)


def draw_dims(P):
    bb = {k: p.bounds for k, p in RPOLY.items()}                 # (minx, miny, maxx, maxy) of each room
    face = lambda wid, sgn, i: WALLS[wid]["a"][i] + sgn * WALLS[wid]["thickness"] / 2
    x0, y0, x1, y1 = B["minX"], B["minY"], B["maxX"], B["maxY"]
    r1, r2, g = 9 * MM, 17 * MM, DIMSTYLE["extGap"]
    liv_front = bb["living"][3] - ROOMS["living"]["size"][1]     # main room front line (bay projects beyond)
    kit_n = bb["kitchen"][1] + ROOMS["kitchen"]["size"][1]
    step_y = face("w_kitchen_n_ext", 1, 1)                       # rear face of the main block (side return begins)
    rear_x = face("w_flank_dining", 1, 0)                        # outer face of the rear wing
    # west: vestibule / hallway / dining, + overall
    chain(P, "y", [y0, bb["vestibule"][1], bb["vestibule"][3], bb["hallway"][1], bb["hallway"][3], bb["dining"][1], bb["dining"][3], y1], x0, x0 - r1)
    chain(P, "y", [y0, y1], x0 - r1, x0 - r2)                    # 2nd rows spring from the 1st row's line
    # east: bay / living / cross wall / kitchen / wc / utility / dining, + main block and rear wing lengths
    ys = [y0, bb["living"][1], liv_front, bb["living"][3], bb["kitchen"][1], kit_n, bb["wc"][1], bb["wc"][3],
          bb["utility"][1], bb["utility"][3], bb["dining"][1], bb["dining"][3], y1]
    chain(P, "y", ys, lambda a, b: x1 if b <= bb["wc"][1] + 1e-6 else rear_x, x1 + r1)
    chain(P, "y", [y0, step_y, y1], x1 + r1, x1 + r2)
    # front: party wall / hall / partition / living / party wall, + overall width.  rear: dining wing
    chain(P, "x", [x0, bb["vestibule"][0], bb["vestibule"][0] + ROOMS["vestibule"]["size"][0], bb["living"][0], bb["living"][2], x1], y0, y0 - r1)
    chain(P, "x", [x0, x1], y0 - r1, y0 - r2)
    chain(P, "x", [x0, bb["dining"][0], bb["dining"][2], rear_x], y1, y1 + 15 * MM)
    # the bay stands forward of the east party wall: carry those extension lines back to the object
    nib_s, cheek_e = face("w_front_nib_e", -1, 1), face("w_bay_cheek_e", 1, 0)
    P.line("A-ANNO-DIMS", (x1, nib_s - g), (x1, y0 - g))
    for y in ys[:2]:
        P.line("A-ANNO-DIMS", (cheek_e + g, y), (x1 + g, y))


def draw_tags(P):
    rooms, boxes = [], []
    for rid, r in ROOMS.items():
        poly = RPOLY[rid]
        at = TAG_AT.get(rid) or tuple(poly.representative_point().coords[0])
        rooms.append({"id": rid, "name": r["name"], "polygon": r["polygon"], "label": list(at), "area": round(poly.area, 2)})
        if not TAG[rid]:
            continue
        lines = [(TAG[rid], T_NAME), ("%d x %d" % (round(r["size"][0] * 1000), round(r["size"][1] * 1000)), T_SUB), ("%.1f m²" % poly.area, T_SUB)]
        gap = 1.3 * MM
        y = top = at[1] + (sum(h for _, h in lines) + gap * (len(lines) - 1)) / 2
        for s, h in lines:
            y -= h
            P.text("A-ANNO-TEXT", (at[0], y), h, s)
            y -= gap
        hw = max(tw(s, h) for s, h in lines) / 2 + 0.6 * MM
        boxes.append((at[0] - hw, y + gap - 0.6 * MM, at[0] + hw, top + 0.6 * MM))
    return rooms, boxes


def draw_notes(P):
    L = "A-ANNO-TEXT"
    cx = (B["minX"] + B["maxX"]) / 2
    P.text(L, (cx, B["maxY"] + 21.2 * MM), T_NOTE, "REAR (GARDEN)")
    P.text(L, (cx, B["minY"] - 22.5 * MM), T_NOTE, "FRONT (STREET)")
    yard = next((Polygon(f["polygon"]) for f in FEATS if f["type"] == "outside_yard"), None)
    if yard:
        P.text(L, (yard.centroid.x + T_SUB / 2, RPOLY["dining"].centroid.y), T_SUB, "SIDE RETURN (NOT SURVEYED)", "center", 90)
    x, y = -0.10, 10.0                                            # datum mark, rear corridor: no level changes on this floor
    P.pl(L, [(x - 0.05, y + 0.09), (x + 0.05, y + 0.09), (x, y)], True)
    P.line(L, (x - 0.14, y), (x + 0.14, y))
    P.text(L, (x, y - 0.06 - T_SUB), T_SUB, "FFL ±0.000")


def draw_sheet(P, src, date):
    L, LB, m = "A-ANNO-TTLB", "A-ANNO-TTLB-BORD", 10 * MM
    bx0, by0, bx1, by1 = SX0 + m, SY0 + m, SX1 - m, SY1 - m
    P.rect(LB, bx0, by0, bx1, by1)
    tx0 = bx1 - 100 * MM
    # title block, 100 x 44 mm: rows of (height mm, [(width mm, caption, value, value height mm)])
    rows = [(14, [(100, "DRAWING TITLE", "GROUND FLOOR PLAN", 4.5)]),
            (8, [(100, "PROJECT", "PRIVATE HOUSE - AS EXISTING - 3D MODEL", 2.5)]),
            (8, [(30, "SCALE", "1:%d @ A3" % SCALE, 2.5), (28, "DRAWING No.", "GA-001", 2.5), (14, "REV", "A", 2.5), (28, "DATE", date, 2.5)]),
            (7, [(100, "SOURCE", "DRAWN FROM VIDEO WALKTHROUGH - NOT A MEASURED SURVEY", 2.0)]),
            (7, [(30, "UNITS", "MILLIMETRES", 2.0), (42, "LEVELS", "FFL ±0.000 THROUGHOUT", 2.0), (28, "SHEET", "1 OF 1", 2.0)])]
    y = by0 + sum(h for h, _ in rows) * MM
    P.pl(L, [(tx0, by0), (tx0, y), (bx1, y)])
    for h, cells in rows:
        y -= h * MM
        if y > by0 + 1e-9:
            P.line(L, (tx0, y), (bx1, y))
        x = tx0
        for i, (w, cap, val, vh) in enumerate(cells):
            if i:
                P.line(L, (x, y), (x, y + h * MM))
            P.text(L, (x + 1.2 * MM, y + (h - 2.4) * MM), 1.2 * MM, cap, "left")
            P.text(L, (x + 1.5 * MM, y + 1.5 * MM), vh * MM, val, "left")
            x += w * MM
    # scale bar: first metre halved, alternate blocks filled
    sy, bh = by0 + 44 * MM + 9 * MM, 1.5 * MM
    P.rect(L, tx0, sy, tx0 + 4.0, sy + bh)
    for a, b in ((0, 0.5), (1, 2), (3, 4)):
        P.hatch(L, [(tx0 + a, sy), (tx0 + b, sy), (tx0 + b, sy + bh), (tx0 + a, sy + bh)], "SOLID")
    for v in (0, 0.5, 1, 2, 3, 4):
        P.line(L, (tx0 + v, sy), (tx0 + v, sy + bh + 0.8 * MM))
        P.text(L, (tx0 + v, sy + bh + 1.6 * MM), 1.8 * MM, ("%g" % v) + (" m" if v == 4 else ""), "center")
    P.text(L, (tx0, sy - 3.4 * MM), 1.8 * MM, "SCALE 1:%d AT A3" % SCALE, "left")
    # notes + line key, top of the title column
    notes = ["NOTES", "",
             "1. ALL DIMENSIONS IN MILLIMETRES.",
             "2. PLAN RECONSTRUCTED FROM A VIDEO WALKTHROUGH.",
             "   DIMENSIONS ARE ESTIMATES: DO NOT SCALE FOR",
             "   CONSTRUCTION, VERIFY ON SITE.",
             "3. ROOM SIZES ARE BETWEEN FINISHED WALL FACES;",
             "   AREAS ARE NET INTERNAL FLOOR AREAS.",
             "4. PLAN CUT 1200 ABOVE FFL.",
             "5. ALL FLOORS FLUSH AT FFL ±0.000, NO STEPS.",
             "6. DOORS SHOWN OPEN AT 90 DEG WITH SWING.",
             "7. FIXTURES AND FURNITURE: " + src,
             "8. SIDE RETURN AND UPPER FLOORS NOT SURVEYED.", "",
             "ABBREVIATIONS", "",
             "FF  FRIDGE-FREEZER      OV  OVEN TOWER",
             "WM  WASHING MACHINE     TD  TUMBLE DRYER",
             "FFL FINISHED FLOOR LEVEL", "",
             "KEY", ""]
    y = by1 - 8 * MM
    for s in notes:
        if s:
            P.text(L if s in ("NOTES", "ABBREVIATIONS", "KEY") else "A-ANNO-TEXT", (tx0, y), 2.0 * MM, s, "left")
        y -= (4.0 if s else 1.5) * MM
    for lay, ls, s in (("A-WALL", None, "WALL, CUT (HATCHED)"), ("A-FLOR-FIXT", None, "FIXED FITTINGS"), ("A-FURN", None, "LOOSE FURNITURE"),
                       ("A-FLOR-OVHD", "dashed", "OVERHEAD: ARCH, VAULT, CLOTHES RAIL"), ("A-FLOR-OVHD", "hidden", "OVERHEAD: WALL UNITS, SHELVES"),
                       ("A-STRS", "hidden", "HIDDEN / ABOVE CUT: TREADS, POCKET DOOR")):
        P.line(lay, (tx0, y + 1.0 * MM), (tx0 + 14 * MM, y + 1.0 * MM), ls)
        P.text("A-ANNO-TEXT", (tx0 + 17 * MM, y), 2.0 * MM, s, "left")
        y -= 4.0 * MM


# ------------------------------------------------------------------ assemble + writers
def rnd(o):
    if isinstance(o, float):
        return round(o, 4)
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [rnd(v) for v in o]
    return o


def build(footprints=OUT / "footprints.json"):
    P = Plan()
    recs, src = load_footprints(Path(footprints))
    for poly in getattr(WALL, "geoms", [WALL]):                 # poche first, linework over it
        for piece in split_holes(poly):
            P.hatch("A-WALL-PATT", list(piece.exterior.coords)[:-1], "ANSI31")
    draw_footprints(P, recs)
    draw_features(P)
    draw_stairs(P)
    draw_openings(P)
    P.geom(WALL, "A-WALL")
    rooms, boxes = draw_tags(P)
    mask_under_text(P, boxes)
    draw_notes(P)
    draw_dims(P)
    date = datetime.date.fromtimestamp((ROOT / "spec" / "house.json").stat().st_mtime).isoformat()
    draw_sheet(P, "FROM 3D MODEL EXPORT." if "footprints.json (" in src else "FROM ROOM SPECS, INDICATIVE.", date)
    return rnd({
        "units": "m",
        "bounds": {"minX": B["minX"] - 22 * MM, "minY": B["minY"] - 25 * MM, "maxX": B["maxX"] + 21 * MM, "maxY": B["maxY"] + 25 * MM},
        "houseBounds": B,
        "sheetBounds": {"minX": SX0, "minY": SY0, "maxX": SX1, "maxY": SY1},
        "layers": [{"name": n, "color": c, "paper": p, "aci": a, "lineweight": lw} for n, c, p, a, lw in LAYERS],
        "linestyles": LINESTYLES,                               # dash, gap, ... in metres
        "hatch": {"ANSI31": "45 deg lines through the origin", "spacing": HATCH_SPACING},
        "dimstyle": DIMSTYLE,                                   # layout rules: tools/plan/render.py dim_geometry()
        "textNote": "text: h = font size (em) in metres, capitals are 0.72 h; p = anchor at the vertical middle of the "
                    "capitals (canvas textBaseline 'middle'), align = horizontal anchor, rot = deg CCW. dim: h likewise, "
                    "optional tp = text middle when lifted off its default place.",
        "footprintSource": src.replace(str(ROOT), "."),
        "entities": P.e,
        "rooms": rooms,
        "sheet": {"title": "GROUND FLOOR PLAN", "scale": "1:%d" % SCALE, "paper": "A3",
                  "orientation": "portrait" if SHEET_H > SHEET_W else "landscape"},
    })


def write_json(plan, path):
    s = json.dumps(plan, ensure_ascii=False, separators=(",", ":"))
    path.write_text(s.replace('},{"layer"', '},\n{"layer"').replace('"entities":[', '"entities":[\n'), encoding="utf-8")


def write_dxf(plan, path):
    """Real CAD entities in millimetres at true scale: LWPOLYLINE/LINE/ARC/CIRCLE/HATCH/TEXT/DIMENSION on named layers."""
    import ezdxf
    from ezdxf.enums import TextEntityAlignment as TA
    from render import dim_geometry
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    doc.header["$MEASUREMENT"], doc.header["$LTSCALE"], doc.header["$LUNITS"], doc.header["$LUPREC"] = 1, 1.0, 2, 0
    for name, pat in plan["linestyles"].items():               # dash, -gap, ... in mm, true length at LTSCALE 1
        mmpat = [v * 1000 * (1 if i % 2 == 0 else -1) for i, v in enumerate(pat)]
        doc.linetypes.add(name.upper(), pattern=[sum(abs(v) for v in mmpat), *mmpat], description=name)
    doc.styles.add("ISO", font="isocp.shx")
    for l in plan["layers"]:
        doc.layers.add(l["name"], color=l["aci"], lineweight=round(l["lineweight"] * 100))
    st = plan["dimstyle"]
    ds = doc.dimstyles.new("PLAN", dxfattribs={
        "dimtxsty": "ISO", "dimtxt": st["h"] * CAP * 1000, "dimtsz": st["tick"] * 1000, "dimasz": st["tick"] * 1000,
        "dimexo": st["extGap"] * 1000, "dimexe": st["extBeyond"] * 1000, "dimgap": st["h"] * (0.7 - CAP / 2) * 1000,
        "dimtad": 1, "dimtih": 0, "dimtoh": 0, "dimdec": 0, "dimlunit": 2, "dimzin": 8, "dimscale": 1.0, "dimlfac": 1.0,
        "dimclrd": 256, "dimclre": 256, "dimclrt": 256})
    msp = doc.modelspace()
    K = lambda p: (p[0] * 1000, p[1] * 1000)
    for e in plan["entities"]:
        at = {"layer": e["layer"]}
        if e.get("ls"):
            at["linetype"] = e["ls"].upper()
        t = e["type"]
        if t == "line":
            msp.add_line(K(e["p1"]), K(e["p2"]), dxfattribs=at)
        elif t == "polyline":
            msp.add_lwpolyline([K(p) for p in e["pts"]], close=e["closed"], dxfattribs=at)
        elif t == "arc":
            msp.add_arc(K(e["c"]), e["r"] * 1000, e["a0"], e["a1"], dxfattribs=at)
        elif t == "circle":
            msp.add_circle(K(e["c"]), e["r"] * 1000, dxfattribs=at)
        elif t == "hatch":
            h = msp.add_hatch(color=256, dxfattribs=at)
            if e["pattern"] == "SOLID":
                h.set_solid_fill(color=256)
            else:                                               # ISO ANSI31 is 3.175 mm apart at scale 1
                h.set_pattern_fill(e["pattern"], color=256, scale=plan["hatch"]["spacing"] * 1000 / 3.175)
            h.paths.add_polyline_path([K(p) for p in e["pts"]], is_closed=True)
        elif t == "text" and e.get("of") != "dim":
            tx = msp.add_text(e["text"], height=e["h"] * CAP * 1000, dxfattribs={**at, "style": "ISO", "rotation": e.get("rot", 0)})
            tx.set_placement(K(e["p"]), align={"left": TA.MIDDLE_LEFT, "center": TA.MIDDLE_CENTER, "right": TA.MIDDLE_RIGHT}[e.get("align", "left")])
        elif t == "dim":
            segs, tp, rot = dim_geometry(e, st)
            loc = K(tp) if e.get("tp") else None                # lifted text: give its mid point explicitly
            ang = math.degrees(math.atan2(e["p2"][1] - e["p1"][1], e["p2"][0] - e["p1"][0]))
            msp.add_linear_dim(base=K(segs[0][0]), p1=K(e["p1"]), p2=K(e["p2"]), angle=ang, location=loc,
                               dimstyle="PLAN", dxfattribs=at).render()
    doc.set_modelspace_vport(height=(plan["sheetBounds"]["maxY"] - plan["sheetBounds"]["minY"]) * 1000,
                             center=K(((plan["sheetBounds"]["minX"] + plan["sheetBounds"]["maxX"]) / 2,
                                       (plan["sheetBounds"]["minY"] + plan["sheetBounds"]["maxY"]) / 2)))
    aud = doc.audit()
    assert not aud.errors, [str(x) for x in aud.errors]
    doc.saveas(path)


def self_check(plan):
    """Cheap invariants; the visual check is tools/plan/check.py."""
    layers = {l["name"] for l in plan["layers"]}
    E = plan["entities"]
    assert all(e["layer"] in layers for e in E)
    for e in E:
        if e["type"] == "dim":
            assert int(e.get("value") or e["text"]) == round(math.dist(e["p1"], e["p2"]) * 1000), e
    rows = {}                                                   # chain rows keyed by where their dimension line runs
    for e in E:
        if e["type"] == "dim":
            horiz = abs(e["p1"][1] - e["p2"][1]) < 1e-9
            key = ("x", round(e["p1"][1] + e["offset"], 3)) if horiz else ("y", round(e["p1"][0] - e["offset"], 3))
            rows[key] = rows.get(key, 0) + int(e.get("value") or e["text"])
    tot_x, tot_y = round((B["maxX"] - B["minX"]) * 1000), round((B["maxY"] - B["minY"]) * 1000)
    assert all(v == tot_y for (a, _), v in rows.items() if a == "y"), rows       # all four Y rows close on the overall length
    assert sum(v == tot_x for (a, _), v in rows.items() if a == "x") == 2, rows  # front room chain + front overall
    hatched = sum(Polygon(e["pts"]).area for e in E if e["layer"] == "A-WALL-PATT")
    assert abs(hatched - WALL.area) < 1e-3, (hatched, WALL.area)
    leaves = sum({"both": 2}.get(o["hinge"], 1) for o in H["openings"] if o["type"] in ("door", "double_door", "french_door") and o["hinge"] != "none")
    assert sum(e["type"] == "arc" and e["layer"] == "A-DOOR" for e in E) == leaves
    assert len(plan["rooms"]) == len(ROOMS)
    assert plan["sheetBounds"]["minY"] + 10 * MM <= plan["bounds"]["minY"] and plan["bounds"]["maxY"] <= plan["sheetBounds"]["maxY"] - 10 * MM


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    from render import render
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--footprints", default=str(OUT / "footprints.json"), help="exported footprints (default docs/assets/footprints.json)")
    ap.add_argument("--out", default=str(OUT), help="output directory (default docs/assets)")
    a = ap.parse_args()
    plan = build(a.footprints)
    self_check(plan)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write_json(plan, out / "plan.json")
    write_dxf(plan, out / "ground-floor-plan.dxf")
    render(plan, out / "ground-floor-plan.pdf", "paper")
    n = {}
    for e in plan["entities"]:
        n[e["type"]] = n.get(e["type"], 0) + 1
    print("PLAN OK  scale 1:%d on A3 %s  entities %s  footprints: %s" % (SCALE, plan["sheet"]["orientation"], n, plan["footprintSource"]))
