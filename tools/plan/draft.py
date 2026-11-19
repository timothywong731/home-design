"""CAD plan drafter: house.json (schema 2) + footprints.json -> plan.json (schema 2), house-plans.dxf, house-plans.pdf.

    python tools/plan/draft.py [--house PATH] [--footprints FILE] [--out DIR]
        # defaults: spec/house.json, docs/assets/footprints.json, docs/assets
    python tools/plan/check.py [--assets DIR]     # audits every sheet, rasterises them into build/plan/

Sheets B, G, 1, 2 at 1:50 and the site plan X at 1:100, all A3 and all in world coordinates (blender/MULTILEVEL.md
11.1). One entity list per sheet (world metres, +Y = rear = up the sheet) feeds plan.json, the DXF (every sheet side
by side in one model space) and the PDF (one A3 page per sheet), so the on-screen plan, the downloads and the model
cannot drift. Spec geometry (chamfers, stair treads, zone falls, opening frames) comes from blender/lib/ctx.py, which
imports without Blender. Needs shapely, ezdxf, matplotlib.

Footprints: [{name, room, plan_sym, obb: [[x, y] x 4], level?, front?}]. A record without `level` takes its room's
(pseudo-rooms and building rooms X, unknown rooms G). A room with at least one exported footprint is drawn only from
the export; other rooms fall back to SPEC_FOOTPRINTS (the phase-1 rooms, transcribed from spec/rooms/*.md) or, on the
site, to exterior.features (cars, fire pit, planters, trellis, bins); rooms with neither stay empty.
"""
import argparse, datetime, json, math, sys
from pathlib import Path
import shapely
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union, linemerge, polylabel

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets"
sys.path.insert(0, str(ROOT / "blender"))
sys.path.insert(0, str(Path(__file__).parent))
from lib import ctx as C                                                        # noqa: E402  (pure data without bpy)

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
    ("A-ROOF", "#a0a0a0", "#444444", 8, 0.18),
    ("L-SITE", "#00c000", "#000000", 3, 0.13),
    ("L-SITE-BNDY", "#ff3030", "#000000", 1, 0.25),
    ("A-ANNO-DIMS", "#ff0000", "#000000", 1, 0.13),
    ("A-ANNO-TEXT", "#ffffff", "#000000", 7, 0.18),
    ("A-ANNO-TTLB", "#ffffff", "#000000", 7, 0.35),
    ("A-ANNO-TTLB-BORD", "#ffffff", "#000000", 7, 0.70),
]
DASHED_LAYERS = {"L-SITE-BNDY"}           # DXF layer linetype DASHED; every entity on it also carries ls "dashed"
# id, title, scale, drawing number. PDF page order = this order.
SHEETS = [("B", "BASEMENT PLAN", 50, "GA-000"), ("G", "GROUND FLOOR PLAN", 50, "GA-001"),
          ("1", "FIRST FLOOR PLAN", 50, "GA-002"), ("2", "SECOND FLOOR (LOFT) PLAN", 50, "GA-003"),
          ("X", "SITE PLAN", 100, "GA-004")]
DXF_PITCH = 40000                         # DXF mm between the origins of consecutive sheets in model space
A3 = (297.0, 420.0)
TAG = {"vestibule": "VESTIBULE", "hallway": "HALLWAY", "living": "LIVING ROOM", "kitchen": "KITCHEN", "wc": "WC",
       "utility": "UTILITY", "dining": "DINING ROOM", "basement": "BASEMENT", "landing1_front": "LANDING",
       "landing1_rear": "LANDING", "landing2_head": "LANDING", "bathroom2": "BATHROOM", "eaves_front": "EAVES",
       "eaves_rear": "EAVES", "blue_ensuite": "EN-SUITE", "shed_workshop": "WORKSHOP", "shed_store": "STORE"}
NO_TAG = {"landing1_ql", "landing2_platform"}           # too small for a tag: FFL datum mark only (stairwells: nothing)
TAG_AT = {"vestibule": (0.0, 1.02), "hallway": (0.0, 3.1), "living": (2.0, 1.42), "kitchen": (2.83, 7.3),
          "wc": (1.72, 9.82), "utility": (1.95, 11.05), "dining": (2.33, 12.86),
          "balcony": (2.95, 17.9),                    # beside it: the French door leaves fill the deck
          "landing1_ql": (0.6, 8.6), "landing2_platform": (-0.25, 7.75)}   # else the pole of inaccessibility
SURF = {"concrete_setts_grey_buff": "CONCRETE SETTS", "concrete_flags": "CONCRETE FLAGS", "asphalt": "ASPHALT",
        "concrete_or_flags": "CONCRETE", "sandstone_flags_grey": "SANDSTONE FLAGS", "grass": "GRASS",
        "composite_deck_dark_brown": "COMPOSITE DECK", "timber_box_dark": "TIMBER STEP", "soil_lavender": "PLANTED",
        "clay_block_paving_red_herringbone": "CLAY PAVERS"}
ZONE_NAME = {"forecourt_alley_mouth": None, "deck_step_n": None, "deck_step_e": None, "road": None,
             "shed_veranda": "VERANDA"}                # None: level only (small or mostly outside the window)
CHAR_W = 0.826          # advance / cap height of the reference monospace face (DejaVu Sans Mono)
CAP = 0.72              # cap height / font size (em): plan.json text h is the font size, DXF TEXT height = CAP * h
CUT = 1.2               # plan cut above each room's own floor


def tw(s, h):
    return len(s) * CHAR_W * h


def ffl(z):
    return "FFL ±0.000" if abs(z) < 5e-4 else "FFL %+.3f" % z


def lvl(z):
    return "±0.000" if abs(z) < 5e-4 else "%+.3f" % z


def set_scale(scale):
    """Paper-derived drafting sizes in model metres for one sheet scale (module globals, one sheet at a time)."""
    global SCALE, MM, T_DIM, T_NAME, T_SUB, T_NOTE, DIMSTYLE, HATCH_SPACING, LINESTYLES
    SCALE, MM = scale, scale / 1000.0                      # model metres per paper millimetre
    T_DIM, T_NAME, T_SUB, T_NOTE = 2.5 * MM, 2.5 * MM, 1.8 * MM, 3.0 * MM
    # dim rules shared with docs/js/plan2d.js: ext lines start extGap off the point and pass the line by extBeyond,
    # 45-degree ticks, text (font size h) centred 0.7 h above the line.
    DIMSTYLE = {"h": T_DIM / CAP, "tick": 1.3 * MM, "extGap": 1.2 * MM, "extBeyond": 1.6 * MM}
    HATCH_SPACING = 1.8 * MM
    LINESTYLES = {"dashed": [2.4 * MM, 1.2 * MM], "hidden": [1.2 * MM, 0.8 * MM], "center": [6 * MM, 1.2 * MM, 1.2 * MM, 1.2 * MM]}


class Plan:
    def __init__(self):
        self.e = []

    def add(self, layer, typ, ls=None, **kw):
        d = {"layer": layer, "type": typ, **kw}
        if ls or layer in DASHED_LAYERS:
            d["ls"] = ls or "dashed"
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
        self.e.append({"layer": layer, "type": "hatch", "pts": [list(p) for p in pts], "pattern": pattern})

    def text(self, layer, p, h, s, align="center", rot=0):
        """Drafted like CAD text (p = baseline point, h = cap height); stored the way the web viewer draws
        text: p = vertical middle of the capitals, h = font size (em), capitals = CAP x h."""
        r = math.radians(rot)
        self.e.append({"layer": layer, "type": "text", "p": [p[0] - math.sin(r) * h / 2, p[1] + math.cos(r) * h / 2],
                       "h": h / CAP, "text": s, "align": align, "rot": rot})

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
        """Emit shapely linework / polygon boundaries as polylines (points are dropped)."""
        if g.is_empty or g.geom_type in ("Point", "MultiPoint"):
            return
        if g.geom_type == "Polygon":
            for ring in [g.exterior, *g.interiors]:
                self.pl(layer, list(ring.coords), True, ls)
        elif g.geom_type in ("LineString", "LinearRing"):
            c = list(g.coords)
            self.pl(layer, c, c[0] == c[-1] and len(c) > 3, ls)
        else:
            for part in g.geoms:
                self.geom(part, layer, ls)

    def arrowhead(self, layer, tip, d, L=0.12, w=0.04):
        """Filled CAD arrowhead at tip pointing along unit d (L, w in model metres)."""
        tri = [tip, (tip[0] - d[0] * L - d[1] * w, tip[1] - d[1] * L + d[0] * w),
               (tip[0] - d[0] * L + d[1] * w, tip[1] - d[1] * L - d[0] * w)]
        self.hatch(layer, tri, "SOLID")
        self.pl(layer, tri, True)


# ------------------------------------------------------------------ spec access (set by setup())
def setup(path):
    global HC, H, ROOMS, WALLS, OPEN, FEATS, EXT
    HC = C.House.load(path)
    if HC.schema != 2:
        raise SystemExit(f"{path}: schema-1 house.json; this drafter needs schema 'house/2' "
                         "(spec/house.json is schema 2 since the phase-2 adoption)")
    H, ROOMS, WALLS, OPEN, FEATS, EXT = HC.spec, HC.rooms, HC.walls, HC.openings, HC.features, HC.spec["exterior"]


def rpoly(rid):
    return Polygon(HC.room_poly(rid))


def room_name(rid):
    if rid in TAG:
        return TAG[rid]
    r = ROOMS.get(rid) or HC.building_rooms[rid]
    return r["name"].split("(")[0].strip().upper()


def unit(a, b):
    L = math.dist(a, b)
    return ((b[0] - a[0]) / L, (b[1] - a[1]) / L)


def mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def parts(g):
    return [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and not p.is_empty]


# ------------------------------------------------------------------ wall frames (as spec/validate_house2.py)
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


def end_ext(w, end, ws):
    """Half-thickness of the thickest perpendicular wall of `ws` through this end, so corners fill."""
    _, _, ux, uy, _ = frame(w)
    e = 0.0
    for o in ws:
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
        for p in parts(poly.intersection(half)):
            if p.area > 1e-6:
                out += split_holes(p)
    return out


def opening_span(oid):
    o = OPEN[oid]
    w = WALLS[o["wall"]]
    s = along_perp(w, o["center"])[0]
    return w, s - o["width"] / 2, s + o["width"] / 2


# ------------------------------------------------------------------ cut plan geometry of one level
def envelope(L):
    return unary_union([Polygon(l["polygon"]) for b in EXT["envelope"]["blocks"] for l in b["levels"] if l["level"] == L])


def at_cut(f, L):
    """Feature f spans the plan cut (CUT above the floor of its room, else of its level's datum)."""
    z = f.get("z")
    if not isinstance(z, list):
        return True
    base = HC.floor_z(f["room"]) if f.get("room") in ROOMS else HC.level_info[L]["datumZ"]
    return z[0] <= base + CUT < z[1]


def room_cut(rid):
    """Room polygon at the cut plane: a bay arris splay (45 degrees below its stop) adds its corner triangle p, v, q."""
    tris = [Polygon([c["p"], c["v"], c["q"]]) for c in HC.chamfers(rid)
            if c["reflex"] and c["z"][0] <= HC.floor_z(rid) + CUT < c["z"][1]]
    return unary_union([rpoly(rid)] + tris)


SOLID_TYPES = ("pier", "pilaster", "chimney_breast", "nib", "poche", "boxing")


