"""House context: spec accessors (schema 1 spec/house.json and schema "house/2"), collections, object tagging.
See blender/CONTRACT.md and blender/MULTILEVEL.md section 3. Everything is pure data except col / add (bpy);
without Blender (plain Python: tests, tools) the module still imports and opening_frame returns tuples for vectors."""
import json
import math
from pathlib import Path

try:
    import bpy
    from mathutils import Vector
except ImportError:                     # plain Python
    bpy = None
    Vector = tuple

ROOT = Path(__file__).resolve().parents[2]
KINDS = {'shell', 'trim', 'joinery', 'fit', 'furn', 'decor', 'light'}
STATIC = {'shell', 'trim', 'joinery', 'fit'}
PSEUDO_ROOMS = ('front', 'side_passage', 'garden', 'shed', 'facade', 'roof', 'neighbours')     # level 'X', kind 'site'
FRAME_D = 0.06                          # depth of an exterior frame (joinery builds to it)
MODULE_OF = {'landing1_front': 'landing1', 'landing1_ql': 'landing1', 'landing1_rear': 'landing1',
             'landing2_head': 'landing2', 'landing2_platform': 'landing2',
             'eaves_front': 'eaves', 'eaves_rear': 'eaves', 'basement_stair': 'basement'}
WINDOWS = ('window', 'bay_window')


class _Stairs(list):
    """The schema-2 stairs list. A string key reads the main flight, so phase-1 room code written against the
    schema-1 dict (ctx.stairs['rise'], ['landing'], ['newel'] ...) keeps working until the rooms are re-fitted."""

    def __getitem__(self, k):
        if isinstance(k, str):
            return next(s for s in self if s['id'] == 'stair_main')[k]
        return list.__getitem__(self, k)


