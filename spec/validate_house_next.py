"""Validate spec/house.next.json (whole house, all levels) and draw the previews.

    python spec/validate_house_next.py            # validate + redraw spec/plan_next_*.png, exit 1 on any error
    python spec/validate_house_next.py --no-draw

Checks (same style as validate_house.py, per level): room polygons closed / CCW / non-overlapping; every polygon edge on a
wall face, a chamfer face or a recess; walls reference existing rooms; openings on their wall, inside its length and height,
not overlapping, connecting rooms the wall separates, with the level change they claim; doors onto exterior zones.
New: stairs flights (risers x rise = floor difference, riser positions, headroom under the flight above); reachability from
the vestibule through doors, arches, hatches and flights; level stacking (floor above >= ceiling below + 0.10); envelope
(contiguous in z, upper levels inside lower ones, rooms inside, external walls on it); facades list every outside opening on
its plane; roof planes above the top ceilings; balcony, exterior steps, shed.
Needs shapely + matplotlib.
"""
import json, math, sys
from pathlib import Path
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

HERE = Path(__file__).parent
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SRC = Path(ARGS[0]) if ARGS else HERE / "house.next.json"
H = json.loads(SRC.read_text(encoding="utf-8"))
LEVELS = [l["id"] for l in H["levels"]]
rooms = {r["id"]: r for r in H["rooms"]}
walls = {w["id"]: w for w in H["walls"]}
opens = {o["id"]: o for o in H["openings"]}
feats = H["features"]
flights = {s["id"]: s for s in H["stairs"]}
EXT, ROOF = H["exterior"], H["roof"]
errs = []
TOL = 0.02
PASSABLE = {"door", "double_door", "arch", "french_door", "opening", "hatch"}
TYPES = PASSABLE | {"window", "bay_window"}
PSEUDO = {"outside", "void"}


def err(msg):
    errs.append(msg)


def wall_frame(w):
    (ax, ay), (bx, by) = w["a"], w["b"]
    L = math.hypot(bx - ax, by - ay)
    return ax, ay, (bx - ax) / L, (by - ay) / L, L


def along_perp(w, p):
    ax, ay, ux, uy, L = wall_frame(w)
    dx, dy = p[0] - ax, p[1] - ay
    return dx * ux + dy * uy, dx * -uy + dy * ux, L


def plane_z(pl, x, y):
    z = pl["z"]
    return z["c0"] + z["cx"] * x + z["cy"] * y


def roof_z(x, y, ground=False):
    zs = [plane_z(p, x, y) for p in ROOF["planes"]
          if (p.get("level") == "G") == ground and Polygon(p["polygon"]).buffer(1e-6).contains(Point(x, y))]
    return max(zs) if zs else None


def ceil_at(r, x, y):
    c = r.get("ceiling") or {}
    if c.get("type") == "under_roof":
        z = roof_z(x, y)
        return None if z is None else z + c["offset"]
    z = r["ceilingZ"]
    if c.get("type") == "planes":
        zs = [plane_z(p, x, y) for p in c["planes"] if Polygon(p["polygon"]).buffer(1e-6).contains(Point(x, y))]
        z = min(zs) if zs else z
    for cz in r.get("ceilingZones", []):
        if Polygon(cz["polygon"]).buffer(1e-6).contains(Point(x, y)):
            z = min(z, cz["z"])
    return z


def floor_at(r, x, y):
    z = r["floorZ"]
    for f in feats:
        if f["type"] == "floor_step" and f.get("room") == r["id"]:
            lx = f["line"][0][0]
            if (f["lowSide"] == "east" and x > lx) or (f["lowSide"] == "west" and x < lx):
                z = f["zLow"]
    return z


def samples(poly, step=0.2):
    x0, y0, x1, y1 = poly.bounds
    pts = []
    for i in range(int((x1 - x0) / step) + 1):
        for j in range(int((y1 - y0) / step) + 1):
            p = Point(x0 + step / 2 + i * step, y0 + step / 2 + j * step)
            if poly.contains(p):
                pts.append((p.x, p.y))
    return pts or [(poly.representative_point().x, poly.representative_point().y)]


# ---------------------------------------------------------------- 1. rooms
polys = {}
for rid, r in rooms.items():
    p = Polygon(r["polygon"])
    polys[rid] = p
    if r.get("level") not in LEVELS:
        err(f"room {rid}: bad level {r.get('level')}")
    if len(r["polygon"]) < 3 or not p.is_valid:
        err(f"room {rid}: invalid polygon")
    if not p.exterior.is_ccw:
        err(f"room {rid}: polygon is not counter-clockwise")
    if r["kind"] != "exterior" and not r["ceilingZ"] > r["floorZ"]:
        err(f"room {rid}: ceilingZ <= floorZ")
ids = list(polys)
for i, a in enumerate(ids):
    for b in ids[i + 1:]:
        if rooms[a]["level"] == rooms[b]["level"] and polys[a].intersection(polys[b]).area > 1e-4:
            err(f"rooms {a} and {b} overlap by {polys[a].intersection(polys[b]).area:.3f} m2")