def poche(L):
    """MULTILEVEL 11.1: envelope of L minus every room of L minus floor voids (and carved recesses / reveals), plus
    inner walls and solid features at the cut, cut at the openings of L. -> (cut poche, uncut mass)."""
    F = [f for f in FEATS if f.get("level") == L]
    rooms = [room_cut(r) for r in HC.rooms_on(L)]
    voids = [Polygon(f["polygon"]) for f in F if f["type"] == "floor_void"]
    carve = [Polygon(f["polygon"]) for f in F if f["type"] in ("recess", "reveal") and at_cut(f, L)]
    solid = [Polygon(f["polygon"]) for f in F if f["type"] in SOLID_TYPES and at_cut(f, L)]
    inner = [wquad(w, 0, frame(w)[4]) for w in WALLS.values()
             if w.get("level") == L and not w.get("building") and not w.get("virtual") and w["rooms"][0] == w["rooms"][1]]
    mass = envelope(L).difference(unary_union(rooms + voids + carve)).union(unary_union(solid + inner))
    cuts = []
    for oid, o in OPEN.items():
        if o.get("level") == L and not o.get("building") and not WALLS[o["wall"]].get("virtual"):
            w, s0, s1 = opening_span(oid)
            cuts.append(wquad(w, s0, s1, 0.05))
    return snap(mass.difference(unary_union(cuts))).simplify(0.0005), mass


def shed_poche():
    ws = [w for w in WALLS.values() if w.get("building")]
    solid = unary_union([wquad(w, -end_ext(w, "a", ws), frame(w)[4] + end_ext(w, "b", ws)) for w in ws])
    cuts = [wquad(*opening_span(oid), 0.02) for oid, o in OPEN.items() if o.get("building")]
    return snap(solid.difference(unary_union(cuts))).simplify(0.0005), solid


def roof_regions():
    """{plane id: part of the plane that is the roof surface}: each plane minus where another plane is higher (the
    upper envelope; the spec's plane polygons overlap at the valleys)."""
    planes = H["roof"]["planes"]
    big = [(-100, -100), (100, -100), (100, 100), (-100, 100)]
    out = {}
    for p in planes:
        g = Polygon(p["polygon"])
        for q in planes:
            if q is p:
                continue
            a = q["z"]["c0"] - p["z"]["c0"]
            b, c = q["z"]["cx"] - p["z"]["cx"], q["z"]["cy"] - p["z"]["cy"]
            if abs(b) < 1e-12 and abs(c) < 1e-12:
                hp = Polygon(big) if a > 1e-9 else None            # parallel: q above everywhere, or never
            else:                                                  # q - p = a + b x + c y > 0: right of P0 -> P0 + (-c, b)
                k = -a / (b * b + c * c)
                P0 = (k * b, k * c)
                hp = Polygon(C.clip_poly(big, P0, (P0[0] - c, P0[1] + b), left=False))
            if hp is not None:
                g = g.difference(Polygon(q["polygon"]).intersection(hp))
        out[p["id"]] = g
    return out


# ------------------------------------------------------------------ openings
def draw_openings(P, oids):
    """Doors: leaf at 90 deg + quarter-circle swing; windows: wall-face lines + frame at its true depth + glass;
    pocket door: dashed leaf in the wall; arch: dashed soffit; plain openings: the cut only."""
    for oid in oids:
        o = OPEN[oid]
        w, s0, s1 = opening_span(oid)
        t = o["type"]
        if w.get("virtual") or t == "opening":
            continue
        fr = HC.opening_frame(oid)
        n0, n1 = fr["face_neg"], fr["face_pos"]
        if t == "arch":
            for n in (n0, n1):
                P.line("A-FLOR-OVHD", wpt(w, s0, n), wpt(w, s1, n), "dashed")
        elif t in ("window", "bay_window"):
            for n in (n0, n1):
                P.line("A-GLAZ", wpt(w, s0, n), wpt(w, s1, n))
            if fr["exterior"]:                            # frame FRAME_D deep, ext_reveal behind the outer face
                sg = 1 if fr["face_out"] > 0 else -1
                na = fr["face_out"] - sg * fr["ext_reveal"]
                fa, fb = sorted((na, na - sg * C.FRAME_D))
            else:
                nm_ = (n0 + n1) / 2
                fa, fb = (nm_ - 0.035, nm_ + 0.035) if n1 - n0 > 0.16 else (nm_, nm_)
            nm = (fa + fb) / 2
            lights = [(s0, s1)]
            if o.get("lightWidth"):                       # bay: lights separated by timber mullions, drawn true
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
                if fb - fa > 0.01:
                    P.pl("A-GLAZ", [wpt(w, a, fa), wpt(w, b, fa), wpt(w, b, fb), wpt(w, a, fb)], True)
                P.line("A-GLAZ", wpt(w, a, nm), wpt(w, b, nm))
            if not o.get("lightWidth") and o.get("lights", 1) > 1:        # casement mullions
                for i in range(1, o["lights"]):
                    s = s0 + (s1 - s0) * i / o["lights"]
                    P.line("A-GLAZ", wpt(w, s, fa), wpt(w, s, fb))
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
        else:                                             # hinged leaves (doors, French doors, eaves hatches)
            side = fr["swing_sign"] or 1
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


def leaf_count(oids):
    return sum(2 if OPEN[i]["hinge"] == "both" else 1 for i in oids if OPEN[i]["type"] in ("door", "double_door", "french_door", "hatch")
               and OPEN[i]["hinge"] != "none" and not WALLS[OPEN[i]["wall"]].get("virtual"))


# ------------------------------------------------------------------ stairs
def flight_lines(st):
    """Riser lines in from -> to order; a riser with an `ellipse` nosing is that quarter ellipse (the bullnose)."""
    ell = {r["n"]: r["ellipse"] for r in (st.get("winders") or {}).get("risers", []) if r.get("ellipse")}
    out = []
    for i, (a, b) in enumerate(st["walk"]["risers"], 1):
        if i in ell:
            (cx, cy), (ra, rb) = ell[i]["centre"], ell[i]["semi"]
            out.append(LineString([(cx - ra * math.sin(t), cy - rb * math.cos(t)) for t in (k * math.pi / 32 for k in range(17))]))
        else:
            out.append(LineString([a, b]))
    return out


def break_line(st):
    """Zigzag break across the first tread at or above the plan cut (CUT over the flight's lower end), and the
    region on the lower end's side of it. Riser lines run with the flight's far side on their left."""
    up = st["toZ"] > st["fromZ"]
    lowz = min(st["fromZ"], st["toZ"])
    rs = st["walk"]["risers"]
    t = next(t for t in sorted(st["treads"], key=lambda t: t["z"]) if t["z"] >= lowz + CUT - 1e-6)
    r0, r1 = rs[t["n"] - 1], rs[t["n"]]                        # tread n lies between riser n and riser n + 1
    a, b = mid(r0[0], r1[0]), mid(r0[1], r1[1])
    u = unit(a, b)
    far = (-u[1], u[0])
    low = (-far[0], -far[1]) if up else far
    A = (a[0] + low[0] * 0.17, a[1] + low[1] * 0.17)
    B = (b[0] - low[0] * 0.17, b[1] - low[1] * 0.17)
    lerp = lambda k: (A[0] + (B[0] - A[0]) * k, A[1] + (B[1] - A[1]) * k)
    m1, m2 = lerp(0.44), lerp(0.56)
    brk = [A, m1, (m1[0] + u[0] * 0.02 - low[0] * 0.09, m1[1] + u[1] * 0.02 - low[1] * 0.09),
           (m2[0] - u[0] * 0.02 + low[0] * 0.09, m2[1] - u[1] * 0.02 + low[1] * 0.09), m2, B]
    A2, B2 = (A[0] - u[0], A[1] - u[1]), (B[0] + u[0], B[1] + u[1])
    lower = Polygon([A2, *brk, B2, (B2[0] + low[0] * 30, B2[1] + low[1] * 30), (A2[0] + low[0] * 30, A2[1] + low[1] * 30)])
    return brk, lower.buffer(0)


def walk_line(st):
    """One point per riser on the walking line: the midpoint of a straight riser; on a winder, the point as far from
    its pivot (the newel end, or the end it shares with the other winders) as the next straight riser's midpoint is
    from that pivot, so the arrow turns round the newel on an arc."""
    rs = st["walk"]["risers"]
    win = {r["n"] for r in (st.get("winders") or {}).get("risers", [])}
    posts = [tuple(p) for p in (st.get("newel"), st.get("turningNewel")) if p]
    ends = [tuple(map(tuple, rs[n - 1])) for n in win]
    out = []
    for i, (a, b) in enumerate(rs, 1):
        if i not in win:
            out.append(mid(a, b))
            continue
        a, b = tuple(a), tuple(b)
        shared = [p for p in (a, b) if sum(p in e for e in ends) > 1]
        pv = shared[0] if shared else min((a, b), key=lambda p: min((math.dist(p, q) for q in posts), default=0))
        far = b if pv == a else a
        j = min((j for j in range(1, len(rs) + 1) if j not in win), key=lambda j: abs(j - i))
        sa, sb = rs[j - 1]
        u = unit(sa, sb)
        m = mid(sa, sb)
        r = abs((m[0] - pv[0]) * u[0] + (m[1] - pv[1]) * u[1])
        d = unit(pv, far)
        out.append((pv[0] + d[0] * r, pv[1] + d[1] * r))
    return out


def flights_on(L):
    """[(stair, role, region, break)] of every flight drawn on sheet L. role 'lo': L holds its lower end, drawn from
    there up to the break with UP; 'hi': L holds its upper end, drawn beyond the break where it is seen from L (the
    stairwells and floor voids of L) with DN, and hidden under the flights that leave L."""
    seen = unary_union([rpoly(r) for r in HC.rooms_on(L) if HC.kind(r) == "stairwell"]
                       + [Polygon(f["polygon"]) for f in FEATS if f.get("level") == L and f["type"] == "floor_void"])
    out = []
    for s in HC.stairs:
        if s["kind"] != "flight":
            continue
        st = HC.stair(s["id"])
        up = s["toZ"] > s["fromZ"]
        lo, hi = (s["fromRoom"], s["toRoom"]) if up else (s["toRoom"], s["fromRoom"])
        walk = Polygon(s["walk"]["polygon"])
        brk, lower = break_line(st)
        if HC.level(lo) == L:
            out.append((st, "lo", lower.intersection(walk.buffer(0.05, join_style=2)), brk))
        if HC.level(hi) == L:
            out.append((st, "hi", walk.difference(lower).intersection(seen.buffer(1e-4)), brk))
    los = unary_union([r for _, role, r, _ in out if role == "lo"])
    return [(st, role, r if role == "lo" else r.difference(los), brk) for st, role, r, brk in out]


def draw_flights(P, L):
    for st, role, reg, brk in flights_on(L):
        if reg.is_empty:
            continue
        keep = reg.buffer(1e-6)
        nw = [box(x - 0.05, y - 0.05, x + 0.05, y + 0.05) for x, y in (st.get(k) for k in ("newel", "turningNewel") if st.get(k))
              if reg.buffer(0.06).contains(Point(x, y))]
        posts = unary_union(nw)
        for ln in flight_lines(st):
            P.geom(ln.intersection(keep).difference(posts), "A-STRS")
        for b in nw:
            P.geom(b, "A-STRS")
        P.geom(LineString(brk) if role == "lo" else LineString(brk).intersection(keep), "A-STRS")
        # arrow along the walking line, from this sheet's end of the flight towards the break
        up = st["toZ"] > st["fromZ"]
        seq = list(zip(walk_line(st), st["walk"]["risers"]))
        if (role == "lo") != up:
            seq = seq[::-1]
        seq = [(m, r) for m, r in seq if keep.contains(Point(m))]
        if len(seq) < 2:
            continue
        pts = [m for m, _ in seq]
        d = unit(pts[-2], pts[-1])
        P.circle("A-STRS", pts[0], 0.02)
        P.pl("A-STRS", [pts[0]] + pts[1:-1] + [(pts[-1][0] - d[0] * 0.1, pts[-1][1] - d[1] * 0.1)])
        P.arrowhead("A-STRS", pts[-1], d)
        par = lambda r, q: abs(unit(*r)[0] * unit(*q)[1] - unit(*r)[1] * unit(*q)[0]) < 1e-3
        i = next((i for i in range(len(seq) - 1) if par(seq[i][1], seq[i + 1][1])), 0)
        p, dd = mid(pts[i], pts[i + 1]), unit(pts[i], pts[i + 1])
        perp = (dd[1], -dd[0])                                    # right of the walking direction
        P.text("A-STRS", (p[0] + perp[0] * 0.07, p[1] + perp[1] * 0.07 - 0.9 * MM), 1.8 * MM,
               "UP" if role == "lo" else "DN", "left" if perp[0] > 0.1 else "right" if perp[0] < -0.1 else "center")


