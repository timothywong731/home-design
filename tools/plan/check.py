"""Verify the drafter's outputs by re-reading them, then rasterise every sheet for a human/agent to look at.

    python tools/plan/check.py [--assets DIR] [--out DIR]     # defaults docs/assets, build/plan
        -> <out>/<sheet>_dxf_dark.png, <sheet>_pdf.png, <sheet>_plan_dark.png, <sheet>_plan_paper.png

plan.json: schema 2, sheets B G 1 2 X in order, 1:50 floor sheets, the site at exactly 1:100 in the plot window,
per-sheet style tables, every entity inside its A3 frame. DXF: ezdxf audit, units, layers (colour, lineweight,
dashed boundary layer), dimstyles PLAN50 + PLAN100 and which sheet uses which, linetype scale 2 on the 1:100 sheet,
every DIMENSION measured against plan.json, each sheet's walls at true scale at its dxfOffset, then each sheet drawn
back with ezdxf's drawing add-on. PDF: one A3 page per sheet in order, vector only, title and scale on each page.
Privacy scan over all three files. Exits non-zero on any failed assertion; prints CHECK OK.
"""
import argparse, getpass, json, os, shutil, subprocess, sys
from collections import Counter
from pathlib import Path
import ezdxf
from ezdxf.addons.drawing import matplotlib as dxfplot

sys.path.insert(0, str(Path(__file__).parent))
from render import render

ROOT = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--assets", default=str(ROOT / "docs" / "assets"), help="directory holding plan.json, house-plans.dxf/.pdf")
ap.add_argument("--out", default=str(ROOT / "build" / "plan"), help="raster directory (default build/plan)")
_a = ap.parse_args()
A, OUT = Path(_a.assets), Path(_a.out)
OUT.mkdir(parents=True, exist_ok=True)
plan = json.loads((A / "plan.json").read_text(encoding="utf-8"))
SHEETS = plan["sheets"]
ORDER = ["B", "G", "1", "2", "X"]

# ---- plan.json
assert plan["schema"] == 2 and [s["id"] for s in SHEETS] == ORDER, [s.get("id") for s in SHEETS]
layer_names = {l["name"] for l in plan["layers"]}
for s in SHEETS:
    mm = int(s["scale"].split(":")[1]) / 1000
    assert s["scale"] == ("1:100" if s["id"] == "X" else "1:50") and s["paper"] == "A3", (s["id"], s["scale"])
    for k in ("bounds", "houseBounds", "sheetBounds", "linestyles", "hatch", "dimstyle", "dxfOffset", "entities", "rooms"):
        assert k in s, (s["id"], k)
    sb = s["sheetBounds"]
    assert abs((sb["maxX"] - sb["minX"]) / mm - 297) < 0.01 and abs((sb["maxY"] - sb["minY"]) / mm - 420) < 0.01, s["id"]
    assert abs(s["linestyles"]["dashed"][0] - 2.4 * mm) < 1e-6 and abs(s["dimstyle"]["tick"] - 1.3 * mm) < 1e-6, s["id"]
    assert abs(s["hatch"]["spacing"] - 1.8 * mm) < 1e-6, s["id"]
    for e in s["entities"]:
        assert e["layer"] in layer_names and e.get("ls") in (None, *s["linestyles"]), (s["id"], e)
        pts = [e[k] for k in ("p1", "p2", "c", "p") if k in e] + e.get("pts", [])
        assert all(sb["minX"] < x < sb["maxX"] and sb["minY"] < y < sb["maxY"] for x, y in pts), (s["id"], e)
site = SHEETS[-1]
house = json.loads((A / "house.json").read_text(encoding="utf-8")) if (A / "house.json").exists() else None
print("JSON schema 2 |", ", ".join(f"{s['id']} {s['title']} {s['scale']} ({len(s['entities'])} entities, {len(s['rooms'])} rooms)" for s in SHEETS))
print("     site window", site["bounds"], "at", site["scale"])

# ---- DXF
doc = ezdxf.readfile(A / "house-plans.dxf")
aud = doc.audit()
assert not aud.errors and not aud.fixes, (aud.errors, aud.fixes)
assert doc.units == ezdxf.units.MM and doc.header["$MEASUREMENT"] == 1 and doc.header["$LTSCALE"] == 1
msp = doc.modelspace()
by_type, by_layer = Counter(e.dxftype() for e in msp), Counter(e.dxf.layer for e in msp)
print("DXF  audit OK | version", doc.dxfversion, "| units mm | entities", sum(by_type.values()))
print("     types :", dict(sorted(by_type.items())))
print("     layers:", dict(sorted(by_layer.items())))
OPTIONAL = {"L-SITE-CTXT"}                    # neighbours: only when they reach into the site window
for l in plan["layers"]:
    lay = doc.layers.get(l["name"])
    assert lay.color == l["aci"] and lay.dxf.lineweight == round(l["lineweight"] * 100), l["name"]
    assert by_layer[l["name"]] > 0 or l["name"] in OPTIONAL, f"layer {l['name']} is empty"
for n in ("L-SITE-BNDY", "L-SITE-CTXT"):
    assert doc.layers.get(n).dxf.linetype.upper() == "DASHED", n
for t in ("LWPOLYLINE", "LINE", "ARC", "CIRCLE", "HATCH", "TEXT", "DIMENSION"):
    assert by_type[t] > 0, f"no {t} entities"


def region(s, pad=0.0):
    """The sheet's A3 frame in DXF millimetres."""
    b, (ox, oy) = s["sheetBounds"], s["dxfOffset"]
    return (b["minX"] * 1000 + ox - pad, b["minY"] * 1000 + oy - pad, b["maxX"] * 1000 + ox + pad, b["maxY"] * 1000 + oy + pad)


