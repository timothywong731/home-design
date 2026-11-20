"""Joinery: door leaves, frames / linings, architraves, doorcases, windows, shutters and door
furniture for every opening in spec/house.json, built by `style` / `surround` key.
Owner: joinery agent. Public API: blender/lib/README.md (section "joinery") and, for the multi-level / exterior
work (sashes, hatches, shed, doorcases, ext_reveal), blender/lib/README.md. Test: blender/test_joinery.py.

Frames used below (all right-handed, Z up, metres):
  side frame  origin = opening centre on the WALL FACE of one room at floor level; +Y out of the
              wall into that room; +X to the LEFT of a viewer in the room facing the wall.
  leaf frame  x = 0 (hinge edge) .. w (latch edge); y = 0 mid-thickness, +y = the face seen from the
              room the leaf swings into; z = 0 .. h. Leaf OBJECTS have their origin on the hinge axis.
"""
import math

from mathutils import Matrix, Vector

from . import interact as IX, mouldings as mo
from .ctx import FRAME_D

MB, PROFILES = mo.MB, mo.PROFILES
SKIN = 0.004            # lining skin fixed on the faces of the hole the shell cut (hole = spec width)
GAP = 0.003             # leaf to lining
FLOOR_GAP = 0.006
POCKET_PROJECT = 0.09   # how much of the WC pocket door stands out of its pocket, as filmed in f_0499 (0.61 = shut)
# open angle per leaf of double doors: f(hinge world xy) -> degrees (house.json has no per-leaf state)
LEAF_ANGLE = {'d_inner': lambda p: 85.0 if p.x < 0 else 0.0}
# interaction tags (blender/INTERACT.md): tooltip noun per opening, and the angle a leaf modelled shut opens to
LABEL = {'d_street': 'Front door', 'd_french': 'Garden door', 'd_back': 'Back door', 'd_basement': 'Basement door',
         'd_understairs': 'Cupboard door', 'd_balcony': 'Balcony door', 'shed_d1': 'Workshop door',
         'shed_store_doors': 'Store door'}
# opening id -> degrees a leaf modelled shut opens to (default 90); lower it where the open leaf would hit something
# d_french 100 (garden.md 10: tips clear the deck chairs and planters); shed_store_doors 90: at 95 the north leaf ran
# 10 mm into the shed front wall
OPEN_DEG = {'d_balcony': 85.0, 'shed_d1': 100.0, 'shed_store_doors': 90.0, 'd_french': 100.0}
# [round 4] living bay shutters: the panels could swing only 5-10 degrees clear of the tied-back curtains and the lamp
# table, so "Open shutter" did nothing visible (IX-02). Opening a shutter now tilts its louvres open, as the owner does
# in v2 f_0759-0766: louvres tilted open (SHUTTER_TILT[0]) as modelled, shut (SHUTTER_TILT[1], the night look of
# living.md 2.3) in state 1.
SHUTTER_TILT = (12.0, 75.0)
HATCH_WEST_DEG = {'h_eaves_rear': 95.0}      # at 110 the west leaf's knob came within 10 mm of the loft TV face (x 1.292)
DARK_HEAD = 0.18        # dark timber head board over the balcony door frame: shows 0.12 under the 2.30 pelmet (v3 f_0159)
POCKET_OPEN = {'d_wc'}  # pocket doors modelled open, as filmed; every other one is modelled shut
T = Matrix.Translation


def RZ(a):
    return Matrix.Rotation(a, 4, 'Z')


def RX(a):
    return Matrix.Rotation(a, 4, 'X')


def base_frame(fr):
    """Opening centre on the wall centreline at floor level: X along the wall, Y = fr['normal']."""
    a, n, c = fr['along'], fr['normal'], fr['center']
    return Matrix(((a.x, n.x, 0, c.x), (a.y, n.y, 0, c.y), (0, 0, 1, fr['z0']), (0, 0, 0, 1)))


def side_frame(fr, sgn):
    """Side frame (see module doc) of the room on the +normal (sgn=+1) or -normal (-1) side."""
    M = base_frame(fr) @ T((0, fr['face_pos'] if sgn > 0 else fr['face_neg'], 0))
    return M if sgn > 0 else M @ RZ(math.pi)


def side_of(fr, room):
    return 1 if room == fr['room_pos'] else -1


def wall_t(fr):
    return fr['face_pos'] - fr['face_neg']


# --------------------------------------------------------------------------- furniture
def lever_handle(mb, x, z, t, plate=(0.045, 0.150), length=0.11, toward=-1, key=False, cyl=False,
                 faces=(1, -1), mat='brass'):
    """Lever on a backplate on the leaf faces at (x, z) (leaf frame); lever points to `toward` x."""
    M0 = mb.M.copy()
    pw, ph = plate
    for s in faces:
        y = s * t / 2
        mb.at(M0)
        mb.box((x - pw / 2, y, z - ph * 0.62), (x + pw / 2, y + s * 0.004, z + ph * 0.38), mat, bev=0.0012)
        mb.at(M0 @ T((x, y + s * 0.004, z)) @ RX(-s * math.pi / 2))
        mb.lathe([(0.011, 0), (0.011, 0.005), (0.0075, 0.009), (0.0075, 0.040), (0, 0.040)], mat, 10)
        mb.at(M0)
        yy = y + s * 0.036
        pts = [(x, yy, z), (x + toward * length * 0.3, yy, z + 0.004), (x + toward * length * 0.7, yy, z + 0.001),
               (x + toward * length, yy, z - 0.006)]
        mb.tube(pts, 0.0065, mat, 8)
        mb.at(M0 @ T(pts[-1]))
        mb.lathe([(0, -0.009), (0.008, -0.005), (0.010, 0), (0.008, 0.005), (0, 0.009)], mat, 8)
        mb.at(M0)
        if key:
            mb.box((x - 0.0025, y + s * 0.004, z - ph * 0.42), (x + 0.0025, y + s * 0.0048, z - ph * 0.30), 'black')
        if cyl:
            mb.at(M0 @ T((x, y + s * 0.004, z - ph * 0.40)) @ RX(-s * math.pi / 2))
            mb.lathe([(0.0085, 0), (0.0085, 0.010), (0, 0.010)], 'chrome', 10)
    mb.at(M0)


def flush_pull(mb, x, z, t, faces=(1, -1)):
    M0 = mb.M.copy()
    for s in faces:
        mb.at(M0 @ T((x, s * t / 2, z)) @ RX(-s * math.pi / 2))
        mb.lathe([(0.0275, 0), (0.0275, 0.003), (0.023, 0.003), (0.021, 0.001), (0, 0.001)], 'brass', 16)
    mb.at(M0)


def butt_hinges(mb, h, upvc=False):
    """Three hinges on the hinge axis (object origin) of a leaf of height h."""
    for zc in (0.22, h / 2, h - 0.21):
        if upvc:
            mb.box((-0.011, -0.022, zc - 0.045), (0.011, 0.007, zc + 0.045), 'upvc_white', bev=0.002)
        else:
            mb.lathe([(0, zc - 0.05), (0.0062, zc - 0.05), (0.0062, zc + 0.05), (0, zc + 0.05)], 'brass', 8)
            mb.box((-0.022, -0.0075, zc - 0.05), (0.022, -0.004, zc + 0.05), 'brass')      # flaps (edge-on)


# --------------------------------------------------------------------------- leaf parts
def _rect_bead(mb, x0, z0, x1, z1, y, s, prof, mat):
    """Moulding run round the inside of a rectangular opening in a leaf face (plane y, facing
    s*Y). Profile d = inward from the frame edge, h = out of the face."""
    path = ([(x0, y, z0), (x0, y, z1), (x1, y, z1), (x1, y, z0)] if s > 0 else
            [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])
    mb.sweep(prof, path, mat, closed=True, up=(0, s, 0))


def _field(mb, x0, z0, x1, z1, ye, yt, inset, s, mat, grain=2):
    """Raised-and-fielded panel face: chamfered margin from depth ye up to a flat field at yt."""
    a = [(x0, ye, z0), (x1, ye, z0), (x1, ye, z1), (x0, ye, z1)]
    b = [(x0 + inset, yt, z0 + inset), (x1 - inset, yt, z0 + inset), (x1 - inset, yt, z1 - inset), (x0 + inset, yt, z1 - inset)]
    off = mb._off()
    mb.face(b, mat, (0, s, 0), grain, off)
    if inset > 0:
        for i in range(4):
            j = (i + 1) % 4
            mb.face([a[i], a[j], b[j], b[i]], mat, (0, s, 0), grain, off)


def _panel(mb, x0, z0, x1, z1, t, mat, bead='bead_bolection', recess=0.008, raised=0.005, margin=0.028):
    """Panel filling a frame opening on both faces: bead round the edge + raised field."""
    prof = [(d, h * recess / 0.008 if h < 0 else h) for d, h in PROFILES[bead]]
    bw = prof[0][0]
    for s in (1, -1):
        y = s * t / 2
        _rect_bead(mb, x0, z0, x1, z1, y, s, prof, mat)
        _field(mb, x0 + bw, z0 + bw, x1 - bw, z1 - bw, y - s * recess, y - s * (recess - raised),
               margin if raised else 0.0, s, mat)


def _glass(gb, x0, z0, x1, z1, key='glass', th=0.006, bevel=0.0):
    """Glass pane with real thickness, centred on y = 0; bevel > 0 = bevelled margin."""
    if not bevel:
        gb.box((x0, -th / 2, z0), (x1, th / 2, z1), key)
        return
    for s in (1, -1):
        _field(gb, x0, z0, x1, z1, s * 0.001, s * th / 2, bevel, s, key)


def _glazing_bead(mb, x0, z0, x1, z1, t, mat, gth=0.006, bw=0.012):
    rec = t / 2 - gth / 2
    prof = [(bw, -rec), (bw * 0.75, -rec * 0.4), (bw * 0.33, 0.0), (0.0, 0.0)]
    for s in (1, -1):
        _rect_bead(mb, x0, z0, x1, z1, s * t / 2, s, prof, mat)


def _frame_boxes(mb, w, h, t, mat, stile, top, bottom, rails=(), muntins=(), stile2=None, bev=0.0015):
    """Stiles (grain vertical), rails (grain horizontal) and muntins of a framed leaf.
    rails: [(z0, z1)...]; muntins: [(x0, x1, z0, z1)...]."""
    s2 = stile if stile2 is None else stile2
    mb.box((0, -t / 2, 0), (stile, t / 2, h), mat, bev, grain=2)
    mb.box((w - s2, -t / 2, 0), (w, t / 2, h), mat, bev, grain=2)
    for z0, z1 in [(0, bottom), (h - top, h)] + list(rails):
        if z1 > z0:
            mb.box((stile, -t / 2, z0), (w - s2, t / 2, z1), mat, bev, grain=0)
    for x0, x1, z0, z1 in muntins:
        mb.box((x0, -t / 2, z0), (x1, t / 2, z1), mat, bev, grain=2)