def draw_steps(P, L):
    """`steps` sets: riser lines and an arrow across them from fromRoom to toRoom, labelled 'UP nR'."""
    for s in HC.stairs:
        if s["kind"] != "steps" or s.get("level") != L:
            continue
        for ln in s["riserLines"]:
            P.pl("A-STRS", ln)
        first = s["riserLines"][0]
        a, b = max(zip(first, first[1:]), key=lambda e: math.dist(*e))
        m, u = mid(a, b), unit(a, b)
        n = (-u[1], u[0])
        if not rpoly(s["toRoom"]).contains(Point(m[0] + n[0] * 0.05, m[1] + n[1] * 0.05)):
            n = (-n[0], -n[1])
        last = s["riserLines"][-1]
        depth = max(0.0, ((last[0][0] - m[0]) * n[0] + (last[0][1] - m[1]) * n[1]))
        p0 = (m[0] - n[0] * 0.18, m[1] - n[1] * 0.18)
        tip = (m[0] + n[0] * (depth + 0.18), m[1] + n[1] * (depth + 0.18))
        P.line("A-STRS", p0, (tip[0] - n[0] * 0.1, tip[1] - n[1] * 0.1))
        P.arrowhead("A-STRS", tip, n, 0.1, 0.035)
        lab = "%s %dR" % ("UP" if s["toZ"] > s["fromZ"] else "DN", s["risers"])
        k = depth / 2 if depth > 0 else -0.09                     # mid first tread, else before the single riser
        q = (m[0] + n[0] * k, m[1] + n[1] * k)
        if abs(n[1]) > abs(n[0]):                                 # arrow runs along y: label to its right
            P.text("A-STRS", (q[0] + 0.05, q[1] - 0.75 * MM), 1.5 * MM, lab, "left")
        else:                                                     # arrow runs along x: label below it
            P.text("A-STRS", (q[0], q[1] - 0.05 - 1.5 * MM), 1.5 * MM, lab, "center")


def draw_virtual(P, L):
    """Virtual walls (well edges, balustrades) as a single line, less the openings and steps drawn on them."""
    skip = [LineString(ln) for s in HC.stairs if s["kind"] == "steps" and s.get("level") == L for ln in s["riserLines"]]
    for oid, o in OPEN.items():
        if o.get("level") == L and WALLS[o["wall"]].get("virtual"):
            w, s0, s1 = opening_span(oid)
            skip.append(LineString([wpt(w, s0), wpt(w, s1)]))
    sk = unary_union(skip).buffer(0.005, cap_style=2) if skip else None
    for w in WALLS.values():
        if w.get("level") == L and w.get("virtual"):
            g = LineString([w["a"], w["b"]])
            P.geom(g.difference(sk) if sk else g, "A-STRS")


# ------------------------------------------------------------------ features, ceilings, roofs below
def draw_features(P, L):
    for f in FEATS:
        if f.get("level") != L:
            continue
        t = f["type"]
        if t == "hearth" or (t == "boxing" and not at_cut(f, L) and f["z"][0] <= HC.floor_z(f["room"]) + 0.01):
            P.pl("A-FLOR-FIXT", f["polygon"], True)                                  # floor-standing: hearth, WC duct
        elif t == "arch_vault":                                                       # overhead: dashed
            P.geom(Polygon(f["polygon"]).exterior.difference(MASS.buffer(0.005)), "A-FLOR-OVHD", "dashed")
        elif t == "floor_step":
            P.pl("A-STRS", f["line"])
        elif t in ("roof_window", "roof_opening"):                                    # overhead glazing
            q = f["polygon"]
            P.pl("A-GLAZ", q, True, "dashed")
            P.line("A-GLAZ", q[0], q[2], "hidden")
            P.line("A-GLAZ", q[1], q[3], "hidden")
            c = Polygon(q).centroid
            P.text("A-GLAZ", (c.x, c.y + 0.06), 1.5 * MM, "ROOF WINDOW" if t == "roof_window" else "ROOF LIGHT")
        elif t == "balcony":                                                          # deck edge, railing, posts
            q = Polygon(f["polygon"])
            P.geom(q, "A-FLOR-FIXT")
            rl = f["railing"]
            x0, y0, x1, y1 = q.bounds
            inset = rl["post"] / 2
            sides = {"west": [(x0 + inset, y0), (x0 + inset, y1 - inset)], "north": [(x0 + inset, y1 - inset), (x1 - inset, y1 - inset)],
                     "east": [(x1 - inset, y1 - inset), (x1 - inset, y0)]}
            for sd in rl["sides"]:
                P.pl("A-FLOR-FIXT", sides[sd])
            for x, y in rl["posts"]:
                x, y = min(max(x, x0 + inset), x1 - inset), min(max(y, y0 + inset), y1 - inset)
                P.rect("A-FLOR-FIXT", x - inset, y - inset, x + inset, y + inset)


def draw_ceilings(P, L):
    """Sloped ceilings: dashed lines where ceiling planes meet, dash-dot 1.5 m headroom line on each sloped plane."""
    for rid in HC.rooms_on(L):
        planes = (ROOMS[rid].get("ceiling") or {}).get("planes", [])
        if not planes:
            continue
        room = rpoly(rid)
        edge = room.exterior.buffer(0.01)
        polys = [Polygon(p["polygon"]) for p in planes]
        for i in range(len(planes)):
            for j in range(i + 1, len(planes)):
                g = polys[i].intersection(polys[j])
                if g.length > 0.01 and abs(C.plane_z(planes[i], *g.centroid.coords[0]) - C.plane_z(planes[j], *g.centroid.coords[0])) < 0.2:
                    P.geom(g.difference(edge), "A-FLOR-OVHD", "dashed")
        fz = HC.floor_z(rid) + 1.5
        for p, g in zip(planes, polys):
            z = p["z"]
            if abs(z["cx"]) < 1e-9 and abs(z["cy"]) < 1e-9:
                continue
            k = (fz - z["c0"]) / (z["cx"] ** 2 + z["cy"] ** 2)
            P0, d = (k * z["cx"], k * z["cy"]), (-z["cy"], z["cx"])
            ln = LineString([(P0[0] - d[0] * 100, P0[1] - d[1] * 100), (P0[0] + d[0] * 100, P0[1] + d[1] * 100)]).intersection(g.intersection(room))
            if ln.length < 0.05:
                continue
            P.geom(ln, "A-FLOR-OVHD", "center")
            x0, y0, x1, y1 = ln.bounds                            # label on the low side, at the line's east end
            up = -1 if z["cy"] > 0 else 1
            P.text("A-FLOR-OVHD", (x1 - 0.05, y1 + up * 0.04 - (1.5 * MM if up < 0 else 0)), 1.5 * MM, "1500 HEADROOM", "right")


def draw_roofs_below(P, L, regions, mask):
    """Roof planes seen from above on this sheet (the porch lean-to from level 1, the bay gable from the loft):
    planes no higher than the level's highest floor + CUT, outside the level's rooms and poche."""
    floors = [ROOMS[r]["floorZ"] for r in HC.rooms_on(L)]
    top, low = max(floors) + CUT + 0.05, HC.level_info[L]["datumZ"] - 0.6
    for p in H["roof"]["planes"]:
        g = regions[p["id"]]
        zs = [C.plane_z(p, *q) for q in g.exterior.coords] if not g.is_empty and g.geom_type == "Polygon" else [99]
        if g.is_empty or not (low <= min(zs) and max(zs) <= top):
            continue
        P.geom(g.boundary.difference(mask), "A-ROOF")


# ------------------------------------------------------------------ fixtures & furniture footprints
FIXT = {"fireplace", "base_unit", "tall_unit", "worktop", "hob", "sink", "sink_belfast", "fridge", "oven_tower", "washer",
        "dryer", "wc", "basin", "radiator", "towel_rail", "bath", "shower", "vanity", "sauna", "boiler", "cylinder",
        "wardrobe", "cabinet", "workbench", "rack", "fire_pit", "planter", "condenser"}     # -> A-FLOR-FIXT
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


