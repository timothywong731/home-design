"""Validate spec/house.json and draw spec/plan_preview.png.

    python spec/validate_house.py            # validate + redraw preview, exit 1 on any error

Checks: room polygons closed/CCW/non-overlapping; every polygon edge lies on a wall face; walls
reference existing rooms; every opening lies on its wall and inside its length and connects rooms the
wall separates; every room is reachable from the vestibule through doors/arches; stair arithmetic.
Needs shapely + Pillow (both on the system Python).
"""
import json, math, sys
from pathlib import Path
from shapely.geometry import Polygon, Point
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "house.json"   # other file: validate only, no preview
H = json.loads(SRC.read_text(encoding="utf-8"))
rooms = {r["id"]: r for r in H["rooms"]}
walls = {w["id"]: w for w in H["walls"]}
errs = []
TOL = 0.02
PASSABLE = {"door", "double_door", "arch", "french_door", "opening"}
TYPES = PASSABLE | {"window", "bay_window"}


def err(msg):
    errs.append(msg)


def wall_frame(w):
    (ax, ay), (bx, by) = w["a"], w["b"]
    L = math.hypot(bx - ax, by - ay)
    return ax, ay, (bx - ax) / L, (by - ay) / L, L


def along_perp(w, p):
    ax, ay, ux, uy, L = wall_frame(w)
    dx, dy = p[0] - ax, p[1] - ay
    return dx * ux + dy * uy, dx * -uy + dy * ux, L   # along, perp (+ = left of a->b), length


# 1. rooms
polys = {}
for rid, r in rooms.items():
    p = Polygon(r["polygon"])
    polys[rid] = p
    if len(r["polygon"]) < 3 or not p.is_valid:
        err(f"room {rid}: invalid polygon")
    if not p.exterior.is_ccw:
        err(f"room {rid}: polygon is not counter-clockwise")
    if not r["ceilingZ"] > r["floorZ"]:
        err(f"room {rid}: ceilingZ <= floorZ")
ids = list(polys)
for i, a in enumerate(ids):
    for b in ids[i + 1:]:
        if polys[a].intersection(polys[b]).area > 1e-4:
            err(f"rooms {a} and {b} overlap by {polys[a].intersection(polys[b]).area:.3f} m2")

# 2. walls
for wid, w in walls.items():
    if math.dist(w["a"], w["b"]) < 0.05:
        err(f"wall {wid}: zero length")
    for r in w["rooms"]:
        if r != "outside" and r not in rooms:
            err(f"wall {wid}: unknown room {r}")
    t = w["thickness"]
    if w.get("virtual"):
        if t != 0:
            err(f"wall {wid}: virtual wall must have thickness 0")
    elif not 0.08 <= t <= 0.70:
        err(f"wall {wid}: thickness {t} out of range")

# 3. every polygon edge sits on a wall face (or inside a recess feature cut into a thick wall)
recesses = [Polygon(f["polygon"]).buffer(TOL) for f in H["features"] if f["type"] == "recess"]


def on_wall_face(p, rid):
    for w in walls.values():
        if rid not in w["rooms"]:
            continue
        s, d, L = along_perp(w, p)
        if -0.40 <= s <= L + 0.40 and abs(abs(d) - w["thickness"] / 2) <= TOL:
            return True
    return any(rc.contains(Point(p)) for rc in recesses)


for rid, r in rooms.items():
    pts = r["polygon"]
    for i, a in enumerate(pts):
        b = pts[(i + 1) % len(pts)]
        for k in (0.1, 0.3, 0.5, 0.7, 0.9):
            p = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
            if not on_wall_face(p, rid):
                err(f"room {rid}: edge {a}->{b} not on a wall face near {p[0]:.2f},{p[1]:.2f}")
                break

# 4. openings
adj = {rid: set() for rid in rooms}
for o in H["openings"]:
    oid = o["id"]
    if o["type"] not in TYPES:
        err(f"opening {oid}: unknown type {o['type']}")
    w = walls.get(o["wall"])
    if not w:
        err(f"opening {oid}: unknown wall {o['wall']}")
        continue
    s, d, L = along_perp(w, o["center"])
    if abs(d) > 0.01:
        err(f"opening {oid}: centre is {abs(d):.3f} m off the centreline of {o['wall']}")
    if s - o["width"] / 2 < -1e-6 or s + o["width"] / 2 > L + 1e-6:
        err(f"opening {oid}: extends past the end of {o['wall']} (s={s:.2f}, L={L:.2f})")
    for r in o["connects"]:
        if r != "outside" and r not in rooms:
            err(f"opening {oid}: unknown room {r}")
        if r not in w["rooms"]:
            err(f"opening {oid}: {r} is not a side of wall {o['wall']}")
    if o["sill"] + o["height"] > w["height"] + 1e-6 and not w.get("virtual"):
        err(f"opening {oid}: taller than its wall")
    if o["type"] in ("door", "double_door", "french_door"):
        if o["hinge"] not in ("left", "right", "both", "none"):
            err(f"opening {oid}: bad hinge {o['hinge']}")
        if o["hinge"] != "none" and o["swingInto"] not in o["connects"]:
            err(f"opening {oid}: swingInto must be one of connects")
    a, b = o["connects"]
    if o["type"] in PASSABLE and a in adj and b in adj:
        adj[a].add(b)
        adj[b].add(a)