# ---------------------------------------------------------------- 2. walls
for wid, w in walls.items():
    if w.get("level") not in LEVELS:
        err(f"wall {wid}: bad level")
    if math.dist(w["a"], w["b"]) < 0.05:
        err(f"wall {wid}: zero length")
    if abs(w["a"][0] - w["b"][0]) > 1e-6 and abs(w["a"][1] - w["b"][1]) > 1e-6:
        err(f"wall {wid}: not axis-aligned (use a chamfer feature for diagonals)")
    for r in w["rooms"] + w.get("roomsBelow", []):
        if r not in PSEUDO and r not in rooms:
            err(f"wall {wid}: unknown room {r}")
    for r in w["rooms"]:
        if r in rooms and rooms[r]["level"] != w["level"]:
            err(f"wall {wid}: room {r} is on another level")
    t = w["thickness"]
    if w.get("virtual"):
        if t != 0:
            err(f"wall {wid}: virtual wall must have thickness 0")
    elif not 0.08 <= t <= 0.70:
        err(f"wall {wid}: thickness {t} out of range")

# ---------------------------------------------------------------- 3. polygon edges on wall faces / chamfers / recesses
recesses = {lv: [Polygon(f["polygon"]).buffer(TOL) for f in feats if f["type"] == "recess" and f["level"] == lv] for lv in LEVELS}
chamfers = [f for f in feats if f["type"] == "chamfer"]
for f in chamfers:
    (ax, ay), (bx, by) = f["face"]
    if abs(abs(bx - ax) - abs(by - ay)) > 0.03:
        err(f"chamfer {f['id']}: face is not at 45 degrees")


def on_wall_face(p, rid):
    for w in walls.values():
        if rid not in w["rooms"]:
            continue
        s, d, L = along_perp(w, p)
        if -0.40 <= s <= L + 0.40 and abs(abs(d) - w["thickness"] / 2) <= TOL:
            return True
    return any(rc.contains(Point(p)) for rc in recesses[rooms[rid]["level"]])


def is_chamfer(a, b, rid):
    for f in chamfers:
        if rid in f["rooms"] and f["level"] == rooms[rid]["level"]:
            fa, fb = f["face"]
            if (math.dist(a, fa) < TOL and math.dist(b, fb) < TOL) or (math.dist(a, fb) < TOL and math.dist(b, fa) < TOL):
                return True
    return False


for rid, r in rooms.items():
    if r["kind"] in ("void", "exterior"):          # bounded by roof planes / railings
        continue
    pts = r["polygon"]
    for i, a in enumerate(pts):
        b = pts[(i + 1) % len(pts)]
        if is_chamfer(a, b, rid):
            continue
        for k in (0.1, 0.3, 0.5, 0.7, 0.9):
            p = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
            if not on_wall_face(p, rid):
                err(f"room {rid}: edge {a}->{b} not on a wall face near {p[0]:.2f},{p[1]:.2f}")
                break

# ---------------------------------------------------------------- 4. openings
zones = {z["id"]: z for z in EXT["zones"]}
adj = {rid: set() for rid in rooms}
spans = {}
for oid, o in opens.items():
    if o["type"] not in TYPES:
        err(f"opening {oid}: unknown type {o['type']}")
    w = walls.get(o["wall"])
    if not w:
        err(f"opening {oid}: unknown wall {o['wall']}")
        continue
    if o["level"] != w["level"]:
        err(f"opening {oid}: level differs from its wall")
    s, d, L = along_perp(w, o["center"])
    if abs(d) > 0.01:
        err(f"opening {oid}: centre is {abs(d):.3f} m off the centreline of {o['wall']}")
    if s - o["width"] / 2 < -1e-6 or s + o["width"] / 2 > L + 1e-6:
        err(f"opening {oid}: extends past the end of {o['wall']} (s={s:.2f}, L={L:.2f})")
    for s0, s1, other in spans.get(o["wall"], []):
        if s - o["width"] / 2 < s1 - 1e-6 and s + o["width"] / 2 > s0 + 1e-6:
            err(f"opening {oid}: overlaps {other} on {o['wall']}")
    spans.setdefault(o["wall"], []).append((s - o["width"] / 2, s + o["width"] / 2, oid))
    sides = set(w["rooms"]) | set(w.get("roomsBelow", []))
    for r in o["connects"]:
        if r not in PSEUDO and r not in rooms:
            err(f"opening {oid}: unknown room {r}")
        elif r in rooms and rooms[r]["kind"] == "exterior":
            if "outside" not in sides:
                err(f"opening {oid}: {r} is exterior but wall {o['wall']} has no outside face")
        elif r not in sides:
            err(f"opening {oid}: {r} is not a side of wall {o['wall']}")
    real = [r for r in o["connects"] if r in rooms]
    if real and not any(abs(rooms[r]["floorZ"] - o["floorZ"]) < 1e-6 for r in real) and o["id"] != "d_basement":
        err(f"opening {oid}: floorZ {o['floorZ']} is not the floor of a room it connects")
    top = o["floorZ"] + o["sill"] + o["height"]
    if not w.get("virtual") and top > w["baseZ"] + w["height"] + 1e-6:
        err(f"opening {oid}: top {top:.2f} is above its wall ({w['baseZ'] + w['height']:.2f})")
    if o["floorZ"] + o["sill"] < w["baseZ"] - 1e-6 and not w.get("virtual"):
        err(f"opening {oid}: starts below its wall")
    if o["type"] in ("door", "double_door", "french_door", "hatch"):
        if o["hinge"] not in ("left", "right", "both", "none"):
            err(f"opening {oid}: bad hinge {o['hinge']}")
        if o["hinge"] != "none" and o["swingInto"] not in o["connects"]:
            err(f"opening {oid}: swingInto must be one of connects")
    a, b = o["connects"]
    if o["type"] in PASSABLE:
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
            if a != b and "stairwell" not in (rooms[a]["kind"], rooms[b]["kind"]):
                dz = abs(rooms[a]["floorZ"] - rooms[b]["floorZ"])
                if abs(dz - o.get("step", 0)) > 1e-6:
                    err(f"opening {oid}: floors differ by {dz:.3f} but step is {o.get('step', 0)}")
        if "outside" in (a, b) and o["type"] != "opening":
            zn = zones.get(o.get("outsideZone"))
            if not zn:
                err(f"opening {oid}: door to the outside needs an outsideZone")
            else:
                ax, ay, ux, uy, _ = wall_frame(w)
                inside = polys[real[0]]
                for sg in (1, -1):
                    q = (o["center"][0] - uy * sg * (w["thickness"] / 2 + 0.3), o["center"][1] + ux * sg * (w["thickness"] / 2 + 0.3))
                    if not inside.buffer(0.02).contains(Point(q)) and not Polygon(zn["polygon"]).buffer(0.05).contains(Point(q)):
                        err(f"opening {oid}: does not open onto zone {zn['id']}")