# --------------------------------------------------------------------------- leaves
def leaf_oak_4panel(mb, gb, w, h, t=0.035, glazed=False, mat='oak'):
    """Victorian 4-panel oak leaf: two tall panels over two short ones, raised-and-fielded with a
    bolection bead. glazed=True: the two upper openings hold obscure glass (kitchen door)."""
    st = 0.100 * (1.10 if w > 0.80 else (0.88 if w < 0.70 else 1.0))
    bot, lock0, lock1, top = 0.215, 0.715, 0.905, 0.100
    xm0, xm1 = (w - st) / 2, (w + st) / 2
    _frame_boxes(mb, w, h, t, mat, st, top, bot, rails=[(lock0, lock1)],
                 muntins=[(xm0, xm1, bot, lock0), (xm0, xm1, lock1, h - top)])
    for x0, x1 in ((st, xm0), (xm1, w - st)):
        _panel(mb, x0, bot, x1, lock0, t, mat, 'bead_ovolo' if glazed else 'bead_bolection')
        if glazed:
            _glass(gb, x0 - 0.008, lock1 - 0.008, x1 + 0.008, h - top + 0.008, 'glass_frosted')
            _glazing_bead(mb, x0, lock1, x1, h - top, t, mat)
        else:
            _panel(mb, x0, lock1, x1, h - top, t, mat)
    return dict(handle_x=w - 0.060, handle_z=1.00)


def leaf_mahogany_glazed(mb, gb, w, h, t=0.040, mat='mahogany'):
    """Inner vestibule door leaf: 2 x 5 bevelled panes, top rail with a shallow segmental arch."""
    hs, ms, bot, top, rise, vb, hb = 0.120, 0.098, 0.215, 0.125, 0.020, 0.032, 0.036
    x0, x1, z0, z1 = hs, w - ms, bot, h - top
    xm = (x0 + x1) / 2
    mb.box((0, -t / 2, 0), (hs, t / 2, h), mat, 0.002, grain=2)
    mb.box((w - ms, -t / 2, 0), (w, t / 2, h), mat, 0.002, grain=2)
    mb.box((x0, -t / 2, 0), (x1, t / 2, bot), mat, 0.002, grain=0)
    arc = [(x0 + (x1 - x0) * i / 10, z1 + rise * (1 - (2 * i / 10 - 1) ** 2)) for i in range(11)]
    mb.prism([(x, -t / 2, z) for x, z in arc + [(x1, h), (x0, h)]], (0, t, 0), mat, grain=0)
    tb = t - 0.008                                                    # glazing bars, slightly set back
    mb.box((xm - vb / 2, -tb / 2, z0), (xm + vb / 2, tb / 2, z1 + rise * 0.96), mat, 0.004, grain=2)
    ph = (z1 - z0 - 4 * hb) / 5
    for i in range(4):
        zb = z0 + (i + 1) * ph + i * hb
        for xa, xb in ((x0, xm - vb / 2), (xm + vb / 2, x1)):
            mb.box((xa, -tb / 2, zb), (xb, tb / 2, zb + hb), mat, 0.004, grain=0)
    for i in range(5):
        za = z0 + i * (ph + hb)
        zb = za + ph + (rise if i == 4 else 0)
        for xa, xb in ((x0, xm - vb / 2), (xm + vb / 2, x1)):
            _glass(gb, xa - 0.004, za - 0.004, xb + 0.004, zb + 0.004, 'glass', 0.006, bevel=0.014)
    return dict(handle_x=w - 0.055, handle_z=0.98)


def _astragal(mb, w, h, t, mat, lap=0.014):
    """Rebated meeting stile of a pair: cover strips on both faces of this leaf's latch edge that
    lap the other leaf by `lap`, closing the gap between the leaves."""
    for s in (1, -1):
        mb.box((w - 0.026, s * t / 2, 0.0), (w + lap, s * (t / 2 + 0.007), h), mat, 0.002, grain=2)


def leaf_upvc_street(mb, gb, w, h, t=0.060, letterbox=False, mat='upvc_white'):
    """Street door leaf: Georgian-bar obscure light (3 x 4) over a solid panel with planted mould."""
    st, zp0, zp1, zg0, zg1 = 0.075, 0.13, 0.81, 0.92, h - 0.08
    _frame_boxes(mb, w, h, t, mat, st, h - zg1, zp0, rails=[(zp1, zg0)], bev=0.003)
    x0, x1 = st, w - st
    _panel(mb, x0, zp0, x1, zp1, t, mat, 'bead_ovolo', recess=0.010, raised=0.0)
    for s in (1, -1):                                                  # planted mould 35 mm in
        _rect_bead(mb, x0 + 0.045, zp0 + 0.045, x1 - 0.045, zp1 - 0.045, s * (t / 2 - 0.010), s,
                   [(0.014, 0.0), (0.010, 0.006), (0.004, 0.006), (0.0, 0.0)], mat)
    _glass(gb, x0 - 0.008, zg0 - 0.008, x1 + 0.008, zg1 + 0.008, 'glass_obscure', 0.020)
    _glazing_bead(mb, x0, zg0, x1, zg1, t, mat, 0.020, 0.014)
    cw, rh = (x1 - x0) / 3, (zg1 - zg0) / 4
    for s in (1, -1):                                                  # Georgian bars on the glass
        ya, yb = s * 0.0102, s * 0.017
        for i in (1, 2):
            mb.box((x0 + i * cw - 0.009, ya, zg0), (x0 + i * cw + 0.009, yb, zg1), mat)
        for j in (1, 2, 3):
            mb.box((x0, ya, zg0 + j * rh - 0.009), (x1, yb, zg0 + j * rh + 0.009), mat)
    if letterbox:
        zc = (zp1 + zg0) / 2
        for s in (1, -1):
            mb.box((w / 2 - 0.15, s * t / 2, zc - 0.0375), (w / 2 + 0.15, s * (t / 2 + 0.006), zc + 0.0375), 'brass', 0.002)
            mb.box((w / 2 - 0.125, s * (t / 2 + 0.006), zc - 0.018), (w / 2 + 0.125, s * (t / 2 + 0.009), zc + 0.018), 'brass', 0.002)
    return dict(handle_x=w - 0.060, handle_z=0.99)


def leaf_upvc_french(mb, gb, w, h, t=0.060, catflap=False, mat='upvc_white', rail=(0.905, 0.995)):
    """French-door leaf: clear light above and below a mid rail (z range `rail`); optional round cat flap."""
    st = 0.070
    _frame_boxes(mb, w, h, t, mat, st, st, st, rails=[rail], bev=0.003)
    for za, zb in ((st, rail[0]), (rail[1], h - st)):
        _glass(gb, st - 0.008, za - 0.008, w - st + 0.008, zb + 0.008, 'glass', 0.020)
        _glazing_bead(mb, st, za, w - st, zb, t, mat, 0.020, 0.014)
    if catflap:
        M0 = mb.M.copy()
        for s in (1, -1):
            mb.at(M0 @ T((w / 2, s * 0.010, 0.33)) @ RX(-s * math.pi / 2))
            mb.lathe([(0.130, 0), (0.130, 0.014), (0.118, 0.020), (0.100, 0.020), (0.100, 0)], mat, 28)
            mb.lathe([(0.100, 0.002), (0.100, 0.006), (0, 0.006)], 'flap_smoked', 28)
        mb.at(M0)
    return dict(handle_x=w - 0.045, handle_z=1.02)


def leaf_upvc_back(mb, gb, w, h, t=0.060, mat='upvc_white'):
    """Half-glazed back door: obscure light over a flat beaded panel with a square cat flap."""
    st = (w - 0.56) / 2
    zp0, zp1, zg0, zg1 = 0.19, 0.91, 1.01, h - 0.09
    _frame_boxes(mb, w, h, t, mat, st, h - zg1, zp0, rails=[(zp1, zg0)], bev=0.003)
    _panel(mb, st, zp0, w - st, zp1, t, mat, 'bead_ovolo', recess=0.012, raised=0.0)
    _glass(gb, st - 0.008, zg0 - 0.008, w - st + 0.008, zg1 + 0.008, 'glass_obscure', 0.020)
    _glazing_bead(mb, st, zg0, w - st, zg1, t, mat, 0.020, 0.014)
    mb.box((st - 0.03, t / 2, zg1 + 0.012), (w - st + 0.03, t / 2 + 0.022, zg1 + 0.037), mat, 0.004)   # drip bar
    cx = w / 2 - 0.08                                                 # cat flap (0.22 x 0.24)
    for s in (1, -1):
        y0, y1 = s * (t / 2 - 0.012), s * (t / 2 + 0.004)
        mb.box((cx - 0.11, y0, zp0), (cx + 0.11, y1, zp0 + 0.24), mat, 0.004)
        arc = [(cx + 0.082 * math.cos(math.pi * i / 10), zp0 + 0.125 + 0.070 * math.sin(math.pi * i / 10)) for i in range(11)]
        mb.prism([(x, y1, z) for x, z in [(cx - 0.082, zp0 + 0.035), (cx + 0.082, zp0 + 0.035)] + arc],
                 (0, s * 0.003, 0), 'flap_smoked')                    # smoked-grey arched flap (f_0330)
        mb.box((cx + 0.07, y1, zp0 + 0.008), (cx + 0.095, y1 + s * 0.006, zp0 + 0.026), 'red_plastic', 0.002)
    return dict(handle_x=w - 0.060, handle_z=1.00)


# --------------------------------------------------------------------------- frames / surrounds
def _lining(mb, hw, top, y0, y1, mat, z0=0.0, sill=False):
    """Thin lining on the jamb and head faces of the hole between depths y0..y1 (side frame)."""
    if y1 - y0 < 1e-4:
        return
    for sx in (1, -1):
        mb.box((sx * hw, y0, z0), (sx * (hw - SKIN), y1, top), mat)
    mb.box((-hw + SKIN, y0, top - SKIN), (hw - SKIN, y1, top), mat)
    if sill:
        mb.box((-hw + SKIN, y0, z0), (hw - SKIN, y1, z0 + SKIN), mat)


def _stop(mb, hw, top, y0, y1, mat, z0=0.0, th=0.012):
    """Planted door stop on the lining."""
    a = hw - SKIN
    for sx in (1, -1):
        mb.box((sx * a, y0, z0), (sx * (a - th), y1, top - SKIN), mat, 0.001)
    mb.box((-a + th, y0, top - SKIN - th), (a - th, y1, top - SKIN), mat, 0.001)


def architrave(mb, key, hw, top, mat='joinery_white', z0=0.0, closed=False, y=0.0, hw2=None):
    """Mitred architrave round an opening (side frame): legs at +hw / -(hw2 or hw), head at `top`;
    closed=True also runs along the bottom (window lights)."""
    a, b = hw, -(hw if hw2 is None else hw2)
    mb.sweep(PROFILES[key] if isinstance(key, str) else key, [(a, y, z0), (a, y, top), (b, y, top), (b, y, z0)],
             mat, closed=closed, up=(0, 1, 0))


def returned(mb, prof, u0, u1, yb, z, mat, back=0.0):
    """Horizontal moulding on the backing plane y = yb from u0 to u1 (u0 < u1), both ends mitred
    and returned to the wall (y = back). prof: (d = projection, h = height)."""
    mb.sweep(prof, [(u0, back - 0.001, z), (u0, yb, z), (u1, yb, z), (u1, back - 0.001, z)], mat)


