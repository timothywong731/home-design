"""Verify the drafter's outputs by re-reading them, then rasterise all three for a human/agent to look at.

    python tools/plan/check.py     -> build/plan/{dxf_dark.png, dxf_paper.png, pdf.png, plan_dark.png, plan_paper.png}

DXF: ezdxf audit, units, layer/entity census, DIMENSION measurements against plan.json, then drawn back with
ezdxf's drawing add-on.  PDF: page size, vector (no images), fonts, rasterised with pdftoppm (or PyMuPDF).
plan.json: rendered in both themes by render.py.  Exits non-zero on any failed assertion.
"""
import getpass, json, os, shutil, subprocess, sys
from collections import Counter
from pathlib import Path
import ezdxf
from ezdxf.addons.drawing import matplotlib as dxfplot

sys.path.insert(0, str(Path(__file__).parent))
from render import render

ROOT = Path(__file__).resolve().parents[2]
A, OUT = ROOT / "docs" / "assets", ROOT / "build" / "plan"
OUT.mkdir(parents=True, exist_ok=True)
plan = json.loads((A / "plan.json").read_text(encoding="utf-8"))

# ---- DXF
doc = ezdxf.readfile(A / "ground-floor-plan.dxf")
aud = doc.audit()
assert not aud.errors and not aud.fixes, (aud.errors, aud.fixes)
assert doc.units == ezdxf.units.MM and doc.header["$MEASUREMENT"] == 1
msp = doc.modelspace()
by_type, by_layer = Counter(e.dxftype() for e in msp), Counter(e.dxf.layer for e in msp)
print("DXF  audit OK | version", doc.dxfversion, "| units mm | entities", sum(by_type.values()))
print("     types :", dict(sorted(by_type.items())))
print("     layers:", dict(sorted(by_layer.items())))
for l in plan["layers"]:
    lay = doc.layers.get(l["name"])
    assert lay.color == l["aci"] and lay.dxf.lineweight == round(l["lineweight"] * 100), l["name"]
    assert by_layer[l["name"]] > 0, f"layer {l['name']} is empty"
for t in ("LWPOLYLINE", "LINE", "ARC", "CIRCLE", "HATCH", "TEXT", "DIMENSION"):
    assert by_type[t] > 0, f"no {t} entities"
dims = [e for e in plan["entities"] if e["type"] == "dim"]
meas = sorted(round(d.get_measurement()) for d in msp.query("DIMENSION"))
assert meas == sorted(int(d.get("value") or d["text"]) for d in dims), "DIMENSION measurements differ from plan.json"
ext = ezdxf.bbox.extents(msp.query("LWPOLYLINE[layer=='A-WALL']"))
hb = plan["houseBounds"]
assert all(abs(a - b * 1000) < 1 for a, b in zip((ext.extmin.x, ext.extmin.y, ext.extmax.x, ext.extmax.y),
                                                 (hb["minX"], hb["minY"], hb["maxX"], hb["maxY"]))), ext
print("     walls extent mm:", [round(v) for v in (ext.extmin.x, ext.extmin.y, ext.extmax.x, ext.extmax.y)], "= house bounds at true scale;",
      len(meas), "DIMENSIONs measure as labelled")
sb = plan["sheetBounds"]
size = ((sb["maxX"] - sb["minX"]) / 2, (sb["maxY"] - sb["minY"]) / 2)        # inches-ish canvas, aspect of the sheet
for name, bg, fg in (("dxf_dark.png", "#0b0d10", None), ("dxf_paper.png", "#ffffff", "#000000")):
    dxfplot.qsave(msp, str(OUT / name), bg=bg, fg=fg, dpi=160, size_inches=size)
    print("     drew", OUT / name)

# ---- PDF
pdf = A / "ground-floor-plan.pdf"
raw = pdf.read_bytes()
import fitz
d = fitz.open(pdf)
pg = d[0]
w_mm, h_mm = pg.rect.width / 72 * 25.4, pg.rect.height / 72 * 25.4
assert len(d) == 1 and abs(w_mm - 297) < 0.5 and abs(h_mm - 420) < 0.5, (w_mm, h_mm)
assert not pg.get_images(), "PDF contains raster images"
paths = pg.get_drawings()
print(f"PDF  1 page {w_mm:.1f} x {h_mm:.1f} mm (A3 portrait) | {len(paths)} vector paths | 0 images | fonts",
      sorted({f[3] for f in pg.get_fonts()}), "| metadata", {k: v for k, v in d.metadata.items() if v})
words = pg.get_text()
assert "GROUND FLOOR PLAN" in words and "1:%s" % plan["sheet"]["scale"].split(":")[1] in words
if shutil.which("pdftoppm"):
    subprocess.run(["pdftoppm", "-r", "110", "-png", "-singlefile", str(pdf), str(OUT / "pdf")], check=True)
else:
    pg.get_pixmap(dpi=110).save(OUT / "pdf.png")
print("     rasterised", OUT / "pdf.png")

# ---- plan.json -> both themes
for theme in ("dark", "paper"):
    render(plan, OUT / f"plan_{theme}.png", theme, dpi=110)
    print("JSON drew", OUT / f"plan_{theme}.png")
types = Counter(e["type"] for e in plan["entities"])
print("     entities", dict(types), "| rooms", [r["id"] for r in plan["rooms"]], "| footprints:", plan["footprintSource"])

# ---- privacy: no user/owner name or address-like strings in any shipped file
banned = {getpass.getuser().lower(), *os.environ.get("USERNAME", "").lower().split(), *getpass.getuser().lower().split()} - {""}
for f in (A / "plan.json", A / "ground-floor-plan.dxf", pdf):
    low = f.read_bytes().lower()
    hits = [b for b in banned if b.encode() in low] + [k for k in (b"street name", b" road", b" avenue", b"postcode") if k in low]
    assert not hits, (f.name, hits)
print("PRIV no OS user name / address strings in plan.json, DXF, PDF (%d patterns)" % (len(banned) + 4))
print("CHECK OK")