class House:
    PSEUDO_ROOMS = PSEUDO_ROOMS
    FRAME_D = FRAME_D

    def __init__(self, spec):
        self.spec = spec                # the raw json, never modified
        self.root = ROOT
        self.schema = 2 if 'levels' in spec else 1
        self.rooms = {r['id']: r for r in spec['rooms']}                    # house rooms only
        self.walls = {w['id']: w for w in spec['walls']}                    # + building walls (level 'X', key 'building')
        self.openings = {o['id']: o for o in spec['openings']}              # + building openings (level 'X', key 'building')
        self.features = spec['features']
        st = spec['stairs']             # schema 1: one dict; schema 2: list of flights / steps (+ phase-1 key access)
        self.stairs = _Stairs(st) if isinstance(st, list) else st
        self.grid = None                # set by shell.build (lib.shell.Grid)
        lv = spec.get('levels') or [dict(id='G', name='Ground floor', datumZ=0.0, floors={'all': 0.0})]
        self.levels = [l['id'] for l in lv]
        self.level_info = {l['id']: l for l in lv}
        ext = spec.get('exterior', {})
        self.zones = {z['id']: z for z in ext.get('zones', [])}
        self.building_rooms = {}
        for b in ext.get('buildings', []):
            for r in b['rooms']:
                self.building_rooms[r['id']] = dict(r, building=b['id'])
            for w in b['walls']:
                out = 'outside' in w.get('rooms', ())
                self.walls[w['id']] = dict({'exterior': out, 'kind': 'external' if out else 'internal'}, **w, building=b['id'])
            for o in b['openings']:
                self.openings[o['id']] = dict(o, building=b['id'])
        self._slab = {}

    @classmethod
    def load(cls, path=None):
        return cls(json.loads(Path(path or ROOT / 'spec' / 'house.json').read_text(encoding='utf-8')))

    # ---- rooms, levels
    def _room(self, rid):
        return self.rooms[rid] if rid in self.rooms else self.building_rooms[rid]

    def tag_room(self, room):
        """Room id objects are tagged with: a building room -> its building's pseudo-room ('shed'); else unchanged."""
        if room in self.building_rooms:
            b = self.building_rooms[room]['building']
            return next(x for x in self.spec['exterior']['buildings'] if x['id'] == b)['room']
        return room

    def level(self, room):
        """'B' | 'G' | '1' | '2' for house rooms, 'X' for everything else (schema 1: always 'G')."""
        if room in self.rooms:
            return self.rooms[room].get('level', 'G')
        return 'X' if self.schema == 2 else 'G'

    def rooms_on(self, level):
        if level == 'X':
            return list(PSEUDO_ROOMS)
        return [rid for rid, r in self.rooms.items() if r.get('level', 'G') == level]

    def kind(self, room):
        """'room' | 'stairwell' | 'void' | 'exterior' | 'site' (pseudo-rooms and building rooms). KeyError if unknown."""
        if room in self.rooms:
            return self.rooms[room].get('kind', 'room')
        if room in PSEUDO_ROOMS or room in self.building_rooms:
            return 'site'
        raise KeyError(room)

    def is_exterior(self, room):
        return self.kind(room) in ('exterior', 'site')

    def module_of(self, room):
        """Name of blender/rooms/<module>.py that furnishes this room."""
        return MODULE_OF.get(room, self.tag_room(room))

    def room_poly(self, rid, rect=False):
        """Room polygon [(x, y)]. rect=True: every polygon-edge chamfer squared off through its outer corner c."""
        poly = [tuple(p) for p in self._room(rid)['polygon']]
        if not rect:
            return poly
        ccw, out, ends = poly_area(poly) > 0, [], set()
        for p, q in zip(poly, poly[1:] + poly[:1]):
            out.append(p)
            if _diagonal(p, q):
                out.append(_outer_corner(p, q, ccw))
                ends |= {p, q}
        return [p for i, p in enumerate(out)
                if p not in ends or abs(_cross(out[i - 1], p, out[(i + 1) % len(out)])) > 1e-9]

    def chamfers(self, rid):
        """[dict(id, p, q, c, v, z=(z0, z1), stop=None|(z1, z2), reflex)], p -> q in polygon loop order.
        Polygon-edge chamfers (reflex=False): p, q = the diagonal edge, c = v = the square corner outside the polygon.
        Bay arris splays (reflex=True, id '<bay id>.<i>'): v = the reflex polygon vertex, p / q = v moved width/sqrt(2)
        along the edge before / after it, c = p + q - v (inside the wall); stop = the 45-to-90 transition above z."""
        if rid not in self.rooms:
            return []
        poly, r, out = self.room_poly(rid), self.rooms[rid], []
        ccw, n = poly_area(poly) > 0, len(poly)
        for i, p in enumerate(poly):
            q = poly[(i + 1) % n]
            if not _diagonal(p, q):
                continue
            f = next((f for f in self.features if f['type'] == 'chamfer' and f.get('level') == r.get('level')
                      and rid in f.get('rooms', [f.get('room')])
                      and {tuple(e) for e in f['face']} == {p, q}), None)
            if f is None:
                raise ValueError(f'room {rid}: diagonal edge {p} -> {q} has no chamfer feature')
            c = _outer_corner(p, q, ccw)
            out.append(dict(id=f['id'], p=p, q=q, c=c, v=c, z=tuple(f['z']), stop=None, reflex=False))
        for f in self.features:
            if f['type'] != 'bay' or f.get('room') != rid:
                continue
            for i, ch in enumerate(f.get('chamfers', [])):
                k = tuple(ch['corner'])
                j = poly.index(k)
                leg = ch['width'] / math.sqrt(2)
                p, q = _toward(k, poly[j - 1], leg), _toward(k, poly[(j + 1) % n], leg)
                c = (round(p[0] + q[0] - k[0], 6), round(p[1] + q[1] - k[1], 6))
                out.append(dict(id=f"{f['id']}.{i}", p=p, q=q, c=c, v=k, z=tuple(ch['z']),
                                stop=tuple(ch['stop']) if ch.get('stop') else None, reflex=True))
        return out

    def floor_z(self, rid, x=None, y=None):
        """floorZ; with x, y: the low side of a floor_step and the treads of `steps` leading into the room."""
        z = float(self._room(rid)['floorZ'])
        if x is None:
            return z
        for f in self.features:
            if f['type'] == 'floor_step' and f.get('room') == rid:
                x0, y0 = f['line'][0]
                if {'east': x > x0, 'west': x < x0, 'north': y > y0, 'south': y < y0}[f['lowSide']]:
                    z = float(f['zLow'])
        for t in self.step_treads(rid):
            if poly_contains(x, y, t['poly']):
                z = t['z']
        return z

    def ceil_z(self, rid, x=None, y=None):
        """No x, y: ceilingZ = the HIGHEST ceiling of the room (None for the balcony). With x, y: the ceiling there =
        min(ceilingZ, ceilingZones, ceiling.planes, ceiling_haunch slopes). under_roof rooms: their lining =
        min(ceilingZ, roof_z + ceiling.offset, ceiling.planes) (roof_under where the room has no offset); lib.envelope
        keeps the slab underside 1 cm above it (eaves_front 1.00 at the knee-wall back, eaves_rear 0.01 under the slab)."""
        r = self._room(rid)
        top = None if r.get('ceilingZ') is None else float(r['ceilingZ'])
        if x is None:
            return top
        c = r.get('ceiling') or {}
        zs = [] if top is None else [top]
        zs += [plane_z(p, x, y) for p in c.get('planes', []) if poly_contains(x, y, p['polygon'])]
        if c.get('type') == 'under_roof':
            rz = self.roof_z(x, y)
            if rz is not None:
                zs.append(rz + c['offset'] if 'offset' in c else self.roof_under(x, y))
            return min(zs) if zs else None
        zs += [float(cz['z']) for cz in r.get('ceilingZones', []) if poly_contains(x, y, cz['polygon'])]
        zs += [_haunch_z(f, x, y) for f in self.features if f['type'] == 'ceiling_haunch' and f.get('room') == rid
               and poly_contains(x, y, f['polygon'])]
        return min(zs) if zs else None

    def feature(self, fid):
        return next(f for f in self.features if f['id'] == fid)

    def room_at(self, x, y, level=None):
        """House room id whose polygon contains (x, y), else None. Rooms stack: pass level on schema 2."""
        for rid, r in self.rooms.items():
            if (level is None or r.get('level', 'G') == level) and point_in_poly(x, y, self.room_poly(rid)):
                return rid
        return None

    # ---- roof
    def _roof_top(self, x, y, ground=False):
        """(z, plane) of the highest roof plane over (x, y), or None. ground=True: the porch lean-to only."""
        best = None
        for p in self.spec.get('roof', {}).get('planes', []):
            if (p.get('level') == 'G') == ground and poly_contains(x, y, p['polygon']):
                z = plane_z(p, x, y)
                if best is None or z > best[0]:
                    best = (z, p)
        return best

    def roof_z(self, x, y, ground=False):
        """Outer roof surface (upper envelope of the planes) at (x, y), or None."""
        top = self._roof_top(x, y, ground)
        return top[0] if top else None

    def roof_plane(self, x, y, ground=False):
        """Id of the plane that is the roof surface at (x, y), or None."""
        top = self._roof_top(x, y, ground)
        return top[1]['id'] if top else None

    def roof_under(self, x, y, ground=False):
        """Underside of the roof slab at (x, y) = roof_z - roof_slab_t(that plane), or None."""
        top = self._roof_top(x, y, ground)
        return top[0] - self.roof_slab_t(top[1]['id']) if top else None

    def roof_slab_t(self, plane_id):
        """Slab thickness of a roof plane: structure.thickness - 0.01 (0.30), reduced on FLAT planes so the underside
        clears the highest ceiling below by 0.01 (rear_flat, stair_dormer: 0.24)."""
        if plane_id not in self._slab:
            roof = self.spec['roof']
            p = next(p for p in roof['planes'] if p['id'] == plane_id)
            t = roof['structure']['thickness'] - 0.01
            # ponytail: pitched planes run parallel to their sloped ceilings at structure.thickness, so only flat planes
            # are measured against the ceilings (10 cm sample grid; rooms of the plane's own level).
            if not p['z']['cx'] and not p['z']['cy']:
                lvl = 'G' if p.get('level') == 'G' else self.levels[-1]
                rooms = [rid for rid, r in self.rooms.items() if r.get('level') == lvl and r.get('kind') == 'room'
                         and (r.get('ceiling') or {}).get('type') != 'under_roof']
                xs, ys = [q[0] for q in p['polygon']], [q[1] for q in p['polygon']]
                for i in range(int((max(xs) - min(xs)) / 0.1)):
                    for j in range(int((max(ys) - min(ys)) / 0.1)):
                        x, y = min(xs) + 0.05 + 0.1 * i, min(ys) + 0.05 + 0.1 * j
                        if point_in_poly(x, y, p['polygon']):
                            for rid in rooms:
                                if point_in_poly(x, y, self.rooms[rid]['polygon']):
                                    t = min(t, p['z']['c0'] - self.ceil_z(rid, x, y) - 0.01)
            self._slab[plane_id] = round(t, 3)
        return self._slab[plane_id]

    # ---- stairs
    def stair(self, sid):
        """The stairs json + 'treads': [dict(n, poly, z, riser)], n = 1 .. risers - 1 (tread n lies behind riser n,
        `riser` = that riser line). Flights: walk.polygon cut by walk.risers; `steps`: strips between riserLines."""
        s = next(s for s in self.stairs if s['id'] == sid)
        return dict(s, treads=_flight_treads(s) if s['kind'] == 'flight' else _steps_treads(s))

    def step_treads(self, rid):
        """Treads [dict(n, poly, z, riser)] of the `steps` sets whose toRoom is this room (they lie inside it)."""
        if self.schema == 1:
            return []
        return [t for s in self.stairs if s['kind'] == 'steps' and s['toRoom'] == rid for t in _steps_treads(s)]

    # ---- site
    def zone(self, zid):
        return self.zones[zid]

    def zones_of(self, pseudo):
        """Ids of the zones owned by a pseudo-room, file order."""
        return [zid for zid, z in self.zones.items() if z.get('room') == pseudo]

    def zone_at(self, x, y):
        """Id of the zone containing (x, y) (1 mm tolerance; smallest area first, so overlays win), else None."""
        hits = [z for z in self.zones.values() if poly_contains(x, y, z['polygon'], 1e-3)]
        return min(hits, key=lambda z: abs(poly_area(z['polygon'])))['id'] if hits else None

    def zone_z(self, zid, x=None, y=None):
        """Surface Z of a zone; with x, y its `fall` is applied (clamped beyond the end points)."""
        z = self.zones[zid]
        fall = z.get('fall')
        if x is None or not fall:
            return float(z['z'])
        (fx, fy), (tx, ty), (z0, z1) = fall['from'], fall['to'], fall['z']
        t = ((x - fx) * (tx - fx) + (y - fy) * (ty - fy)) / ((tx - fx) ** 2 + (ty - fy) ** 2)
        return z0 + min(1.0, max(0.0, t)) * (z1 - z0)

    def ground_z(self, x, y):
        """Outdoor surface Z at (x, y): exterior step treads override zones; None outside every zone."""
        treads = [t for s in self.spec.get('exterior', {}).get('steps', []) for t in s.get('treads', [])
                  if poly_contains(x, y, t['polygon'], 1e-3)]
        if treads:
            return float(min(treads, key=lambda t: abs(poly_area(t['polygon'])))['z'])
        zid = self.zone_at(x, y)
        return None if zid is None else self.zone_z(zid, x, y)

    def neighbour_top(self, nb, x, y):
        """(z, part index) of a neighbour's massing over (x, y): the highest of its `parts` there (`top` = a flat Z or
        a plane c0 / cx / cy), else (z[1], -1) where it has no part (or no parts at all)."""
        best = None
        for i, pt in enumerate(nb.get('parts', [])):
            if poly_contains(x, y, pt['polygon'], 1e-4):
                t = pt['top']
                z = t['c0'] + t['cx'] * x + t['cy'] * y if isinstance(t, dict) else float(t)
                if best is None or z > best[0]:
                    best = (z, i)
        return best or (float(nb['z'][1]) if not nb.get('parts') else -99.0, -1)

    # ---- collections / tagging
    def col(self, name):
        c = bpy.data.collections.get(name)
        if c is None:
            c = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(c)
        return c

    def add(self, obj, room, kind, plan_sym=None, lm=None):
        """Link obj AND its parented children (props [H] hierarchies) into room_<room> ('shell' when
        kind == 'shell') and tag them: room (after tag_room), level, kind, lm. plan_sym goes on obj only. Returns obj."""
        assert kind in KINDS, f'ctx.add: unknown kind {kind!r}'
        room = self.tag_room(room)
        level = self.level(room)
        target = self.col('shell' if kind == 'shell' else f'room_{room}')
        for o in [obj] + list(obj.children_recursive):
            for c in list(o.users_collection):
                if c is not target:
                    c.objects.unlink(o)
            if o.name not in target.objects:
                target.objects.link(o)
            o['room'] = room
            o['level'] = level
            o['kind'] = 'light' if o.type == 'LIGHT' else kind      # child lamps count as light fittings
            o['lm'] = lm or ('static' if o['kind'] in STATIC else 'dynamic')
        if plan_sym:
            obj['plan_sym'] = plan_sym
        return obj

    # ---- openings
    def _outside_end(self, o):
        """The end of `connects` that stands for outside ('outside' or a kind-'exterior' room), else None."""
        return next((r for r in o['connects']
                     if r == 'outside' or (r in self.rooms and self.rooms[r].get('kind') == 'exterior')), None)

    def exterior_openings(self, level=None):
        """Ids of the openings to the outside (house and buildings), file order; level 'X' = the building openings."""
        return [oid for oid, o in self.openings.items()
                if (level is None or o.get('level', 'G') == level) and self._outside_end(o) is not None]

    def facade_of(self, oid):
        return next((f for f in self.spec.get('exterior', {}).get('facades', []) if oid in f['openings']), None)

    def opening_frame(self, oid):
        """Placement frame of an opening. Vectors are mathutils.Vector (tuples without Blender).
        center  (x, y, z): on the wall CENTRELINE, mid-width, z = bottom of the hole (z0 + sill)
        z0      world Z the opening is measured from = its floorZ (schema 1: floor of the room it connects)
        along   unit xy along the wall a->b;  normal = unit xy LEFT of a->b (points into room_pos)
        width, height (clear, above sill), sill, head (= sill+height), top (hole top incl. fanlight): above z0
        wall_thickness; face_pos / face_neg = signed distance along normal from the centreline to
        the actual wall faces (differs from +-t/2 where a 'reveal' feature sets the frame back)
        room_pos / room_neg = the WALL's rooms on the +normal / -normal side; swing_sign = +1/-1/0 side the
        leaf swings to (a kind-'exterior' room such as the balcony counts as the wall's 'outside' side)
        level; exterior (bool); for exterior openings, else None: outward (unit xy towards outside), face_out
        (signed distance centreline -> outer wall face), ext_reveal (outer face -> outside of the frame, which is
        FRAME_D deep), outside_room (the connects end standing for outside: 'outside' or e.g. 'balcony')
        plus the raw json fields (type, style, surround, hinge, hingeAt, ...)."""
        o = self.openings[oid]
        w = self.walls[o['wall']]
        (ax, ay), (bx, by) = w['a'], w['b']
        ln = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / ln, (by - ay) / ln
        nx, ny = -uy, ux
        t = w['thickness']
        cx, cy = o['center']
        if 'floorZ' in o:
            z0 = float(o['floorZ'])
        else:
            inside = next((r for r in o['connects'] if r != 'outside'), None)
            z0 = self.floor_z(inside) if inside in self.rooms else 0.0
        head = o['sill'] + o['height']
        top = max(head, (o.get('transom') or {}).get('height', 0.0))
        fp, fn = t / 2, -t / 2
        for f in self.features:             # reveals (of the opening's level) set the frame back from the room face
            if f['type'] != 'reveal' or f.get('level') != o.get('level'):
                continue
            ds = [(p[0] - cx) * nx + (p[1] - cy) * ny for p in f['polygon']]
            ss = [(p[0] - cx) * ux + (p[1] - cy) * uy for p in f['polygon']]
            if not (min(ss) < 0 < max(ss)):
                continue
            if min(ds) <= fp - 0.01 <= max(ds):
                fp = min(ds)
            if min(ds) <= fn + 0.01 <= max(ds):
                fn = max(ds)
        rp, rn = w['rooms'][0], w['rooms'][1]
        out_room = self._outside_end(o)
        out_sign = 1 if rp == 'outside' else -1 if rn == 'outside' else 0
        exterior = out_room is not None and out_sign != 0
        sw = o.get('swingInto')
        if sw is None or rp == rn:
            swing = 0
        else:
            swing = 1 if sw == rp else -1 if sw == rn else out_sign if exterior and sw == out_room else 0
        f = dict(o)
        f.update(center=Vector((cx, cy, z0 + o['sill'])), along=Vector((ux, uy)), normal=Vector((nx, ny)),
                 width=o['width'], height=o['height'], sill=o['sill'], head=head, top=top, z0=z0,
                 wall_thickness=t, face_pos=round(fp, 4), face_neg=round(fn, 4), room_pos=rp, room_neg=rn,
                 swing_sign=swing, virtual=bool(w.get('virtual')), level=o.get('level', 'G'), exterior=exterior,
                 outward=None, face_out=None, ext_reveal=None, outside_room=None)
        if exterior:
            face_out = out_sign * t / 2
            if 'extReveal' in o:
                er = o['extReveal']
            elif 'revealDepth' in o:
                er = t - o['revealDepth'] - FRAME_D
            else:                           # d = outer face -> room-side face after reveals
                d = abs(face_out - (fn if out_sign > 0 else fp))
                er = min(0.10 if o['type'] in WINDOWS else 0.08, d - FRAME_D)
            f.update(outward=Vector((nx * out_sign, ny * out_sign)), face_out=round(face_out, 4),
                     ext_reveal=round(max(0.01, er), 4), outside_room=out_room)
        return f


