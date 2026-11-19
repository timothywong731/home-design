"""Interaction tags (see blender/INTERACT.md). tag() writes obj['ix'] = json; the viewer animates."""
import json
import math

from mathutils import Matrix, Vector

TYPES = {
    'hinge': {'p', 'deg'},
    'slide': {'d'},
    'show': {'when'},
    'trigger': set(),
    'clock': {'hand', 'p', 'a'},
    'light': {'rooms'},
    'lamp': set(),
}
OPTIONAL = {'g', 'label', 'on', 'reach', 'blocks', 'a', 'dur', 'fx', 'rooms', 'excl'}
FX = {'none', 'water', 'flame', 'tv', 'glow'}


def _vec(v):
    return [round(float(c), 4) for c in v]


def tag(obj, t, **kw):
    """Tag one object. Points/vectors are Blender world metres of the object as modelled (state 0)."""
    if t not in TYPES:
        raise ValueError(f'ix type {t!r}: expected one of {sorted(TYPES)}')
    missing = TYPES[t] - kw.keys()
    unknown = kw.keys() - TYPES[t] - OPTIONAL
    if missing or unknown:
        raise ValueError(f'ix {t} on {obj.name}: missing {sorted(missing)}, unknown {sorted(unknown)}')
    if kw.get('fx', 'none') not in FX:
        raise ValueError(f'ix fx {kw["fx"]!r}: expected one of {sorted(FX)}')
    if t == 'clock' and kw['hand'] not in ('h', 'm', 's'):
        raise ValueError('ix clock hand must be h, m or s')
    d = {'t': t, 'g': kw.pop('g', None) or obj.name}
    for k, v in kw.items():
        d[k] = _vec(v) if k in ('p', 'a', 'd') else v
    obj['ix'] = json.dumps(d, separators=(',', ':'))
    return obj


def tag_many(objs, t, **kw):
    """Same tag on several objects that move together (they must share g)."""
    if 'g' not in kw:
        raise ValueError('tag_many needs g=')
    return [tag(o, t, **kw) for o in objs]


def pose(objs, state=1):
    """Apply state 1 in Blender for a check render (hinge / slide move, show hides or reveals)."""
    for o in objs:
        if 'ix' not in o.keys():
            continue
        d = json.loads(o['ix'])
        if d['t'] == 'hinge' and state:
            p, a = Vector(d['p']), Vector(d.get('a', (0, 0, 1)))
            m = Matrix.Translation(p) @ Matrix.Rotation(math.radians(d['deg']), 4, a) @ Matrix.Translation(-p)
            o.matrix_world = m @ o.matrix_world
        elif d['t'] == 'slide' and state:
            o.matrix_world = Matrix.Translation(Vector(d['d'])) @ o.matrix_world
        elif d['t'] == 'show':
            o.hide_render = o.hide_viewport = d['when'] != state


def _demo():
    class O(dict):
        name = 'x.door'
    o = tag(O(), 'hinge', p=(1, 2, 0), deg=-95, label='Door')
    assert json.loads(o['ix']) == {'t': 'hinge', 'g': 'x.door', 'p': [1.0, 2.0, 0.0], 'deg': -95, 'label': 'Door'}
    for bad in (lambda: tag(O(), 'hinge', deg=1), lambda: tag(O(), 'spin'), lambda: tag(O(), 'show', when=1, fx='smoke')):
        try:
            bad()
        except ValueError:
            continue
        raise AssertionError('bad tag accepted')
    print('IX OK')


if __name__ == '__main__':
    _demo()