# 5. reachability from the vestibule
seen, todo = {"vestibule"}, ["vestibule"]
while todo:
    for n in adj[todo.pop()]:
        if n not in seen:
            seen.add(n)
            todo.append(n)
for rid in rooms:
    if rid not in seen:
        err(f"room {rid}: not reachable from the vestibule")

# 6. stairs
S = H["stairs"]
if abs(S["risers"] * S["rise"] - S["landingZ"]) > 0.01:
    err("stairs: risers x rise != landingZ")
if abs(S["firstStraightRiserY"] + (S["risers"] - 4) * S["going"] - S["lastRiserY"]) > 0.01:
    err("stairs: riser positions do not add up")

# ---------------------------------------------------------------- preview
SC, M = 92, 70                       # px per metre, margin
B = H["bounds"]
Wpx = int((B["maxX"] - B["minX"]) * SC) + 2 * M + 250
Hpx = int((B["maxY"] - B["minY"]) * SC) + 2 * M
img = Image.new("RGB", (Wpx, Hpx), "white")
dr = ImageDraw.Draw(img)


def font(sz):
    try:
        return ImageFont.truetype("arial.ttf", sz)
    except OSError:
        return ImageFont.load_default()


F, FS = font(15), font(12)
X = lambda x: M + (x - B["minX"]) * SC
Y = lambda y: Hpx - M - (y - B["minY"]) * SC
P = lambda p: (X(p[0]), Y(p[1]))
FILL = {"vestibule": "#d9e2ec", "hallway": "#f3e9c9", "stairs": "#dcdcdc", "living": "#f2cfc4", "kitchen": "#cfd6e6",
        "wc": "#d5d5db", "utility": "#dfe8d8", "dining": "#e6d3bd"}


def end_ext(w, end):
    """Half-thickness of the thickest non-parallel wall whose centreline passes through this end (fills corners)."""
    _, _, ux, uy, _ = wall_frame(w)
    e = 0.0
    for o in walls.values():
        if o is w or o.get("virtual"):
            continue
        _, _, vx, vy, _ = wall_frame(o)
        s, d, L = along_perp(o, w[end])
        if abs(ux * vx + uy * vy) < 0.1 and abs(d) < 0.01 and -0.01 <= s <= L + 0.01:
            e = max(e, o["thickness"] / 2)
    return e


def wall_quad(w, s0=None, s1=None, grow=0.0):
    ax, ay, ux, uy, L = wall_frame(w)
    s0 = -end_ext(w, "a") if s0 is None else s0
    s1 = L + end_ext(w, "b") if s1 is None else s1
    h = w["thickness"] / 2 + grow
    return [P((ax + ux * s + -uy * n, ay + uy * s + ux * n)) for s, n in ((s0, h), (s1, h), (s1, -h), (s0, -h))]


for rid, r in rooms.items():
    dr.polygon([P(p) for p in r["polygon"]], fill=FILL.get(rid, "#eee"))
for f in H["features"]:
    if f["type"] in ("outside_yard", "poche"):
        dr.polygon([P(p) for p in f["polygon"]], fill="#f4f4f4" if f["type"] == "outside_yard" else "#555")
for w in walls.values():
    if w.get("virtual"):
        dr.line([P(w["a"]), P(w["b"])], fill="#999", width=1)
    else:
        dr.polygon(wall_quad(w), fill="#3c3c3c")
for f in H["features"]:                      # recesses are cut out of thick walls; projections drawn solid
    if f["type"] == "recess":
        dr.polygon([P(p) for p in f["polygon"]], fill=FILL[f["room"]], outline="#3c3c3c")
    elif f["type"] in ("pier", "pilaster", "chimney_breast", "nib"):
        dr.polygon([P(p) for p in f["polygon"]], fill="#3c3c3c")
    elif f["type"] in ("boxing", "soffit", "hearth", "arch_vault", "reveal") and "polygon" in f:
        dr.polygon([P(p) for p in f["polygon"]], outline="#8a6d3b")

for o in H["openings"]:
    w = walls[o["wall"]]
    ax, ay, ux, uy, L = wall_frame(w)
    s, _, _ = along_perp(w, o["center"])
    s0, s1 = s - o["width"] / 2, s + o["width"] / 2
    pt = lambda ss, n=0.0: (ax + ux * ss - uy * n, ay + uy * ss + ux * n)
    if not w.get("virtual"):
        dr.polygon(wall_quad(w, s0, s1, 0.01), fill="white")
    if o["type"] in ("window", "bay_window"):
        for n in (-0.03, 0.03):
            dr.line([P(pt(s0, n)), P(pt(s1, n))], fill="#1f6fd0", width=2)
    elif o["type"] in ("arch", "opening"):
        dr.line([P(pt(s0)), P(pt(s1))], fill="#b03030", width=1)
    elif o["hinge"] == "none":               # pocket door: leaf drawn half-slid
        dr.line([P(pt(s0 - o["width"] * 0.6)), P(pt(s0 + o["width"] * 0.4))], fill="#b05a00", width=3)
    else:
        tgt, sign = o["swingInto"], 1
        if tgt == "outside":                 # swing away from the inside room
            tgt, sign = next(r for r in o["connects"] if r != "outside"), -1
        left = polys[tgt].contains(Point(pt(s, w["thickness"] / 2 + 0.1)))
        side = sign * (1 if left else -1)    # +1 = left of a->b
        if o["hinge"] == "both":
            leaves = [(s0, 1, o["width"] / 2), (s1, -1, o["width"] / 2)]
        else:
            ha = along_perp(w, o["hingeAt"])[0]
            leaves = [(ha, 1 if abs(ha - s0) < abs(ha - s1) else -1, o["width"])]
        for hs, dirn, lw in leaves:
            hp, tip = pt(hs), pt(hs, side * lw)
            dr.line([P(hp), P(tip)], fill="#b05a00", width=2)
            arc = [P(pt(hs + dirn * lw * math.cos(a), side * lw * math.sin(a))) for a in [i * math.pi / 24 for i in range(13)]]
            dr.line(arc, fill="#b05a00", width=1)

# stairs: risers + up arrow
sx0, sx1 = rooms["stairs"]["polygon"][0][0], rooms["stairs"]["polygon"][1][0]
for n in range(4, S["risers"] + 1):
    yy = S["firstStraightRiserY"] + (n - 4) * S["going"]
    dr.line([P((sx0, yy)), P((sx1, yy))], fill="#666", width=1)
nx, ny = S["newel"]
y0s = S["start"][1]                           # bullnose R1 (quarter ellipse from the nib corner to the newel), R2, R3
dr.line([P((0.65 - 0.53 * math.sin(i * math.pi / 24), ny - (ny - y0s - 0.02) * math.cos(i * math.pi / 24))) for i in range(13)], fill="#666")
dr.line([P((nx + 0.05, ny - 0.03)), P((sx1, ny - 0.22))], fill="#666")
dr.line([P((nx + 0.05, ny + 0.03)), P((sx1, ny + 0.03))], fill="#666")
dr.ellipse([X(nx) - 4, Y(ny) - 4, X(nx) + 4, Y(ny) + 4], fill="#4a2216")
mx = (sx0 + sx1) / 2
dr.line([P((mx, S["start"][1] + 0.1)), P((mx, S["lastRiserY"]))], fill="#b03030", width=1)
dr.polygon([P((mx, S["lastRiserY"] + 0.12)), P((mx - 0.08, S["lastRiserY"] - 0.05)), P((mx + 0.08, S["lastRiserY"] - 0.05))], fill="#b03030")

for rid, r in rooms.items():
    p = polys[rid]
    x0, y0, x1, y1 = p.bounds
    c = p.representative_point()
    sw, sd = r.get("size", [x1 - x0, y1 - y0])    # nominal size if given, else bounding box
    label = f"{r['name']}\n{sw:.2f} x {sd:.2f}\nceil {r['ceilingZ']:.2f}"
    if rid in ("stairs", "vestibule", "hallway"):
        label = f"{rid}\n{sw:.2f}x{sd:.2f}"
        dr.multiline_text((X(c.x), Y(c.y)), label, fill="black", font=FS, anchor="mm", align="center")
    else:
        dr.multiline_text((X(c.x), Y(c.y)), label, fill="black", font=F, anchor="mm", align="center")

for yv in range(0, int(B["maxY"]) + 1):       # metre ruler on the right
    xr = X(B["maxX"]) + 30
    dr.line([(xr, Y(yv)), (xr + (12 if yv % 5 == 0 else 6), Y(yv))], fill="black")
    dr.text((xr + 16, Y(yv) - 7), f"y={yv}", fill="black", font=FS)
lx, ly = X(B["maxX"]) + 90, M
for i, t in enumerate(["+Y = rear (garden)", "+X = right walking in", "origin = street-door threshold", "",
                       "dark = walls / piers / breast", "orange = door leaf + swing", "blue = window",
                       "red = arch / opening / stair up", "brown outline = boxing, soffit, reveal",
                       f"footprint {B['maxX'] - B['minX']:.2f} x {B['maxY'] - B['minY']:.2f} m"]):
    dr.text((lx, ly + i * 18), t, fill="black", font=FS)
if SRC.resolve() == (HERE / "house.json").resolve():
    img.save(HERE / "plan_preview.png")

if errs:
    print(f"FAIL: {len(errs)} error(s)")
    for e in errs:
        print("  -", e)
    sys.exit(1)
print(f"OK: {len(rooms)} rooms, {len(walls)} walls, {len(H['openings'])} openings, {len(H['features'])} features; "
      f"all rooms reachable from the vestibule")