# ---------------------------------------------------------------- 5. stairs flights
STRUCT, HEADROOM = 0.25, 1.95


def riser_ys(s):
    """y of the straight risers of a flight running along Y."""
    n = s.get("straightRisers")
    if not n:
        return []
    return [s["firstStraightRiserY"] + s["direction"][1] * s["going"] * i for i in range(n)]


def tread_z(s, y):
    """Level you stand on at y (straight part), counting winders before the straight risers."""
    sg = 1 if s["toZ"] > s["fromZ"] else -1
    d = s["direction"][1]
    passed = sum(1 for ry in riser_ys(s) if (y - ry) * d >= -1e-9)
    return s["fromZ"] + sg * (s.get("risersBeforeStraight", 0) + passed) * s["rise"]


for sid, s in flights.items():
    if abs(s["risers"] * s["rise"] - abs(s["toZ"] - s["fromZ"])) > 1e-6:
        err(f"stairs {sid}: {s['risers']} x {s['rise']} != |{s['toZ']} - {s['fromZ']}|")
    for end, zk in (("fromRoom", "fromZ"), ("toRoom", "toZ")):
        r = rooms.get(s[end])
        if not r:
            err(f"stairs {sid}: unknown {end} {s[end]}")
        elif abs(r["floorZ"] - s[zk]) > 1e-6:
            err(f"stairs {sid}: {zk} {s[zk]} != floorZ of {s[end]} ({r['floorZ']})")
    for t in s.get("through", []):
        if t not in rooms:
            err(f"stairs {sid}: unknown through room {t}")
    for v in s.get("viaOpenings", []):
        if v not in opens:
            err(f"stairs {sid}: unknown opening {v}")
    ys = riser_ys(s)
    if ys:
        if abs(ys[-1] - s["lastStraightRiserY"]) > 0.011:
            err(f"stairs {sid}: riser positions do not add up ({ys[-1]:.3f} vs {s['lastStraightRiserY']})")
        if s.get("risersBeforeStraight", 0) + len(ys) + s.get("risersAfterStraight", 0) != s["risers"]:
            err(f"stairs {sid}: winder + straight risers != risers")
        well = unary_union([polys[t] for t in s.get("through", []) if t in polys]).buffer(0.03)
        x = s["start"][0]
        if not all(well.contains(Point(x, y)) for y in ys):
            err(f"stairs {sid}: risers leave the stairwell rooms {s.get('through')}")
    up = flights.get(s.get("above", ""))
    if s.get("above") and not up:
        err(f"stairs {sid}: unknown flight above {s['above']}")
    if up and ys and riser_ys(up):
        uy = riser_ys(up)
        lo, hi = max(min(ys), min(uy)), min(max(ys), max(uy))
        for k in range(11):
            y = lo + (hi - lo) * k / 10
            clear = tread_z(up, y) - STRUCT - tread_z(s, y)
            if clear < HEADROOM:
                err(f"stairs {sid}: headroom {clear:.2f} under {up['id']} at y {y:.2f}")
    for a, b in zip([s["fromRoom"]] + s.get("through", []), s.get("through", []) + [s["toRoom"]]):
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)

# ---------------------------------------------------------------- 6. reachability from the vestibule
seen, todo = {"vestibule"}, ["vestibule"]
while todo:
    for n in adj[todo.pop()]:
        if n not in seen:
            seen.add(n)
            todo.append(n)
for rid in rooms:
    if rid not in seen:
        err(f"room {rid}: not reachable from the vestibule")

# ---------------------------------------------------------------- 7. level stacking: floor above >= ceiling below + 0.10
MIN_ZONE = 0.10
for a, ra in rooms.items():
    if ra["kind"] in ("stairwell", "exterior"):
        continue
    for b, rb in rooms.items():
        if a == b or rb["kind"] == "stairwell" or rb["floorZ"] <= ra["floorZ"] or ra["level"] == rb["level"]:
            continue
        inter = polys[a].intersection(polys[b])
        if inter.area < 0.02:
            continue
        geoms = [g for g in getattr(inter, "geoms", [inter]) if g.geom_type == "Polygon"]
        worst = min(floor_at(rb, x, y) - ceil_at(ra, x, y) for g in geoms for x, y in samples(g))
        if worst < MIN_ZONE - 1e-6:
            err(f"stacking: {b} floor is only {worst:.2f} above the ceiling of {a}")

