"""Auxiliary map sets shared by constant-colour materials - all synthesised."""
import numpy as np
from common import save, reg, normal, orm, noise

SYN = 'synthesised by gen/misc.py'


def main():
    # brushed stainless / nickel: fine streaks along U; roughness varies with the streaks, metallic 1
    N, P = 512, 0.30
    st = noise(N, N, 1.2, 4.0, 101, aniso=(0, 70))
    n = save('brushed_nrm', normal(0.000015 * st, P / N), SYN)
    o = save('brushed_orm', orm(np.clip(0.30 + 0.07 * st, 0.12, 0.6), metal=np.ones((N, N), np.float32)), SYN)
    reg('_brushed', None, (P, P), nrm=n, orm=o, rough=0.30, metal=1.0, note='streaks along U')

    # roller-applied emulsion: faint orange-peel stipple for matt wall paint
    N, P = 1024, 1.0
    h = 0.00004 * noise(N, N, 2.0, 7.0, 102) + 0.0003 * noise(N, N, 150, 600, 103)
    n = save('paint_nrm', normal(h, P / N), SYN)
    reg('_paint', None, (P, P), nrm=n, rough=0.9, note='shared by materials.paint() for matt walls')

    # obscure "stippled" glazing (street doors, WC window)
    N, P = 512, 0.15
    n = save('glass_stipple_nrm', normal(0.0006 * noise(N, N, 5, 16, 104), P / N), SYN)
    reg('_stipple', None, (P, P), nrm=n, rough=0.15, note='obscure glass relief')
