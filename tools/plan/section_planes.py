"""The cross-section planes of the drawing set: data only, no geometry of its own.

Read by blender/export_sections.py (cuts the built model on these planes -> sections.json) and by tools/plan/draft.py
(drafts the section sheets and the section marks on the plan sheets). Pure Python: imports without Blender or shapely.

A plane is vertical and axis-aligned. Its position is not a number: `through` lists the rooms and openings it has to
pass through, and it stands in the middle of what they have in common, so it follows spec/house.json when dimensions
move. `look` = +1 looks toward +axis (axis 'x': east, the viewer stands west of the plane; axis 'y': north = rear).

    SECTIONS[i]            the table
    resolve(spec, sec)     -> the plane in world metres (see resolve)
"""

SECTIONS = [
    # A-A, longitudinal, along the circulation spine: every doorway of the hall axis on all three floors, so the front
    # door, vestibule, hallway, hall arch, dining room, the landings with their split levels, the Slate Room under the
    # front roof slope and the Rose Room are cut; both stair flights stand just beyond the plane, in elevation.
    dict(id='AA', letter='A', axis='x', look=1,
         through=['d_street', 'd_inner', 'a_hall', 'd_dining', 'd_green', 'a_landing1', 'd_blue', 'd_loft',
                  'a_landing2', 'd_study'],
         # rooms the plane misses, drawn dashed where they lie beyond it (cut on a plane through their own middle)
         hidden=['basement_stair', 'basement']),
    # B-B, transverse through the front block, looking to the rear: hall and living room (through the living-room
    # door), the front bedroom, the Slate Room.
    dict(id='BB', letter='B', axis='y', look=1, through=['living', 'green_bedroom', 'loft_office', 'd_living']),
    # C-C, longitudinal through the rooms: both bay windows, living room, basement, kitchen, WC, utility, dining room
    # and the French doors; green bedroom and bathroom, yellow room, en-suite, blue bedroom, balcony; front eaves,
    # Slate Room, rear eaves under the rear slope, Lavender Room, bathroom, Rose Room.
    dict(id='CC', letter='C', axis='x', look=1,
         through=['basement', 'eaves_rear', 'w_bay_front', 'w_green_bay', 'd_wc', 'd_ensuite', 'h_eaves_rear',
                  'd_french', 'd_balcony', 'w_study']),
]
MIN_SPAN = 0.10         # m: the common span of `through` must be at least this wide (else the table needs a new line)
MARGIN = 0.30           # m: the section runs this far past the plot, as the site sheet does


def _bbox(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def _things(spec):
    """{id: (x0, y0, x1, y1)} of every room (also the shed's) and opening (its clear width along its wall)."""
    out = {}
    ext = spec.get('exterior', {})
    rooms = list(spec['rooms']) + [r for b in ext.get('buildings', []) for r in b['rooms']]
    walls = {w['id']: w for w in list(spec['walls']) + [w for b in ext.get('buildings', []) for w in b['walls']]}
    for r in rooms:
        out[r['id']] = _bbox(r['polygon'])
    for o in list(spec['openings']) + [o for b in ext.get('buildings', []) for o in b['openings']]:
        (ax, ay), (bx, by) = walls[o['wall']]['a'], walls[o['wall']]['b']
        L = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
        ux, uy, h = (bx - ax) / L, (by - ay) / L, o['width'] / 2
        cx, cy = o['center']
        out[o['id']] = _bbox([(cx - ux * h, cy - uy * h), (cx + ux * h, cy + uy * h)])
    return out


def span(spec, ids, axis):
    """(lo, hi) on `axis` ('x' | 'y') that every room / opening of `ids` covers."""
    T, k = _things(spec), 0 if axis == 'x' else 1
    return max(T[i][k] for i in ids), min(T[i][k + 2] for i in ids)


def resolve(spec, sec):
    """The plane of one SECTIONS entry in world metres:
    at       position on its axis (middle of the common span of `through`)
    normal   unit plan vector the viewer looks along; right = unit plan vector to the viewer's right
    origin   plan point of section coordinate s = 0, the left end of the drawing; s = (p - origin) . right
    length   the drawing runs s = 0 .. length (the plot's extent along the plane + MARGIN at both ends)
    hidden   [{room, at}] planes for the rooms drawn dashed beyond
    A point (x, y, z) projects to (s, z). Raises ValueError when `through` no longer has a common span."""
    axis, look = sec['axis'], sec['look']
    lo, hi = span(spec, sec['through'], axis)
    if hi - lo < MIN_SPAN:
        raise ValueError('section %s: %s have only %.3f m in common on %s (need %.2f): revise tools/plan/section_planes.py'
                         % (sec['id'], sec['through'], hi - lo, axis, MIN_SPAN))
    at = round((lo + hi) / 2, 3)
    normal = (look, 0) if axis == 'x' else (0, look)
    right = (normal[1], -normal[0])                  # looking along +x: -y is on the right; along +y: +x
    px0, py0, px1, py1 = _bbox(spec['exterior']['plot']['polygon'])
    a, b = ((py0, py1) if axis == 'x' else (px0, px1))
    a, b = a - MARGIN, b + MARGIN
    r = right[1] if axis == 'x' else right[0]        # +1: s grows with the world coordinate along the plane, -1: against
    start = a if r > 0 else b
    origin = (at, start) if axis == 'x' else (start, at)
    hidden = []
    for rid in sec.get('hidden', []):
        h0, h1 = span(spec, [rid], axis)
        hidden.append(dict(room=rid, at=round((h0 + h1) / 2, 3)))
    return dict(id=sec['id'], letter=sec['letter'], axis=axis, look=look, at=at, span=[round(lo, 4), round(hi, 4)],
                through=list(sec['through']), normal=list(normal), right=list(right), origin=[round(v, 4) for v in origin],
                length=round(b - a, 4), hidden=hidden)


def to_s(plane, x, y):
    """Section coordinate of a plan point."""
    return (x - plane['origin'][0]) * plane['right'][0] + (y - plane['origin'][1]) * plane['right'][1]


def to_xy(plane, s):
    """Plan point on the plane at section coordinate s."""
    return plane['origin'][0] + plane['right'][0] * s, plane['origin'][1] + plane['right'][1] * s


if __name__ == '__main__':                           # python tools/plan/section_planes.py [house.json]
    import json, sys
    from pathlib import Path
    spec = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'spec' / 'house.json')
                      .read_text(encoding='utf-8'))
    for sec in SECTIONS:
        p = resolve(spec, sec)
        print('%s  %s = %+.3f (common span %+.3f..%+.3f)  looking %s  length %.2f m  hidden %s'
              % (p['id'], p['axis'], p['at'], *p['span'], p['normal'], p['length'], p['hidden']))