def fpc(name, sym, cx, cy, w, d, front, room=None):
    """Footprint from centre, width across, depth front-to-back and facing vector."""
    L = math.hypot(*front)
    fx, fy = front[0] / L, front[1] / L
    ux, uy = fy, -fx
    obb = [[round(cx + a * ux * w / 2 + b * fx * d / 2, 4), round(cy + a * uy * w / 2 + b * fy * d / 2, 4)]
           for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return {"name": name, "room": room or name.split(".")[0], "plan_sym": sym, "height": 0.0, "obb": obb, "front": [fx, fy]}


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
    return F + site_footprints()


def site_footprints():
    """FALLBACK ONLY - garden and front items from exterior.features (the site room modules export the real ones)."""
    out = []
    room = lambda x, y: HC.zones[HC.zone_at(x, y)]["room"] if HC.zone_at(x, y) else "garden"
    for f in EXT.get("features", []):
        t = f["type"]
        if t == "car":
            a = math.radians(f.get("yawDeg", 0))
            out.append(fpc("front." + f["id"], "car", *f["center"], f["size"][1], f["size"][0], (-math.sin(a), math.cos(a)), "front"))
        elif t == "fire_pit":
            out.append(fpc("garden." + f["id"], "fire_pit", *f["center"], f["size"][0], f["size"][1], (0, -1), room(*f["center"])))
        elif t == "trellis":
            (ax, ay), (bx, by) = f["line"]
            c, d = mid((ax, ay), (bx, by)), unit((ax, ay), (bx, by))
            out.append(fpc("garden." + f["id"], "trellis", *c, math.dist((ax, ay), (bx, by)), 0.04, (d[1], -d[0]), room(*c)))
        elif t == "planters":
            for it in f["items"]:
                xs, ys = [p[0] for p in it["polygon"]], [p[1] for p in it["polygon"]]
                out.append(fp("garden." + it["id"], "planter", min(xs), min(ys), max(xs), max(ys)) | {"room": room(sum(xs) / len(xs), sum(ys) / len(ys))})
        elif t == "bins":
            for i, (x, y) in enumerate(f["items"]):
                out.append(fpc(f"front.bin.{i}", "bin", x, y, 0.58, 0.74, (-1, 0), room(x, y)))
    return out


def rec_level(r):
    if r.get("level"):
        return r["level"]
    if r["room"] in ROOMS:
        return HC.level(r["room"])
    return "X" if r["room"] in C.PSEUDO_ROOMS or r["room"] in HC.building_rooms else "G"


def load_footprints(f):
    spec = spec_footprints()
    data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    if data is None or (isinstance(data, dict) and data.get("standin")):       # the viewer's stand-in file is not an export
        exp = []
    else:
        items = data["items"] if isinstance(data, dict) else data
        exp = [{**r, "room": r.get("room") or str(r.get("name", "")).split(".")[0], "plan_sym": r.get("plan_sym") or r.get("sym"),
                "obb": r.get("obb") or r.get("poly")} for r in items]            # untagged / degenerate records are not plan items
        exp = [r for r in exp if r["plan_sym"] and r["obb"] and len(r["obb"]) == 4 and Polygon(r["obb"]).area > 1e-6]
    for r in exp:
        r["src"] = "export"
    rooms = {r["room"] for r in exp}
    recs = exp + [dict(r, src="spec") for r in spec if r["room"] not in rooms]
    for r in recs:
        r["level"] = rec_level(r)
    left = sorted({r["room"] for r in spec} - rooms)
    src = f"footprints.json ({len(exp)} items); spec fallback for {left or 'no rooms'}" if exp else \
        "spec/rooms/*.md + exterior.features fallback (no exported footprints)"
    return recs, src


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
    if not f and r["plan_sym"] in ("chair", "armchair", "stool", "office_chair") and tables:      # tucked under a table: face it
        me = Polygon(p)
        t = min(tables, key=me.distance)
        if me.distance(t) < 0.12:
            q = shapely.ops.nearest_points(t, Point(c))[0]
            f = (q.x - c[0], q.y - c[1]) if q.distance(Point(c)) > 1e-6 else (t.centroid.x - c[0], t.centroid.y - c[1])
    if not f:                                                                    # back to the nearest wall (windows count)
        f = min(cands, key=lambda cd: MASS.distance(Point(c[0] - cd[0][0] * cd[1] / 2, c[1] - cd[0][1] * cd[1] / 2)))[0]
    v, d = max(cands, key=lambda cd: cd[0][0] * f[0] + cd[0][1] * f[1])
    w = next(L for dd, L in cands if abs(dd[0] * v[0] + dd[1] * v[1]) < 0.5)
    return c, (v[1], -v[0]), v, w, d


def draw_footprints(P, recs):
    recs = [r for r in recs if r["plan_sym"] not in SKIP]
    tables = [Polygon(r["obb"]) for r in recs if r["plan_sym"] in ("table", "table_round", "desk")]
    appliances = [Polygon(r["obb"]).centroid for r in recs if r["plan_sym"] in ("fridge", "oven_tower", "washer", "dryer")]
    for sym in ("base_unit", "worktop", "wall_unit"):            # runs: node the outlines so shared edges are drawn once
        for room in sorted({r["room"] for r in recs}):
            rings = [Polygon(r["obb"]).exterior for r in recs if r["plan_sym"] == sym and r["room"] == room]
            if rings:
                g = snap(unary_union(rings))
                g = linemerge(g) if g.geom_type == "MultiLineString" else g          # a single ring is already one line
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
        Cc = lambda a, b, rad: P.circle(lay, T(a, b), rad)
        ell = lambda a, b, ra, rb, t0=0.0, t1=360.0, n=24: [T(a + ra * math.cos(math.radians(t0 + (t1 - t0) * i / n)),
                                                              b + rb * math.sin(math.radians(t0 + (t1 - t0) * i / n))) for i in range(n + 1)]
        rr = lambda a0, b0, a1, b1, rad: P.pl(lay, [T(*q) for q in box(a0, b0, a1, b1).buffer(-rad, join_style=2).buffer(rad, quad_segs=3).exterior.coords], True)
        lh = 1.5 * MM

        def label(s):
            P.text(lay, (c[0], c[1] - lh / 2), lh, s)
            labs.append(box(c[0] - tw(s, lh) / 2 - 0.33 * lh, c[1] - 0.87 * lh, c[0] + tw(s, lh) / 2 + 0.33 * lh, c[1] + 0.87 * lh))
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
        elif sym == "office_chair":
            Cc(0, 0, 0.42 * min(w, d)); Ln(-0.3 * w, -hd + 0.04, 0.3 * w, -hd + 0.04)
        elif sym in ("stool", "coffee_table"):
            full(); R(-hw + 0.05, -hd + 0.05, hw - 0.05, hd - 0.05)
        elif sym == "table_round":
            Cc(0, 0, min(hw, hd))
        elif sym in ("bookcase", "tv_unit", "chest", "bureau", "cabinet", "workbench", "bench"):
            full(); Ln(-hw, hd - 0.04, hw, hd - 0.04)
        elif sym == "wardrobe":                                  # hanging rail with hangers
            full(); Ln(-hw + 0.05, 0, hw - 0.05, 0)
            for i in range(1, max(2, int(w / 0.15))):
                a = -hw + i * w / max(2, int(w / 0.15))
                Ln(a - 0.03, -0.12, a + 0.03, 0.12)
        elif sym == "bed":                                       # head against the wall (back = -hd), two pillows, sheet fold
            full()
            n = 2 if w >= 1.1 else 1
            for i in range(n):
                a0 = -hw + 0.06 + i * (w - 0.12) / n
                rr(a0 + 0.02, -hd + 0.06, a0 + (w - 0.12) / n - 0.02, -hd + 0.36, 0.05)
            Ln(-hw, -hd + 0.55, hw, -hd + 0.55); Ln(-hw, -hd + 0.55, -hw + 0.25, -hd + 0.75)
        elif sym == "bedside":
            full(); Cc(0, 0, 0.3 * min(w, d))
        elif sym == "rug":
            full("dashed")
        elif sym in ("plant", "planter") and abs(w - d) < 0.2:
            rad = min(hw, hd)
            Cc(0, 0, rad); Cc(0, 0, rad * 0.35)
            for i in range(8):
                a = math.radians(i * 45 + 22.5)
                Ln(rad * 0.35 * math.cos(a), rad * 0.35 * math.sin(a), rad * math.cos(a), rad * math.sin(a))
        elif sym == "planter":
            full(); R(-hw + 0.05, -hd + 0.05, hw - 0.05, hd - 0.05)
        elif sym == "fireplace":
            full(); P.pl(lay, [T(-0.22 * w, hd), T(-0.22 * w, -hd + 0.05), T(0.22 * w, -hd + 0.05), T(0.22 * w, hd)])
        elif sym == "fire_pit":
            full(); R(-hw + 0.215, -hd + 0.215, hw - 0.215, hd - 0.215); label("FP")
        elif sym == "tall_unit":
            full()
            if not any(Polygon(r["obb"]).contains(a) for a in appliances):      # full-height unit: crossed
                Ln(-hw, -hd, hw, hd); Ln(-hw, hd, hw, -hd)
        elif sym == "hob":
            full()
            burners = ([(-0.33 * w, 0, 0.08), (0, -0.24 * d, 0.055), (0, 0.24 * d, 0.045), (0.33 * w, -0.24 * d, 0.055), (0.33 * w, 0.24 * d, 0.045)]
                       if w >= 0.7 else [(sx * 0.22 * w, sy * 0.22 * d, 0.05) for sx in (-1, 1) for sy in (-1, 1)])
            for a, b, rad in burners:
                Cc(a, b, rad); Cc(a, b, rad * 0.4)
        elif sym == "sink":
            full()
            n = 2 if w >= 0.7 else 1
            for i in range(n):
                a0, a1 = -hw + i * w / n, -hw + (i + 1) * w / n
                rr(a0 + 0.02, -hd + 0.02, a1 - 0.02, hd - 0.02, 0.04); Cc((a0 + a1) / 2, 0, 0.022)
        elif sym == "sink_belfast":
            full(); rr(-hw + 0.03, -hd + 0.03, hw - 0.03, hd - 0.03, 0.04); Cc(0, 0, 0.022)
        elif sym == "fridge":
            full(); Ln(-hw, hd - 0.07, hw, hd - 0.07); Ln(-0.08 * w, hd - 0.07, -0.08 * w, hd); label("FF")
        elif sym == "oven_tower":
            full(); Ln(-hw, hd - 0.04, hw, hd - 0.04); label("OV")
        elif sym in ("washer", "dryer"):
            full(); Cc(0, 0, 0.37 * min(w, d)); label("WM" if sym == "washer" else "TD")
        elif sym == "wc":
            b1 = -hd + 0.35 * d
            P.pl(lay, [T(-hw, -hd), *ell(0, b1, hw, hd - b1, 180, 0), T(hw, -hd)], True)
            P.pl(lay, ell(0, b1 + 0.08 * d, 0.62 * hw, 0.5 * (hd - b1)), True)
            if d > 0.6:
                Ln(-hw, -hd + 0.18, hw, -hd + 0.18)                              # close-coupled cistern
        elif sym in ("basin", "vanity"):
            if sym == "vanity":
                full()
            n = 2 if sym == "vanity" and w >= 1.0 else 1
            for i in range(n):
                a = -hw + (i + 0.5) * w / n
                if sym == "basin":
                    rr(-hw, -hd, hw, hd, 0.03)
                P.pl(lay, ell(a, 0.03, 0.72 * w / n / 2, 0.58 * hd), True); Cc(a, -hd + 0.05, 0.02)
        elif sym == "bath":
            full(); rr(-hw + 0.06, -hd + 0.06, hw - 0.06, hd - 0.06, 0.12); Cc(-hw + 0.2, 0, 0.025)
        elif sym == "shower":                                    # tray with diagonals and waste
            full(); Ln(-hw, -hd, hw, hd); Ln(-hw, hd, hw, -hd); Cc(0, 0, 0.04)
        elif sym == "sauna":
            full(); R(-hw + 0.05, -hd + 0.05, hw - 0.05, hd - 0.05); Ln(-hw + 0.05, -hd + 0.45, hw - 0.05, -hd + 0.45); label("SAUNA")
        elif sym == "boiler":
            full(); label("B")
        elif sym == "cylinder":
            Cc(0, 0, min(hw, hd)); label("HW")
        elif sym == "rack":
            full(); Ln(-hw, 0, hw, 0) if w >= d else Ln(0, -hd, 0, hd)
        elif sym == "radiator":
            full(); Ln(-hw, 0, hw, 0)
        elif sym == "condenser":
            full(); Cc(0, 0, 0.35 * min(w, d))
        elif sym == "towel_rail":
            full()
            for i in range(1, int(w / 0.05)):
                Ln(-hw + i * 0.05, -hd, -hw + i * 0.05, hd)
        elif sym == "airer":
            (Ln(-hw, 0, hw, 0, "dashed") if w >= d else Ln(0, -hd, 0, hd, "dashed"))
        elif sym == "shelf":
            full("hidden")
        elif sym == "trellis":                                   # panel on the wall: frame + lattice
            full()
            n = max(2, int(w / 0.3))
            for i in range(n):
                a0, a1 = -hw + i * w / n, -hw + (i + 1) * w / n
                Ln(a0, -hd, a1, hd); Ln(a0, hd, a1, -hd)
        elif sym == "flagpole":
            Cc(0, 0, max(0.03, min(hw, hd)))
        elif sym == "bin":
            full(); Ln(-hw, hd - 0.06, hw, hd - 0.06)
        elif sym == "car":                                       # body, bonnet / roof glazing lines, four wheels
            P.pl(lay, [T(*q) for q in box(-hw, -hd, hw, hd).buffer(-0.25, join_style=2).buffer(0.25, quad_segs=4).exterior.coords], True)
            Ln(-hw + 0.12, hd - 0.95, hw - 0.12, hd - 0.95); Ln(-hw + 0.12, hd - 2.1, hw - 0.12, hd - 2.1)
            Ln(-hw + 0.12, hd - 0.95, -hw + 0.12, hd - 2.1); Ln(hw - 0.12, hd - 0.95, hw - 0.12, hd - 2.1)
            for sa in (-1, 1):
                for b in (hd - 0.75, -hd + 0.7):
                    R(sa * (hw - 0.03), b - 0.3, sa * (hw - 0.22), b + 0.3)
        else:                                                    # table, console, tv, desk and unknown keys: plain outline
            full()
        if sym in ("chair", "armchair", "stool", "office_chair") and not tops.is_empty:
            P.e[n0:] = clip(P.e[n0:], tops)                      # tucked under the table: hidden part not drawn
        elif sym == "rug":                                       # ... nor the rug edge under furniture standing on it
            over = [Polygon(q["obb"]) for q in recs if q["room"] == r["room"] and q["plan_sym"] not in OVHD | MERGED | {"rug"}]
            P.e[n0:] = clip(P.e[n0:], unary_union(over))
    if labs:                                                     # overhead lines give way to the appliance labels
        m = unary_union(labs)
        P.e = [x for e in P.e for x in (clip([e], m) if e["layer"] == "A-FLOR-OVHD" else [e])]


def mask_under_text(P, boxes, layers=("A-FURN", "A-FLOR-FIXT", "A-FLOR-OVHD")):
    """Break linework where it would run under a tag (CAD text-mask look)."""
    if boxes:
        m = unary_union([box(*b) for b in boxes])
        P.e = [x for e in P.e for x in (clip([e], m) if e["layer"] in layers else [e])]


def clip(ents, m, inside=False):
    """Cut line / polyline / circle / arc entities where they run inside polygon m (inside=True: keep only that
    part); the rest pass through."""
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
        if inside and m.contains(g) or not inside and not g.intersects(m):
            out.append(e)
            continue
        g = g.intersection(m) if inside else g.difference(m)
        for part in getattr(g, "geoms", [g]):
            if part.geom_type == "LineString" and part.length > 1e-4:
                d = {"layer": e["layer"], "type": "polyline", "pts": [list(q) for q in part.coords], "closed": False}
                if e.get("ls"):
                    d["ls"] = e["ls"]
                out.append(d)
    return out


# ------------------------------------------------------------------ annotation
def chain(P, axis, coords, base, line_at, rows=None, avoid=()):
    """Dimension chain along x (points (c, base)) or y (points (base, c)); `base` may be f(c0, c1).
    A value too wide to sit between its own extension lines (wall thicknesses) moves to the far side of the
    dimension line, where no extension lines run; at the two ends of a chain it also moves outside the chain.
    `avoid` = [(along, half width)] of values lifted towards this row by the previous one: a value of this row that
    would sit on one slides along its line. -> the lifted values of this row, as `avoid` for the next."""
    n, lifted = len(coords) - 1, []
    std = 1 if axis == "x" else -1                                # values normally sit above / left of the line
    for i, (c0, c1) in enumerate(zip(coords, coords[1:])):
        b = base(c0, c1) if callable(base) else base
        p1, p2 = ((c0, b), (c1, b)) if axis == "x" else ((b, c0), (b, c1))
        off = (line_at - b) if axis == "x" else (b - line_at)
        half = tw(str(round((c1 - c0) * 1000)), T_DIM) / 2
        tp = None
        if 2 * half + 1.0 * MM > c1 - c0:
            end = n > 1 and i in (0, n - 1)
            away = 1 if line_at > b else -1
            perp = line_at + away * (0.7 * T_DIM / CAP if end and away == std else DIMSTYLE["extBeyond"] + 1.0 * MM + T_DIM / 2)
            along = (c0 + c1) / 2 if not end else c0 - half - 0.8 * MM if i == 0 else c1 + half + 0.8 * MM
            tp = (along, perp) if axis == "x" else (perp, along)
            if away != std or not end:
                lifted.append((along, half))
        else:
            c = (c0 + c1) / 2
            hit = next(((a, h) for a, h in avoid if abs(c - a) < half + h + 1.0 * MM), None)
            if hit:                                               # slide clear of the value lifted from the row inside
                sg = 1 if c >= hit[0] else -1
                c = hit[0] + sg * (hit[1] + half + 3.0 * MM)
                perp = line_at + std * 0.7 * T_DIM / CAP
                tp = (c, perp) if axis == "x" else (perp, c)
        P.dim(p1, p2, off, tp)
    if rows is not None:
        rows.append((axis, round(line_at, 3), round((coords[-1] - coords[0]) * 1000)))
    return lifted


OUTN = {"front": (0, -1), "rear": (0, 1), "west": (-1, 0), "east": (1, 0)}


def face(env, side, c):
    """Outer face of env on `side` along the line through c (x for front / rear, y for west / east), or None."""
    ln = LineString([(c, -1e3), (c, 1e3)]) if side in ("front", "rear") else LineString([(-1e3, c), (1e3, c)])
    g = env.intersection(ln)
    if g.is_empty:
        return None
    x0, y0, x1, y1 = g.bounds
    return {"front": y0, "rear": y1, "west": x0, "east": x1}[side]


def facing(poly, side):
    """Axis-aligned exterior edges of poly whose outward normal points to `side`."""
    nx, ny = OUTN[side]
    ring, out = list(poly.exterior.coords), []
    for p, q in zip(ring, ring[1:]):
        along_x = abs(p[1] - q[1]) < 1e-9 and abs(p[0] - q[0]) > 1e-9
        along_y = abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) > 1e-9
        if (along_x if side in ("front", "rear") else along_y):
            m = mid(p, q)
            if not poly.contains(Point(m[0] + nx * 1e-3, m[1] + ny * 1e-3)) and poly.contains(Point(m[0] - nx * 1e-3, m[1] - ny * 1e-3)):
                out.append((p, q))
    return out


