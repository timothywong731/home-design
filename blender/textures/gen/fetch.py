"""Download the CC0 Poly Haven source maps used by make_all.py into build/texsrc/<asset>/ (git-ignored).
Run: python -I blender/textures/gen/fetch.py
Only the processed, colour-corrected outputs in blender/textures/*.jpg are committed."""
import json, os, sys, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SRC = os.path.join(ROOT, 'build', 'texsrc')
UA = {'User-Agent': 'texture-fetch/1.0'}

# asset id -> resolution. Maps fetched: Diffuse, nor_gl, Rough (jpg).
ASSETS = {
    'oak_veneer_01': '2k', 'oak_veneer_03': '2k', 'ash_veneer': '2k', 'sapele_veneer_02': '2k',
    'cherry_veneer': '2k', 'smoked_walnut_veneer': '2k', 'black_walnut_veneer_01': '2k',
    'washed_grey_oak_veneer': '2k', 'grey_oak_veneer_01': '2k',
    'velour_velvet': '2k', 'rough_linen': '1k', 'caban': '1k', 'dirty_carpet': '2k',
    'polar_fleece': '1k', 'marble_01': '2k', 'white_plaster_02': '1k', 'painted_plaster_wall': '1k',
}
MAPS = ('Diffuse', 'nor_gl', 'Rough')


def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(path, 'wb') as f:
        f.write(r.read())


def main(only=None):
    for aid, res in ASSETS.items():
        if only and aid not in only:
            continue
        d = os.path.join(SRC, aid)
        os.makedirs(d, exist_ok=True)
        meta = os.path.join(d, 'files.json')
        get(f'https://api.polyhaven.com/files/{aid}', meta)
        files = json.load(open(meta, encoding='utf8'))
        for m in MAPS:
            if m not in files:
                print('  (no', m, 'for', aid, ')')
                continue
            url = files[m][res]['jpg']['url']
            get(url, os.path.join(d, f'{m}.jpg'))
        print('ok', aid, res, sorted(os.listdir(d)))


if __name__ == '__main__':
    main(set(sys.argv[1:]))
