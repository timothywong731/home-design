"""Render plan.json with matplotlib - the vector PDF pages and PNG proofs come from the JSON alone.

    python tools/plan/render.py [--json docs/assets/plan.json] [--out build/plan] [--sheet G] [--bounds x0,y0,x1,y1] [--zoom 2] [--tag crop]

writes <out>/<sheet>_plan_dark[_tag].png and <out>/<sheet>_plan_paper[_tag].png for every sheet (or --sheet). Doubles
as the reference for how a viewer should interpret every plan.json entity type (dim layout, hatches ANSI31 / EARTH /
SOLID, text height = cap height, line styles, `paths` = several polylines in one entity). plan.json schema 2 keeps
linestyles / hatch / dimstyle per sheet; schema 1 is read as one sheet. A sheet is drawn in its own frame at its own
size: the plans A3 portrait, a cross-section sheet (kind 'section', x = metres along the plane, y = Z) as it says.
"""
import argparse, json, math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.collections import LineCollection
from matplotlib.patches import Arc, Circle, Polygon as MPoly
from shapely.geometry import Polygon, LineString, MultiLineString

FONT, CAP = "DejaVu Sans Mono", 0.72             # cap height / font size; text "h" is the font size (em)
BG = {"dark": "#0b0d10", "paper": "#ffffff"}
PT = 72 / 25.4                                   # points per mm
plt.rcParams.update({"lines.scale_dashes": False, "pdf.fonttype": 42, "lines.solid_capstyle": "butt",
                     "lines.dash_capstyle": "butt", "lines.solid_joinstyle": "miter"})


def sheets(plan):
    """Sheet dicts of a plan.json: schema 2 as is; schema 1 as its single ground-floor sheet."""
    if plan.get("schema") == 2:
        return plan["sheets"]
    return [{**plan, **plan["sheet"], "id": "G"}]


def dim_geometry(e, st):
    """-> (line segments, text anchor (centre of baseline), text rotation deg) for a 'dim' entity.

    The dimension line is parallel to p1->p2, displaced by `offset` along the LEFT normal of p1->p2
    (negative = right).  Extension lines run from each point (less a gap) to just past the line, with
    45-degree tick terminators.  Text sits above the line in reading direction unless `tp` is given."""
    (x1, y1), (x2, y2) = e["p1"], e["p2"]
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    o = e["offset"]
    sg = 1 if o >= 0 else -1
    a, b = (x1 + nx * o, y1 + ny * o), (x2 + nx * o, y2 + ny * o)
    rx, ry = (-ux, -uy) if ux < -1e-9 or (abs(ux) < 1e-9 and uy < 0) else (ux, uy)      # reading direction
    tx, ty = (rx - ry) * st["tick"] * 0.7071, (ry + rx) * st["tick"] * 0.7071           # tick half-vector
    segs = [(a, b)]
    for (px, py), (qx, qy) in (((x1, y1), a), ((x2, y2), b)):
        segs.append(((px + nx * sg * st["extGap"], py + ny * sg * st["extGap"]),
                     (qx + nx * sg * st["extBeyond"], qy + ny * sg * st["extBeyond"])))
        segs.append(((qx - tx, qy - ty), (qx + tx, qy + ty)))
    up = 0.7 * e.get("h", st["h"])                                                      # text middle, as plan2d.js
    tp = e.get("tp") or [(a[0] + b[0]) / 2 - ry * up, (a[1] + b[1]) / 2 + rx * up]
    return segs, tp, math.degrees(math.atan2(ry, rx))


def draw_text(ax, p, h, s, col, k, align="left", rot=0, z=0):
    """h = font size (em, metres); p = vertical middle of the capitals -> shift to the baseline for matplotlib."""
    r = math.radians(rot)
    ax.text(p[0] + math.sin(r) * CAP * h / 2, p[1] - math.cos(r) * CAP * h / 2, s, fontsize=h * k * PT, family=FONT, color=col,
            ha=align, va="baseline", rotation=rot, rotation_mode="anchor", zorder=z)


def hatch_lines(pts, spacing):
    """ANSI31: 45-degree lines at `spacing` (perpendicular), globally aligned on the origin, clipped to pts."""
    poly = Polygon(pts)
    x0, y0, x1, y1 = poly.bounds
    step = spacing * math.sqrt(2)
    out = []
    for k in range(math.floor((x0 - y1) / step), math.ceil((x1 - y0) / step) + 1):
        g = LineString([(x0, x0 - k * step), (x1, x1 - k * step)]).intersection(poly)
        for part in getattr(g, "geoms", [g]):
            if part.geom_type == "LineString" and not part.is_empty:
                out.append(list(part.coords))
    return out


def earth_lines(pts, spacing):
    """EARTH: square cells of 2 x spacing on a grid through the origin, three lines in each, alternately along x and
    along y, clipped to pts (docs/js/plan2d.js draws the same; the DXF carries AutoCAD's EARTH at that cell size)."""
    poly = Polygon(pts)
    c = 2 * spacing
    x0, y0, x1, y1 = poly.bounds
    segs = []
    for i in range(math.floor(x0 / c), math.ceil(x1 / c)):
        for j in range(math.floor(y0 / c), math.ceil(y1 / c)):
            for k in (1, 3, 5):
                t = k * c / 6
                segs.append(((i * c, j * c + t), (i * c + c, j * c + t)) if (i + j) % 2 == 0 else ((i * c + t, j * c), (i * c + t, j * c + c)))
    g = MultiLineString(segs).intersection(poly.buffer(0)) if segs else LineString()
    return [list(part.coords) for part in getattr(g, "geoms", [g]) if part.geom_type == "LineString" and not part.is_empty]


