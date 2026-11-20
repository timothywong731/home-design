"""Smoke test for footprints the Blender export will produce: every plan symbol of MULTILEVEL.md section 10 draws on
the sheet of its level (with and without a `level` field), unknown / unreadable records fall back to their outline,
spec fallback and export never double-draw, `front` vectors orient symbols, car yaw is read from the spec, title-block
cells fit any text, neighbours are dashed context inside the site window, and the drafter's self-checks still pass.

    python tools/plan/test_draft.py [--house PATH]      -> TEST OK   (default spec/house.json)
"""
import argparse, json, math, sys, tempfile
from pathlib import Path
from shapely.geometry import Point, Polygon, box as sbox

sys.path.insert(0, str(Path(__file__).parent))
import draft as D

R = lambda room, sym, x0, y0, x1, y1, level=None, front=None: dict(
    {"name": f"{room}.{sym}", "room": room, "plan_sym": sym, "obb": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]},
    **({"level": level} if level else {}), **({"front": front} if front is not None else {}))
RECS = [
    R("green_bedroom", "bed", 1.2, 2.75, 2.8, 4.8, front=[0, -1]), R("green_bedroom", "bedside", 0.65, 4.35, 1.1, 4.8, "1"),
    R("green_bedroom", "wardrobe", -0.65, 1.3, -0.05, 3.1, front=[1, 0, 0]), R("green_bedroom", "chest", 3.5, 4.3, 4.3, 4.8),
    R("green_bedroom", "bureau", 3.75, 2.0, 4.3, 3.0, front="N"), R("blue_bedroom", "desk", 2.2, 15.6, 3.1, 16.85, front=[0, 0]),
    R("blue_bedroom", "office_chair", 2.35, 15.0, 2.95, 15.55), R("blue_bedroom", "cabinet", -0.65, 15.5, -0.2, 16.5),
    R("blue_bedroom", "chair", 1.0, 15.0, 1.5, 15.5), R("blue_bedroom", "tv", 0.5, 13.0, 1.6, 13.06),
    R("blue_bedroom", "radiator", 3.0, 13.0, 3.8, 13.1), R("blue_bedroom", "frobnicator", 1.8, 13.4, 2.2, 13.8),
    R("blue_ensuite", "bath", 0.6, 11.35, 1.3, 13.0), R("blue_ensuite", "vanity", 2.0, 11.35, 3.0, 11.85),
    R("blue_ensuite", "wc", 2.4, 12.4, 2.9, 13.0), R("blue_ensuite", "basin", 1.6, 12.6, 2.1, 13.0),
    R("green_bathroom", "shower", 3.4, 7.8, 4.3, 8.7), R("bathroom2", "sauna", 1.9, 12.2, 3.1, 13.4),
    R("basement", "boiler", 3.0, 8.3, 3.6, 8.73), R("basement", "cylinder", 1.4, 8.1, 2.0, 8.7, "B"),
    R("basement", "rack", 1.3, 5.3, 3.3, 5.75), R("shed_workshop", "workbench", 0.0, 28.0, 2.0, 28.6),
    R("shed_workshop", "bench", 3.0, 26.0, 4.1, 26.5), R("front", "car", -0.07, -5.0, 1.63, -1.1, "X"),
    R("garden", "planter", 2.95, 18.2, 3.37, 20.05), R("garden", "fire_pit", 0.77, 21.76, 1.77, 22.76),
    R("garden", "trellis", -0.76, 17.85, -0.72, 19.65), R("front", "flagpole", 0.94, -0.3, 1.02, -0.22),
    R("garden", "condenser", 3.42, 15.0, 3.72, 15.8, "X"), R("garden", "bench", 2.0, 23.0, 3.2, 23.45, "X"),
    dict(R("facade", "pipe", 3.43, 12.3, 3.54, 12.41, "X"), name="facade.downpipe.1"), R("front", "bin", 3.9, -1.0, 4.5, -0.3, "X"),
    R("front", "pipe", 2.0, -0.6, 2.1, -0.5, "X"),             # a round post (lamp column): drawn, not labelled RWP
]
SKEW = dict(R("green_bedroom", "bed", 0, 0, 1, 1), name="green_bedroom.skewed",
            obb=[[1.0, 1.0], [2.0, 1.0], [2.9, 1.5], [1.9, 1.5]])           # valid, not a rectangle: symbols cannot read it

