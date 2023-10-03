WIDTH, HEIGHT = 1600, 900
PADDING = 12
BASE_FONT_SIZE = 13
BASE_FONT_FAMILY = 'TCM_____'
BASE_FONT_FAMILY_MONOSPACE = 'consola'
N_DISPLAY = 10
N_AGE_GROUPS = 18


def tx(px: float):
    assert 0 <= px <= 1
    return px * (WIDTH - PADDING * 2)


def ty(py: float):
    assert 0 <= py <= 1
    return py * (HEIGHT - PADDING * 2)


def pad(z: float):
    return int(z + PADDING)


def font_size(p: float):
    return BASE_FONT_SIZE * p


def get_position(i_rank):
    if i_rank == N_DISPLAY:
        return 'All Others'
    if i_rank == 0:
        return 'Top'
    if i_rank == 1:
        return '2nd'
    if i_rank == 2:
        return '3rd'
    return f'{i_rank + 1}th'


DX = tx(1.0 / (N_AGE_GROUPS + 3))
DY = ty(1.0 / (N_DISPLAY + 6))