def side_chain(P, side, env, rooms, r1, r2=None, rows=None, near=0.6):
    """Row 1: the faces of the rooms along one side; row 2 (optional): the steps of the outer face, which is the
    overall length when that side is straight. West / east chains run the full length (each extension line starts at
    the local outer face); front / rear chains take only faces within 1.0 m of the extreme face (a rear wing's face
    does not reach the main block's rear chain)."""
    horiz = side in ("front", "rear")
    k = 0 if horiz else 1
    env = env.simplify(1e-6)                                      # drop collinear vertices left by the block union
    x0, y0, x1, y1 = env.bounds
    extreme = {"front": y0, "rear": y1, "west": x0, "east": x1}[side]
    sg = -1 if side in ("front", "west") else 1

    def faces(polys, room):
        pts = set()
        for poly in polys:
            for p, q in facing(poly, side):
                at = p[1 - k]                                     # the edge's own coordinate across the chain
                for t in (0.02, 0.5, 0.98):
                    f = face(env, side, p[k] + t * (q[k] - p[k]))
                    if f is not None and (not horiz or abs(f - extreme) <= 1.0) and (not room or abs(f - at) <= near):
                        pts |= {round(p[k], 4), round(q[k], 4)}
                        break
        return pts
    outer = faces([env], False)
    if not horiz:
        outer |= {round(y0, 4), round(y1, 4)}
    ends = {min(outer), max(outer)}
    rows_ = [sorted(faces(rooms, True) | ends), sorted(ends if horiz else outer)]
    line_at = extreme + sg * r1
    lifted = []
    for i, pts in enumerate(rows_[:2 if r2 else 1]):
        cs = []
        for c in pts:
            if not cs or c - cs[-1] > 0.001:
                cs.append(c)
        if i == 0:
            lifted = chain(P, "x" if horiz else "y", cs, lambda a, b: face(env, side, (a + b) / 2), line_at, rows)
        else:
            chain(P, "x" if horiz else "y", cs, line_at, extreme + sg * r2, rows, lifted)


def draw_tags(P, rids, at=None):
    """Room tags: NAME / W x D / area / FFL; small rooms: an FFL datum mark only. -> (rooms[], text boxes)."""
    rooms, boxes = [], []
    for rid in rids:
        r = ROOMS.get(rid) or HC.building_rooms[rid]
        poly = rpoly(rid)
        kind = HC.kind(rid) if rid in ROOMS else "room"
        pt = (at or {}).get(rid) or TAG_AT.get(rid) or tuple(polylabel(poly, 0.01).coords[0])
        rooms.append({"id": rid, "name": r["name"], "polygon": r["polygon"], "label": list(pt), "floorZ": r["floorZ"],
                      "area": round(poly.area, 2)})
        if kind == "stairwell":
            continue
        if rid in NO_TAG:
            boxes.append(datum(P, pt[0], pt[1], ffl(r["floorZ"])))
            continue
        x0, y0, x1, y1 = poly.bounds
        sz = r.get("size") or (x1 - x0, y1 - y0)
        lines = [(room_name(rid), T_NAME), ("%d x %d" % (round(sz[0] * 1000), round(sz[1] * 1000)), T_SUB),
                 ("%.1f m²" % poly.area, T_SUB), (ffl(r["floorZ"]), T_SUB)]
        gap = 1.3 * MM
        bw = lambda ls: max(tw(s, h) for s, h in ls) + 1.2 * MM
        bh = lambda ls: sum(h for _, h in ls) + gap * (len(ls) - 1) + 1.2 * MM
        rw, rh = x1 - x0, y1 - y0
        rot = 0
        if bw(lines) > rw and rid not in TAG_AT:                  # does not fit across: turn it, else the name only
            if rh > rw and bh(lines) <= rw and bw(lines) <= rh:
                rot = 90
            else:
                lines = lines[:1]
                rot = 90 if bw(lines) > rw and rh > rw else 0
        boxes.append(text_block(P, "A-ANNO-TEXT", pt, lines, rot, gap))
    return rooms, boxes


def datum(P, x, y, s):
    """Level datum mark: triangle on a line, value below. -> its text-mask box."""
    L = "A-ANNO-TEXT"
    P.pl(L, [(x - 1.0 * MM, y + 1.8 * MM), (x + 1.0 * MM, y + 1.8 * MM), (x, y)], True)
    P.line(L, (x - 2.8 * MM, y), (x + 2.8 * MM, y))
    P.text(L, (x, y - 1.2 * MM - T_SUB), T_SUB, s)
    hw = max(tw(s, T_SUB) / 2, 2.8 * MM) + 0.5 * MM
    return (x - hw, y - 1.7 * MM - T_SUB, x + hw, y + 2.3 * MM)


def draw_sheet(P, sh, notes, levels, footsrc, date, n_sheets):
    """Border, title block (100 x 44 mm), scale bar, notes + line key at the top of the title column."""
    L, LB, m = "A-ANNO-TTLB", "A-ANNO-TTLB-BORD", 10 * MM
    SX0, SY0, SX1, SY1 = sh["sheetBounds"]["minX"], sh["sheetBounds"]["minY"], sh["sheetBounds"]["maxX"], sh["sheetBounds"]["maxY"]
    bx0, by0, bx1, by1 = SX0 + m, SY0 + m, SX1 - m, SY1 - m
    P.rect(LB, bx0, by0, bx1, by1)
    tx0 = bx1 - 100 * MM
    rows = [(14, [(100, "DRAWING TITLE", sh["title"], 4.5)]),
            (8, [(100, "PROJECT", "PRIVATE HOUSE - AS EXISTING - 3D MODEL", 2.5)]),
            (8, [(30, "SCALE", "%s @ A3" % sh["scale"], 2.5), (28, "DRAWING No.", sh["number"], 2.5), (14, "REV", "B", 2.5), (28, "DATE", date, 2.5)]),
            (7, [(100, "SOURCE", "DRAWN FROM VIDEO WALKTHROUGHS - NOT A MEASURED SURVEY", 2.0)]),
            (7, [(30, "UNITS", "MILLIMETRES", 2.0), (42, "LEVELS", levels, 2.0), (28, "SHEET", "%d OF %d" % (sh["index"], n_sheets), 2.0)])]
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
            vh = min(vh, (w - 3.0) / (len(val) * CHAR_W))           # long values shrink to fit their cell
            P.text(L, (x + 1.2 * MM, y + (h - 2.4) * MM), 1.2 * MM, cap, "left")
            P.text(L, (x + 1.5 * MM, y + 1.5 * MM), vh * MM, val, "left")
            x += w * MM
    # scale bar, 80 mm long: first unit halved, alternate blocks filled
    u = SCALE / 50.0
    sy, bh = by0 + 44 * MM + 9 * MM, 1.5 * MM
    P.rect(L, tx0, sy, tx0 + 4 * u, sy + bh)
    for a, b in ((0, 0.5), (1, 2), (3, 4)):
        P.hatch(L, [(tx0 + a * u, sy), (tx0 + b * u, sy), (tx0 + b * u, sy + bh), (tx0 + a * u, sy + bh)], "SOLID")
    for v in (0, 0.5, 1, 2, 3, 4):
        P.line(L, (tx0 + v * u, sy), (tx0 + v * u, sy + bh + 0.8 * MM))
        P.text(L, (tx0 + v * u, sy + bh + 1.6 * MM), 1.8 * MM, ("%g" % (v * u)) + (" m" if v == 4 else ""), "center")
    P.text(L, (tx0, sy - 3.4 * MM), 1.8 * MM, "SCALE %s AT A3" % sh["scale"], "left")
    common = ["NOTES", "",
              "1. ALL DIMENSIONS IN MILLIMETRES, LEVELS IN METRES",
              "   ABOVE GROUND FLOOR FFL ±0.000.",
              "2. PLAN RECONSTRUCTED FROM VIDEO WALKTHROUGHS.",
              "   DIMENSIONS ARE ESTIMATES: DO NOT SCALE FOR",
              "   CONSTRUCTION, VERIFY ON SITE.",
              "3. ORIENTATION: NO NORTH POINT (BEARING NOT",
              "   SURVEYED). STREET AT THE BOTTOM OF EVERY SHEET.",
              "4. FIXTURES AND FURNITURE: " + footsrc]
    y = by1 - 8 * MM
    numbered, k = [], 5
    for t in notes:                                               # "   ..." continues the note above
        numbered.append(t if t.startswith(" ") else "%d. %s" % (k, t))
        k += not t.startswith(" ")
    for s in common + numbered + ["", "KEY", ""]:
        if s:
            P.text(L if s in ("NOTES", "KEY") else "A-ANNO-TEXT", (tx0, y), 2.0 * MM, s, "left")
        y -= (4.0 if s else 1.5) * MM
    key = [("A-WALL", None, "WALL, CUT (HATCHED)"), ("A-FLOR-FIXT", None, "FIXED FITTINGS"), ("A-FURN", None, "LOOSE FURNITURE"),
           ("A-FLOR-OVHD", "dashed", "OVERHEAD: ARCH, VAULT, CEILING BREAK"), ("A-FLOR-OVHD", "hidden", "OVERHEAD: WALL UNITS, SHELVES"),
           ("A-DOOR", "hidden", "POCKET DOOR LEAF IN WALL")]
    if sh["id"] == "2":
        key.append(("A-FLOR-OVHD", "center", "1.5 M HEADROOM UNDER SLOPED CEILING"))
    if sh["id"] in ("1", "2"):
        key.append(("A-ROOF", None, "ROOF BELOW"))
    if sh["id"] == "X":
        key = [("A-WALL", None, "BUILDING OUTLINE / SHED WALL, CUT"), ("A-ROOF", None, "ROOF PLAN: EAVES, RIDGES, VALLEYS"),
               ("L-SITE", None, "EXTERNAL SURFACES, STEPS"), ("L-SITE-BNDY", "dashed", "PLOT / BOUNDARY: WALL, FENCE"),
               ("A-FURN", None, "CARS, GARDEN ITEMS (INDICATIVE)")]
    for lay, ls, s in key:
        P.line(lay, (tx0, y + 1.0 * MM), (tx0 + 14 * MM, y + 1.0 * MM), ls)
        P.text("A-ANNO-TEXT", (tx0 + 17 * MM, y), 2.0 * MM, s, "left")
        y -= 4.0 * MM


# ------------------------------------------------------------------ sheets
def sheet_frame(sid, hb, bottom):
    """A3 portrait frame in model metres: drawing 42 mm from the left edge, `bottom` mm above the bottom edge."""
    x0, y0 = hb["minX"] - 42 * MM, hb["minY"] - bottom * MM
    assert (hb["maxX"] - hb["minX"]) / MM + 42 + 100 + 20 <= A3[0], f"sheet {sid}: plan too wide for A3 at 1:{SCALE}"
    return {"minX": x0, "minY": y0, "maxX": x0 + A3[0] * MM, "maxY": y0 + A3[1] * MM}


def floor_layout(sid, P, hb):
    """Vertical layout of a 1:50 sheet in paper mm: dimension rows clear the leaves of doors that swing out past the
    front / rear face; when the standard rows do not fit A3 (level 1 with its balcony) the compact one drops the rear
    chain. -> dict(r1, r2, front (note), rear (chain or None), rear_note, bottom (margin))."""
    ys = [p[1] for e in P.e if e["layer"] == "A-DOOR" and e["type"] == "polyline" for p in e["pts"]]
    pf = max(0.0, (hb["minY"] - min(ys, default=hb["minY"])) / MM)            # paper mm in front of the house
    pr = max(0.0, (max(ys, default=hb["maxY"]) - hb["maxY"]) / MM)
    hh = (hb["maxY"] - hb["minY"]) / MM
    r1 = max(9.0, pf + 3)
    r2 = r1 + 8 if r1 == 9 else r1 + 5.5
    lay = dict(r1=r1, r2=r2, front=r2 + 5.5 if r1 == 9 else r2 + 4.3, rear=max(15.0, pr + 3))
    lay["rear_note"] = lay["rear"] + 5.5
    need_b, need_t = lay["front"] + 11.5, lay["rear_note"] + 13.8        # note descenders + 10 mm frame margin
    if hh + need_b + need_t > A3[1]:                              # compact: 7 / 13 mm rows, no rear chain
        r1 = max(7.0, pf + 3)
        lay = dict(r1=r1, r2=r1 + 6, front=r1 + 10.5, rear=None, rear_note=3.5)
        need_b, need_t = lay["front"] + 11.5, lay["rear_note"] + 13.8
    slack = A3[1] - hh - need_b - need_t
    assert slack >= -1e-6, f"sheet {sid} does not fit A3 at 1:{SCALE}"
    lay["bottom"] = need_b + slack / 2
    return lay


def floor_sheet(sid, title, number, recs, regions):
    global MASS
    L = sid
    P = Plan()
    cut, MASS = poche(L)
    env = envelope(L)
    hb = dict(H["bounds"])                                       # one window for B, G, 2; level 1 adds the balcony
    rids = HC.rooms_on(L)
    for rid in rids:
        if HC.kind(rid) == "exterior":
            hb["maxY"] = max(hb["maxY"], rpoly(rid).bounds[3])
    for poly in parts(cut):                                      # poche first, linework over it
        for piece in split_holes(poly):
            P.hatch("A-WALL-PATT", list(piece.exterior.coords)[:-1], "ANSI31")
    if L == "B":                                                 # context: the ground floor outline over
        g = envelope("G")
        P.geom(g.exterior.difference(cut.buffer(0.005)), "A-FLOR-OVHD", "dashed")
        P.text("A-FLOR-OVHD", (g.bounds[0] + 0.15, g.bounds[1] + 0.5), 1.8 * MM, "OUTLINE OF GROUND FLOOR OVER", "left")
    fps = [r for r in recs if r["level"] == L]
    draw_footprints(P, fps)
    draw_features(P, L)
    draw_roofs_below(P, L, regions, unary_union([MASS] + [room_cut(r) for r in rids]).buffer(0.002))
    draw_flights(P, L)
    draw_steps(P, L)
    draw_virtual(P, L)
    oids = [oid for oid, o in OPEN.items() if o.get("level") == L and not o.get("building")]
    draw_openings(P, oids)
    lay = floor_layout(sid, P, hb)
    sb = sheet_frame(sid, hb, lay["bottom"])
    P.geom(cut, "A-WALL")
    draw_ceilings(P, L)
    rooms, boxes = draw_tags(P, rids)
    mask_under_text(P, boxes)
    L_ = "A-ANNO-TEXT"
    cx = (hb["minX"] + hb["maxX"]) / 2
    P.text(L_, (cx, hb["maxY"] + lay["rear_note"] * MM), T_NOTE, "REAR (GARDEN)")
    P.text(L_, (cx, hb["minY"] - lay["front"] * MM), T_NOTE, "FRONT (STREET)")
    rows = []
    rms = [rpoly(r) for r in rids if HC.kind(r) != "exterior"]
    for side in ("west", "east"):
        side_chain(P, side, env, rms, lay["r1"] * MM, lay["r2"] * MM, rows)
    side_chain(P, "front", env, rms, lay["r1"] * MM, lay["r2"] * MM, rows)
    if lay["rear"]:
        side_chain(P, "rear", env, rms, lay["rear"] * MM, None, rows)
    floors = sorted({ROOMS[r]["floorZ"] for r in rids if HC.kind(r) in ("room", "exterior", "void")})
    levels = "FFL ±0.000 THROUGHOUT" if floors == [0] else "FFL " + " / ".join(lvl(z) for z in floors)
    notes = ["ROOM SIZES ARE BETWEEN FINISHED WALL FACES;", "   AREAS ARE NET INTERNAL FLOOR AREAS.",
             "PLAN CUT 1200 ABOVE EACH FLOOR LEVEL (FFL).", "DOORS SHOWN OPEN AT 90 DEG WITH SWING.",
             "STAIRS: TREADS TO THE BREAK LINE ON THE LOWER", "   FLOOR (UP), BEYOND IT ON THE UPPER (DN)."]
    if L == "1":
        notes.append("SPLIT LEVEL: STEPS MARKED UP nR = n RISERS.")
    if L == "2":
        notes += ["SLOPED CEILINGS: DASH-DOT LINE = 1500", "   HEADROOM; EAVES ARE STORAGE VOIDS."]
    if L == "B":
        notes.append("BASEMENT BELOW THE MAIN BLOCK ONLY.")
    footsrc = fsrc(fps)
    sh = {"id": sid, "level": L, "title": title, "number": number, "scale": "1:%d" % SCALE, "paper": "A3",
          "orientation": "portrait", "sheetBounds": sb}
    return P, sh, rooms, dict(cut=cut, rows=rows, leaves=leaf_count(oids), notes=notes, levels=levels, footsrc=footsrc,
                              hb=hb, bounds={"minX": hb["minX"] - 22 * MM, "minY": hb["minY"] - (lay["front"] + 0.5) * MM,
                                             "maxX": hb["maxX"] + 21 * MM, "maxY": hb["maxY"] + (lay["rear_note"] + 3.5) * MM})


def fsrc(fps):
    src = {r["src"] for r in fps}
    return {frozenset(): "NOT YET MODELLED.", frozenset({"export"}): "FROM 3D MODEL EXPORT.",
            frozenset({"spec"}): "FROM ROOM SPECS, INDICATIVE."}.get(frozenset(src), "3D MODEL EXPORT; SOME FROM SPECS.")


def site_window():
    x0, y0, x1, y1 = Polygon(EXT["plot"]["polygon"]).bounds
    return (round(x0 - 0.3, 3), round(y0 - 0.3, 3), round(x1 + 0.3, 3), round(y1 + 0.3, 3))


