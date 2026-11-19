"""Rectified crops of the three watercolours on the staircase walls -> blender/textures/art/stairs_p<n>.jpg.

Only the painted paper inside the white mount is kept (spec/rooms/landing1.md 11.4: P1 winter river, P2 rowing
boat, P3 jetty).  P3 has a tiny seated angler at the end of the jetty: he and his rod are painted out (privacy rule,
no people).  Run once with the system Python from the repo root; needs the private full-resolution stills
(v3 frame N is at t = N - 1 s):

    for t in 23 26 32.5; do ffmpeg -v error -ss $t -i ".../PXL_20261119_104053938.mp4" -frames:v 1 -q:v 2 \\
        reference/work/stairs2026/v3_t$t.jpg; done
    python blender/rooms/stairs_art.py
"""
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'reference' / 'work' / 'stairs2026'
OUT = ROOT / 'blender' / 'textures' / 'art'
W, H = 900, 600                                    # 3:2, the painted paper is about 0.30 x 0.20 m

# name: (still, paper quad TL TR BR BL in 1080 x 1920 still pixels, polygons to paint out in still pixels)
ART = {
    'p1': ('v3_t23', [(358, 695), (808, 690), (776, 968), (375, 997)], []),
    'p2': ('v3_t26', [(237, 707), (843, 720), (825, 1118), (250, 1110)], []),
    'p3': ('v3_t32.5', [(243, 739), (867, 736), (858, 1155), (258, 1150)],
           [[(720, 850), (752, 850), (754, 886), (720, 886)],                   # the angler, above the planks
            [(737, 879), (782, 836), (787, 840), (742, 884)]]),                 # his rod
}


def main():
    for name, (still, quad, holes) in ART.items():
        im = cv2.imread(str(SRC / f'{still}.jpg'))
        if holes:                                  # fill each row with the clear sky beside it, then blend the rim
            mask = np.zeros(im.shape[:2], np.uint8)
            for poly in holes:
                cv2.fillPoly(mask, [np.int32(poly)], 255)
            for y in np.nonzero(mask.any(axis=1))[0]:
                im[y, mask[y] > 0] = np.median(im[y, 795:840], axis=0)
            rim = cv2.dilate(mask, np.ones((5, 5), np.uint8)) - cv2.erode(mask, np.ones((5, 5), np.uint8))
            im = cv2.inpaint(im, rim, 3, cv2.INPAINT_TELEA)
        M = cv2.getPerspectiveTransform(np.float32(quad), np.float32([(0, 0), (W, 0), (W, H), (0, H)]))
        flat = cv2.warpPerspective(im, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        cv2.imwrite(str(OUT / f'stairs_{name}.jpg'), flat, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print('ART OK')


if __name__ == '__main__':
    main()