ap = argparse.ArgumentParser()
ap.add_argument("--house", default=str(D.ROOT / "spec" / "house.json"))
house = ap.parse_args().house
with tempfile.TemporaryDirectory() as tmp:
    fp = Path(tmp) / "footprints.json"
    fp.write_text(json.dumps(RECS + [SKEW]), encoding="utf-8")
    plan, checks = D.build(house, fp)
    D.self_check(plan, checks)
    sheets = {s["id"]: s for s in plan["sheets"]}
    for r in RECS + [SKEW]:                                     # every record drew something on its level's sheet
        lvl = D.rec_level(dict(r))
        bx = Polygon(r["obb"]).buffer(0.03)
        n = sum(any(bx.contains(Point(p)) for p in [e[k] for k in ("p1", "p2", "c") if k in e] + e.get("pts", []))
                for e in sheets[lvl]["entities"] if e["layer"] in ("A-FURN", "A-FLOR-FIXT"))
        assert n >= 1, (r["name"], lvl, n)
    assert {D.rec_level(dict(r)) for r in RECS} == {"B", "1", "2", "X"}
    X = sheets["X"]
    assert sum(e["type"] == "text" and e["text"] == "RWP" for e in X["entities"]) == 1, "pipe label: the downpipe only"

    # spec fallback vs export: an exported site item filed under another room replaces the spec item it covers
    fp.write_text(json.dumps([R("facade", "bin", 3.92, -0.74, 4.5, -0.16, "X")]), encoding="utf-8")
    recs, src = D.load_footprints(fp)
    exp = [Polygon(r["obb"]) for r in recs if r["src"] == "export"]
    spec = [Polygon(r["obb"]) for r in recs if r["src"] == "spec"]
    assert not [g for g in spec for e in exp if g.intersection(e).area > 0.3 * g.area], "spec and export double-draw"
    names = {r["name"] for r in recs}
    assert "front.bin.0" not in names and {"front.bin.1", "front.car_grey", "garden.fire_pit"} <= names, names

# front vectors: 2D / 3D accepted and normalised, zero / malformed dropped; a front orients the symbol
assert D.front_vec([0, 2, 0.5]) == [0, 1] and D.front_vec([3, 4]) == [0.6, 0.8]
assert all(D.front_vec(f) is None for f in (None, [0, 0], "N", [1], {"x": 1}, [float("nan"), 1]))
for f in ([0, -1], [0, 1], [1, 0]):
    _, _, v, w, d = D.local_frame({"obb": [[0, 0], [1.6, 0], [1.6, 2.0], [0, 2.0]], "plan_sym": "bed", "front": f}, [])
    assert v == tuple(f) and (w, d) == ((1.6, 2.0) if f[0] == 0 else (2.0, 1.6)), (f, v, w, d)

# cars: yawDeg read from the spec (nose-out: -Y at yaw 0), never a fixed skew
D.setup(house)
car = next(f for f in D.EXT["features"] if f["type"] == "car")
for yaw in (car.get("yawDeg", 0), 30):
    car["yawDeg"] = yaw
    rec = next(r for r in D.site_footprints() if r["name"] == "front." + car["id"])
    a = math.radians(yaw)
    assert math.dist(rec["front"], (math.sin(a), -math.cos(a))) < 1e-9, (yaw, rec["front"])

# title block: any text fits its cell (width with the raster slack, height under the caption)
for s in ("", "X", "MILLIMETRES", "A" * 300, "FFL " + " / ".join(["+3.420"] * 30), "SECOND FLOOR (LOFT) PLAN OF A LONG NAME"):
    for w, h, vh in ((42, 7, 2.0), (18, 7, 2.0), (100, 14, 4.5), (28, 8, 2.5)):
        fit = D.fit_cell(s, w, h, vh)
        assert " ".join(t for t, _ in fit) == s and len(fit) in (1, 2), (s, fit)
        sz = fit[0][1]
        assert all(D.tw(t, z) <= (w - 3.0) * 0.9 + 1e-9 and z <= vh for t, z in fit), (s, w, fit)
        assert sz * (1 + 1.6 * (len(fit) - 1)) <= h - 4.9 + 1e-9, (s, h, fit)
for sh in plan["sheets"]:                                       # ... and on every sheet no value runs into the next cell
    mm = int(sh["scale"].split(":")[1]) / 1000
    E = sh["entities"]
    vert = [e for e in E if e["layer"].startswith("A-ANNO-TTLB") and e["type"] in ("line", "polyline")]
    segs = [(a, b) for e in vert for a, b in ([(e["p1"], e["p2"])] if e["type"] == "line" else
            zip(e["pts"], e["pts"][1:] + ([e["pts"][0]] if e["closed"] else []))) if abs(a[0] - b[0]) < 1e-9]
    tb_top = max(max(a[1], b[1]) for a, b in segs if min(a[1], b[1]) < sh["sheetBounds"]["minY"] + 15 * mm)
    for e in E:
        if e["layer"] == "A-ANNO-TTLB" and e["type"] == "text" and e["p"][1] < tb_top and e.get("align") == "left":
            x1 = e["p"][0] + D.tw(e["text"], e["h"] * D.CAP)
            right = min(a[0] for a, b in segs if a[0] > e["p"][0] + 1e-9 and min(a[1], b[1]) <= e["p"][1] <= max(a[1], b[1]))
            assert x1 <= right - 0.5 * mm, (sh["id"], e["text"], x1, right)

# neighbours: light dashed context, only inside the site window
ctx = [e for e in X["entities"] if e["layer"] == "L-SITE-CTXT" and e["type"] == "polyline"]       # (the key sample is a line)
win = sbox(*D.site_window()).buffer(1e-6)
assert ctx and all(e.get("ls") == "dashed" and all(win.contains(Point(p)) for p in e["pts"]) for e in ctx)
assert sorted(D.SYMBOLS) == sorted(set(D.SYMBOLS))
print("TEST OK  %d symbols drawn on their sheets (+1 unreadable as its outline); fallback dedupe, front vectors, car yaw, "
      "title-block fit, neighbour context, self-checks pass" % len(RECS))
