"""Smoke test for footprints the Blender export will produce: every plan symbol of MULTILEVEL.md section 10 draws on
the sheet of its level (with and without a `level` field), unknown / unreadable records fall back to their outline,
spec fallback and export never double-draw, `front` vectors orient symbols, car yaw is read from the spec, title-block
cells fit any text, neighbours are dashed context inside the site window, and the drafter's self-checks still pass.
Cross-sections (a sections.json cut from the model by blender/export_sections.py): without one the set is the five
plans; with one every section is a sheet after them (closed cut outlines, both hatches, level marks that are levels
of house.json, the cut rooms named from house.json, the walker's projection landing in the room it stands in), the
plans carry the cutting lines on the planes of section_planes.py, every title block counts the whole set, the DXF
audits clean with the section layers and the PDF has a page per sheet; a sections.json holding one section gives a
set of six; and sections.json stands within 20 mm of house.json.

    python tools/plan/test_draft.py [--house PATH] [--sections FILE] [--no-sections]      -> TEST OK
        # defaults: spec/house.json, docs/assets/sections.json. None there: the test fails (the export writes it), unless
        # --no-sections says the plan sheets alone are to be tested
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
ap.add_argument("--sections", default=str(D.OUT / "sections.json"), help="sections.json of an export (default docs/assets)")
ap.add_argument("--no-sections", action="store_true", help="test the plan sheets alone (no sections.json at hand)")
house, sections = ap.parse_args().house, Path(ap.parse_args().sections)
assert sections.exists() or ap.parse_args().no_sections, (
    "no %s: blender/export.py writes it on every export (blender/export_sections.py alone: 20 s); --no-sections tests "
    "the plan sheets only" % sections)
with tempfile.TemporaryDirectory() as tmp:
    fp = Path(tmp) / "footprints.json"
    fp.write_text(json.dumps(RECS + [SKEW]), encoding="utf-8")
    plan, checks = D.build(house, fp)
    D.self_check(plan, checks)
    sheets = {s["id"]: s for s in plan["sheets"]}
    assert list(sheets) == ["B", "G", "1", "2", "X"] and not D.SECS, "no sections.json beside the footprints: the five plans"
    assert not any(l["name"].startswith(("A-SECT", "A-ANNO-SECT", "A-ANNO-LEVL")) for l in plan["layers"])
    assert all(any(e["type"] == "text" and e["text"] == "%d OF 5" % s["index"] for e in s["entities"]) for s in plan["sheets"])
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

# cross-sections
import section_planes as SP
for sec in SP.SECTIONS:                                         # the planes are data: resolved from the spec, each through its list
    pl = SP.resolve(D.H, sec)
    lo, hi = SP.span(D.H, sec["through"], sec["axis"])
    assert lo < pl["at"] < hi and hi - lo >= SP.MIN_SPAN and abs(pl["at"] - (lo + hi) / 2) < 1e-3, (sec["id"], lo, hi)
    assert abs(SP.to_s(pl, *SP.to_xy(pl, 3.21)) - 3.21) < 1e-9 and pl["right"] == [pl["normal"][1], -pl["normal"][0]]
note = "section sheets not tested (--no-sections)"
if sections.exists() and not ap.parse_args().no_sections:
    import ezdxf, fitz
    from shapely.geometry import LineString
    from render import render_pdf
    secs = json.loads(sections.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        fp = Path(tmp) / "footprints.json"
        fp.write_text(json.dumps(RECS), encoding="utf-8")
        plan, checks = D.build(house, fp, sections)
        D.self_check(plan, checks)                              # incl. section_check: closed outlines, names, level marks
        ids = [s["id"] for s in plan["sheets"]]
        cut = [sid for sid, _, _ in D.SECTION_SHEETS if sid in D.SECS]
        assert ids == ["B", "G", "1", "2", "X"] + cut and len(cut) >= 2, ids
        n = len(ids)
        for s in plan["sheets"]:                                # every title block counts the whole set
            assert any(e["type"] == "text" and e["text"] == "%d OF %d" % (s["index"], n) for e in s["entities"]), (s["id"], n)
        spec_floors = {round(float(r["floorZ"]), 3) for r in list(D.ROOMS.values()) + list(D.HC.building_rooms.values())}
        named = set()
        for s in plan["sheets"][5:]:
            sec, E = D.SECS[s["id"]], s["entities"]
            assert s["kind"] == "section" and s["scale"] in ("1:50", "1:100", "1:200") and s["number"].startswith("GA-"), s["id"]
            assert s["title"] == "SECTION %s-%s" % (sec["letter"], sec["letter"]) and s["section"]["at"] == sec["at"]
            by = lambda lay, typ: [e for e in E if e["layer"] == lay and e["type"] == typ]
            assert by("A-SECT", "polyline") and all(e["closed"] for e in by("A-SECT", "polyline")[:1]), s["id"]
            assert {e["pattern"] for e in by("A-SECT-PATT", "hatch")} == {"ANSI31", "EARTH"}, s["id"]
            for lay in ("A-SECT-BYND", "A-SECT-FIXT"):          # the packed layers: flat lists of x, y pairs
                p = by(lay, "paths")
                assert len(p) == 1 and p[0]["paths"] and all(len(q) >= 4 and len(q) % 2 == 0 for q in p[0]["paths"]), (s["id"], lay)
            texts = {e["text"] for e in E if e["type"] == "text"}
            marks = [t for e in by("A-ANNO-LEVL", "text") for t in e["text"].split(" / ")]
            assert all(any(D.ffl(z) == t for z in spec_floors) for t in marks if t.startswith("FFL")), (s["id"], marks)
            assert any(t.startswith(("RIDGE", "FLAT ROOF")) for t in marks) and by("A-ANNO-DIMS", "dim"), s["id"]
            assert D.ENDS[tuple(sec["right"])] in texts and D.ENDS[(-sec["right"][0], -sec["right"][1])] in texts, s["id"]
            for r in s["rooms"]:                                # the viewer's projection: on the plane inside a room -> inside its outline
                if r["id"] not in D.ROOMS or D.HC.kind(r["id"]) != "room":
                    continue
                assert D.room_name(r["id"]) in texts, (s["id"], r["id"])
                named.add(D.room_name(r["id"]))
                g = LineString([D.sec_xy(sec, -50), D.sec_xy(sec, 50)]).intersection(Polygon(D.ROOMS[r["id"]]["polygon"]))
                x, y = g.interpolate(0.5, normalized=True).coords[0]
                sm = (x - s["section"]["origin"][0]) * s["section"]["right"][0] + (y - s["section"]["origin"][1]) * s["section"]["right"][1]
                assert Polygon(r["polygon"]).buffer(0.01).contains(Point(sm, r["floorZ"] + 0.5)), (s["id"], r["id"], sm)
        for rid in ("loft_office", "study", "purple_room"):     # the names are house.json's (round 3 renamed these three)
            assert D.room_name(rid) == D.ROOMS[rid]["name"].split("(")[0].strip().upper() and D.room_name(rid) in named, rid
        for s in plan["sheets"][:5]:                            # cutting lines on the plans: on the plane, lettered at both ends
            E = s["entities"]
            for sid in cut:
                sec = D.SECS[sid]
                k = 0 if sec["axis"] == "x" else 1
                lines = [e for e in E if e["layer"] == "A-ANNO-SECT-CUTL" and all(abs(p[k] - sec["at"]) < 1e-6 for p in
                         ([e["p1"], e["p2"]] if e["type"] == "line" else e["pts"]))]
                letters = [e for e in E if e["layer"] == "A-ANNO-SECT" and e["type"] == "text" and e["text"] == sec["letter"]]
                crossed = s["id"] == "X" or LineString([D.sec_xy(sec, -50), D.sec_xy(sec, 50)]).intersects(D.envelope(s["id"]))
                assert (len(letters) == 2 and lines and all(e.get("ls") == "center" for e in lines)) if crossed else not letters, (s["id"], sid)
        reg = D.section_registration()
        worst = max(reg, key=lambda r: abs(r[3] - r[4]))
        assert abs(worst[3] - worst[4]) <= 0.02 and sum(r[2] != "floor" for r in reg) >= 10, ("registration", worst)
        D.write_dxf(plan, Path(tmp) / "t.dxf")                  # audits inside; re-read: the section layers hold entities
        msp = ezdxf.readfile(Path(tmp) / "t.dxf").modelspace()
        used = {e.dxf.layer for e in msp}
        assert {n_ for n_, *_ in D.SECTION_LAYERS} - {"A-SECT-HIDN"} <= used, used
        assert {"EARTH", "ANSI31"} <= {h.dxf.pattern_name for h in msp.query("HATCH")}
        # a sections.json holding one section: a set of six, counted so on every sheet, six PDF pages
        one = Path(tmp) / "one.json"
        one.write_text(json.dumps(dict(secs, sections=[q for q in secs["sections"] if q["id"] == cut[1]])), encoding="utf-8")
        plan6, checks6 = D.build(house, fp, one)
        D.self_check(plan6, checks6)
        assert [s["id"] for s in plan6["sheets"]] == ["B", "G", "1", "2", "X", cut[1]]
        assert all(any(e["type"] == "text" and e["text"] == "%d OF 6" % s["index"] for e in s["entities"]) for s in plan6["sheets"])
        render_pdf(plan6, Path(tmp) / "t.pdf")
        doc = fitz.open(Path(tmp) / "t.pdf")
        pages = len(doc)
        doc.close()
        assert pages == 6, pages
    note = "%d section sheets (%s): closed cut, hatches, level marks, room names, cutting lines on the plans, registration " \
           "within %.0f mm over %d checks, DXF layers, set of six" % (len(cut), " ".join(cut), abs(worst[3] - worst[4]) * 1000, len(reg))
print("TEST OK  %d symbols drawn on their sheets (+1 unreadable as its outline); fallback dedupe, front vectors, car yaw, "
      "title-block fit, neighbour context, self-checks pass; %s" % (len(RECS), note))