# ---------------------------------------------------------------- 8. envelope: contiguous, stacked, rooms inside, walls on it
env = {lv: [] for lv in LEVELS}
for blk in EXT["envelope"]["blocks"]:
    lv = blk["levels"]
    for lo, hi in zip(lv, lv[1:]):
        if abs(lo["z"][1] - hi["z"][0]) > 1e-6:
            err(f"envelope {blk['id']}: level {lo['level']} top {lo['z'][1]} != level {hi['level']} base {hi['z'][0]}")
    for l in lv:
        p = Polygon(l["polygon"])
        if not p.is_valid:
            err(f"envelope {blk['id']} level {l['level']}: invalid polygon")
        env[l["level"]].append(p)
env = {k: unary_union(v) for k, v in env.items()}
for lo, hi in zip(LEVELS[1:], LEVELS[2:]):                         # G -> 1 -> 2 (the basement is below ground)
    over = env[hi].difference(env[lo].buffer(0.01)).area
    if over > 1e-3:
        err(f"envelope: level {hi} oversails level {lo} by {over:.2f} m2")
for rid, r in rooms.items():
    if r["kind"] != "exterior" and polys[rid].difference(env[r["level"]].buffer(0.03)).area > 1e-3:
        err(f"room {rid}: outside the level {r['level']} envelope")
for wid, w in walls.items():
    if w["kind"] in ("external", "party") and not w.get("aboveRoof"):
        ax, ay, ux, uy, L = wall_frame(w)
        mid = (ax + ux * L / 2, ay + uy * L / 2)
        faces = [Point(mid[0] - uy * sg * w["thickness"] / 2, mid[1] + ux * sg * w["thickness"] / 2) for sg in (1, -1)]
        if min(f.distance(env[w["level"]].boundary) for f in faces) > TOL:
            err(f"wall {wid}: {w['kind']} wall is not on the level {w['level']} envelope")
STACKS = {"stair flank wall (x 0.99..1.25)": ["w_b_spine", "w_stair_kitchen", "w_stair_gbath_b", "w_well_e_2"],
          "west party wall": ["w_party_w_hall", "w_party_w_1b", "w_party_w_2c"],
          "east wall": ["w_party_e_kitchen", "w_east_1b", "w_east_2b"],
          "flank wall": ["w_flank_utility", "w_flank_1_yellow", "w_flank_2_purple"],
          "rear wall": ["w_dining_n", "w_rear_1", "w_rear_2"],
          "old rear wall of the main house": ["w_arch", "w_main_rear_1a", "w_addition_s_2"],
          "upper arch wall": ["w_arch1", "w_arch2"]}
for name, ws in STACKS.items():
    for a, b in zip(ws, ws[1:]):
        wa, wb = walls[a], walls[b]
        k = 0 if abs(wa["a"][0] - wa["b"][0]) < 1e-6 else 1          # coordinate across the wall
        lo = max(wa["a"][k] - wa["thickness"] / 2, wb["a"][k] - wb["thickness"] / 2)
        hi = min(wa["a"][k] + wa["thickness"] / 2, wb["a"][k] + wb["thickness"] / 2)
        if hi - lo < 0.08:
            err(f"stack '{name}': {b} does not stand on {a}")

# ---------------------------------------------------------------- 9. facades
listed = {}
for fc in EXT["facades"]:
    k = 0 if fc["axis"] == "x" else 1
    for oid in fc["openings"]:
        o = opens.get(oid)
        if not o:
            err(f"facade {fc['id']}: unknown opening {oid}")
            continue
        if oid in listed:
            err(f"opening {oid}: in two facades")
        listed[oid] = fc["id"]
        w = walls[o["wall"]]
        if min(abs(w["a"][k] + sg * w["thickness"] / 2 - fc["at"]) for sg in (1, -1)) > 0.011:
            err(f"facade {fc['id']}: wall of {oid} has no face on {fc['axis']} = {fc['at']}")
        c = o["center"][1 - k]
        if not (fc["extent"][0] - 1e-6 <= c - o["width"] / 2 and c + o["width"] / 2 <= fc["extent"][1] + 1e-6):
            err(f"facade {fc['id']}: {oid} is outside the facade extent")
for oid, o in opens.items():
    out = "outside" in o["connects"] or any(r in rooms and rooms[r]["kind"] == "exterior" for r in o["connects"])
    if out and oid not in listed:
        err(f"opening {oid}: faces outside but is in no facade")

# ---------------------------------------------------------------- 10. roof above the ceilings
top = LEVELS[-1]
for rid, r in rooms.items():
    if r["level"] != top:
        if r["level"] == "G":                                  # ground-floor parts with nothing above need a ground roof
            lone = polys[rid].difference(env["1"].buffer(0.01))
            for g in [g for g in getattr(lone, "geoms", [lone]) if g.geom_type == "Polygon" and g.area > 0.05]:
                for x, y in samples(g):
                    z = roof_z(x, y, ground=True)
                    if z is None or z < ceil_at(r, x, y) + 0.10:
                        err(f"roof: ground-floor room {rid} at {x:.2f},{y:.2f} is not under a ground-level roof plane")
                        break
        continue
    for x, y in samples(polys[rid]):
        z = roof_z(x, y)
        if z is None:
            err(f"roof: {rid} at {x:.2f},{y:.2f} is under no roof plane")
            break
        c = ceil_at(r, x, y)
        if (r.get("ceiling") or {}).get("type") != "under_roof" and z < c + 0.10:
            err(f"roof: {rid} ceiling {c:.2f} at {x:.2f},{y:.2f} is above / too close to the roof ({z:.2f})")
            break
for f in feats:
    if f["type"] in ("roof_opening", "roof_window"):
        pl = next((p for p in ROOF["planes"] if p["id"] == f["roofPlane"]), None)
        if not pl or Polygon(f["polygon"]).difference(Polygon(pl["polygon"])).area > 1e-4:
            err(f"feature {f['id']}: not inside roof plane {f['roofPlane']}")
