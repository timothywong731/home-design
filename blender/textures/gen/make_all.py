"""Regenerate every texture in blender/textures/ + manifest.json + SOURCES.md.
Run (system Python 3 with numpy + opencv):
    python -I blender/textures/gen/fetch.py                # once: Poly Haven sources -> build/texsrc/
    python -I blender/textures/gen/make_all.py [woods tiles fabrics misc phase2]
Also writes build/texsrc/_tiled.jpg: every base colour tiled 2x2, to eyeball the seams."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
import common

GROUPS = ('woods', 'tiles', 'fabrics', 'misc', 'phase2')


def sources_md(manifest, sources):
    path = os.path.join(common.TEX, 'SOURCES.md')
    old = {}
    if os.path.exists(path):                       # keep rows of groups not regenerated this run
        for ln in open(path, encoding='utf8'):
            p = [c.strip() for c in ln.strip().strip('|').split('|')]
            if len(p) == 3 and p[0].endswith('.jpg'):
                old[p[0]] = p[1]
    old.update(sources)
    files = sorted(f for f in os.listdir(common.TEX) if f.endswith('.jpg'))
    with open(path, 'w', encoding='utf8') as f:
        f.write('# Texture sources and licences\n\n'
                'Every file here is produced by `gen/make_all.py`. "Poly Haven CC0" = a map from the named asset at\n'
                'https://polyhaven.com/a/<asset> (licence CC0 1.0, no attribution required), processed as described.\n'
                '"synthesised" = generated from scratch by the named script in `gen/` (project code, no third-party\n'
                'content). Nothing in this directory is taken from the reference video.\n'
                '`art/` (rectified crops of paintings / rug / tapestry patterns; BRIEF privacy rules apply) is not generated\n'
                'here: whoever adds a crop records its source frame in `art/SOURCES.md`.\n\n'
                '| file | source | licence |\n|---|---|---|\n')
        for fn in files:
            s = old.get(fn, '?')
            f.write(f"| {fn} | {s} | {'CC0 1.0 (Poly Haven), derivative' if 'Poly Haven' in s else 'project-generated, no third-party content'} |\n")
    return files


def tiled_sheet(manifest):
    cells = []
    for k in sorted(k for k in manifest if 'base' in manifest[k]):
        im = cv2.imread(os.path.join(common.TEX, manifest[k]['base']))
        im = cv2.resize(im, (128, 128), interpolation=cv2.INTER_AREA)
        im = np.tile(im, (2, 2, 1))
        cv2.putText(im, k, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 0), 3)
        cv2.putText(im, k, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
        cells.append(im)
    while len(cells) % 7:
        cells.append(np.zeros_like(cells[0]))
    sheet = np.vstack([np.hstack(cells[i:i + 7]) for i in range(0, len(cells), 7)])
    cv2.imwrite(os.path.join(common.SRC, '_tiled.jpg'), sheet)


def main():
    todo = [a for a in sys.argv[1:] if a in GROUPS] or GROUPS
    for g in todo:
        __import__(g).main()
    manifest, sources = common.write_manifest()
    files = sources_md(manifest, sources)
    tiled_sheet(manifest)
    total = sum(os.path.getsize(os.path.join(common.TEX, f)) for f in files)
    worst = max(max(e['seam']) for e in manifest.values())
    print(f'TEXTURES OK: {len(manifest)} materials, {len(files)} jpg, {total / 1e6:.1f} MB, worst seam ratio {worst}')


if __name__ == '__main__':
    main()
