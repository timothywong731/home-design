"""Render plan.json with matplotlib - the vector PDF sheet and PNG proofs come from the JSON alone.

    python tools/plan/render.py [--json docs/assets/plan.json] [--out build/plan] [--bounds x0,y0,x1,y1] [--zoom 2] [--tag crop]

writes <out>/plan_dark[_tag].png and <out>/plan_paper[_tag].png.  Doubles as the reference for how a viewer
should interpret every plan.json entity type (dim layout, hatch, text height = cap height, line styles).
"""
import argparse, json, math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Arc, Circle, Polygon as MPoly
from shapely.geometry import Polygon, LineString

FONT, CAP = "DejaVu Sans Mono", 0.72             # cap height / font size; text "h" is the font size (em)
BG = {"dark": "#0b0d10", "paper": "#ffffff"}
PT = 72 / 25.4                                   # points per mm
plt.rcParams.update({"lines.scale_dashes": False, "pdf.fonttype": 42, "lines.solid_capstyle": "butt",
                     "lines.dash_capstyle": "butt", "lines.solid_joinstyle": "miter"})


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


def render(plan, out, theme="paper", bounds=None, zoom=1.0, dpi=200):
    """Draw every entity. At zoom 1 one model metre is 1000/scale paper mm, so a PDF is true to scale."""
    mm = int(plan["sheet"]["scale"].split(":")[1]) / 1000.0          # model metres per paper mm
    b = bounds or plan["sheetBounds"]
    k = zoom / mm                                                     # paper mm per model metre
    fig = plt.figure(figsize=((b["maxX"] - b["minX"]) * k / 25.4, (b["maxY"] - b["minY"]) * k / 25.4), facecolor=BG[theme])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(b["minX"], b["maxX"]); ax.set_ylim(b["minY"], b["maxY"]); ax.axis("off")
    lay = {l["name"]: l for l in plan["layers"]}
    key = "color" if theme == "dark" else "paper"
    for z, e in enumerate(plan["entities"]):
        l = lay[e["layer"]]
        col, lw = l[key], max(l["lineweight"] * zoom * PT, 0.12)
        ls = "-"
        if e.get("ls"):
            ls = (0, [v * k * PT for v in plan["linestyles"][e["ls"]]])
        kw = dict(color=col, lw=lw, ls=ls, zorder=z)
        t = e["type"]
        if t == "line":
            ax.plot(*zip(e["p1"], e["p2"]), **kw)
        elif t == "polyline":
            pts = e["pts"] + ([e["pts"][0]] if e["closed"] else [])
            ax.plot(*zip(*pts), **kw)
        elif t == "arc":
            ax.add_patch(Arc(e["c"], 2 * e["r"], 2 * e["r"], theta1=e["a0"], theta2=e["a1"], **kw))
        elif t == "circle":
            ax.add_patch(Circle(e["c"], e["r"], fill=False, ec=col, lw=lw, ls=ls, zorder=z))
        elif t == "hatch":
            if e["pattern"] == "SOLID":
                ax.add_patch(MPoly(e["pts"], closed=True, fc=col, ec="none", zorder=z))
            else:
                ax.add_collection(LineCollection(hatch_lines(e["pts"], plan["hatch"]["spacing"]), colors=col, linewidths=lw, zorder=z))
        elif t == "text":
            draw_text(ax, e["p"], e["h"], e["text"], col, k, e.get("align", "left"), e.get("rot", 0), z)
        elif t == "dim":
            segs, tp, rot = dim_geometry(e, plan["dimstyle"])
            ax.add_collection(LineCollection(segs, colors=col, linewidths=lw, zorder=z))
            if e["text"]:                                              # "" = value drawn by a separate text entity at tp
                draw_text(ax, tp, e.get("h", plan["dimstyle"]["h"]), e["text"], col, k, "center", rot, z)
        else:
            raise ValueError(f"unknown entity type {t}")
    meta = {"Title": plan["sheet"]["title"], "Subject": f"Scale {plan['sheet']['scale']} on {plan['sheet']['paper']}",
            "Creator": "tools/plan/draft.py", "CreationDate": None} if str(out).endswith(".pdf") else None
    fig.savefig(out, dpi=dpi, facecolor=BG[theme], metadata=meta)
    plt.close(fig)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(root / "docs/assets/plan.json"))
    ap.add_argument("--out", default=str(root / "build/plan"))
    ap.add_argument("--bounds")
    ap.add_argument("--zoom", type=float, default=1.0)
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    plan = json.loads(Path(a.json).read_text(encoding="utf-8"))
    bounds = dict(zip(("minX", "minY", "maxX", "maxY"), map(float, a.bounds.split(",")))) if a.bounds else None
    Path(a.out).mkdir(parents=True, exist_ok=True)
    for theme in ("dark", "paper"):
        f = Path(a.out) / f"plan_{theme}{'_' + a.tag if a.tag else ''}.png"
        render(plan, f, theme, bounds, a.zoom, a.dpi)
        print("wrote", f)