def doorcase_pediment(mb, hw, top, mat='joinery_white'):
    """Broken-pediment doorcase (hall side of the living-room door), living.md 2.2: architrave, bed
    mould, frieze plate, two acanthus consoles, shelf, break-front frieze with shell-and-scroll
    ornament, base cornice, two raking cornices with scrolled tympanum boards, central pedestal."""
    architrave(mb, 'arch_living', hw, top, mat)
    zo = top + 0.100 - 2.10                         # the spec quotes heights with the architrave top at 2.10
    Z = lambda z: z + zo
    M0 = mb.M.copy()
    mb.box((-0.51, 0, Z(2.10)), (0.51, 0.012, Z(2.225)), mat)
    mb.sweep(PROFILES['ped_bed'], [(-0.51, 0.012, Z(2.10)), (0.51, 0.012, Z(2.10))], mat)
    for s in (1, -1):
        mb.at(M0 @ T((s * 0.56, 0, Z(2.065))))
        mo.scroll_corbel(mb, 0.10, 0.16, 0.075, 0.045, mat)
    mb.at(M0)
    returned(mb, PROFILES['ped_shelf'], -0.54, 0.54, 0.0, Z(2.225), mat, back=-0.002)
    mb.box((-0.27, 0, Z(2.285)), (0.27, 0.020, Z(2.395)), mat)
    for s in (1, -1):
        mb.box((s * 0.27, 0, Z(2.285)), (s * 0.595, 0.045, Z(2.395)), mat)
    mb.at(M0 @ T((0, 0.020, Z(2.340))) @ RX(-math.pi / 2) @ RZ(math.pi))
    mo.shell_scroll_ornament(mb, 0.35, 0.075, 0.010, mat)
    mb.at(M0)
    mb.sweep(PROFILES['ped_cornice'],
             [(-0.595, -0.001, Z(2.395)), (-0.595, 0.045, Z(2.395)), (-0.27, 0.045, Z(2.395)), (-0.27, 0.020, Z(2.395)),
              (0.27, 0.020, Z(2.395)), (0.27, 0.045, Z(2.395)), (0.595, 0.045, Z(2.395)), (0.595, -0.001, Z(2.395))], mat)
    zb, th, dp = Z(2.465), math.radians(27.0), 0.09
    c, s_ = math.cos(th), math.sin(th)
    z_ti = zb + (0.60 - 0.185) * math.tan(th)       # top edge at the plumb inner cut
    z_bi = z_ti - dp / c
    rake = [(q * dp / 0.07, p) for p, q in reversed(PROFILES['ped_cornice'])]
    for sx in (1, -1):
        p1, p2 = Vector((sx * (0.60 - dp / s_), 0.045, zb)), Vector((sx * 0.185, 0.045, z_bi))
        cut_h, cut_v = Vector((sx / s_, 0, 0)), Vector((0, 0, 1 / c))
        if sx > 0:
            mb.sweep(rake, [p1, p2], mat, up=(0, 1, 0), ends=(cut_h, cut_v))
        else:
            mb.sweep(rake, [p2, p1], mat, up=(0, 1, 0), ends=(cut_v, cut_h))
        arc = mo._q((0.285, zb), (0.185, z_bi), 'vh', 6)
        poly = [(0.60, zb), (0.285, zb)] + arc + [(0.185, z_ti)]
        mb.prism([(sx * x, 0, z) for x, z in poly], (0, 0.045, 0), mat)
    mb.prism([(-0.0525, 0, zb), (0.0525, 0, zb), (0.07, 0, zb + 0.10), (-0.07, 0, zb + 0.10)], (0, 0.075, 0), mat)
    returned(mb, PROFILES['ped_cap'], -0.07, 0.07, 0.075, zb + 0.10, mat, back=-0.002)


def dark_surround(mb, hw, top, cap_top, aw=0.11, key='arch_dark', cap_h=0.09, cap_over=0.035, mat='dark_stain'):
    """Dark stained reeded architrave legs to the floor + plain frieze board + returned cornice cap
    (dining side of the hall door; the E-window aedicules)."""
    leg_top = cap_top - cap_h - 0.08
    prof = PROFILES[key]
    mb.sweep(prof, [(hw, 0, 0), (hw, 0, leg_top)], mat, up=(0, 1, 0))
    mb.sweep(prof, [(-hw, 0, leg_top), (-hw, 0, 0)], mat, up=(0, 1, 0))
    if leg_top > top + 0.002:
        mb.box((-hw, 0, top), (hw, 0.012, leg_top), mat)
    ow = hw + aw
    mb.box((-ow, 0, leg_top), (ow, 0.020, leg_top + 0.08), mat, 0.001, grain=0)
    cap = mo._scale(PROFILES['dark_cap'], 1.0, cap_h / 0.09)
    cx = ow + cap_over - 0.060
    returned(mb, cap, -cx, cx, 0.020, leg_top + 0.08, mat, back=-0.002)


# doorcases of the upper floors. Heights are ABOVE THE DOOR HEAD (`top`), widths in metres; shelf = (length or None for
# architrave width + 90 mm, height, projection); consoles = (width, height, projection), hung under the shelf just
# outside the architrave. Sources: landing1.md 2, green_bedroom.md 3.3, green_bathroom.md 3.2, blue_bedroom.md 3.
DOORCASES = {
    'cornice_hood_on_consoles': dict(arch='arch_upper', frieze=0.09, shelf=(1.25, 0.10, 0.11), consoles=(0.09, 0.17, 0.075)),
    'pediment_scrolled': dict(arch='arch_100', frieze=0.23, shelf=(1.30, 0.06, 0.10), consoles=(0.09, 0.36, 0.09), apex=0.62,
                              rake=0.06, frieze_ornament=True, tympanum_ornament=0.42, volutes=True),
    # bathroom face of d_green_slide: 1.30 overall with its cornice (green_bathroom.md 3.2; v4 f_0164 ~1.2), was 1.50
    'pediment_tall_plain': dict(arch='arch_100', frieze=0.17, shelf=(1.10, 0.08, 0.10), consoles=(0.10, 0.45, 0.10), apex=0.75,
                                rake=0.07, band=True),
    'pediment_triangular': dict(arch='arch_70', frieze=0.03, shelf=(None, 0.04, 0.045), apex=0.37, rake=0.045,
                                tympanum_ornament=0.26),
}


def doorcase(mb, hw, top, arch='arch_70', aw=None, frieze=0.03, shelf=(None, 0.04, 0.045), consoles=None, apex=None,
             rake=0.05, frieze_ornament=False, tympanum_ornament=0.0, volutes=False, band=False, mat='joinery_white'):
    """Parametric doorcase on one face (side frame current in mb): architrave `aw` wide, frieze board, optional
    egg band / applied shell-and-scroll relief, acanthus consoles, returned cornice shelf and - when `apex` is given
    - a triangular pediment (raking cornices mitred plumb at the apex, tympanum board, optional relief and volutes)."""
    w0 = mo.profile_size(arch)[0]
    aw = aw or w0
    architrave(mb, mo._scale(PROFILES[arch], aw / w0, 1.0), hw, top, mat)
    M0 = mb.M.copy()
    ow, z1 = hw + aw, top + aw                      # outer half width, top of the architrave
    zs = z1 + frieze                                # underside of the shelf
    sw, sh, sp = shelf
    sw = sw or 2 * ow + 0.09
    mb.box((-ow, 0, z1 - 0.002), (ow, 0.012, zs), mat)
    if frieze_ornament:
        mb.at(M0 @ T((0, 0.012, (z1 + zs) / 2)) @ RX(-math.pi / 2) @ RZ(math.pi))
        mo.shell_scroll_ornament(mb, min(1.7 * ow, 0.62), 0.55 * frieze, 0.010, mat)
        mb.at(M0)
    if band:                                        # ponytail: the egg-and-dart band is a row of eggs
        n = int(2 * ow / 0.034)
        for i in range(n):
            mb.at(M0 @ T((-ow + (i + 0.5) * 2 * ow / n, 0.012, zs - 0.024)) @ RX(-math.pi / 2))
            mb.dome(0.011, 0.016, 0.008, mat, 6, 2)
        mb.at(M0)
    if consoles:
        cw, ch, cp = consoles
        for s in (1, -1):
            mb.at(M0 @ T((s * (ow + cw / 2 + 0.004), 0, zs - ch)))
            mo.scroll_corbel(mb, cw, ch, cp, 0.6 * cp, mat)
        mb.at(M0)
    returned(mb, mo._scale(PROFILES['ped_shelf'], sp / 0.075, sh / 0.060), -sw / 2, sw / 2, 0.0, zs, mat, back=-0.002)
    if apex is None:
        return
    zb, za, half, yt = zs + sh, top + apex, sw / 2 - 0.008, 0.012
    th = math.atan2(za - zb, half)
    c, s_ = math.cos(th), math.sin(th)
    rk = [(q * rake / 0.07, p * (sp - 0.006 - yt) / 0.07) for p, q in reversed(PROFILES['ped_cornice'])]
    xi, zi = half - rake / s_, za - rake / c        # inner triangle (lower edges of the raking cornices)
    for sx in (1, -1):
        p1, p2 = Vector((sx * xi, yt, zb)), Vector((0, yt, zi))
        cut_h, cut_v = Vector((sx / s_, 0, 0)), Vector((0, 0, 1 / c))
        if sx > 0:
            mb.sweep(rk, [p1, p2], mat, up=(0, 1, 0), ends=(cut_h, cut_v))
        else:
            mb.sweep(rk, [p2, p1], mat, up=(0, 1, 0), ends=(cut_v, cut_h))
    mb.prism([(-half, 0, zb), (half, 0, zb), (0, 0, za)], (0, yt, 0), mat)                     # tympanum board
    if tympanum_ornament:
        hgt = min(0.55 * (zi - zb), tympanum_ornament * 0.3)
        mb.at(M0 @ T((0, yt, zb + 0.5 * hgt + 0.012)) @ RX(-math.pi / 2) @ RZ(math.pi))
        mo.shell_scroll_ornament(mb, tympanum_ornament, hgt, 0.007, mat)
        mb.at(M0)
    if volutes:                                     # small scroll where each raking moulding lands on the shelf
        for sx in (1, -1):
            mb.at(M0 @ T((sx * (half - 0.030), sp - 0.012, zb + 0.030)) @ RX(-math.pi / 2))
            mb.tube([(0.022 * math.cos(2 * math.pi * j / 12), 0.022 * math.sin(2 * math.pi * j / 12), 0) for j in range(12)],
                    0.008, mat, 6, closed=True)
            mb.dome(0.010, 0.010, 0.008, mat, 8, 2)
        mb.at(M0)


def _surround(mb, key, oid, room, hw, top, drop=0.0):
    """Surround of an ordinary door on one side (side frame current in mb). drop = how far that room's floor lies
    below the threshold (d_loft, platform side): plain architrave legs run on down to it."""
    if key == 'plain_architrave':
        k = mo.architrave_key(oid, room)
        architrave(mb, k, hw, top, z0=-drop)
        if room == 'kitchen':                       # small plinth blocks
            w = mo.profile_size(k)[0]
            for sx in (1, -1):
                mb.box((sx * (hw - 0.002), 0, 0), (sx * (hw + w + 0.004), 0.027, 0.165), 'joinery_white', 0.002)
    elif key == 'pediment':
        doorcase_pediment(mb, hw, top)
    elif key == 'dark_architrave':
        dark_surround(mb, hw, top, 2.20)
    elif key in DOORCASES:
        cfg = dict(DOORCASES[key])
        if key == 'pediment_triangular' and room.startswith('landing'):     # landing face of d_blue (landing1.md 2)
            cfg.update(aw=mo.doorcase_arch(key, room), shelf=(1.03, 0.04, 0.045), apex=0.28)
        doorcase(mb, hw, top, **cfg)


def _finish(ctx, mb, name, room, matrix=None, **props):
    if not mb.bm.faces:
        mb.bm.free()
        return None
    ob = ctx.add(mb.finish(name, matrix), room, 'joinery')
    for k, v in props.items():
        ob[k] = v
    return ob


def hang_leaf(ctx, name, room, MA, px, t, hinge_x, angle, build, yA=-0.002, zb=FLOOR_GAP, upvc=False, h=1.97,
              hinges=True, blocks=True, label=None, swing=None, **props):
    """Create a hinged leaf (+ its glass) as objects whose origin is the hinge axis.
    MA = side frame of the side the leaf swings to; px = x of the hinge edge there; hinge_x = +1 hinge at the +X
    jamb, -1 at the -X jamb; build(mb, gb) draws the leaf in the leaf frame; yA = y (in MA) of the leaf face on the
    swing side when shut; zb = bottom of the leaf above MA's z = 0. Tagged (when props has door=<opening id>) as one
    interaction group: modelled shut -> state 1 opens it `swing` degrees (OPEN_DEG, default 90); modelled open ->
    state 1 shuts it. blocks=False for leaves that close no doorway (hatches)."""
    py = yA + 0.006
    L = T((0, -t / 2 - 0.006, zb)) @ (Matrix.Scale(-1, 4, (1, 0, 0)) if hinge_x > 0 else Matrix.Identity(4))
    mb, gb = MB(), MB()
    mb.at(L)
    gb.at(L)
    build(mb, gb)
    mb.at()
    if hinges:
        butt_hinges(mb, h, upvc)
    Mo = MA @ T((px, py, 0)) @ RZ(-hinge_x * math.radians(angle))
    ob = _finish(ctx, mb, name, room, Mo, open_deg=float(angle), hinge_side=int(hinge_x), **props)
    gl = _finish(ctx, gb, name + '.glass', room, Mo)
    oid = props.get('door')
    if oid:                                         # one group per leaf (leaf + its glass), g = the leaf's name
        shut = abs(angle) < 0.5                     # modelled shut: state 1 swings it open; modelled open: state 1 shuts it
        deg = -hinge_x * (swing or OPEN_DEG.get(oid, 90.0)) if shut else hinge_x * angle
        kw = dict(blocks=oid) if blocks else {}
        if not shut:
            kw['on'] = True
        IX.tag_many([o for o in (ob, gl) if o], 'hinge', g=name, label=label or LABEL.get(oid, 'Door'),
                    p=Mo.translation, a=(0, 0, 1), deg=round(deg, 2), **kw)
    return ob


# --------------------------------------------------------------------------- rooms of an opening
def _room_names(fr):
    """(room on the +normal side, room on the -normal side) by their `connects` names. The wall's own rooms can
    differ: d_basement (wall hallway | stairs, connects hallway | basement_stair), d_balcony (wall outside |
    blue_bedroom, connects blue_bedroom | balcony)."""
    con, wall = list(fr['connects']), [fr['room_pos'], fr['room_neg']]
    out = [w if w in con else None for w in wall]
    for i in (0, 1):
        if out[i] is None:
            rest = [c for c in con if c != out[1 - i]]
            out[i] = rest[0] if rest else wall[i]
    return out


def _is_out(fr, room):
    return room == 'outside' or (room is not None and room == fr.get('outside_room'))


def _inside(fr):
    """(inside room, +1 / -1 side it lies on) of an opening to the outside; for an internal opening the +normal room."""
    pos, neg = _room_names(fr)
    return (neg, -1) if _is_out(fr, pos) else (pos, 1)


def _own(ctx, fr, room):
    """Room the joinery on the `room` side is named after and tagged with: the inside room where that side is the
    outside (also the balcony side of d_balcony); a building room -> its pseudo-room (shed)."""
    if _is_out(fr, room):
        room = _inside(fr)[0]
    return ctx.tag_room(room) if hasattr(ctx, 'tag_room') else room


def _ext_depth(fr, Tw):
    """(ya, yb): depth of an exterior frame in the side frame of the INSIDE room (y = 0 room face, -Tw outer face).
    The frame is ctx.FRAME_D deep and sits fr['ext_reveal'] behind the outer face (MULTILEVEL section 8); in a wall
    thinner than that (the 40 mm shed partition) it takes what is left."""
    er = fr.get('ext_reveal')
    if er is None:                                  # internal wall: centred
        return -Tw / 2 - FRAME_D / 2, -Tw / 2 + FRAME_D / 2
    ya = -Tw + er
    return ya, ya + min(FRAME_D, max(0.02, Tw - er))


# --------------------------------------------------------------------------- door assemblies
def _hinge_x(fr):
    """+1 / -1: hinge jamb in the swing-side frame ('left' seen from the swing room = +X)."""
    return 1 if fr.get('hinge') == 'left' else -1


def _door_internal(ctx, oid, fr):
    """Oak internal door (oak_4panel / oak_glazed): painted linings + stop, surround per side, leaf."""
    sg = fr['swing_sign'] or 1
    pos, neg = _room_names(fr)
    A, B = (pos, neg) if sg > 0 else (neg, pos)
    MA, MBk, Tw = side_frame(fr, sg), side_frame(fr, -sg), wall_t(fr)
    hw, top = fr['width'] / 2, fr['head']
    sur = {r: mo.surround_of(fr, r) for r in (A, B)}
    lin = lambda r: 'dark_stain' if str(sur[r] or '').startswith('dark') else 'joinery_white'
    t = 0.035
    ys = -0.002 - t                                                   # back face of the shut leaf
    f = MB().at(MA)
    _lining(f, hw, top, ys, 0.0, lin(A))
    _lining(f, hw, top, -Tw, ys, lin(B))
    _stop(f, hw, top, ys - 0.030, ys, lin(B))
    _finish(ctx, f, f'{A}.{oid}.lining', A)
    for room, M in ((A, MA), (B, MBk)):
        if sur[room]:
            s = MB().at(M)
            drop = max(0.0, fr['z0'] - ctx.floor_z(room)) if room in ctx.rooms else 0.0
            _surround(s, sur[room], oid, room, hw, top, drop if 0.01 < drop < 0.5 else 0.0)
            _finish(ctx, s, f'{room}.{oid}.surround', room, surround=sur[room])
    lw, lh = fr['width'] - 2 * (SKIN + GAP), top - SKIN - GAP - FLOOR_GAP
    hx = _hinge_x(fr)

    def build(mb, gb):
        info = leaf_oak_4panel(mb, gb, lw, lh, t, glazed=fr['style'] == 'oak_glazed')
        lever_handle(mb, info['handle_x'], info['handle_z'] - FLOOR_GAP, t, (0.042, 0.150), 0.11)

    hang_leaf(ctx, f'{A}.{oid}.leaf', A, MA, hx * (hw - SKIN - GAP), t, hx, fr.get('openAngle') or 0, build,
              h=lh, door=oid)


def _door_mahogany(ctx, oid, fr):
    """Mahogany glazed screen: frame wall to wall with clear fanlight, pair of 2x5-pane leaves."""
    sg = fr['swing_sign'] or 1
    A = fr['room_pos'] if sg > 0 else fr['room_neg']
    MA, Tw = side_frame(fr, sg), wall_t(fr)
    hw, head, top, m, p, t = fr['width'] / 2, fr['head'], fr['top'], 'mahogany', 0.004, 0.040
    ji = hw - 0.018                                                   # inner face of the jambs
    f, g = MB().at(MA), MB().at(MA)
    for sx in (1, -1):
        f.box((sx * ji, -Tw - p, 0), (sx * (hw + 0.041), p, top + 0.04), m, 0.002, grain=2)
        f.box((sx * ji, -Tw - p, 0), (sx * (ji - 0.012), -0.002 - t - 0.002, head + 0.004), m, 0.001, grain=2)   # stop
    f.box((-ji, -Tw - p, top - 0.035), (ji, p, top + 0.04), m, 0.002, grain=0)                # head
    z_t0, z_t1 = head + 0.004, head + 0.064
    f.box((-ji, -Tw - p, z_t0), (ji, p, z_t1), m, 0.002, grain=0)                             # transom bar
    f.box((-ji, -Tw - p, z_t0 - 0.012), (ji, -0.002 - t - 0.002, z_t0), m, 0.001, grain=0)    # head stop
    f.at(MA @ T((0, -Tw / 2, 0)))
    g.at(MA @ T((0, -Tw / 2, 0)))
    _glass(g, -ji - 0.006, z_t1 - 0.006, ji + 0.006, top - 0.035 + 0.006, 'glass')
    _glazing_bead(f, -ji, z_t1, ji, top - 0.035, Tw + 2 * p, m, 0.006, 0.014)
    _finish(ctx, f, f'{A}.{oid}.frame', A)
    _finish(ctx, g, f'{A}.{oid}.frame.glass', A)
    lw, lh = ji - GAP - 0.0015, head - FLOOR_GAP - 0.001
    for i, hx in enumerate((1, -1)):
        px = hx * (ji - GAP)
        hp = MA @ Vector((px, 0, 0))
        ang = LEAF_ANGLE.get(oid, lambda q: 0.0)(hp)

        def build(mb, gb, east=hp.x > fr['center'].x):
            info = leaf_mahogany_glazed(mb, gb, lw, lh, t)
            lever_handle(mb, info['handle_x'], info['handle_z'] - FLOOR_GAP, t, (0.050, 0.270), 0.115, key=east)
            M0 = mb.M.copy()
            mb.at(M0 @ T((lw - 0.035, t / 2, 0.12)) @ RX(-math.pi / 2))
            mb.dome(0.010, 0.010, 0.012, 'brass', 8, 2)                                       # flush-bolt knob
            mb.at(M0)

        hang_leaf(ctx, f'{A}.{oid}.leaf.{i}', A, MA, px, t, hx, ang, build, h=lh, door=oid)


def _upvc_doorset(ctx, oid, fr, leaf, jamb=0.06, transom=0.07, sill=0.04, fan_glass='glass', fan_lights=1,
                  flange=0.0, vents=False):
    """White uPVC door set in an external wall: frame FRAME_D deep at ext_reveal behind the outer face (jambs, head,
    threshold, transom bar and glazed fanlight(s) when the hole is taller than the leaves), one or two leaves hung
    in it on the side fr['swing_sign'] names (outside for d_street / d_french / d_balcony / shed_d1, the room for
    d_back). leaf(mb, gb, lw, lh, t, zb, west) draws one leaf in the leaf frame. -> (inside room, its side frame)."""
    R, sgR = _inside(fr)
    own = _own(ctx, fr, R)
    MR, MO, Tw = side_frame(fr, sgR), side_frame(fr, -sgR), wall_t(fr)
    hw, head, top, t, m = fr['width'] / 2, fr['head'], fr['top'], 0.060, 'upvc_white'
    ya, yb = _ext_depth(fr, Tw)
    f, g = MB().at(MR), MB().at(MR)
    for sx in (1, -1):
        f.box((sx * hw, ya, 0), (sx * (hw - jamb), yb, top), m, 0.003)
    f.box((-hw + jamb, ya, top - jamb), (hw - jamb, yb, top), m, 0.003)
    f.box((-hw + jamb, ya, 0), (hw - jamb, yb, sill), m, 0.003)
    if top - head > 0.12:                                             # transom bar + fanlight(s)
        f.box((-hw + jamb, ya, head), (hw - jamb, yb, head + transom), m, 0.003)
        wc = (2 * (hw - jamb) - (fan_lights - 1) * 0.06) / fan_lights
        for i in range(fan_lights):
            a = -hw + jamb + i * (wc + 0.06)
            if i:
                f.box((a - 0.06, ya, head + transom), (a, yb, top - jamb), m, 0.003)
            _glaze(f, g, a, a + wc, head + transom, top - jamb, ya, yb, fan_glass)
    if flange and yb > -0.008:                                        # frame flush with the room face: flange on the plaster
        for sx in (1, -1):
            f.box((sx * (hw - 0.002), 0, 0), (sx * (hw + flange), 0.012, top + flange), m, 0.003)
        f.box((-hw, 0, top - 0.002), (hw, 0.012, top + flange), m, 0.003)
    if vents:                                                         # trickle-vent hoods on the transom bar
        for sx in (1, -1):
            f.box((sx * 0.12, yb, head + 0.02), (sx * 0.23, yb + 0.015, head + 0.045), m, 0.003)
    _finish(ctx, f, f'{own}.{oid}.frame', own)
    _finish(ctx, g, f'{own}.{oid}.frame.glass', own)
    out = (fr['swing_sign'] or -sgR) == -sgR                          # the leaves swing to the outside
    MA, yA = (MO, -(Tw + ya)) if out else (MR, yb)                    # leaf face flush with the frame on the swing side
    zb = sill + 0.003
    # the leaves stop under the transom bar, or under the frame head where there is none (shed_d1: they ran up behind
    # the head rail, flush with its face - a coplanar overlap that rendered black)
    lh = (head if top - head > 0.12 else top - jamb) - 0.003 - zb
    pair = fr['type'] != 'door'
    lw = (hw - jamb - GAP - 0.0015) if pair else 2 * (hw - jamb - GAP)
    for i, hx in enumerate((1, -1) if pair else (_hinge_x(fr),)):
        px = hx * (hw - jamb - GAP)
        west = (MA @ Vector((px, 0, 0))).x < fr['center'].x

        def build(mb, gb, west=west):
            leaf(mb, gb, lw, lh, t, zb, west)

        hang_leaf(ctx, f'{own}.{oid}.leaf' + (f'.{i}' if pair else ''), own, MA, px, t, hx,
                  0.0 if pair else (fr.get('openAngle') or 0), build, yA=yA, zb=zb, upvc=True, h=lh, door=oid)
    return R, MR


def _door_street(ctx, oid, fr):
    """White uPVC street doors: pair of Georgian-bar leaves, plain frosted transom (no lettering), letterbox on the
    west leaf, trickle-vent hoods, flag hinges. Swing outward (phase 2) or inward (phase 1) per the spec."""
    def leaf(mb, gb, lw, lh, t, zb, west):
        info = leaf_upvc_street(mb, gb, lw, lh, t, letterbox=west)
        if west:
            _astragal(mb, lw, lh, t, 'upvc_white')
        lever_handle(mb, info['handle_x'], info['handle_z'], t, (0.030, 0.240), 0.11, cyl=west)

    _upvc_doorset(ctx, oid, fr, leaf, jamb=0.045, transom=0.09, sill=0.03, fan_glass='glass_frosted', flange=0.030, vents=True)


def _door_french(ctx, oid, fr):
    """White uPVC French doors (dining -> deck with a round cat flap in the west leaf; blue bedroom -> balcony with
    two fanlights; shed workshop without a fanlight). Room-side surround: the dining dark recess / screen, or the
    dark board lining of the balcony door reveal."""
    shed = fr.get('style') == 'shed_french'

    def leaf(mb, gb, lw, lh, t, zb, west):
        info = leaf_upvc_french(mb, gb, lw, lh, t, catflap=west and oid == 'd_french',
                                rail=(0.75 - zb, 0.85 - zb) if shed else (0.905, 0.995))
        if west:
            _astragal(mb, lw, lh, t, 'upvc_white')
        lever_handle(mb, info['handle_x'], info['handle_z'] - zb, t, (0.035, 0.220), 0.11)

    R, MR = _upvc_doorset(ctx, oid, fr, leaf, sill=0.07 if shed else 0.04, fan_lights=2 if oid == 'd_balcony' else 1)
    own, sur = _own(ctx, fr, R), (fr.get('surround') or {}).get(R)
    if sur == 'dark_screen':
        feat = _recess(ctx, R, fr, MR)
        if feat and _bounds_w(feat, MR) > fr['width'] + 0.5:          # phase-1 geometry: one screen across the wall
            _dark_screen(ctx, R, fr, MR)
        elif feat:
            _dark_recess(ctx, own, oid, fr, MR, feat, seat=False)
    elif sur == 'dark_timber_reveal':                                 # jambs and head lined with dark-stained boards,
        s = MB().at(MR)                                               # a head board on the wall over the frame head
        _lining(s, fr['width'] / 2, fr['top'], _ext_depth(fr, wall_t(fr))[1], 0.0, 'dark_stain')
        s.box((-fr['width'] / 2, 0.0, fr['top']), (fr['width'] / 2, 0.012, fr['top'] + DARK_HEAD), 'dark_stain', grain=0)
        _finish(ctx, s, f'{own}.{oid}.surround', own, surround=sur)


def _door_back(ctx, oid, fr):
    """White uPVC back door: frame in the plaster reveal, obscure toplight, half-glazed (obscure) leaf with a square
    cat flap (corrections K5)."""
    def leaf(mb, gb, lw, lh, t, zb, west):
        info = leaf_upvc_back(mb, gb, lw, lh, t)
        lever_handle(mb, info['handle_x'], info['handle_z'] - zb, t, (0.030, 0.240), 0.11, cyl=True)

    _upvc_doorset(ctx, oid, fr, leaf, jamb=0.045, sill=0.02, flange=0.05, fan_glass='glass_obscure')


def _door_timber_pair(ctx, oid, fr):
    """Shed store doors (shed_oxblood_pair): painted timber frame 45 mm, pair of two-panel leaves (tall raised-and-
    fielded panel over a short one), turned knobs, rebated meeting stiles, opening outward."""
    R, sgR = _inside(fr)
    own = _own(ctx, fr, R)
    MR, MO, Tw = side_frame(fr, sgR), side_frame(fr, -sgR), wall_t(fr)
    hw, top, t, m, fw = fr['width'] / 2, fr['head'], 0.035, 'oxblood', 0.045
    ya, yb = _ext_depth(fr, Tw)
    f = MB().at(MR)
    for sx in (1, -1):
        f.box((sx * hw, ya, 0), (sx * (hw - fw), yb, top), m, 0.002, grain=2)
    f.box((-hw + fw, ya, top - fw), (hw - fw, yb, top), m, 0.002, grain=0)
    _finish(ctx, f, f'{own}.{oid}.frame', own)
    lw, lh = hw - fw - GAP - 0.0015, top - fw - GAP - FLOOR_GAP
    st, bot, r0, r1, tp = 0.12, 0.20, 0.82, 0.95, 0.10

    def build(mb, gb, first):
        _frame_boxes(mb, lw, lh, t, m, st, tp, bot, rails=[(r0, r1)])
        _panel(mb, st, bot, lw - st, r0, t, m)
        _panel(mb, st, r1, lw - st, lh - tp, t, m)
        if first:
            _astragal(mb, lw, lh, t, m)
        M0 = mb.M.copy()
        mb.at(M0 @ T((lw - 0.055, t / 2, 0.95)) @ RX(-math.pi / 2))
        mb.lathe([(0, 0), (0.008, 0), (0.008, 0.014), (0.0175, 0.020), (0.0175, 0.028), (0.010, 0.034), (0, 0.035)], m, 12)
        mb.at(M0)

    for i, hx in enumerate((1, -1)):
        hang_leaf(ctx, f'{own}.{oid}.leaf.{i}', own, MO, hx * (hw - fw - GAP), t, hx, 0.0,
                  lambda mb, gb, first=(i == 0): build(mb, gb, first), yA=-(Tw + ya), h=lh, door=oid)


def _hatch(ctx, oid, fr):
    """Eaves hatch (white_flush_pair, loft_office.md 2.3): the json hole is the OUTER size of the white frame; a pair
    of flat 18 mm lay-on leaves on concealed hinges at the outer stiles, brass mushroom knobs by the meeting edge,
    each swinging 110 degrees into the room named by swingInto. The frame lines the hole through the knee wall."""
    sg = fr['swing_sign'] or 1
    pos, neg = _room_names(fr)
    A = pos if sg > 0 else neg
    MA, Tw = side_frame(fr, sg), wall_t(fr)
    hw, z0, z1, m, t = fr['width'] / 2, fr['sill'], fr['head'], 'joinery_white', 0.018
    fx, fz, yf = 0.075, 0.05, 0.010                                   # frame members, how far the frame stands proud
    f = MB().at(MA)
    for sx in (1, -1):
        f.box((sx * hw, -Tw, z0), (sx * (hw - fx), yf, z1), m, 0.003)
    for za, zb in ((z1 - fz, z1), (z0, z0 + fz)):
        f.box((-hw + fx, -Tw, za), (hw - fx, yf, zb), m, 0.003)
    _finish(ctx, f, f'{A}.{oid}.frame', A)
    lap = 0.008
    lw, lh = hw - fx + lap - 0.0015, z1 - z0 - 2 * fz + 2 * lap

    def build(mb, gb):
        mb.box((0, -t / 2, 0), (lw, t / 2, lh), m, 0.002)
        M0 = mb.M.copy()
        mb.at(M0 @ T((lw - 0.06, t / 2, lh / 2)) @ RX(-math.pi / 2))
        mb.lathe([(0, 0), (0.006, 0), (0.006, 0.012), (0.015, 0.016), (0.015, 0.022), (0, 0.026)], 'brass', 12)
        mb.at(M0)

    for i, hx in enumerate((1, -1)):
        west = (MA @ Vector((hx * (hw - fx + lap), 0, 0))).x < fr['center'].x
        hang_leaf(ctx, f'{A}.{oid}.leaf.{i}', A, MA, hx * (hw - fx + lap), t, hx, 0.0, build, yA=yf + 0.001 + t,
                  zb=z0 + fz - lap, h=lh, hinges=False, blocks=False, label='Eaves hatch',
                  swing=HATCH_WEST_DEG.get(oid, 110.0) if west else 110.0, door=oid)


def _door_pocket(ctx, oid, fr):
    """Sliding oak pocket door: oak lining with a dark pocket slot / head track, surrounds both sides, 4-panel leaf
    with brass flush pulls. POCKET_OPEN doors are modelled open (standing POCKET_PROJECT out of the pocket, as the
    WC door was filmed); the others shut."""
    M, Tw = side_frame(fr, 1), wall_t(fr)
    hw, top, t = fr['width'] / 2, fr['head'], 0.035
    sl = fr.get('slideToward') or (-fr['along'].x, -fr['along'].y)
    sx = 1 if (sl[0] * fr['along'].x + sl[1] * fr['along'].y) > 0 else -1          # pocket side in frame M
    pos, neg = _room_names(fr)
    A = pos
    f = MB().at(M)
    _lining(f, hw, top, -Tw, 0.0, 'oak')
    ym = -Tw / 2
    f.box((sx * (hw - SKIN + 0.0004), ym - 0.024, 0), (sx * (hw - SKIN - 0.0012), ym + 0.024, top - SKIN), 'black')
    f.box((-hw + SKIN, ym - 0.024, top - SKIN - 0.0012), (hw - SKIN, ym + 0.024, top - SKIN + 0.0004), 'black')
    _finish(ctx, f, f'{A}.{oid}.lining', A)
    for room, sg in ((pos, 1), (neg, -1)):
        sur = mo.surround_of(fr, room)
        if sur:
            s = MB().at(side_frame(fr, sg))
            _surround(s, sur, oid, room, hw, top)
            _finish(ctx, s, f'{room}.{oid}.surround', room, surround=sur)
    lw, lh = fr['width'] + 0.05, top - SKIN - GAP - FLOOR_GAP
    mb, gb = MB(), MB()
    leaf_oak_4panel(mb, gb, lw, lh, t)
    flush_pull(mb, 0.055, 0.95 - FLOOR_GAP, t)
    is_open = oid in POCKET_OPEN
    travel = 2 * (hw - SKIN) - 0.001 - POCKET_PROJECT                # from POCKET_PROJECT out of the pocket to the far jamb
    x_lead = sx * (hw - SKIN - 0.001) - sx * (POCKET_PROJECT if is_open else POCKET_PROJECT + travel)
    Mo = M @ T((x_lead, ym, FLOOR_GAP)) @ (RZ(math.pi) if sx < 0 else Matrix.Identity(4))
    ob = _finish(ctx, mb, f'{A}.{oid}.leaf', A, Mo, door=oid, slide=1, projects=POCKET_PROJECT if is_open else lw)
    d = M.to_3x3() @ Vector(((-sx if is_open else sx) * travel, 0, 0))
    IX.tag(ob, 'slide', label=LABEL.get(oid, 'Door'), d=d, blocks=oid, **({'on': True} if is_open else {}))


# --------------------------------------------------------------------------- windows
def _glaze(f, g, a0, a1, c0, c1, ya, yb, glass='glass', m='upvc_white'):
    """20 mm glazing unit + bead filling the clear rectangle a0..a1, c0..c1 of a frame between depths ya..yb."""
    ym = (ya + yb) / 2
    Mg, Mf = g.M.copy(), f.M.copy()
    g.at(Mg @ T((0, ym, 0)))
    _glass(g, a0 - 0.006, c0 - 0.006, a1 + 0.006, c1 + 0.006, glass, 0.020)
    g.at(Mg)
    f.at(Mf @ T((0, ym, 0)))
    _glazing_bead(f, a0, c0, a1, c1, yb - ya, m, 0.020, 0.012)
    f.at(Mf)


def _ring(f, a0, a1, c0, c1, fw, y0, y1, m='upvc_white'):
    f.box((a0, y0, c0), (a0 + fw, y1, c1), m, 0.003)
    f.box((a1 - fw, y0, c0), (a1, y1, c1), m, 0.003)
    f.box((a0 + fw, y0, c1 - fw), (a1 - fw, y1, c1), m, 0.003)
    f.box((a0 + fw, y0, c0), (a1 - fw, y1, c0 + fw), m, 0.003)
    return a0 + fw, a1 - fw, c0 + fw, c1 - fw


def upvc_light(f, g, x0, x1, z0, z1, ya, yb, face=0.045, glass='glass', sash=False, m='upvc_white'):
    """White uPVC frame filling the rectangle x0..x1, z0..z1 between depths ya..yb (side frame),
    20 mm glazing unit and bead; sash=True adds the frame-within-frame of an opening light.
    -> clear glass rectangle (x0, x1, z0, z1)."""
    a0, a1, c0, c1 = _ring(f, x0, x1, z0, z1, face, ya, yb, m)
    if sash:
        a0, a1, c0, c1 = _ring(f, a0 - 0.012, a1 + 0.012, c0 - 0.012, c1 + 0.012, 0.045, ya + 0.012, yb + 0.012, m)
    _glaze(f, g, a0, a1, c0, c1, ya, yb, glass, m)
    return a0, a1, c0, c1


# shed windows carry no lights / sashes in the spec json: shed.md 2.2 (two top-hung fanlights over one fixed pane,
# "you can open the top two sections") and 2.4 (two equal fixed lights)
SHED_WINDOWS = {'shed_w1': dict(transomBar=1.05 + 0.62, cols=(1, 2),
                                sashes=[dict(light='fanlights', type='top_hung', swing='out', angle=30)]),
                'shed_w2': dict(lights=2, glass='glass_obscure')}   # misted (shed.md 2.4); it faces a hedge 0.8 m off
COLS3 = (0.27, 0.46, 0.27)          # width shares of a three-light window (green bedroom bay: 0.55 | 0.92 | 0.55)
SASH_DEG = {'top_hung': 20.0, 'side_hung': 45.0}
UPPER, LOWER = ('upper', 'fanlight', 'fanlights', 'centre_top'), ('lower', 'main', 'west', 'east', 'centre', 'lower_w', 'lower_e')


def _sash_of(sashes, r, c, nrow, ncol, low_col):
    """The sash json governing cell (row r from the bottom, column c) of a window, or None (fixed). low_col = the
    column index at the west / south end. Light names: all | lower main | upper fanlight(s) | west east centre |
    lower_w lower_e | centre_top (MULTILEVEL section 8)."""
    top = nrow > 1 and r == nrow - 1
    for s in sashes or ():
        k = s.get('light', 'all')
        if k == 'all':
            return s
        if (k in UPPER) != top:
            continue
        if k in ('upper', 'fanlight', 'fanlights', 'lower', 'main'):
            return s
        want = {'west': low_col, 'lower_w': low_col, 'east': ncol - 1 - low_col, 'lower_e': ncol - 1 - low_col}.get(k, (ncol - 1) / 2)
        if c == want:
            return s
    return None


def _window_upvc(ctx, oid, fr):
    """White uPVC window: outer frame FRAME_D deep at ext_reveal behind the outer face, a transom at `transomBar`,
    `lights` columns, fixed glazing or - per `sashes` - opening lights. Every sash that is not `fixed` is its own
    object (+ glass) hinged at the top (top_hung) or on a stile (side_hung), opening outward, tagged as one
    interaction group unless `operated` is false. Room-side surrounds: plaster reveal (nothing), flat white boards
    (WC), dark aedicule (dining E), dark recess with window seat (dining N)."""
    R, sgR = _inside(fr)
    own = _own(ctx, fr, R)
    MR, Tw = side_frame(fr, sgR), wall_t(fr)
    hw, z0, z1 = fr['width'] / 2, fr['sill'], fr['sill'] + fr['height']
    sur, style = (fr.get('surround') or {}).get(R), fr['style']
    extra = SHED_WINDOWS.get(oid, {}) if style == 'shed_window' else {}
    get = lambda k, d=None: fr[k] if fr.get(k) is not None else extra.get(k, d)
    glass, face, mul = get('glass') or ('glass_obscure' if 'obscure' in style else 'glass'), 0.050, 0.050
    if sur == 'flat_white_surround':                # ponytail: the WC light keeps its phase-1 place 25 mm behind the
        ya, yb, face = -0.085, -0.025, 0.072        # tiles (wc.md 2.2), not ext_reveal; spec request: extReveal for w_wc
    else:
        ya, yb = _ext_depth(fr, Tw)
    tb = get('transomBar')
    tb = tb if tb and z0 + 0.15 < tb < z1 - 0.15 else None
    rows = [(z0 + face, z1 - face)] if not tb else [(z0 + face, tb - mul / 2), (tb + mul / 2, z1 - face)]
    cols = get('cols') or (get('lights', 1),) * len(rows)
    f, g = MB().at(MR), MB().at(MR)
    _ring(f, -hw, hw, z0, z1, face, ya, yb)
    if tb:
        f.box((-hw + face, ya, tb - mul / 2), (hw - face, yb, tb + mul / 2), 'upvc_white', 0.003)
    wx = MR.to_3x3() @ Vector((1, 0, 0))            # world direction of +x of the side frame
    axis = 0 if abs(wx.x) > abs(wx.y) else 1
    out = MR.to_3x3() @ Vector((0, -1, 0))          # outward
    lap, proud, sw_ = 0.012, 0.012, 0.045
    n_sash = 0
    for r, (ca, cb) in enumerate(rows):
        n = cols[r]
        share = COLS3 if n == 3 else (1.0 / n,) * n
        clear = 2 * (hw - face) - (n - 1) * mul
        a = -hw + face
        low_col = 0 if wx[axis] > 0 else n - 1
        for c in range(n):
            b = a + share[c] * clear
            if c:
                f.box((a - mul, ya, ca), (a, yb, cb), 'upvc_white', 0.003)
            s = _sash_of(get('sashes'), r, c, len(rows), n, low_col)
            if s is None or s.get('type', 'fixed') == 'fixed':
                _glaze(f, g, a, b, ca, cb, ya, yb, glass)
                a = b + mul
                continue
            sf, sg = MB().at(MR), MB().at(MR)       # opening light: sash lapping the frame, 12 mm proud outside
            y0, y1 = ya - proud, yb - proud
            _ring(sf, a - lap, b + lap, ca - lap, cb + lap, sw_, y0, y1)
            _glaze(sf, sg, a - lap + sw_, b + lap - sw_, ca - lap + sw_, cb + lap - sw_, y0, y1, glass)
            xm, zm = (a + b) / 2, (ca + cb) / 2
            if s['type'] == 'top_hung':             # handle on the bottom rail, hinge along the head
                sf.box((xm - 0.06, y1, ca + 0.004), (xm + 0.06, y1 + 0.014, ca + 0.020), 'upvc_white', 0.003)
                sf.box((xm - 0.015, y1, ca - 0.006), (xm + 0.015, y1 + 0.022, ca + 0.030), 'upvc_white', 0.003)
                p, ax_, v = MR @ Vector((xm, y0, cb + lap)), wx, Vector((0, 0, -1))
            else:                                   # side hung: hinge on the named stile, handle on the other
                h = s.get('hinge', 'west')
                at_low = h in ('west', 'south')
                xh = a - lap if (wx[axis] > 0) == at_low else b + lap
                xf = b + lap - sw_ / 2 if xh < xm else a - lap + sw_ / 2
                if s.get('handle') == 'bottom':     # brass lever centred on the bottom rail (purple room, hr_v4_415)
                    zr = ca - lap + sw_ / 2
                    sf.box((xm - 0.016, y1, zr - 0.017), (xm + 0.016, y1 + 0.006, zr + 0.017), 'brass', 0.002)
                    sf.box((xm - 0.006, y1 + 0.006, zr - 0.006), (xm + 0.006, y1 + 0.026, zr + 0.006), 'brass', 0.002)
                    lx = 0.10 if xh < xm else -0.10                       # the lever points away from the hinge
                    sf.box((min(xm, xm + lx), y1 + 0.020, zr - 0.006), (max(xm, xm + lx), y1 + 0.032, zr + 0.006), 'brass', 0.003)
                else:
                    sf.box((xf - 0.008, y1, zm - 0.06), (xf + 0.008, y1 + 0.014, zm + 0.06), 'upvc_white', 0.003)
                    sf.box((xf - 0.015, y1, zm - 0.015), (xf + 0.015, y1 + 0.024, zm + 0.015), 'upvc_white', 0.003)
                p, ax_, v = MR @ Vector((xh, y0, zm)), Vector((0, 0, 1)), MR.to_3x3() @ Vector((xm - xh, 0, 0))
            name = f'{own}.{oid}.sash.{n_sash}'
            n_sash += 1
            obs = [o for o in (_finish(ctx, sf, name, own, door=oid, sash=s['type']), _finish(ctx, sg, name + '.glass', own)) if o]
            if s.get('operated', True):
                deg = (1 if ax_.cross(v).dot(out) > 0 else -1) * float(s.get('angle') or SASH_DEG[s['type']])
                IX.tag_many(obs, 'hinge', g=name, label='Window', p=p, a=ax_, deg=round(deg, 1))
            a = b + mul
    if oid == 'w_dining_n_e':                                         # trickle vent at the head
        f.box((-0.15, yb, z1 - 0.040), (0.15, yb + 0.012, z1 - 0.018), 'upvc_white', 0.003)
    _finish(ctx, f, f'{own}.{oid}.frame', own)
    _finish(ctx, g, f'{own}.{oid}.glass', own)
    if sur == 'dark_aedicule':
        s, m = MB().at(MR), 'dark_stain'
        dark_surround(s, hw, z1, 2.45, 0.10, 'arch_dark_window', 0.10, 0.04)
        _lining(s, hw, z1, yb, 0.0, m, z0=z0)
        s.box((-hw, 0, 0), (hw, 0.003, z0 - 0.03), m, grain=2)                                # apron
        s.box((-hw, yb - 0.002, z0 - 0.03), (hw, 0.043, z0 + 0.004), m, 0.004, grain=0)       # sill board
        _finish(ctx, s, f'{own}.{oid}.surround', own, surround=sur)
    elif sur == 'dark_recess':
        feat = _recess(ctx, R, fr, MR)
        if feat:
            _dark_recess(ctx, own, oid, fr, MR, feat, seat=True)


def _recess(ctx, R, fr, MR):
    """The `reveal` feature of room R (same level) that this opening sits at the back of, or None."""
    inv = MR.inverted()
    for f in ctx.features:
        if f['type'] != 'reveal' or f.get('room') != R or f.get('level', 'G') != fr.get('level', 'G'):
            continue
        pts = [inv @ Vector((p[0], p[1], 0)) for p in f['polygon']]
        if min(p.x for p in pts) < 0 < max(p.x for p in pts) and min(p.y for p in pts) < 0.03 and max(p.y for p in pts) > 0.03:
            return f
    return None


def _bounds_w(feat, MR):
    inv = MR.inverted()
    xs = [(inv @ Vector((p[0], p[1], 0))).x for p in feat['polygon']]
    return max(xs) - min(xs)


def _dark_recess(ctx, own, oid, fr, MR, feat, seat):
    """Dark-lined recess of the dining north wall (ground_corrections D1-D3): jamb and head boards as deep as the
    reveal, back panel between the frame and the recess head, 0.10 reeded architrave on the room face with its legs
    to the floor; for the windows a window-seat board (top = recess floor, 30 mm nosing) over a flat apron and a
    60 mm plinth. MR = side frame at the BACK of the recess (y = 0), the room face is y = D."""
    inv = MR.inverted()
    pts = [inv @ Vector((p[0], p[1], 0)) for p in feat['polygon']]
    xa, xb, D = min(p.x for p in pts), max(p.x for p in pts), max(p.y for p in pts)
    zb, zt = feat['z'][0] - fr['z0'], feat['z'][1] - fr['z0']
    m, bt = 'dark_stain', 0.012
    s = MB().at(MR)
    for x0, x1 in ((xa, xa + bt), (xb - bt, xb)):
        s.box((x0, 0, zb), (x1, D, zt), m, grain=2)
    s.box((xa + bt, 0, zt - bt), (xb - bt, D, zt), m, grain=0)
    if zt - bt - fr['top'] > 0.004:                                   # back panel over the frame head
        s.box((xa + bt, 0, fr['top']), (xb - bt, 0.006, zt - bt), m, grain=0)
    s.sweep(PROFILES['arch_dark_window'], [(xb, D, 0), (xb, D, zt), (xa, D, zt), (xa, D, 0)], m, up=(0, 1, 0))
    if seat:
        if fr['sill'] - zb > 0.004:                                   # back panel under the frame
            s.box((xa + bt, 0, zb), (xb - bt, 0.006, fr['sill']), m, grain=0)
        s.box((xa + bt, 0.006, zb - 0.036), (xb - bt, D + 0.030, zb + 0.004), m, 0.004, grain=0)      # seat board
        s.box((xa, D, 0.06), (xb, D + 0.006, zb - 0.036), m, grain=2)                         # apron
        s.box((xa, D, 0), (xb, D + 0.014, 0.06), m, 0.002, grain=0)                           # plinth
    _finish(ctx, s, f'{own}.{oid}.surround', own, surround='dark_recess' if seat else 'dark_screen')


def _dark_screen(ctx, R, fr, MR):
    """PHASE-1 GEOMETRY (one reveal across the whole dining N wall, dining.md 2.3): jamb posts filling the ends of
    the 0.22 recess, architrave on the room face, soffit lining, back panelling round the three openings (aprons,
    fills over the heads) and the two posts beside the French-door frame."""
    c0 = fr['center']
    feat = next((f for f in ctx.features if f['type'] == 'reveal' and f.get('room') == R
                 and min(p[0] for p in f['polygon']) < c0.x < max(p[0] for p in f['polygon'])
                 and min(p[1] for p in f['polygon']) - 0.3 < c0.y < max(p[1] for p in f['polygon']) + 0.3), None)
    if feat is None:
        return
    inv = MR.inverted()
    pts = [inv @ Vector((p[0], p[1], 0)) for p in feat['polygon']]
    xa, xb = min(p.x for p in pts), max(p.x for p in pts)
    D, zt, aw, m = max(p.y for p in pts), feat['z'][1], 0.10, 'dark_stain'
    s = MB().at(MR)
    for x0, x1 in ((xa, xa + aw), (xb - aw, xb)):
        s.box((x0, 0, 0), (x1, D, zt), m, grain=2)
    s.sweep(PROFILES['arch_dark_window'], [(xb - aw, D, 0), (xb - aw, D, zt), (xa + aw, D, zt), (xa + aw, D, 0)],
            m, up=(0, 1, 0))
    s.box((xa + aw, 0, zt - 0.004), (xb - aw, D, zt), m, grain=0)
    ops = []
    for o in ctx.openings.values():
        if o['wall'] == fr['wall'] and (o.get('surround') or {}).get(R) == 'dark_screen':
            c = inv @ Vector((o['center'][0], o['center'][1], 0))
            top = max(o['sill'] + o['height'], (o.get('transom') or {}).get('height', 0.0))
            ops.append((c.x - o['width'] / 2, c.x + o['width'] / 2, o['sill'], top))
    x = xa + aw
    for x0, x1, z0, z1 in sorted(ops):
        if x0 - x > 0.002:
            s.box((x, 0, 0), (x0, 0.004, zt - 0.004), m, grain=2)
        if z0 > 0.002:
            s.box((x0, 0, 0), (x1, 0.004, z0), m, grain=2)
        if zt - 0.004 - z1 > 0.002:
            s.box((x0, 0, z1), (x1, 0.004, zt - 0.004), m, grain=0)
        x = x1
    if xb - aw - x > 0.002:
        s.box((x, 0, 0), (xb - aw, 0.004, zt - 0.004), m, grain=2)
    for sx in (1, -1):
        s.box((sx * (fr['width'] / 2 + 0.045), 0.004, 0), (sx * (fr['width'] / 2 + 0.165), D - 0.004, zt - 0.004), m, 0.003, grain=2)
    _finish(ctx, s, f'{R}.screen', R, surround='dark_screen')


def _shutter(sb, x0, x1, z0, z1, y0, y1, m='shutter_white', louvres=None):
    """Plantation shutter panel: 50 stiles, 90 rails, 63 mm elliptical louvres at ~52 pitch, shut
    (tilt 75 deg, blades sloping down toward the room, +Y): neighbours overlap by ~9 mm, so nothing
    shows through from eye height on either side (f_0019). louvres: [(MB, tilt deg)] - the blades go there, once per
    tilt, instead of into sb (the bay's open / shut louvre objects)."""
    st, rl = 0.050, 0.090
    sb.box((x0, y0, z0), (x0 + st, y1, z1), m, 0.002)
    sb.box((x1 - st, y0, z0), (x1, y1, z1), m, 0.002)
    sb.box((x0 + st, y0, z0), (x1 - st, y1, z0 + rl), m, 0.002)
    sb.box((x0 + st, y0, z1 - rl), (x1 - st, y1, z1), m, 0.002)
    n = max(1, int(round((z1 - z0 - 2 * rl) / 0.052)))
    pitch = (z1 - z0 - 2 * rl) / n
    a, b, ym = 0.0315, 0.0045, (y0 + y1) / 2
    hexa = [(-a, 0), (-0.6 * a, b), (0.6 * a, b), (a, 0), (0.6 * a, -b), (-0.6 * a, -b)]
    for mb, tilt in louvres or [(sb, 75.0)]:
        ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        for i in range(n):
            zc = z0 + rl + (i + 0.5) * pitch
            mb.prism([(x0 + st + 0.001, ym + p * ca + q * sa, zc - p * sa + q * ca) for p, q in hexa],
                     (x1 - x0 - 2 * st - 0.002, 0, 0), m)


def _bay_window(ctx, oid, fr):
    """Mock-Tudor bay light group (living.md 2.3): dark timber posts / mullions / transom / head and
    corner cladding, white uPVC lower lights and fanlights, white plantation shutters on the lower
    lights (room side) - one panel per light whose louvres tilt open / shut (SHUTTER_TILT) - and the moulded dark sill
    board round the bay (built with the front opening).
    The west return also gets the vestibule-side white two-light architraves.
    ponytail: the uPVC sits 15 mm behind the outer face (the shutters need the rest of the 0.12 wall), not at
    fr['ext_reveal']; the spec should carry extReveal 0.015 for the two exterior bay openings."""
    R = next((r for r in fr['connects'] if any(f['type'] == 'bay' and f.get('room') == r for f in ctx.features)),
             next(r for r in fr['connects'] if r != 'outside'))
    sgR = side_of(fr, R)
    MR, Tw = side_frame(fr, sgR), wall_t(fr)
    hw, z0, z1 = fr['width'] / 2, fr['sill'], fr['sill'] + fr['height']
    zt0, tr, tm = (fr.get('transom') or {}).get('height', 1.80), 0.13, 'dark_stain'
    n, lwid, mul = fr.get('lights', 1), fr.get('lightWidth', fr['width']), fr.get('mullion', 0.15)
    x = -(n * lwid + (n - 1) * mul) / 2
    spans = [(x + i * (lwid + mul), x + i * (lwid + mul) + lwid) for i in range(n)]
    yt0, yt1 = max(-Tw + 0.005, -0.110), 0.012
    d = MB().at(MR)
    _lining(d, hw, z1, yt0, 0.0, tm, z0=z0, sill=True)
    edges = [-hw] + [v for sp in spans for v in sp] + [hw]
    for i in range(0, len(edges), 2):                                 # posts / mullions between the lights
        if edges[i + 1] - edges[i] > 0.002:
            d.box((edges[i], yt0, z0), (edges[i + 1], yt1, z1), tm, 0.003, grain=2)
    for a, b in spans:
        d.box((a, yt0, zt0), (b, yt1, zt0 + tr), tm, 0.003, grain=0)  # transom
    bay = next((f for f in ctx.features if f['type'] == 'bay' and f.get('room') == R), None)
    lo, hi = -hw - 0.12, hw + 0.12
    inv = MR.inverted()
    if bay:
        on = [q.x for q in (inv @ Vector((p[0], p[1], 0)) for p in bay['polygon']) if abs(q.y) < 0.02]
        if len(on) >= 2:
            lo, hi = max(lo, min(on)), min(hi, max(on))
    for a, b in ((lo, -hw), (hw, hi)):                                # corner / jamb post cladding on the wall
        if b - a > 0.002:
            d.box((a, 0, z0), (b, yt1, z1), tm, 0.003, grain=2)
    zh = z1 + 0.20                                                    # head board: up to the underside of the cornice,
    ck = (mo.TRIM.get(R) or {}).get('cornice')                        # never behind its fascia (same 12 mm plane: z-fight)
    ck = ck[0] if isinstance(ck, list) else ck
    if ck:
        zh = min(zh, ctx.ceil_z(R) - fr['z0'] - mo.profile_size(ck['profile'])[1])
    d.box((lo, 0, z1), (hi, yt1, zh), tm, 0.003, grain=0)
    _finish(ctx, d, f'{R}.{oid}.timber', R)
    u, g = MB().at(MR), MB().at(MR)
    ya = -Tw + (0.03 if Tw > 0.18 else 0.015)
    yb = ya + 0.06
    other = fr['room_neg'] if sgR > 0 else fr['room_pos']
    # The return seen from the vestibule (f_0019): one architrave, a thin lining, then glass 0.43 wide
    # (68 % of the architrave's outer width), so its lights are fixed with a slim 22 mm sightline.
    slim = (fr.get('surround') or {}).get(other) == 'white_architrave_two_lights'
    for i, (a, b) in enumerate(spans):
        upvc_light(u, g, a, b, z0, zt0, ya, yb, 0.022 if slim else 0.055)
        opener = not slim and (n == 1 or i in (0, n - 1))
        upvc_light(u, g, a, b, zt0 + tr, z1, ya, yb, 0.022 if slim else 0.045, sash=opener)
        if opener:                                                    # white stay handle on the bottom rail
            u.box(((a + b) / 2 - 0.06, yb + 0.012, zt0 + tr + 0.045), ((a + b) / 2 + 0.06, yb + 0.026, zt0 + tr + 0.060),
                  'upvc_white', 0.003)
        # shutter panel (round 4: it no longer swings, its louvres tilt; SHUTTER_TILT)
        sh, lo_, ls_ = MB().at(MR), MB().at(MR), MB().at(MR)
        _shutter(sh, a + 0.005, b - 0.005, z0 + 0.005, zt0 - 0.003, -0.042, -0.014,
                 louvres=[(lo_, SHUTTER_TILT[0]), (ls_, SHUTTER_TILT[1])])
        name = f'{R}.{oid}.shutter.{i}'
        ob = _finish(ctx, sh, name, R, door=oid)                      # the panel: clicked, stays put
        IX.tag(ob, 'trigger', g=name, label='Shutter')
        IX.tag(_finish(ctx, lo_, name + '.louvres', R), 'show', g=name, when=0, fx='none')
        IX.tag(_finish(ctx, ls_, name + '.louvres_shut', R, lm='dynamic'), 'show', g=name, when=1, fx='none')
    _finish(ctx, u, f'{R}.{oid}.frame', R)
    _finish(ctx, g, f'{R}.{oid}.glass', R)
    if slim:
        v = MB().at(side_frame(fr, -sgR))
        yv = -(Tw + ya) + 0.0                                         # uPVC face seen from this side
        # upper light head: 0.05 under the frame head, or its architrave 0.10 under a ceiling haunch on this wall
        zu = z1 - 0.05
        k = 0 if abs(fr['normal'][0]) > 0.5 else 1
        face = fr['center'][k] + fr['normal'][k] * (fr['face_pos'] if -sgR > 0 else fr['face_neg'])
        for h in ctx.features:
            if h['type'] == 'ceiling_haunch' and h.get('room') == other and abs(h.get('wallAt', 1e9) - face) < 0.02:
                zu = min(zu, h['z'][0] - fr['z0'] - 0.10 - mo.profile_size('arch_vest_window')[0])
        for za, zb in ((zt0, zt0 + 0.17), (zu, z1)):                  # white wall bands between / above the lights
            v.box((-hw, yv, za), (hw, 0.001, zb), 'plaster_white')
        for za, zb in ((z0, zt0), (zt0 + 0.17, zu)):
            _lining(v, hw, zb, yv, 0.0, 'joinery_white', z0=za, sill=True)
            architrave(v, 'arch_vest_window', hw, zb, z0=za, closed=True)
        _finish(ctx, v, f'{other}.{oid}.surround', other, surround='white_architrave_two_lights')
    if bay and n > 1:                                                 # moulded sill board round the three sides
        ye = {}
        for k, o in ctx.openings.items():                             # the two return (cheek) lights
            if o.get('style') == fr['style'] and k != oid:
                q = inv @ Vector((o['center'][0], o['center'][1], 0))
                ye[1 if q.x > 0 else -1] = q.y + o['width'] / 2 + 0.12
        zs = z0 - 0.09
        path = [(lo, 0, zs), (hi, 0, zs)]
        if -1 in ye:
            path.insert(0, (lo, ye[-1], zs))
        if 1 in ye:
            path.append((hi, ye[1], zs))
        sb = MB().at(MR)
        sb.sweep(PROFILES['bay_sill'], path, tm)
        _finish(ctx, sb, f'{R}.bay.sill', R)


# --------------------------------------------------------------------------- entry point
BUILDERS = {'oak_4panel': _door_internal, 'oak_glazed': _door_internal, 'mahogany_glazed_double': _door_mahogany,
            'white_back_door': _door_back, 'pocket_oak': _door_pocket, 'white_upvc_fixed': _window_upvc,
            'white_upvc_obscure': _window_upvc, 'white_upvc_casement': _window_upvc,
            'white_upvc_two_light': _window_upvc, 'white_upvc_obscure_top_hung': _window_upvc,
            'shed_window': _window_upvc, 'dark_timber_white_upvc_shutters': _bay_window,
            'white_flush_pair': _hatch, 'shed_french': _door_french, 'shed_oxblood_pair': _door_timber_pair}
SURROUNDS = ('plain_architrave', 'pediment', 'dark_architrave', 'dark_aedicule', 'dark_screen', 'plaster_reveal',
             'flat_white_surround', 'white_upvc_frame', 'mahogany_frame', 'white_architrave_two_lights', 'dark_timber',
             'cornice_hood_on_consoles', 'pediment_scrolled', 'pediment_tall_plain', 'pediment_triangular',
             'dark_timber_reveal', 'dark_recess')
NO_JOINERY = ('arch', 'opening')        # plain_semicircular_arch, segmental_arch_corbels: plaster only (shell / trim)


def builder_for(o):
    if o.get('style') == 'white_glazed_double':
        return _door_french if o['type'] == 'french_door' else _door_street
    return BUILDERS.get(o.get('style'))


def validate(ctx):
    """-> list of problems: style / surround keys in the spec this module does not know."""
    out = []
    for oid, o in ctx.openings.items():
        if o.get('style') and o['type'] not in NO_JOINERY and builder_for(o) is None:
            out.append(f'{oid}: no builder for style {o["style"]!r}')
        out += [f'{oid}: unknown surround {k!r} ({r})' for r, k in (o.get('surround') or {}).items() if k not in SURROUNDS]
    return out


def build_opening(ctx, oid):
    """Build the joinery of one opening (frame / lining, surrounds, leaves, sashes, glass, furniture). Everything is
    measured from fr['z0'] (the opening's floorZ); a door with a sill (d_loft, 0.27 above the platform) is built from
    its threshold."""
    o = ctx.openings[oid]
    fr = ctx.opening_frame(oid)
    if fr.get('virtual') or o['type'] in NO_JOINERY or not o.get('style'):
        return
    fn = builder_for(o)
    if fn is None:
        raise KeyError(f'joinery: no builder for style {o["style"]!r} ({oid})')
    if o['type'] in mo.DOORS and fr['sill'] > 0.001:
        s = fr['sill']
        fr = dict(fr, z0=fr['z0'] + s, head=fr['head'] - s, top=fr['top'] - s, sill=0.0)
    fn(ctx, oid, fr)


def install_openings(ctx):
    """Create the joinery for every opening of the spec (house and shed). Objects are named
    <room>.<opening id>.<part> and tagged kind='joinery'; leaf objects pivot on their hinge axis."""
    import traceback
    for msg in validate(ctx):
        print('[joinery] WARNING ' + msg)
    for oid in ctx.openings:
        try:
            build_opening(ctx, oid)
        except Exception:
            traceback.print_exc()
            print(f'[joinery] ERROR building {oid} - continuing')
            errs = getattr(ctx, 'errors', None)
            if errs is None:
                raise
            errs.append(f'joinery:{oid}')