# ---- pure 2D helpers (polygons are sequences of (x, y))
def point_in_poly(x, y, poly):
    poly = list(poly)
    inside = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def poly_contains(x, y, poly, tol=1e-6):
    """Inside the polygon or within tol of its boundary."""
    poly = list(poly)
    if point_in_poly(x, y, poly):
        return True
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        dx, dy = x1 - x0, y1 - y0
        t = min(1.0, max(0.0, ((x - x0) * dx + (y - y0) * dy) / ((dx * dx + dy * dy) or 1.0)))
        if math.hypot(x - x0 - t * dx, y - y0 - t * dy) <= tol:
            return True
    return False


def poly_area(poly):
    """Signed area, > 0 for counter-clockwise."""
    poly = list(poly)
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1])) / 2


def plane_z(plane, x, y):
    """z = c0 + cx*x + cy*y of a roof / ceiling plane dict."""
    z = plane['z']
    return z['c0'] + z['cx'] * x + z['cy'] * y


def _haunch_z(f, x, y):
    """Z of a ceiling_haunch slope at (x, y): z[0] at the wall line wallAt (an x or a y edge of its polygon), rising
    linearly to z[1] at the opposite edge (as lib.shell._haunch builds it)."""
    xs, ys = [p[0] for p in f['polygon']], [p[1] for p in f['polygon']]
    (z0, z1), w = f['z'], f['wallAt']
    if min(abs(w - min(xs)), abs(w - max(xs))) < 1e-6:
        v, o = x, (max(xs) if abs(w - min(xs)) < 1e-6 else min(xs))
    else:
        v, o = y, (max(ys) if abs(w - min(ys)) < 1e-6 else min(ys))
    return z0 + (z1 - z0) * min(1.0, max(0.0, (v - w) / (o - w)))


