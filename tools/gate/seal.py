"""Seal the site for publishing behind a password.

Copies docs/ (without test/) to --out (default build/site) with every file under assets/ and renders/ encrypted
(AES-256-GCM, 12-byte IV in front; key = PBKDF2-SHA256(password, random salt, 600k)), and writes gate.json. The viewer
(docs/js/gate.js + docs/sw.js) asks for the password and decrypts in the browser. docs/gate.json says
{"sealed": false}, so the unsealed docs/ (local dev, tests) runs without a gate.

Password: env VIEWER_PASSWORD, else the first line of .viewer-password at the repo root (git-ignored), else a prompt.
    python tools/gate/seal.py [--src docs] [--out build/site]          -> SEAL OK
"""
import argparse
import base64
import getpass
import json
import os
import shutil
import stat
import sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROOT = Path(__file__).resolve().parents[2]
ITER = 600_000
SEALED = ('assets', 'renders')
CHECK = b'home-design gate v1'
b64 = lambda b: base64.b64encode(b).decode()


def password():
    pw = os.environ.get('VIEWER_PASSWORD', '')
    f = ROOT / '.viewer-password'
    if not pw and f.exists():
        pw = (f.read_text(encoding='utf-8').splitlines() or [''])[0].strip()
    if not pw:
        pw = getpass.getpass('Viewer password: ')
    if len(pw) < 8:
        sys.exit('seal: the password needs 8 characters at least')
    return pw


def seal(src, out, pw):
    salt = os.urandom(16)
    aes = AESGCM(PBKDF2HMAC(hashes.SHA256(), 32, salt, ITER).derive(pw.encode('utf-8')))

    def enc(data):
        iv = os.urandom(12)
        return iv + aes.encrypt(iv, data, None)

    if out.exists():                    # the deploy repo inside it has read-only git objects on Windows
        shutil.rmtree(out, onexc=lambda fn, path, _: (os.chmod(path, stat.S_IWRITE), fn(path)))
    shutil.copytree(src, out, ignore=shutil.ignore_patterns('test'))
    n = 0
    for d in SEALED:
        for f in sorted((out / d).rglob('*')):
            if f.is_file():
                f.write_bytes(enc(f.read_bytes()))
                n += 1
    gate = {'v': 1, 'kdf': 'PBKDF2-SHA256', 'iter': ITER, 'salt': b64(salt), 'check': b64(enc(CHECK))}
    (out / 'gate.json').write_text(json.dumps(gate), encoding='utf-8')
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=str(ROOT / 'docs'))
    ap.add_argument('--out', default=str(ROOT / 'build' / 'site'))
    a = ap.parse_args()
    src, out = Path(a.src).resolve(), Path(a.out).resolve()
    if out in (src, ROOT) or src.is_relative_to(out) or out.is_relative_to(src):   # never wipe the source
        sys.exit(f'seal: --out {out} must lie outside --src {src}')
    n = seal(src, out, password())
    size = sum(f.stat().st_size for f in out.rglob('*') if f.is_file() and '.git' not in f.parts)
    print(f'[seal] {n} files encrypted under {", ".join(SEALED)}; {size / 1048576:.1f} MB in {out}')
    print('SEAL OK')


if __name__ == '__main__':
    main()