if abs(roof_z(2.0, 5.0 - 1e-6) - ROOF["ridge"]["z"]) > 0.02:
    err("roof: ridge z does not match the planes")

# ---------------------------------------------------------------- 11. balcony, exterior zones and steps, shed
for f in feats:
    if f["type"] == "balcony":
        r, door = rooms[f["room"]], next(o for o in opens.values() if f["room"] in o["connects"])
        under = [o for o in opens.values() if o["level"] == "G" and walls[o["wall"]]["id"] == "w_dining_n"]
        rear = next(fc for fc in EXT["facades"] if fc["id"] == "rear_R")
        ys = [p[1] for p in f["polygon"]]
        if abs(min(ys) - rear["at"]) > 1e-6:
            err("balcony: deck does not start on the rear wall face")
        inner = next(c for c in door["connects"] if c != f["room"])
        if abs(f["deckTopZ"] - r["floorZ"]) > 1e-6 or f["deckTopZ"] > rooms[inner]["floorZ"]:
            err("balcony: deck level inconsistent with the room / bedroom floor")
        head = max(max(o["sill"] + o["height"], (o.get("transom") or {}).get("height", 0)) for o in under)
        if f["deckTopZ"] - f["deckThickness"] < head + 0.3:
            err("balcony: deck underside too close to the ground-floor door head")
        for px, _ in f["supports"]["wallPosts"]:
            for o in under:
                if abs(px - o["center"][0]) < o["width"] / 2 + 0.03:
                    err(f"balcony: wall post at x {px} stands in front of {o['id']}")
zp = {}
for z in EXT["zones"]:
    p = Polygon(z["polygon"])
    zp[z["id"]] = p
    if not p.is_valid:
        err(f"zone {z['id']}: invalid polygon")
zi = [z for z in EXT["zones"] if not z.get("overlay")]
for i, a in enumerate(zi):
    for b in zi[i + 1:]:
        if zp[a["id"]].intersection(zp[b["id"]]).area > 0.05:
            err(f"zones {a['id']} and {b['id']} overlap")
    if a["group"] != "street" and zp[a["id"]].intersection(env["G"]).area > 0.05:
        err(f"zone {a['id']}: overlaps the house")
shed = EXT["buildings"][0]
srooms = {r["id"]: r for r in shed["rooms"]}
for st in EXT["steps"]:
    if abs(st["risers"] * st["rise"] - (st["toZ"] - st["fromZ"])) > 1e-6:
        err(f"exterior step {st['id']}: risers x rise != level difference")
    if abs(zones[st["fromZone"]]["z"] - st["fromZ"]) > 1e-6:
        err(f"exterior step {st['id']}: fromZ is not the level of zone {st['fromZone']}")
    tz = zones[st["toZone"]]["z"] if "toZone" in st else (rooms.get(st["toRoom"]) or srooms[st["toRoom"]])["floorZ"]
    if abs(tz - st["toZ"]) > 1e-6:
        err(f"exterior step {st['id']}: toZ mismatch")
for oid, o in opens.items():
    if o.get("outsideZone") and not any(st.get("opening") == oid for st in EXT["steps"]):
        err(f"opening {oid}: no exterior step / threshold entry")
so = Polygon(shed["outline"])
swalls = {w["id"]: w for w in shed["walls"]}
for r in shed["rooms"]:
    if not Polygon(r["polygon"]).within(so.buffer(0.01)):
        err(f"shed room {r['id']}: outside the shed outline")
for o in shed["openings"]:
    s, d, L = along_perp(swalls[o["wall"]], o["center"])
    if abs(d) > 0.01 or s - o["width"] / 2 < -1e-6 or s + o["width"] / 2 > L + 1e-6:
        err(f"shed opening {o['id']}: not on its wall")
if so.intersection(env["G"]).area > 0 or not so.within(Polygon(EXT["plot"]["polygon"]).buffer(0.05)):
    err("shed: outline clashes with the house or leaves the plot")

# ---------------------------------------------------------------- 12. solids clear of stair wells; keyed offsets (verification T1, T2)
SOLID = {"boxing", "pier", "pilaster", "chimney_breast", "nib", "poche"}
for v in [f for f in feats if f["type"] == "floor_void"]:
    for f in feats:
        if f["type"] in SOLID and f["level"] == v["level"] and Polygon(f["polygon"]).intersection(Polygon(v["polygon"])).area > 1e-4:
            if f.get("z", [v["z"]])[-1] > v["z"] + 1e-6:              # solid above the level the void is cut in
                err(f"feature {f['id']}: solid stands in the open well {v['id']}")
for f in feats:
    k = f.get("offsetFromWall")
    if k:
        w = walls[k["wall"]]
        d = min(abs(abs(along_perp(w, p)[1]) - w["thickness"] / 2) for p in f["polygon"])   # nearest vertex to a wall face
        if abs(d - k["distance"]) > 0.011:
            err(f"feature {f['id']}: is {d:.2f} from {k['wall']}, expected {k['distance']}")

if errs:
    print(f"FAIL: {len(errs)} error(s)")
    for e in errs:
        print("  -", e)
else:
    print(f"OK: {len(rooms)} rooms on {len(LEVELS)} levels, {len(walls)} walls, {len(opens)} openings, {len(feats)} features, "
          f"{len(flights)} flights; all rooms reachable from the vestibule")
if "--no-draw" in sys.argv:
    sys.exit(1 if errs else 0)

# ================================================================ previews (matplotlib)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly

PASTEL = ["#f3e9c9", "#f2cfc4", "#cfd6e6", "#dfe8d8", "#e6d3bd", "#d9e2ec", "#e3d5ea", "#d5d5db", "#f6e0b5", "#cfe6e2"]
INK, DOOR, WIN, RED = "#3c3c3c", "#b05a00", "#1f6fd0", "#b03030"
LNAME = {l["id"]: l["name"] for l in H["levels"]}


def end_ext(w, end, ws):
    _, _, ux, uy, _ = wall_frame(w)
    e = 0.0
    for o in ws:
        if o is w or o.get("virtual"):
            continue
        _, _, vx, vy, _ = wall_frame(o)
        s, d, L = along_perp(o, w[end])
        if abs(ux * vx + uy * vy) < 0.1 and abs(d) < 0.01 and -0.01 <= s <= L + 0.01:
            e = max(e, o["thickness"] / 2)
    return e


def wall_quad(w, ws, s0=None, s1=None, grow=0.0):
    ax, ay, ux, uy, L = wall_frame(w)
    s0 = -end_ext(w, "a", ws) if s0 is None else s0
    s1 = L + end_ext(w, "b", ws) if s1 is None else s1
    h = w["thickness"] / 2 + grow
    return [(ax + ux * s - uy * n, ay + uy * s + ux * n) for s, n in ((s0, h), (s1, h), (s1, -h), (s0, -h))]


def draw_flight(ax, s):
    if s["kind"] == "steps":
        for ln in s["riserLines"]:
            ax.plot(*zip(*ln), color=RED, lw=1.4)
        return
    hw, x, ys = s["width"] / 2, s["start"][0], riser_ys(s)
    for y in ys:
        ax.plot([x - hw, x + hw], [y, y], color="#666", lw=0.7)
    ax.annotate("", xy=(x, ys[-1]), xytext=(x, ys[0]), arrowprops=dict(arrowstyle="->", color=RED, lw=1))
    ax.text(x, (ys[0] + ys[-1]) / 2, ("UP" if s["toZ"] > s["fromZ"] else "DN") + f" {s['risers']}R", color=RED, fontsize=6,
            ha="center", va="center", rotation=90, backgroundcolor="white")