def clip_poly(poly, a, b, left=True):
    """Part of poly on the left (or right) of the infinite line a -> b (Sutherland-Hodgman)."""
    sg = 1 if left else -1
    poly = [tuple(p) for p in poly]
    side = [sg * _cross(a, b, p) for p in poly]
    out = []
    for i, p in enumerate(poly):
        q, sp, sq = poly[(i + 1) % len(poly)], side[i], side[(i + 1) % len(poly)]
        if sp >= -1e-9:
            out.append(p)
        if (sp > 1e-9 and sq < -1e-9) or (sp < -1e-9 and sq > 1e-9):
            k = sp / (sp - sq)
            out.append((round(p[0] + (q[0] - p[0]) * k, 6), round(p[1] + (q[1] - p[1]) * k, 6)))
    return [p for i, p in enumerate(out) if p != out[i - 1]]


def _cross(a, b, p):
    """> 0 when p is on the left of a -> b."""
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def _diagonal(p, q):
    return abs(p[0] - q[0]) > 1e-9 and abs(p[1] - q[1]) > 1e-9


def _outer_corner(p, q, ccw):
    """Of (p.x, q.y) and (q.x, p.y), the one outside the polygon whose edge p -> q this is."""
    c = (p[0], q[1])
    return c if (_cross(p, q, c) < 0) == ccw else (q[0], p[1])