def site_sheet(sid, title, number, recs, regions):
    """Site plan X at 1:100: plot, zones with surface and level, steps, boundaries, gate swing, shed with poche,
    house outline + roof plan, cars and garden items; everything clipped to the plot window."""
    global MASS
    P = Plan()
    win_t = site_window()
    win = box(*win_t)
    hb = dict(zip(("minX", "minY", "maxX", "maxY"), win_t))
    assert (win_t[3] - win_t[1]) / MM + 2 * 30 <= A3[1], "site window does not fit A3 at 1:100"
    sb = sheet_frame(sid, hb, (A3[1] - (win_t[3] - win_t[1]) / MM) / 2)
    house = envelope("G")
    shed_cut, shed_solid = shed_poche()
    MASS = unary_union([house, shed_solid])
    # zones: visible part of each (smaller zones lie on top), outlines once, labels
    zs = sorted(EXT["zones"], key=lambda z: Polygon(z["polygon"]).area)
    vis, above = {}, Polygon()
    for z in zs:
        g = Polygon(z["polygon"])
        vis[z["id"]] = g.difference(above).difference(house).intersection(win)
        above = above.union(g)
    edges = unary_union([g.boundary for g in vis.values() if not g.is_empty]).difference(house.buffer(0.01))
    P.geom(linemerge(edges) if edges.geom_type == "MultiLineString" else edges, "L-SITE")
    boxes = []
    fps = [r for r in recs if r["level"] == "X"]
    items = unary_union([Polygon(r["obb"]).buffer(0.15) for r in fps])
    for z in zs:
        g = vis[z["id"]]
        if g.is_empty or g.area < 0.05:
            continue
        name = ZONE_NAME.get(z["id"], z["id"].replace("_", " ").upper())
        big = max(parts(g), key=lambda p: p.area)
        if z.get("fall"):
            big = big.difference(LineString([z["fall"]["from"], z["fall"]["to"]]).buffer(0.3))
            big = max(parts(big), key=lambda p: p.area) if not big.is_empty else max(parts(g), key=lambda p: p.area)
        free = big.difference(items)                              # labels clear of cars, planters, the fire pit, falls
        free = max(parts(free), key=lambda p: p.area) if not free.is_empty else big
        c = free.centroid
        pt = (c.x, c.y) if free.buffer(-0.3).contains(c) else polylabel(free, 0.02).coords[0]
        fall = z.get("fall")
        lines = [(name, T_SUB), (SURF.get(z["surface"], z["surface"].upper()), 1.5 * MM)] if name else []
        if not fall:
            lines.append((lvl(HC.zone_z(z["id"])), 1.5 * MM))
        fx0, fy0, fx1, fy1 = free.bounds
        fit = fit_block(lines, fx1 - fx0, fy1 - fy0)
        if fit:
            boxes.append(text_block(P, "L-SITE", pt, *fit))
        if fall:                                              # fall arrow, the level at both ends beside it
            a, b = fall["from"], fall["to"]
            ab = LineString([a, b]).intersection(win)
            if ab.is_empty:
                continue
            a2, b2 = ab.coords[0], ab.coords[-1]
            d = unit(a2, b2)
            P.line("L-SITE", a2, (b2[0] - d[0] * 0.25, b2[1] - d[1] * 0.25))
            P.arrowhead("L-SITE", b2, d, 0.3, 0.1)
            rot = math.degrees(math.atan2(d[1], d[0]))
            rot = rot - 180 if rot > 90 else rot + 180 if rot <= -90 else rot     # readable from below / the right
            up = (-math.sin(math.radians(rot)), math.cos(math.radians(rot)))       # the text's up, beside the arrow
            h = 1.5 * MM
            for p, s, k in ((a2, lvl(HC.zone_z(z["id"], *a2)), 0.6), (b2, lvl(HC.zone_z(z["id"], *b2)), -0.8)):
                q = (p[0] + d[0] * k - up[0] * (0.1 + h), p[1] + d[1] * k - up[1] * (0.1 + h))
                P.text("L-SITE", q, h, s, "center", round(rot, 3))
    # steps: treads and single riser lines
    for s in EXT["steps"]:
        for t in s.get("treads", []):
            P.pl("L-SITE", t["polygon"], True)
        if s.get("line"):
            P.pl("L-SITE", s["line"])
    # boundaries (dashed layer), gate leaf at 50 degrees into its swing room
    for b in EXT["boundaries"]:
        if b["type"] == "gate":
            hp = tuple(b["hingeAt"])
            far = tuple(b["line"][1]) if math.dist(b["line"][0], hp) < 1e-6 else tuple(b["line"][0])
            a0 = math.atan2(far[1] - hp[1], far[0] - hp[0])
            r = b.get("width", math.dist(hp, far))
            into = Polygon(HC.zones[b["swingInto"]]["polygon"]) if b["swingInto"] in HC.zones else None
            for sg in (1, -1):
                a1 = a0 + sg * math.radians(50)
                tip = (hp[0] + r * math.cos(a1), hp[1] + r * math.sin(a1))
                if into is None or into.contains(Point(mid(hp, tip))):
                    break
            P.line("A-DOOR", hp, tip)
            lo_, hi_ = sorted((math.degrees(a0), math.degrees(a1)))
            P.arc("A-DOOR", hp, r, lo_, hi_)
            for q in (hp, far):
                P.rect("L-SITE-BNDY", q[0] - 0.05, q[1] - 0.05, q[0] + 0.05, q[1] + 0.05)
        elif "polygon" in b:
            P.geom(Polygon(b["polygon"]).intersection(win), "L-SITE-BNDY")
        elif b["type"] == "wall" and b.get("thickness"):
            (ax, ay), (bx, by) = b["line"]
            P.geom(LineString([(ax, ay), (bx, by)]).buffer(b["thickness"] / 2, cap_style=2).intersection(win), "L-SITE-BNDY")
        else:
            P.geom(LineString(b["line"]).intersection(win), "L-SITE-BNDY")
    P.geom(Polygon(EXT["plot"]["polygon"]).exterior.intersection(win), "L-SITE-BNDY")
    for n in EXT.get("neighbours", []):                          # massing only, no numbers
        P.geom(Polygon(n["polygon"]).boundary.intersection(win).difference(house.buffer(0.01)), "A-ROOF")
    # shed: walls cut and hatched, openings, roof edge over the veranda
    for poly in parts(shed_cut):
        for piece in split_holes(poly):
            P.hatch("A-WALL-PATT", list(piece.exterior.coords)[:-1], "ANSI31")
    shed_ops = [oid for oid, o in OPEN.items() if o.get("building")]
    draw_openings(P, shed_ops)
    P.geom(shed_cut, "A-WALL")
    for bld in EXT.get("buildings", []):
        P.geom(Polygon(bld["roof"]["polygon"]).exterior.difference(shed_solid.buffer(0.01)), "A-ROOF", "dashed")
    # house: outline + roof plan (upper envelope of the planes), chimney stack, balcony, pitch arrows
    roofg = unary_union([g.boundary for g in regions.values() if not g.is_empty])
    P.geom(linemerge(roofg) if roofg.geom_type == "MultiLineString" else roofg, "A-ROOF")
    for f in EXT.get("features", []):
        if f["type"] == "chimney":                                # the stack above the roof (envelope builds it so)
            g = Polygon(f["polygon"]).intersection(box(-100, 16.46, -0.53, 100)).intersection(win)
            if not g.is_empty:
                P.geom(g, "A-ROOF")
                gx0, gy0, gx1, gy1 = g.bounds
                P.line("A-ROOF", (gx0, gy0), (gx1, gy1)); P.line("A-ROOF", (gx0, gy1), (gx1, gy0))
    for rid in ROOMS:                                             # the balcony, overhead
        if HC.kind(rid) == "exterior":
            P.geom(rpoly(rid).exterior.difference(house.buffer(0.005)), "A-ROOF", "dashed")
    for p in H["roof"]["planes"]:
        g = regions[p["id"]]
        z = p["z"]
        if g.is_empty or (abs(z["cx"]) < 1e-9 and abs(z["cy"]) < 1e-9) or g.area < 1.0:
            continue
        big = max(parts(g), key=lambda q: q.area)
        c = polylabel(big, 0.02)
        r = min(0.4, 0.8 * big.exterior.distance(c))                # arrow half-length within the plane
        c = c.coords[0]
        d = unit((0, 0), (-z["cx"], -z["cy"]))                     # downhill
        P.line("A-ROOF", (c[0] - d[0] * r, c[1] - d[1] * r), (c[0] + d[0] * (r - 0.25), c[1] + d[1] * (r - 0.25)))
        P.arrowhead("A-ROOF", (c[0] + d[0] * r, c[1] + d[1] * r), d, 0.25, 0.08)
        P.text("A-ROOF", (c[0] + abs(d[1]) * 0.12, c[1] + abs(d[0]) * 0.12 - 0.75 * MM * abs(d[1])), 1.5 * MM, "%g°" % p["pitchDeg"],
               "left" if abs(d[1]) > abs(d[0]) else "center")
    P.geom(house.exterior, "A-WALL")
    hx = polylabel(house, 0.02).coords[0]
    ridge = H["roof"]["ridge"]
    boxes.append(text_block(P, "A-ANNO-TEXT", (hx[0] - 0.4, hx[1]), [("HOUSE", T_NAME), ("RIDGE %s" % lvl(ridge["z"]), T_SUB),
                                                                       ("FLAT ROOF %s" % lvl(max(p["z"]["c0"] for p in H["roof"]["planes"] if not p["z"]["cy"] and not p["z"]["cx"])), T_SUB),
                                                                       ("GROUND " + ffl(0.0), T_SUB)], 90))
    draw_footprints(P, fps)
    rooms, tb = draw_tags(P, list(HC.building_rooms))
    boxes += tb
    mask_under_text(P, boxes, ("A-FURN", "A-FLOR-FIXT", "A-FLOR-OVHD", "L-SITE", "A-ROOF"))
    P.e = clip(P.e, win.buffer(1e-6), inside=True)               # nothing of the model outside the plot window
    rows = []
    plot = Polygon(EXT["plot"]["polygon"])
    px0, py0, px1, py1 = plot.bounds
    ys = sorted({py0, house.bounds[1], house.bounds[3], Polygon(EXT["buildings"][0]["outline"]).bounds[1], py1})
    chain(P, "y", ys, px0, px0 - 9 * MM, rows)
    chain(P, "y", [ys[0], ys[-1]], px0 - 9 * MM, px0 - 17 * MM, rows)
    chain(P, "x", [px0, house.bounds[2], px1], py0, py0 - 9 * MM, rows)
    chain(P, "x", [px0, px1], py0 - 9 * MM, py0 - 17 * MM, rows)
    P.text("A-ANNO-TEXT", ((px0 + px1) / 2, py1 + 21.2 * MM), T_NOTE, "REAR (GARDEN)")
    P.text("A-ANNO-TEXT", ((px0 + px1) / 2, py0 - 22.5 * MM), T_NOTE, "FRONT (STREET)")
    site_rooms = []
    for pr in ("front", "side_passage", "garden", "shed"):        # as manifest rooms[]: largest walkable zone / workshop
        if pr == "shed" and EXT.get("buildings"):
            r = next(r for b in EXT["buildings"] if b["room"] == pr for r in b["rooms"] if r.get("walk", True))
            poly, fz = r["polygon"], r["floorZ"]
        else:
            cand = [z for z in EXT["zones"] if z.get("room") == pr and z.get("walk", True)]
            if not cand:
                continue
            z = max(cand, key=lambda z: Polygon(z["polygon"]).area)
            poly, fz = z["polygon"], z["z"]
        site_rooms.append({"id": pr, "name": pr.replace("_", " ").capitalize(), "polygon": poly, "floorZ": fz,
                           "area": round(Polygon(poly).area, 2), "label": list(polylabel(Polygon(poly), 0.02).coords[0])})
    notes = ["SITE PLAN WINDOW = PLOT + 300; THE FOOTWAY,", "   CARRIAGEWAY AND NEIGHBOURS ARE NOT SHOWN.",
             "SURFACE LEVELS IN METRES; ARROW = FALL, LEVEL", "   GIVEN AT BOTH ENDS.",
             "BOUNDARIES APPROXIMATE, NOT SURVEYED.", "HOUSE SHOWN AS ROOF PLAN OVER ITS OUTLINE."]
    sh = {"id": sid, "level": "X", "title": title, "number": number, "scale": "1:%d" % SCALE, "paper": "A3",
          "orientation": "portrait", "sheetBounds": sb}
    return P, sh, rooms + site_rooms, dict(cut=shed_cut, rows=rows, leaves=leaf_count(shed_ops) + 1, notes=notes,
                                           levels="SURFACES -0.450 TO ±0.000", footsrc=fsrc(fps), hb=hb, bounds=hb)


def fit_block(lines, w, h):
    """-> (lines, rot) of the first of: every line, the first line, the last line, that fits a w x h box across or
    turned 90 degrees; None when nothing fits."""
    bw = lambda ls: max(tw(s, k) for s, k in ls) + 1.0 * MM
    bh = lambda ls: sum(k for _, k in ls) + 1.0 * MM * len(ls)
    for ls in (lines, lines[:1], lines[-1:]):
        if ls and bw(ls) <= w and bh(ls) <= h:
            return ls, 0
        if ls and bw(ls) <= h and bh(ls) <= w:
            return ls, 90
    return None


def text_block(P, layer, pt, lines, rot=0, gap=None):
    """Centred stack of text lines at pt (rot 0 or 90). -> its text-mask box."""
    gap = 1.0 * MM if gap is None else gap
    tot = sum(h for _, h in lines) + gap * (len(lines) - 1)
    hw = max(tw(s, h) for s, h in lines) / 2 + 0.6 * MM
    off = tot / 2
    for s, h in lines:
        off -= h
        if rot == 90:
            P.text(layer, (pt[0] - off, pt[1]), h, s, "center", 90)
        else:
            P.text(layer, (pt[0], pt[1] + off), h, s)
        off -= gap
    if rot == 90:
        return (pt[0] - tot / 2 - 0.6 * MM, pt[1] - hw, pt[0] + tot / 2 + 0.6 * MM, pt[1] + hw)
    return (pt[0] - hw, pt[1] - tot / 2 - 0.6 * MM, pt[0] + hw, pt[1] + tot / 2 + 0.6 * MM)


# ------------------------------------------------------------------ assemble + writers
def rnd(o):
    if isinstance(o, float):
        return round(o, 4)
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [rnd(v) for v in o]
    return o


