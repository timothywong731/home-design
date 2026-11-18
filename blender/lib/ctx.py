"""House context: spec/house.json accessors, collections, object tagging. See blender/CONTRACT.md."""
import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
KINDS = {'shell', 'trim', 'joinery', 'fit', 'furn', 'decor', 'light'}
STATIC = {'shell', 'trim', 'joinery', 'fit'}


class House:
    def __init__(self, spec):
        self.spec = spec
        self.root = ROOT
        self.rooms = {r['id']: r for r in spec['rooms']}
        self.walls = {w['id']: w for w in spec['walls']}
        self.openings = {o['id']: o for o in spec['openings']}
        self.features = spec['features']
        self.stairs = spec['stairs']
        self.grid = None          # set by shell.build (lib.shell.Grid)

    @classmethod
    def load(cls, path=None):
        return cls(json.loads(Path(path or ROOT / 'spec' / 'house.json').read_text(encoding='utf-8')))

    # ---- accessors
    def room_poly(self, rid):
        return [tuple(p) for p in self.rooms[rid]['polygon']]

    def floor_z(self, rid):
        return float(self.rooms[rid]['floorZ'])

    def ceil_z(self, rid):
        return float(self.rooms[rid]['ceilingZ'])

    def feature(self, fid):
        return next(f for f in self.features if f['id'] == fid)

    def room_at(self, x, y):
        """Room id whose polygon contains (x, y), else None."""
        for rid in self.rooms:
            if point_in_poly(x, y, self.room_poly(rid)):
                return rid
        return None

    # ---- collections / tagging
    def col(self, name):
        c = bpy.data.collections.get(name)
        if c is None:
            c = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(c)
        return c

    def add(self, obj, room, kind, plan_sym=None, lm=None):
        """Link obj AND its parented children (props [H] hierarchies) into room_<room> ('shell' when
        kind == 'shell') and tag them. plan_sym goes on obj only. Returns obj."""
        assert kind in KINDS, f'ctx.add: unknown kind {kind!r}'
        target = self.col('shell' if kind == 'shell' else f'room_{room}')
        for o in [obj] + list(obj.children_recursive):
            for c in list(o.users_collection):
                if c is not target:
                    c.objects.unlink(o)
            if o.name not in target.objects:
                target.objects.link(o)
            o['room'] = room
            o['kind'] = 'light' if o.type == 'LIGHT' else kind      # child lamps count as light fittings
            o['lm'] = lm or ('static' if o['kind'] in STATIC else 'dynamic')
        if plan_sym:
            obj['plan_sym'] = plan_sym
        return obj

    # ---- openings
    def opening_frame(self, oid):
        """Placement frame of an opening. All vectors are mathutils.Vector.
        center  (x, y, z): on the wall CENTRELINE, mid-width, z = bottom of the hole (floor + sill)
        along   unit xy along the wall a->b;  normal = unit xy LEFT of a->b (points into room_pos)
        width, height (clear, above sill), sill, head (= sill+height), top (hole top incl. fanlight)
        wall_thickness; face_pos / face_neg = signed distance along normal from the centreline to
        the actual wall faces (differs from +-t/2 where a 'reveal' feature sets the frame back)
        room_pos / room_neg = rooms on the +normal / -normal side; swing_sign = +1/-1/0 side the
        leaf swings to; plus the raw json fields (type, style, surround, hinge, hingeAt, ...)."""
        o = self.openings[oid]
        w = self.walls[o['wall']]
        a, b = Vector(w['a']), Vector(w['b'])
        along = (b - a).normalized()
        normal = Vector((-along.y, along.x))
        t = w['thickness']
        c2 = Vector(o['center'])
        inside = next((r for r in o['connects'] if r != 'outside'), None)
        z0 = self.floor_z(inside) if inside in self.rooms else 0.0
        head = o['sill'] + o['height']
        top = max(head, (o.get('transom') or {}).get('height', 0.0))
        fp, fn = t / 2, -t / 2
        for f in self.features:             # reveals set the frame back from the room face
            if f['type'] != 'reveal':
                continue
            ds = [(Vector(p) - c2).dot(normal) for p in f['polygon']]
            ss = [(Vector(p) - c2).dot(along) for p in f['polygon']]
            if not (min(ss) < 0 < max(ss)):
                continue
            if min(ds) <= fp - 0.01 <= max(ds):
                fp = min(ds)
            if min(ds) <= fn + 0.01 <= max(ds):
                fn = max(ds)
        rp, rn = w['rooms'][0], w['rooms'][1]
        sw = o.get('swingInto')
        f = dict(o)
        f.update(center=Vector((c2.x, c2.y, z0 + o['sill'])), along=along, normal=normal,
                 width=o['width'], height=o['height'], sill=o['sill'], head=head, top=top, z0=z0,
                 wall_thickness=t, face_pos=round(fp, 4), face_neg=round(fn, 4), room_pos=rp, room_neg=rn,
                 swing_sign=0 if sw is None or rp == rn else (1 if sw == rp else -1 if sw == rn else 0),
                 virtual=bool(w.get('virtual')))
        return f


def point_in_poly(x, y, poly):
    inside = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside
