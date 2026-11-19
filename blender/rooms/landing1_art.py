"""Rectified painting crops for the first-floor landings -> blender/textures/art/landing1_<name>.jpg.

Run once with system Python (cv2) from the repo root; needs the private stills, extracted at full resolution
(reference frame N is at t = N - 0.5 s):
    ffmpeg -v error -ss <N - 0.5> -i <video> -frames:v 1 -q:v 2 reference/work/landing1/<v>_<N>.jpg
    python blender/rooms/landing1_art.py
Only the painted picture inside each frame is kept (landscapes; the people in two of them are painted out:
the strollers on the Venice bridge and the angler on the rocks of P4, spec/rooms/landing1.md section 7).
"""
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'reference' / 'work' / 'landing1'
OUT = ROOT / 'blender' / 'textures' / 'art'
S, MARGIN = 1000, 0.06          # rectified pixels per metre; margin round the outer frame

# name: (still, outer-frame quad TL TR BR BL in 720 x 1280 frame pixels, frame w, h in metres,
#        picture rectangle x0 y0 x1 y1 in rectified pixels, [inpaint polygons in rectified pixels])
ART = {
    'w1': ('v4_273', [(335, 362), (665, 372), (658, 782), (306, 760)], 0.50, 0.60, (101, 107, 509, 614),
           [[(222, 218), (266, 218), (266, 247), (222, 247)]]),                      # three figures on the bridge
    'w2': ('v4_278', [(-7, -78), (352, 172), (365, 575), (65, 588)], 0.55, 0.70, (125, 101, 557, 697), []),
    'w3': ('v4_283', [(22, 0), (548, 268), (527, 648), (30, 657)], 0.95, 0.70, (134, 130, 896, 684), []),
    'w4': ('v4_287', [(168, 250), (610, 285), (582, 642), (165, 625)], 0.72, 0.56, (114, 111, 721, 571), []),
    'w5': ('v3_145', [(70, 282), (630, 320), (620, 760), (75, 768)], 0.72, 0.56, (129, 126, 719, 564), []),
    'p4': ('v3_39', [(30, 340), (560, 224), (540, 796), (44, 730)], 0.50, 0.40, (169, 171, 454, 367),
           [dict(sky=(398, 452), poly=[(355, 213), (366, 203), (381, 203), (386, 214), (390, 227), (394, 235),   # angler
                                       (395, 248), (386, 250), (378, 243), (366, 243), (354, 238)]),
            dict(sky=(398, 452), poly=[(378, 222), (438, 195), (446, 199), (383, 232)])]),                       # his rod
}


def _fill(flat, holes):
    """Painted-out figures: a plain polygon is inpainted from its surroundings; dict(poly, sky=(x0, x1)) is filled row
    by row with the median of columns x0..x1 of the same row (clear sky beside it), then only its rim is inpainted, so
    nothing dark from the figure or the rock beside it bleeds back in."""
    mask = np.zeros(flat.shape[:2], np.uint8)
    for h in holes:
        poly = h['poly'] if isinstance(h, dict) else h
        cv2.fillPoly(mask, [np.int32(poly)], 255)
    rim = mask.copy()
    for h in holes:
        if isinstance(h, dict):
            one = np.zeros_like(mask)
            cv2.fillPoly(one, [np.int32(h['poly'])], 255)
            x0, x1 = h['sky']
            ys = np.nonzero(one.any(axis=1))[0]
            med = np.array([np.median(flat[y, x0:x1][mask[y, x0:x1] == 0], axis=0) for y in ys])
            med = cv2.GaussianBlur(med[:, None, :].astype(np.float32), (1, 9), 0)[:, 0]   # no row-to-row banding
            for y, c in zip(ys, med):
                flat[y, one[y] > 0] = c
            rim[cv2.erode(one, np.ones((5, 5), np.uint8)) > 0] = 0
    return cv2.inpaint(flat, cv2.dilate(rim, np.ones((3, 3), np.uint8)), 3, cv2.INPAINT_TELEA)


def main(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (still, quad, w, h, (x0, y0, x1, y1), holes) in ART.items():
        if only and name not in only:
            continue
        im = cv2.imread(str(SRC / f'{still}.jpg'))
        k = im.shape[1] / 720
        m = MARGIN * S
        dst = np.float32([(m, m), (m + w * S, m), (m + w * S, m + h * S), (m, m + h * S)])
        H = cv2.getPerspectiveTransform(np.float32(quad) * k, dst)
        flat = cv2.warpPerspective(im, H, (int(w * S + 2 * m), int(h * S + 2 * m)), flags=cv2.INTER_CUBIC,
                                   borderMode=cv2.BORDER_REPLICATE)
        if holes:
            flat = _fill(flat, holes)
        cv2.imwrite(str(OUT / f'landing1_{name}.jpg'), flat[y0:y1, x0:x1], [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(name, x1 - x0, y1 - y0)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