def build(house, footprints):
    setup(house)
    recs, src = load_footprints(Path(footprints))
    regions = roof_regions()
    date = datetime.date.fromtimestamp(Path(house).stat().st_mtime).isoformat()
    sheets, checks = [], []
    for i, (sid, title, scale, number) in enumerate(SHEETS):
        set_scale(scale)
        P, sh, rooms, ex = (site_sheet if sid == "X" else floor_sheet)(sid, title, number, recs, regions)
        sh["index"] = i + 1
        draw_sheet(P, sh, ex["notes"], ex["levels"], ex["footsrc"], date, len(SHEETS))
        walls = [e for e in P.e if e["layer"] == "A-WALL" and e["type"] == "polyline"]
        xs = [p[0] for e in walls for p in e["pts"]]
        ys = [p[1] for e in walls for p in e["pts"]]
        sh.update(bounds=ex["bounds"], houseBounds={"minX": min(xs), "minY": min(ys), "maxX": max(xs), "maxY": max(ys)},
                  linestyles=LINESTYLES, hatch={"ANSI31": "45 deg lines through the origin", "spacing": HATCH_SPACING},
                  dimstyle=DIMSTYLE, dxfOffset=[i * DXF_PITCH, 0], entities=P.e, rooms=rooms)
        sheets.append(rnd(sh))
        checks.append(dict(ex, mm=MM))
    return {"schema": 2, "units": "m",
            "layers": [{"name": n, "color": c, "paper": p, "aci": a, "lineweight": lw} for n, c, p, a, lw in LAYERS],
            "textNote": "text: h = font size (em) in metres, capitals are 0.72 h; p = anchor at the vertical middle of the "
                        "capitals (canvas textBaseline 'middle'), align = horizontal anchor, rot = deg CCW. dim: h likewise, "
                        "optional tp = text middle when lifted off its default place. Per sheet: linestyles (dash, gap, ...), "
                        "hatch spacing and dimstyle in model metres; dxfOffset = where the sheet sits in the DXF, in mm.",
            "footprintSource": src.replace(str(ROOT), "."), "sheets": sheets}, checks


def write_json(plan, path):
    s = json.dumps(plan, ensure_ascii=False, separators=(",", ":"))
    path.write_text(s.replace('},{"layer"', '},\n{"layer"').replace('"entities":[', '"entities":[\n'), encoding="utf-8")


def write_dxf(plan, path):
    """Real CAD entities in millimetres at true scale on named layers, every sheet in one model space, shifted by
    its dxfOffset. 1:50 sheets use DIMSTYLE PLAN50; the 1:100 sheet PLAN100 and entity linetype scale 2."""
    import ezdxf
    from ezdxf.enums import TextEntityAlignment as TA
    from render import dim_geometry
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    doc.header["$MEASUREMENT"], doc.header["$LTSCALE"], doc.header["$LUNITS"], doc.header["$LUPREC"] = 1, 1.0, 2, 0
    base = next(s for s in plan["sheets"] if s["scale"] == "1:50")
    for name, pat in base["linestyles"].items():               # dash, -gap, ... in mm, true length at LTSCALE 1 on 1:50
        mmpat = [v * 1000 * (1 if i % 2 == 0 else -1) for i, v in enumerate(pat)]
        doc.linetypes.add(name.upper(), pattern=[sum(abs(v) for v in mmpat), *mmpat], description=name)
    doc.styles.add("ISO", font="isocp.shx")
    for l in plan["layers"]:
        doc.layers.add(l["name"], color=l["aci"], lineweight=round(l["lineweight"] * 100),
                       linetype="DASHED" if l["name"] in DASHED_LAYERS else "Continuous")
    for s in plan["sheets"]:
        st, nm = s["dimstyle"], "PLAN" + s["scale"].split(":")[1]
        if nm not in doc.dimstyles:
            doc.dimstyles.new(nm, dxfattribs={
                "dimtxsty": "ISO", "dimtxt": st["h"] * CAP * 1000, "dimtsz": st["tick"] * 1000, "dimasz": st["tick"] * 1000,
                "dimexo": st["extGap"] * 1000, "dimexe": st["extBeyond"] * 1000, "dimgap": st["h"] * (0.7 - CAP / 2) * 1000,
                "dimtad": 1, "dimtih": 0, "dimtoh": 0, "dimdec": 0, "dimlunit": 2, "dimzin": 8, "dimscale": 1.0, "dimlfac": 1.0,
                "dimclrd": 256, "dimclre": 256, "dimclrt": 256})
    msp = doc.modelspace()
    for s in plan["sheets"]:
        ox, oy = s["dxfOffset"]
        K = lambda p: (p[0] * 1000 + ox, p[1] * 1000 + oy)
        lts = int(s["scale"].split(":")[1]) / int(base["scale"].split(":")[1])
        st, dsn = s["dimstyle"], "PLAN" + s["scale"].split(":")[1]
        for e in s["entities"]:
            at = {"layer": e["layer"]}
            if e.get("ls"):
                at["linetype"] = e["ls"].upper()
            if lts != 1:
                at["ltscale"] = lts
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
                h = msp.add_hatch(color=256, dxfattribs={"layer": e["layer"]})
                if e["pattern"] == "SOLID":
                    h.set_solid_fill(color=256)
                else:                                           # ISO ANSI31 is 3.175 mm apart at scale 1
                    h.set_pattern_fill(e["pattern"], color=256, scale=s["hatch"]["spacing"] * 1000 / 3.175)
                h.paths.add_polyline_path([K(p) for p in e["pts"]], is_closed=True)
            elif t == "text" and e.get("of") != "dim":
                tx = msp.add_text(e["text"], height=e["h"] * CAP * 1000, dxfattribs={"layer": e["layer"], "style": "ISO", "rotation": e.get("rot", 0)})
                tx.set_placement(K(e["p"]), align={"left": TA.MIDDLE_LEFT, "center": TA.MIDDLE_CENTER, "right": TA.MIDDLE_RIGHT}[e.get("align", "left")])
            elif t == "dim":
                segs, tp, rot = dim_geometry(e, st)
                loc = K(tp) if e.get("tp") else None            # lifted text: give its mid point explicitly
                ang = math.degrees(math.atan2(e["p2"][1] - e["p1"][1], e["p2"][0] - e["p1"][0]))
                msp.add_linear_dim(base=K(segs[0][0]), p1=K(e["p1"]), p2=K(e["p2"]), angle=ang, location=loc,
                                   dimstyle=dsn, dxfattribs={"layer": e["layer"]}).render()
    sbs = [(s["sheetBounds"], s["dxfOffset"]) for s in plan["sheets"]]
    x0 = min(b["minX"] * 1000 + o[0] for b, o in sbs)
    x1 = max(b["maxX"] * 1000 + o[0] for b, o in sbs)
    y0 = min(b["minY"] * 1000 + o[1] for b, o in sbs)
    y1 = max(b["maxY"] * 1000 + o[1] for b, o in sbs)
    doc.set_modelspace_vport(height=(y1 - y0) * 1.05, center=((x0 + x1) / 2, (y0 + y1) / 2))
    aud = doc.audit()
    assert not aud.errors, [str(x) for x in aud.errors]
    doc.saveas(path)


def self_check(plan, checks):
    """Cheap invariants per sheet; the visual check is tools/plan/check.py."""
    layers = {l["name"] for l in plan["layers"]}
    assert [s["id"] for s in plan["sheets"]] == [s[0] for s in SHEETS]
    for sh, ex in zip(plan["sheets"], checks):
        E, sid = sh["entities"], sh["id"]
        assert all(e["layer"] in layers for e in E), sid
        assert all(e.get("ls") in (None, *sh["linestyles"]) for e in E), sid
        for e in E:
            if e["type"] == "dim":
                assert int(e.get("value") or e["text"]) == round(math.dist(e["p1"], e["p2"]) * 1000), (sid, e)
        rows = {}                                               # chain rows keyed by where their dimension line runs
        for e in E:
            if e["type"] == "dim":
                horiz = abs(e["p1"][1] - e["p2"][1]) < 1e-9
                key = ("x", round(e["p1"][1] + e["offset"], 3)) if horiz else ("y", round(e["p1"][0] - e["offset"], 3))
                rows[key] = rows.get(key, 0) + int(e.get("value") or e["text"])
        for axis, at, total in ex["rows"]:                      # every chain closes on its own overall length
            assert rows.get((axis, round(at, 3))) == total, (sid, axis, at, total, rows.get((axis, round(at, 3))))
        for axis in ("x", "y"):                                 # ... and the rows of one side agree with each other
            sums = [v for (a, _), v in rows.items() if a == axis]
            assert sums, (sid, axis)
        hatched = sum(Polygon(e["pts"]).area for e in E if e["layer"] == "A-WALL-PATT" and e["type"] == "hatch")
        assert abs(hatched - ex["cut"].area) < 2e-3, (sid, hatched, ex["cut"].area)
        assert sum(e["type"] == "arc" and e["layer"] == "A-DOOR" for e in E) == ex["leaves"], sid
        sb, b = sh["sheetBounds"], sh["bounds"]
        m = 10 * ex["mm"]
        assert sb["minX"] + m <= b["minX"] and b["maxX"] <= sb["maxX"] - m and sb["minY"] + m <= b["minY"] and b["maxY"] <= sb["maxY"] - m, (sid, b, sb)
        assert abs((sb["maxX"] - sb["minX"]) / ex["mm"] - A3[0]) < 0.01 and abs((sb["maxY"] - sb["minY"]) / ex["mm"] - A3[1]) < 0.01, sid
        if sid != "X":
            assert len(sh["rooms"]) == len(HC.rooms_on(sid)), sid
            edge = ex["cut"].boundary                           # chamfers of both kinds drawn true at the cut
            for rid in HC.rooms_on(sid):
                for c in HC.chamfers(rid):
                    if c["z"][0] <= HC.floor_z(rid) + CUT < c["z"][1]:
                        assert edge.distance(Point(mid(c["p"], c["q"]))) < 2e-3 and edge.distance(Point(c["p"])) < 2e-3, (sid, c["id"])
            roles = {(st["id"], role) for st, role, reg, _ in flights_on(sid) if not reg.is_empty}
            for s in HC.stairs:                                 # every flight: UP on its lower sheet, DN on its upper
                if s["kind"] == "flight":
                    lo, hi = sorted((s["fromRoom"], s["toRoom"]), key=lambda r: ROOMS[r]["floorZ"])
                    for room, role in ((lo, "lo"), (hi, "hi")):
                        assert HC.level(room) != sid or (s["id"], role) in roles, (sid, s["id"], role)
    site = plan["sheets"][-1]
    assert site["scale"] == "1:100" and tuple(site["bounds"][k] for k in ("minX", "minY", "maxX", "maxY")) == site_window()
    assert all(f["scale"] == "1:50" for f in plan["sheets"][:-1])


if __name__ == "__main__":
    from render import render_pdf
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--house", default=str(ROOT / "spec" / "house.json"), help="house.json, schema 2 (default spec/house.json)")
    ap.add_argument("--footprints", default=str(OUT / "footprints.json"), help="exported footprints (default docs/assets/footprints.json)")
    ap.add_argument("--out", default=str(OUT), help="output directory (default docs/assets)")
    a = ap.parse_args()
    plan, checks = build(a.house, a.footprints)
    self_check(plan, checks)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write_json(plan, out / "plan.json")
    write_dxf(plan, out / "house-plans.dxf")
    render_pdf(plan, out / "house-plans.pdf")
    for old in ("ground-floor-plan.dxf", "ground-floor-plan.pdf"):    # phase-1 downloads are replaced
        (out / old).unlink(missing_ok=True)
    for s in plan["sheets"]:
        n = {}
        for e in s["entities"]:
            n[e["type"]] = n.get(e["type"], 0) + 1
        print("  sheet %-2s %-26s %s  %s" % (s["id"], s["title"], s["scale"], n))
    print("PLAN OK  %d sheets on A3  footprints: %s" % (len(plan["sheets"]), plan["footprintSource"]))