def draw_level(lv):
    rs = [r for r in rooms.values() if r["level"] == lv]
    ws = [w for w in walls.values() if w["level"] == lv]
    fig, ax = plt.subplots(figsize=(9, 17))
    for i, r in enumerate(rs):
        ax.add_patch(MPoly(r["polygon"], closed=True, fc=PASTEL[i % len(PASTEL)], ec="none",
                           hatch="//" if r["kind"] in ("void", "exterior") else None, alpha=0.9))
    for f in feats:
        if f["level"] != lv:
            continue
        if f["type"] in ("poche", "pier", "pilaster", "chimney_breast", "nib"):
            ax.add_patch(MPoly(f["polygon"], closed=True, fc=INK, ec=INK))
        elif f["type"] == "chamfer":
            ax.plot(*zip(*f["face"]), color=INK, lw=3)
        elif f["type"] == "floor_void":
            ax.add_patch(MPoly(f["polygon"], closed=True, fc="none", ec="#888", hatch="xx", lw=0.5))
        elif f["type"] in ("roof_opening", "roof_window"):
            ax.add_patch(MPoly(f["polygon"], closed=True, fc="#bfe6ff", ec=WIN, ls="--", lw=1))
        elif f["type"] == "floor_step":
            ax.plot(*zip(*f["line"]), color=RED, lw=1.4)
        elif "polygon" in f:
            ax.add_patch(MPoly(f["polygon"], closed=True, fc="none", ec="#8a6d3b", lw=0.8))
    for w in ws:
        if w.get("virtual"):
            ax.plot(*zip(w["a"], w["b"]), color="#999", lw=0.6, ls=":")
        else:
            ax.add_patch(MPoly(wall_quad(w, ws), closed=True, fc=INK, ec=INK, lw=0.3))
    for o in opens.values():
        if o["level"] != lv:
            continue
        w = walls[o["wall"]]
        wx, wy, ux, uy, L = wall_frame(w)
        s, _, _ = along_perp(w, o["center"])
        s0, s1 = s - o["width"] / 2, s + o["width"] / 2
        pt = lambda ss, n=0.0: (wx + ux * ss - uy * n, wy + uy * ss + ux * n)
        if not w.get("virtual"):
            ax.add_patch(MPoly(wall_quad(w, ws, s0, s1, 0.01), closed=True, fc="white", ec="white"))
        if o["type"] in ("window", "bay_window"):
            for n in (-0.03, 0.03):
                ax.plot(*zip(pt(s0, n), pt(s1, n)), color=WIN, lw=1.5)
        elif o["type"] in ("arch", "opening"):
            ax.plot(*zip(pt(s0), pt(s1)), color=RED, lw=0.8, ls="--")
        elif o["hinge"] == "none":                                   # sliding / pocket door
            sx, sy = o.get("slideToward", [-ux, -uy])                    # leaf drawn half-slid into its pocket
            e, sg = (s1, 1) if sx * ux + sy * uy > 0 else (s0, -1)
            ax.plot(*zip(pt(e - sg * o["width"] * 0.4), pt(e + sg * o["width"] * 0.6)), color=DOOR, lw=2.5)
        else:
            tgt = o["swingInto"]
            inner = next((r for r in o["connects"] if r in rooms and rooms[r]["kind"] != "exterior"), None)
            if tgt in polys and rooms[tgt]["kind"] != "exterior":
                side = 1 if polys[tgt].buffer(0.02).contains(Point(pt(s, w["thickness"] / 2 + 0.1))) else -1
            else:                                                    # swings outside: away from the inside room
                side = -1 if polys[inner].buffer(0.02).contains(Point(pt(s, w["thickness"] / 2 + 0.1))) else 1
            if o["hinge"] == "both":
                leaves = [(s0, 1, o["width"] / 2), (s1, -1, o["width"] / 2)]
            else:
                ha = along_perp(w, o["hingeAt"])[0]
                leaves = [(ha, 1 if abs(ha - s0) < abs(ha - s1) else -1, o["width"])]
            for hs, dirn, lw_ in leaves:
                ax.plot(*zip(pt(hs), pt(hs, side * lw_)), color=DOOR, lw=1.5)
                ax.plot(*zip(*[pt(hs + dirn * lw_ * math.cos(a), side * lw_ * math.sin(a)) for a in [i * math.pi / 24 for i in range(13)]]),
                        color=DOOR, lw=0.6)
    for s in flights.values():
        if s["level"] == lv:
            draw_flight(ax, s)
    if lv == top:
        for p in ROOF["planes"]:
            if p.get("level") != "G":
                ax.add_patch(MPoly(p["polygon"], closed=True, fc="none", ec="#2a8", ls="-.", lw=0.7))
        ax.plot(*zip(*ROOF["ridge"]["line"]), color="#2a8", lw=1.5)
    for r in rs:
        c = polys[r["id"]].representative_point()
        sz = r.get("size")
        ceil = "open" if r["ceilingZ"] is None else f"CL {r['ceilingZ']:+.2f}"
        ax.text(c.x, c.y, f"{r['id']}\n" + (f"{sz[0]:.2f} x {sz[1]:.2f}\n" if sz else "") + f"FFL {r['floorZ']:+.2f}  {ceil}",
                fontsize=5.5, ha="center", va="center")
    B = H["bounds"]
    ax.set_xlim(B["minX"] - 0.6, B["maxX"] + 0.6)
    ax.set_ylim(B["minY"] - 0.8, B["maxY"] + 1.4)
    ax.set_aspect("equal")
    ax.set_title(f"house.next.json - level {lv}: {LNAME[lv]}   (+Y = rear, +X = right walking in; world Z)", fontsize=9)
    ax.grid(True, lw=0.2, color="#ccc")
    ax.set_xticks(range(-1, 6))
    ax.set_yticks(range(0, 19))
    ax.tick_params(labelsize=6)
    fig.savefig(HERE / f"plan_next_{lv}.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


def draw_site():
    COL = {"grass": "#b9d7a0", "soil_lavender": "#c9b6dc", "asphalt": "#bdbdbd", "concrete_flags": "#dedede"}
    fig, ax = plt.subplots(figsize=(8, 19))
    for z in EXT["zones"]:
        col = COL.get(z["surface"], "#8a6a55" if "deck" in z["surface"] or "timber" in z["surface"] else
                      "#cf9a86" if "clay" in z["surface"] else "#e2ddd0")
        ax.add_patch(MPoly(z["polygon"], closed=True, fc=col, ec="#777", lw=0.5))
        c = zp[z["id"]].representative_point()
        ax.text(c.x, c.y, f"{z['id']}\nZ {z['z']:+.2f}", fontsize=5, ha="center", va="center")
    for g in getattr(env["G"], "geoms", [env["G"]]):
        ax.add_patch(MPoly(list(g.exterior.coords), closed=True, fc="#f4f4f4", ec=INK, lw=1.5))
    for r in rooms.values():
        if r["level"] == "G" or r["kind"] == "exterior":
            ax.add_patch(MPoly(r["polygon"], closed=True, fc="none", ec="#999", lw=0.4, ls="--" if r["kind"] == "exterior" else "-"))
    ax.add_patch(MPoly(shed["outline"], closed=True, fc="#e9c9bd", ec=INK, lw=1.5))
    for r in shed["rooms"]:
        ax.add_patch(MPoly(r["polygon"], closed=True, fc="#f7efe9", ec="#777", lw=0.5))
        c = Polygon(r["polygon"]).representative_point()
        ax.text(c.x, c.y, f"{r['id']}\nFFL {r['floorZ']:+.2f}", fontsize=5, ha="center", va="center")
    for b in EXT["boundaries"]:
        if "line" in b:
            ax.plot(*zip(*b["line"]), color={"fence": "#7a5a3a", "gate": RED}.get(b["type"], INK), lw=2.5 if b["type"] != "gate" else 1.5)
        else:
            ax.add_patch(MPoly(b["polygon"], closed=True, fc=INK))
    for f in EXT["features"]:
        if f["type"] in ("car", "fire_pit"):
            (cx, cy), (L, wd) = f["center"], f["size"][:2]
            a = math.radians(f.get("yawDeg", 0))
            hx, hy = (wd / 2, L / 2) if f["type"] == "car" else (L / 2, wd / 2)
            q = [(cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)) for x, y in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy))]
            ax.add_patch(MPoly(q, closed=True, fc="#9aa3ad" if f["type"] == "car" else "#d8c58a", ec=INK, lw=0.6))
            ax.text(cx, cy, f["id"], fontsize=5, ha="center", va="center")
        elif f["type"] == "chimney":
            ax.add_patch(MPoly(f["polygon"], closed=True, fc="#a99873", ec=INK, lw=0.5))
    ax.add_patch(MPoly(EXT["plot"]["polygon"], closed=True, fc="none", ec=RED, ls="--", lw=0.8))
    S = H["siteBounds"]
    ax.set_xlim(S["minX"], S["maxX"])
    ax.set_ylim(S["minY"] - 0.5, S["maxY"] + 0.5)
    ax.set_aspect("equal")
    ax.set_title("house.next.json - site plan (zones with surface Z; red dashes = plot)", fontsize=9)
    ax.tick_params(labelsize=6)
    fig.savefig(HERE / "plan_next_site.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


def draw_section(xc=-0.25, xr=2.5):
    fig, ax = plt.subplots(figsize=(17, 8.5))
    ys = [i * 0.05 for i in range(-10, 360)]
    for i, r in enumerate(rooms.values()):
        cut = polys[r["id"]].intersection(LineString([(xc, -5), (xc, 30)]))
        for g in getattr(cut, "geoms", [cut]):
            if g.is_empty or g.geom_type != "LineString" or r["kind"] == "exterior":
                continue
            y0, y1 = g.bounds[1], g.bounds[3]
            n = max(2, int((y1 - y0) / 0.05))
            yy = [y0 + (y1 - y0) * k / n for k in range(n + 1)]
            topz = [ceil_at(r, xc, min(max(y, y0 + 1e-4), y1 - 1e-4)) or r["floorZ"] for y in yy]
            ax.add_patch(MPoly([(y0, r["floorZ"])] + list(zip(yy, topz)) + [(y1, r["floorZ"])], closed=True,
                               fc=PASTEL[i % len(PASTEL)], ec=INK, lw=0.8))
            ax.text((y0 + y1) / 2, r["floorZ"] + 0.9, f"{r['id']}\n{r['floorZ']:+.2f}", fontsize=6, ha="center")
    for xs, st in ((xc, "-"), (xr, "--")):
        pts = [(y, roof_z(xs, y)) for y in ys if roof_z(xs, y) is not None]
        ax.plot(*zip(*pts), color="#2a8", lw=1.4, ls=st, label=f"roof at x = {xs}")
    for rid, st in (("loft_office", ":"), ("green_bathroom", ":"), ("kitchen", ":"), ("basement", ":"), ("eaves_rear", ":")):
        r = rooms[rid]
        x0, y0, x1, y1 = polys[rid].bounds
        yy = [y0 + (y1 - y0) * k / 40 for k in range(41)]
        xs = min(max(xr, x0 + 0.05), x1 - 0.05)
        cz = [ceil_at(r, xs, min(max(y, y0 + 1e-4), y1 - 1e-4)) for y in yy]
        ax.plot([y0] + yy + [y1, y0], [r["floorZ"]] + cz + [r["floorZ"], r["floorZ"]], color="#777", lw=0.8, ls=st)
        ax.text((y0 + y1) / 2, r["floorZ"] + 0.35, f"({rid} beyond)", fontsize=5.5, ha="center", color="#555")
    for s in flights.values():
        ry = riser_ys(s)
        if not ry:
            if s["kind"] == "steps" and s.get("direction"):
                yy = [ln[0][1] for ln in s["riserLines"]]
                pts, z = [(yy[0] + 0.4, s["fromZ"])], s["fromZ"]
                for y in yy:
                    pts += [(y, z), (y, z + s["rise"])]
                    z += s["rise"]
                ax.plot(*zip(*(pts + [(yy[-1] - 0.4, z)])), color=RED, lw=1.2)
            continue
        sg, d = (1 if s["toZ"] > s["fromZ"] else -1), s["direction"][1]
        z = s["fromZ"] + sg * s.get("risersBeforeStraight", 0) * s["rise"]
        pts = [(ry[0] - d * 0.3, z)]
        for y in ry:
            pts += [(y, z), (y, z + sg * s["rise"])]
            z += sg * s["rise"]
        pts.append((ry[-1] + d * s["going"], z))
        ax.plot(*zip(*pts), color=RED, lw=1.2)
        ax.text(pts[len(pts) // 2][0], pts[len(pts) // 2][1] + 0.25, f"{s['id']} {s['risers']} x {s['rise']}", fontsize=6, color=RED)
    for l in H["levels"]:
        for nm, z in l["floors"].items():
            ax.axhline(z, color="#bbb", lw=0.3)
            ax.text(18.3, z, f"{l['id']}:{nm} {z:+.2f}", fontsize=5.5, va="center")
    ax.plot([-5.2, -0.12], [-0.06, -0.06], color="#555", lw=1)
    ax.plot([17.36, 23.4], [-0.05, -0.45], color="#555", lw=1)
    for y in (-0.12, 17.36):
        ax.axvline(y, color="#999", lw=0.5, ls=":")
    ax.set_xlim(-1.5, 20)
    ax.set_ylim(-2.8, 10)
    ax.set_aspect("equal")
    ax.set_xlabel("world Y (m): street <- -> garden")
    ax.set_ylabel("world Z (m)")
    ax.legend(fontsize=6, loc="upper right")
    ax.set_title(f"house.next.json - section looking east, cut at x = {xc} (hall / landings); stairs (x 0.15..0.99) projected in red; "
                 f"dotted = rooms beyond at x = {xr}", fontsize=9)
    fig.savefig(HERE / "plan_next_section.png", dpi=110, bbox_inches="tight")
    plt.close(fig)


if SRC.resolve() == (HERE / "house.next.json").resolve():
    for lv in LEVELS:
        draw_level(lv)
    draw_site()
    draw_section()
    print("previews: " + ", ".join(f"plan_next_{k}.png" for k in LEVELS + ["site", "section"]))
sys.exit(1 if errs else 0)
