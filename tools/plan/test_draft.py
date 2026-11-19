"""Smoke test for footprints the Blender export will produce: every plan symbol of MULTILEVEL.md section 10 draws on
the sheet of its level (with and without a `level` field), and the drafter's self-checks still pass.

    python tools/plan/test_draft.py [--house PATH]      -> TEST OK   (default: spec/house.json once it is schema 2,
                                                                      else spec/house.json)
"""
import argparse, json, sys, tempfile
from pathlib import Path
from shapely.geometry import Point, Polygon

sys.path.insert(0, str(Path(__file__).parent))
import draft as D

R = lambda room, sym, x0, y0, x1, y1, level=None, front=None: dict(
    {"name": f"{room}.{sym}", "room": room, "plan_sym": sym, "obb": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]},
    **({"level": level} if level else {}), **({"front": front} if front else {}))
RECS = [
    R("green_bedroom", "bed", 1.2, 2.75, 2.8, 4.8, front=[0, -1]), R("green_bedroom", "bedside", 0.65, 4.35, 1.1, 4.8, "1"),
    R("green_bedroom", "wardrobe", -0.65, 1.3, -0.05, 3.1), R("green_bedroom", "chest", 3.5, 4.3, 4.3, 4.8),
    R("green_bedroom", "bureau", 3.75, 2.0, 4.3, 3.0), R("blue_bedroom", "desk", 2.2, 15.6, 3.1, 16.85),
    R("blue_bedroom", "office_chair", 2.35, 15.0, 2.95, 15.55), R("blue_bedroom", "cabinet", -0.65, 15.5, -0.2, 16.5),
    R("blue_ensuite", "bath", 0.6, 11.35, 1.3, 13.0), R("blue_ensuite", "vanity", 2.0, 11.35, 3.0, 11.85),
    R("green_bathroom", "shower", 3.4, 7.8, 4.3, 8.7), R("bathroom2", "sauna", 1.9, 12.2, 3.1, 13.4),
    R("basement", "boiler", 3.0, 8.3, 3.6, 8.73), R("basement", "cylinder", 1.4, 8.1, 2.0, 8.7, "B"),
    R("basement", "rack", 1.3, 5.3, 3.3, 5.75), R("shed_workshop", "workbench", 0.0, 28.0, 2.0, 28.6),
    R("shed_workshop", "bench", 3.0, 26.0, 4.1, 26.5), R("front", "car", -0.07, -5.0, 1.63, -1.1, "X"),
    R("garden", "planter", 2.95, 18.2, 3.37, 20.05), R("garden", "fire_pit", 0.77, 21.76, 1.77, 22.76),
    R("garden", "trellis", -0.76, 17.85, -0.72, 19.65), R("front", "flagpole", 0.94, -0.3, 1.02, -0.22),
    R("garden", "condenser", 3.42, 15.0, 3.72, 15.8, "X"),
]

ap = argparse.ArgumentParser()
spec = D.ROOT / "spec" / "house.json"                         # schema 2 after integration, else the step-0 fixture
ap.add_argument("--house", default=str(spec if json.loads(spec.read_text(encoding="utf-8")).get("schema") == "house/2"
                                       else D.ROOT / "spec" / "house.json"))
house = ap.parse_args().house
with tempfile.TemporaryDirectory() as tmp:
    fp = Path(tmp) / "footprints.json"
    fp.write_text(json.dumps(RECS), encoding="utf-8")
    plan, checks = D.build(house, fp)
D.self_check(plan, checks)
sheets = {s["id"]: s for s in plan["sheets"]}
for r in RECS:
    lvl = D.rec_level(dict(r))
    box = Polygon(r["obb"]).buffer(0.03)
    n = sum(any(box.contains(Point(p)) for p in [e[k] for k in ("p1", "p2", "c") if k in e] + e.get("pts", []))
            for e in sheets[lvl]["entities"] if e["layer"] in ("A-FURN", "A-FLOR-FIXT"))
    assert n >= 1, (r["name"], lvl, n)
assert {D.rec_level(dict(r)) for r in RECS} == {"B", "1", "2", "X"}
print("TEST OK  %d symbols drawn on their sheets; self-checks pass" % len(RECS))