def figure(sh, layers, theme="paper", bounds=None, zoom=1.0):
    """Draw every entity of one sheet. At zoom 1 one model metre is 1000/scale paper mm, so a page is true to scale."""
    mm = int(sh["scale"].split(":")[1]) / 1000.0                       # model metres per paper mm
    b = bounds or sh["sheetBounds"]
    k = zoom / mm                                                     # paper mm per model metre
    fig = plt.figure(figsize=((b["maxX"] - b["minX"]) * k / 25.4, (b["maxY"] - b["minY"]) * k / 25.4), facecolor=BG[theme])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(b["minX"], b["maxX"]); ax.set_ylim(b["minY"], b["maxY"]); ax.axis("off")
    lay = {l["name"]: l for l in layers}
    key = "color" if theme == "dark" else "paper"
    for z, e in enumerate(sh["entities"]):
        l = lay[e["layer"]]
        col, lw = l[key], max(l["lineweight"] * zoom * PT, 0.12)
        ls = "-"
        if e.get("ls"):
            ls = (0, [v * k * PT for v in sh["linestyles"][e["ls"]]])
        kw = dict(color=col, lw=lw, ls=ls, zorder=z)
        t = e["type"]
        if t == "line":
            ax.plot(*zip(e["p1"], e["p2"]), **kw)
        elif t == "polyline":
            pts = e["pts"] + ([e["pts"][0]] if e["closed"] else [])
            ax.plot(*zip(*pts), **kw)
        elif t == "paths":
            ax.add_collection(LineCollection([list(zip(q[0::2], q[1::2])) for q in e["paths"]], colors=col, linewidths=lw, zorder=z))
        elif t == "arc":
            ax.add_patch(Arc(e["c"], 2 * e["r"], 2 * e["r"], theta1=e["a0"], theta2=e["a1"], **kw))
        elif t == "circle":
            ax.add_patch(Circle(e["c"], e["r"], fill=False, ec=col, lw=lw, ls=ls, zorder=z))
        elif t == "hatch":
            if e["pattern"] == "SOLID":
                ax.add_patch(MPoly(e["pts"], closed=True, fc=col, ec="none", zorder=z))
            else:
                lines = (earth_lines if e["pattern"] == "EARTH" else hatch_lines)(e["pts"], sh["hatch"]["spacing"])
                ax.add_collection(LineCollection(lines, colors=col, linewidths=lw, zorder=z))
        elif t == "text":
            draw_text(ax, e["p"], e["h"], e["text"], col, k, e.get("align", "left"), e.get("rot", 0), z)
        elif t == "dim":
            segs, tp, rot = dim_geometry(e, sh["dimstyle"])
            ax.add_collection(LineCollection(segs, colors=col, linewidths=lw, zorder=z))
            if e["text"]:                                              # "" = value drawn by a separate text entity at tp
                draw_text(ax, tp, e.get("h", sh["dimstyle"]["h"]), e["text"], col, k, "center", rot, z)
        else:
            raise ValueError(f"unknown entity type {t}")
    return fig


def render(plan, out, theme="paper", bounds=None, zoom=1.0, dpi=200, sheet=None):
    """One sheet (id `sheet`, default the first) to a raster or single-page file."""
    sh = next(s for s in sheets(plan) if sheet in (None, s["id"]))
    fig = figure(sh, plan["layers"], theme, bounds, zoom)
    fig.savefig(out, dpi=dpi, facecolor=BG[theme])
    plt.close(fig)


def render_pdf(plan, out):
    """Every sheet as one vector page of a PDF, paper theme, true to scale on its paper size."""
    with PdfPages(out, metadata={"Title": "House plans", "Subject": ", ".join(f"{s['title']} {s['scale']}" for s in sheets(plan)),
                                 "Creator": "tools/plan/draft.py", "CreationDate": None}) as pdf:
        for sh in sheets(plan):
            fig = figure(sh, plan["layers"], "paper")
            pdf.savefig(fig, facecolor=BG["paper"])
            plt.close(fig)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(root / "docs/assets/plan.json"))
    ap.add_argument("--out", default=str(root / "build/plan"))
    ap.add_argument("--sheet", help="sheet id (default: every sheet)")
    ap.add_argument("--bounds")
    ap.add_argument("--zoom", type=float, default=1.0)
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    plan = json.loads(Path(a.json).read_text(encoding="utf-8"))
    bounds = dict(zip(("minX", "minY", "maxX", "maxY"), map(float, a.bounds.split(",")))) if a.bounds else None
    Path(a.out).mkdir(parents=True, exist_ok=True)
    for sh in sheets(plan):
        if a.sheet not in (None, sh["id"]):
            continue
        for theme in ("dark", "paper"):
            f = Path(a.out) / f"{sh['id']}_plan_{theme}{'_' + a.tag if a.tag else ''}.png"
            render(plan, f, theme, bounds, a.zoom, a.dpi, sh["id"])
            print("wrote", f)