def _toward(k, a, d):
    ln = math.hypot(a[0] - k[0], a[1] - k[1])
    return (round(k[0] + (a[0] - k[0]) * d / ln, 6), round(k[1] + (a[1] - k[1]) * d / ln, 6))


def _flight_treads(s):
    # Tread k = footprint beyond risers 1..k (left of each) and before riser k+1. ponytail: riser lines are taken as
    # infinite, so the strip <= 5 cm wide behind a newel goes to whichever tread the extended lines give it.
    wk = s['walk']
    rs, sg = wk['risers'], 1 if s['toZ'] > s['fromZ'] else -1
    out, beyond = [], wk['polygon']
    for k in range(1, len(rs)):
        beyond = clip_poly(beyond, *rs[k - 1])
        out.append(dict(n=k, poly=clip_poly(beyond, *rs[k], left=False), z=round(s['fromZ'] + sg * k * s['rise'], 4),
                        riser=rs[k - 1]))
    return out


def _steps_treads(s):
    ls, sg = s.get('riserLines', []), 1 if s['toZ'] > s['fromZ'] else -1
    return [dict(n=k + 1, poly=[tuple(p) for p in ls[k]] + [tuple(p) for p in reversed(ls[k + 1])],
                 z=round(s['fromZ'] + sg * (k + 1) * s['rise'], 4), riser=ls[k]) for k in range(len(ls) - 1)]