def sheet_of(e):
    bb = ezdxf.bbox.extents([e], fast=True)
    if not bb.has_data:
        return None
    cx, cy = (bb.extmin.x + bb.extmax.x) / 2, (bb.extmin.y + bb.extmax.y) / 2
    return next((s["id"] for s in SHEETS if region(s)[0] <= cx <= region(s)[2] and region(s)[1] <= cy <= region(s)[3]), None)


SHEET_OF = {e.dxf.handle: sheet_of(e) for e in msp}
assert all(SHEET_OF.values()), "entities outside every sheet frame"
assert {"PLAN50", "PLAN100"} <= {d.dxf.name for d in doc.dimstyles}
for s in SHEETS:
    ents = [e for e in msp if SHEET_OF[e.dxf.handle] == s["id"]]
    dims = [d for d in ents if d.dxftype() == "DIMENSION"]
    want = "PLAN" + s["scale"].split(":")[1]
    assert dims and all(d.dxf.dimstyle == want for d in dims), (s["id"], {d.dxf.dimstyle for d in dims})
    lts = {round(e.dxf.get("ltscale", 1.0), 3) for e in ents if e.dxftype() in ("LINE", "LWPOLYLINE", "ARC", "CIRCLE")}
    assert lts == ({2.0} if s["id"] == "X" else {1.0}), (s["id"], lts)
    meas = sorted(round(d.get_measurement()) for d in dims)
    jd = sorted(int(d.get("value") or d["text"]) for d in s["entities"] if d["type"] == "dim")
    assert meas == jd, (s["id"], "DIMENSION measurements differ from plan.json")
    walls = [e for e in ents if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "A-WALL"]
    ext = ezdxf.bbox.extents(walls)
    hb, (ox, oy) = s["houseBounds"], s["dxfOffset"]
    got = (ext.extmin.x - ox, ext.extmin.y - oy, ext.extmax.x - ox, ext.extmax.y - oy)
    assert all(abs(a - b * 1000) < 1 for a, b in zip(got, (hb["minX"], hb["minY"], hb["maxX"], hb["maxY"]))), (s["id"], got, hb)
    print(f"     sheet {s['id']}: {len(ents)} entities, {len(dims)} DIMENSIONs ({want}) measure as labelled, walls "
          f"{[round(v) for v in got]} mm = houseBounds at true scale, offset {s['dxfOffset']}")
    x0, y0, x1, y1 = region(s)
    sid = s["id"]
    dxfplot.qsave(msp, str(OUT / f"{sid}_dxf_dark.png"), bg="#0b0d10", dpi=110, size_inches=((x1 - x0) / 1000 / (int(s["scale"].split(":")[1]) / 1000) / 25.4,
                                                                                            (y1 - y0) / 1000 / (int(s["scale"].split(":")[1]) / 1000) / 25.4),
                  filter_func=lambda e, sid=sid: SHEET_OF.get(e.dxf.handle) == sid)
print("     drew", ", ".join(f"{s['id']}_dxf_dark.png" for s in SHEETS), "in", OUT)

# ---- PDF
pdf = A / "house-plans.pdf"
import fitz
d = fitz.open(pdf)
assert len(d) == len(SHEETS), (len(d), len(SHEETS))
for i, (pg, s) in enumerate(zip(d, SHEETS)):
    w_mm, h_mm = pg.rect.width / 72 * 25.4, pg.rect.height / 72 * 25.4
    assert abs(w_mm - 297) < 0.5 and abs(h_mm - 420) < 0.5, (s["id"], w_mm, h_mm)
    assert not pg.get_images(), f"PDF page {i + 1} contains raster images"
    words = pg.get_text()
    assert s["title"] in words and s["scale"] in words, (s["id"], "title / scale missing on its page")
    assert "%d OF %d" % (i + 1, len(SHEETS)) in words and "NOTES" in words and "KEY" in words, (s["id"], "title block / notes")
    paths = pg.get_drawings()
    print(f"PDF  page {i + 1} {s['id']}: {w_mm:.1f} x {h_mm:.1f} mm, {len(paths)} vector paths, 0 images")
    pg.get_pixmap(dpi=110).save(OUT / f"{s['id']}_pdf.png")
print("     fonts", sorted({f[3] for f in d[0].get_fonts()}), "| metadata", {k: v for k, v in d.metadata.items() if v})

# ---- plan.json -> both themes
for s in SHEETS:
    for theme in ("dark", "paper"):
        render(plan, OUT / f"{s['id']}_plan_{theme}.png", theme, dpi=110, sheet=s["id"])
    print("JSON drew", f"{s['id']}_plan_dark.png / _paper.png", "| entities", dict(Counter(e["type"] for e in s["entities"])))
print("     footprints:", plan["footprintSource"])

# ---- privacy: no user/owner name or address-like strings in any shipped file
banned = {getpass.getuser().lower(), *os.environ.get("USERNAME", "").lower().split(), *getpass.getuser().lower().split()} - {""}
for f in (A / "plan.json", A / "house-plans.dxf", pdf):
    low = f.read_bytes().lower()
    hits = [b for b in banned if b.encode() in low] + [k for k in (b"street name", b" road", b" avenue", b"postcode") if k in low]
    assert not hits, (f.name, hits)
print("PRIV no OS user name / address strings in plan.json, DXF, PDF (%d patterns)" % (len(banned) + 4))
print("CHECK OK")
